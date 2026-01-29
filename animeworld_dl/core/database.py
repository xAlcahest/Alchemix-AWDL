"""
AnimeWorld Downloader - Database Module
SQLite database for tracking downloads and cache
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from ..ui.logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database manager"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row  # Enable column access by name

            cursor = self.conn.cursor()

            # Anime table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anime (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT,
                    description TEXT,
                    genres TEXT,
                    total_episodes INTEGER,
                    is_dub BOOLEAN,
                    added_date TEXT,
                    last_updated TEXT
                )
            """)

            # Episodes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    id TEXT PRIMARY KEY,
                    anime_id TEXT NOT NULL,
                    episode_number INTEGER NOT NULL,
                    season INTEGER DEFAULT 1,
                    title TEXT,
                    url TEXT,
                    video_url TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    downloaded BOOLEAN DEFAULT 0,
                    download_date TEXT,
                    FOREIGN KEY (anime_id) REFERENCES anime(id)
                )
            """)

            # Download queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS download_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anime_id TEXT NOT NULL,
                    episode_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    added_date TEXT,
                    started_date TEXT,
                    completed_date TEXT,
                    error_message TEXT,
                    FOREIGN KEY (anime_id) REFERENCES anime(id),
                    FOREIGN KEY (episode_id) REFERENCES episodes(id)
                )
            """)

            # Cache table for scraped data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at TEXT
                )
            """)

            # Settings/metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_anime_id
                ON episodes(anime_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_episodes_downloaded
                ON episodes(downloaded)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_queue_status
                ON download_queue(status)
            """)

            self.conn.commit()
            logger.debug("database.initialized", path=str(self.db_path))

        except Exception as e:
            logger.error("database.init_failed", error=str(e))
            raise DatabaseError(f"Failed to initialize database: {e}")

    def add_anime(self, anime_id: str, title: str, **kwargs) -> bool:
        """Add or update anime in database"""
        try:
            cursor = self.conn.cursor()

            now = datetime.now().isoformat()

            cursor.execute("""
                INSERT OR REPLACE INTO anime
                (id, title, url, description, genres, total_episodes, is_dub, added_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT added_date FROM anime WHERE id = ?), ?),
                    ?)
            """, (
                anime_id,
                title,
                kwargs.get("url", ""),
                kwargs.get("description", ""),
                ",".join(kwargs.get("genres", [])),
                kwargs.get("total_episodes", 0),
                kwargs.get("is_dub", False),
                anime_id,  # For COALESCE check
                now,  # added_date if new
                now   # last_updated always now
            ))

            self.conn.commit()
            return True

        except Exception as e:
            logger.error("database.add_anime_failed", error=str(e))
            return False

    def add_episode(self, episode_id: str, anime_id: str, episode_number: int, **kwargs) -> bool:
        """Add or update episode in database"""
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO episodes
                (id, anime_id, episode_number, season, title, url, video_url,
                 file_path, file_size, downloaded, download_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id,
                anime_id,
                episode_number,
                kwargs.get("season", 1),
                kwargs.get("title", ""),
                kwargs.get("url", ""),
                kwargs.get("video_url", ""),
                kwargs.get("file_path", ""),
                kwargs.get("file_size", 0),
                kwargs.get("downloaded", False),
                kwargs.get("download_date", "")
            ))

            self.conn.commit()
            return True

        except Exception as e:
            logger.error("database.add_episode_failed", error=str(e))
            return False

    def mark_downloaded(self, episode_id: str, file_path: str, file_size: int = 0) -> bool:
        """Mark episode as downloaded"""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
                UPDATE episodes
                SET downloaded = 1, file_path = ?, file_size = ?, download_date = ?
                WHERE id = ?
            """, (file_path, file_size, now, episode_id))

            self.conn.commit()
            return True

        except Exception as e:
            logger.error("database.mark_downloaded_failed", error=str(e))
            return False

    def get_anime(self, anime_id: str) -> Optional[Dict]:
        """Get anime by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error("database.get_anime_failed", error=str(e))
            return None

    def get_episodes(self, anime_id: str, downloaded_only: bool = False) -> List[Dict]:
        """Get episodes for anime"""
        try:
            cursor = self.conn.cursor()

            query = "SELECT * FROM episodes WHERE anime_id = ?"
            if downloaded_only:
                query += " AND downloaded = 1"
            query += " ORDER BY season, episode_number"

            cursor.execute(query, (anime_id,))
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error("database.get_episodes_failed", error=str(e))
            return []

    def is_downloaded(self, episode_id: str) -> bool:
        """Check if episode is already downloaded"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT downloaded FROM episodes WHERE id = ?",
                (episode_id,)
            )
            row = cursor.fetchone()
            return bool(row and row[0])

        except Exception as e:
            logger.error("database.is_downloaded_check_failed", error=str(e))
            return False

    def search_anime(self, query: str) -> List[Dict]:
        """Search anime by title"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM anime
                WHERE title LIKE ?
                ORDER BY last_updated DESC
            """, (f"%{query}%",))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error("database.search_failed", error=str(e))
            return []

    def get_download_stats(self) -> Dict:
        """Get download statistics"""
        try:
            cursor = self.conn.cursor()

            # Total anime
            cursor.execute("SELECT COUNT(*) FROM anime")
            total_anime = cursor.fetchone()[0]

            # Total episodes
            cursor.execute("SELECT COUNT(*) FROM episodes")
            total_episodes = cursor.fetchone()[0]

            # Downloaded episodes
            cursor.execute("SELECT COUNT(*) FROM episodes WHERE downloaded = 1")
            downloaded_episodes = cursor.fetchone()[0]

            # Total size
            cursor.execute("SELECT SUM(file_size) FROM episodes WHERE downloaded = 1")
            total_size = cursor.fetchone()[0] or 0

            return {
                "total_anime": total_anime,
                "total_episodes": total_episodes,
                "downloaded_episodes": downloaded_episodes,
                "pending_episodes": total_episodes - downloaded_episodes,
                "total_size_bytes": total_size,
                "total_size_gb": total_size / (1024 ** 3) if total_size else 0
            }

        except Exception as e:
            logger.error("database.stats_failed", error=str(e))
            return {}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass
