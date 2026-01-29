"""
AnimeWorld Downloader - Web Scraper
Handles scraping and parsing of AnimeWorld website
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from ..ui.logger import get_logger

logger = get_logger(__name__)

BASE_URL = "https://www.animeworld.ac"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class AlchemixScraper:
    """Scraper for AnimeWorld website"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search_anime(self, query: str) -> List[Dict]:
        """
        Search for anime by title

        Args:
            query: Search query

        Returns:
            List[Dict]: List of anime results
        """
        try:
            logger.info("scraper.searching", query=query)

            # AnimeWorld search endpoint
            search_url = f"{BASE_URL}/search"
            params = {"keyword": query}

            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            results = []

            # Parse search results - adjust selectors based on actual HTML structure
            anime_cards = soup.select(".film-list .item, .anime-card, .film-poster")

            for card in anime_cards:
                try:
                    # Extract title
                    title_elem = card.select_one("a.name, .film-name, a[title]")
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href", "")

                    if not link.startswith("http"):
                        link = urljoin(BASE_URL, link)

                    # Extract ID from link (e.g., /play/anime-name.idHere)
                    anime_id = self._extract_id_from_url(link)

                    # Extract image
                    img_elem = card.select_one("img")
                    image = img_elem.get("src", "") if img_elem else ""
                    if image and not image.startswith("http"):
                        image = urljoin(BASE_URL, image)

                    # Check for dub/sub badge
                    badge = card.select_one(".dub, .badge")
                    is_dub = "DUB" in badge.get_text(strip=True).upper() if badge else False

                    results.append({
                        "title": title,
                        "id": anime_id,
                        "url": link,
                        "image": image,
                        "is_dub": is_dub
                    })

                except Exception as e:
                    logger.debug("scraper.card_parse_error", error=str(e))
                    continue

            logger.success("scraper.search_complete", count=len(results))
            return results

        except Exception as e:
            logger.error("scraper.search_failed", error=str(e))
            raise ScraperError(f"Search failed: {e}")

    def get_anime_info(self, anime_url: str) -> Dict:
        """
        Get detailed anime information and episode list

        Args:
            anime_url: URL to anime page

        Returns:
            Dict: Anime information including episodes
        """
        try:
            logger.info("scraper.fetching_info", url=anime_url)

            response = self.session.get(anime_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract anime info
            title_elem = soup.select_one("h1, .anime-title, .film-name")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Extract description
            desc_elem = soup.select_one(".description, .film-description, .plot")
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Extract genres
            genres = []
            genre_elems = soup.select(".genre a, .genres a")
            for genre in genre_elems:
                genres.append(genre.get_text(strip=True))

            # Extract episodes
            episodes = self._extract_episodes(soup, anime_url)

            # Detect seasons
            seasons = self._detect_seasons(episodes)

            anime_id = self._extract_id_from_url(anime_url)

            info = {
                "id": anime_id,
                "title": title,
                "description": description,
                "genres": genres,
                "url": anime_url,
                "episodes": episodes,
                "seasons": seasons,
                "total_episodes": len(episodes)
            }

            logger.success("scraper.info_fetched", title=title, episodes=len(episodes))
            return info

        except Exception as e:
            logger.error("scraper.info_failed", error=str(e))
            raise ScraperError(f"Failed to get anime info: {e}")

    def _extract_episodes(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract episode list from anime page"""
        episodes = []

        # Try multiple selectors for episodes
        episode_elems = (
            soup.select(".episode-list a, .episodes a, .server.active a") or
            soup.select("a[href*='/play/']")
        )

        for elem in episode_elems:
            try:
                episode_text = elem.get_text(strip=True)
                episode_url = elem.get("href", "")

                if not episode_url:
                    continue

                if not episode_url.startswith("http"):
                    episode_url = urljoin(base_url, episode_url)

                # Extract episode number from text or URL
                episode_num = self._extract_episode_number(episode_text, episode_url)

                # Extract episode ID from URL
                episode_id = self._extract_id_from_url(episode_url)

                episodes.append({
                    "number": episode_num,
                    "id": episode_id,
                    "url": episode_url,
                    "title": episode_text
                })

            except Exception as e:
                logger.debug("scraper.episode_parse_error", error=str(e))
                continue

        # Sort by episode number
        episodes.sort(key=lambda x: x["number"])

        return episodes

    def _extract_episode_number(self, text: str, url: str) -> int:
        """Extract episode number from text or URL"""
        # Try to find number in text first
        match = re.search(r'(\d+)', text)
        if match:
            return int(match.group(1))

        # Try URL
        match = re.search(r'ep?(\d+)|episode[_-]?(\d+)', url, re.IGNORECASE)
        if match:
            return int(match.group(1) or match.group(2))

        return 0

    def _detect_seasons(self, episodes: List[Dict]) -> Dict[int, List[Dict]]:
        """
        Detect seasons from episode list

        This is a heuristic approach - adjust based on actual HTML structure
        """
        if not episodes:
            return {1: []}

        # Simple approach: assume all episodes are season 1 unless we find markers
        # In future, parse season markers from HTML if available

        # Check for large gaps in episode numbers (might indicate season change)
        seasons = {1: []}
        current_season = 1

        for i, episode in enumerate(episodes):
            if i > 0:
                prev_num = episodes[i - 1]["number"]
                curr_num = episode["number"]

                # If episode number resets or has large gap, might be new season
                if curr_num < prev_num or (curr_num - prev_num) > 50:
                    current_season += 1
                    seasons[current_season] = []

            if current_season not in seasons:
                seasons[current_season] = []

            seasons[current_season].append(episode)

        return seasons

    def get_video_url(self, episode_url: str) -> str:
        """
        Extract direct video download URL from episode page

        Args:
            episode_url: URL to episode player page

        Returns:
            str: Direct download URL
        """
        try:
            logger.info("scraper.extracting_video", url=episode_url)

            response = self.session.get(episode_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Try multiple methods to extract video URL

            # Method 1: Look for alternative download link (direct MP4, not PHP)
            # Priority: alternativeDownloadLink > download attribute > downloadLink
            alternative_link = soup.select_one("a#alternativeDownloadLink, a[download][href*='.mp4']")
            if alternative_link:
                download_url = alternative_link.get("href", "")
                if download_url and download_url.endswith(".mp4"):
                    if not download_url.startswith("http"):
                        download_url = urljoin(BASE_URL, download_url)
                    logger.success("scraper.video_found", url=download_url)
                    return download_url

            # Method 2: Look for any direct .mp4 link (avoid PHP files)
            mp4_links = soup.select("a[href$='.mp4']")
            for link in mp4_links:
                download_url = link.get("href", "")
                if download_url and "download-file.php" not in download_url:
                    if not download_url.startswith("http"):
                        download_url = urljoin(BASE_URL, download_url)
                    logger.success("scraper.video_found", url=download_url)
                    return download_url

            # Method 2: Look for video source in scripts
            scripts = soup.find_all("script")
            for script in scripts:
                script_text = script.string or ""

                # Look for video URLs in JavaScript
                # Common patterns: "url":"...", 'src':'...', etc.
                url_matches = re.findall(
                    r'["\'](?:url|src|file)["\']:\s*["\']([^"\']+\.(?:mp4|m3u8|mpd))["\']',
                    script_text,
                    re.IGNORECASE
                )

                if url_matches:
                    video_url = url_matches[0]
                    if not video_url.startswith("http"):
                        video_url = urljoin(BASE_URL, video_url)
                    logger.success("scraper.video_found", url=video_url)
                    return video_url

            # Method 3: Look for iframe
            iframe = soup.select_one("iframe")
            if iframe:
                iframe_src = iframe.get("src", "")
                if iframe_src:
                    # May need to scrape the iframe page too
                    logger.info("scraper.iframe_found", src=iframe_src)
                    # Recursively get video from iframe (with protection against infinite loops)
                    if not iframe_src.startswith("http"):
                        iframe_src = urljoin(BASE_URL, iframe_src)
                    # For now, return iframe URL - may need deeper scraping
                    return iframe_src

            raise ScraperError("Could not find video URL")

        except Exception as e:
            logger.error("scraper.video_extraction_failed", error=str(e))
            raise ScraperError(f"Failed to extract video URL: {e}")

    def _extract_id_from_url(self, url: str) -> str:
        """Extract ID from AnimeWorld URL"""
        # Pattern: /play/anime-name.ID or /play/anime-name.ID/episodeID
        match = re.search(r'\.([a-zA-Z0-9]+)(?:/|$)', url)
        if match:
            return match.group(1)
        return ""


class ScraperError(Exception):
    """Custom exception for scraper errors"""
    pass
