"""
AnimeWorld Downloader - Download Manager
Handles downloading with Axel, retry logic, and resume support
"""

import os
import time
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable
from ..utils.axel_manager import AxelManager, AxelError
from ..ui.logger import get_logger, get_progress
from rich.progress import TaskID

logger = get_logger(__name__)


class DownloadManager:
    """Manages downloads using Axel with retry and resume support"""

    def __init__(self, axel_manager: AxelManager, config: dict):
        self.axel_manager = axel_manager
        self.config = config
        self.current_download: Optional[Path] = None

    def check_disk_space(self, path: Path, required_mb: int = 100) -> bool:
        """
        Check if enough disk space is available

        Args:
            path: Path to check
            required_mb: Required space in MB

        Returns:
            bool: True if enough space available
        """
        try:
            stat = shutil.disk_usage(path)
            available_gb = stat.free / (1024 ** 3)
            required_gb = required_mb / 1024

            if available_gb < required_gb:
                logger.warning("download.disk_space_low", available=f"{available_gb:.2f}")
                return False

            if available_gb < 5:  # Warn if less than 5GB
                logger.warning("download.disk_space_low", available=f"{available_gb:.2f}")

            return True

        except Exception as e:
            logger.error("download.disk_space_check_failed", error=str(e))
            return True  # Continue anyway

    def download(
        self,
        url: str,
        output_path: Path,
        connections: int = 4,
        resume: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Download file using Axel

        Args:
            url: Download URL
            output_path: Output file path
            connections: Number of connections
            resume: Enable resume support
            progress_callback: Optional callback for progress updates

        Returns:
            bool: True if download succeeded
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Check disk space if configured
            if self.config.get("download", {}).get("check_disk_space", True):
                if not self.check_disk_space(output_path.parent):
                    logger.error("download.failed", error="Insufficient disk space")
                    return False

            # Clean up partial download files from previous failed attempts
            # Axel creates .st files for resume state
            state_file = Path(str(output_path) + ".st")
            if state_file.exists():
                logger.debug("download.removing_state_file", file=str(state_file))
                state_file.unlink()

            # Also remove partial output file if it exists without state file
            if output_path.exists() and not state_file.exists():
                logger.debug("download.removing_partial_file", file=str(output_path))
                output_path.unlink()

            # Store current download for interrupt handling
            self.current_download = output_path

            logger.info("download.starting", filename=output_path.name)

            # Build Axel command
            cmd = self.axel_manager.build_command(
                url=url,
                output=str(output_path),
                connections=connections,
                user_agent=self.config.get("network", {}).get("user_agent", ""),
                speed_limit=self.config.get("network", {}).get("speed_limit", 0)
            )

            # Execute download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Monitor progress and collect output
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    logger.debug("axel.output", output=line)

                    # Parse progress if callback provided
                    if progress_callback:
                        progress_callback(line)

            process.wait()

            if process.returncode == 0:
                logger.success("download.completed", filename=output_path.name)
                self.current_download = None
                return True
            else:
                # Show last few lines of output for debugging
                error_output = "\n".join(output_lines[-5:]) if output_lines else "No output"
                logger.error("download.failed", error=f"Axel exited with code {process.returncode}", details=error_output)
                raise DownloadError(f"Axel failed (code {process.returncode}): {error_output}")

        except Exception as e:
            logger.error("download.failed", error=str(e))
            return False

    def download_with_retry(
        self,
        url: str,
        output_path: Path,
        connections: int = 4,
        max_attempts: int = 3,
        backoff: bool = True
    ) -> bool:
        """
        Download with retry and exponential backoff

        Args:
            url: Download URL
            output_path: Output file path
            connections: Number of connections
            max_attempts: Maximum retry attempts
            backoff: Use exponential backoff

        Returns:
            bool: True if download succeeded
        """
        attempt = 1
        wait_time = 1  # Initial wait time in seconds

        while attempt <= max_attempts:
            try:
                if attempt > 1:
                    logger.info("download.retrying", attempt=attempt, max_attempts=max_attempts)

                    if backoff:
                        logger.debug("download.backoff_wait", seconds=wait_time)
                        time.sleep(wait_time)
                        wait_time *= 2  # Exponential backoff

                # Attempt download
                success = self.download(url, output_path, connections)

                if success:
                    return True

                attempt += 1

            except KeyboardInterrupt:
                logger.warning("download.interrupted")
                raise

            except DownloadError as e:
                logger.error("download.attempt_failed", attempt=attempt, error=str(e))
                if attempt >= max_attempts:
                    # On final attempt, show the full error
                    logger.error("download.final_error", details=str(e))
                attempt += 1

            except Exception as e:
                logger.error("download.attempt_failed", attempt=attempt, error=str(e))
                attempt += 1

        logger.error("download.failed_all_attempts", attempts=max_attempts)
        return False

    def get_file_size(self, url: str) -> Optional[int]:
        """
        Get remote file size via HEAD request

        Args:
            url: URL to check

        Returns:
            Optional[int]: File size in bytes or None
        """
        import requests

        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            size = response.headers.get('Content-Length')
            if size:
                return int(size)
        except Exception as e:
            logger.debug("download.size_check_failed", error=str(e))

        return None

    def format_filename(
        self,
        anime_title: str,
        episode_number: int,
        season: int = 1,
        extension: str = "mp4",
        pattern: str = "original",
        original_filename: Optional[str] = None
    ) -> str:
        """
        Format filename based on pattern

        Args:
            anime_title: Anime title
            episode_number: Episode number
            season: Season number
            extension: File extension
            pattern: Naming pattern (original, season_episode, custom)
            original_filename: Original filename from server

        Returns:
            str: Formatted filename
        """
        if pattern == "original" and original_filename:
            return original_filename

        if pattern == "season_episode":
            # Format: Anime Name - S01E01.mp4
            safe_title = "".join(c for c in anime_title if c.isalnum() or c in (' ', '-', '_')).strip()
            return f"{safe_title} - S{season:02d}E{episode_number:02d}.{extension}"

        if pattern == "custom":
            # Use custom pattern from config
            custom = self.config.get("download", {}).get("custom_pattern", "")
            if custom:
                safe_title = "".join(c for c in anime_title if c.isalnum() or c in (' ', '-', '_')).strip()
                try:
                    return custom.format(
                        anime_name=safe_title,
                        season=season,
                        episode=episode_number,
                        ext=extension
                    )
                except KeyError:
                    pass

        # Fallback to simple format
        safe_title = "".join(c for c in anime_title if c.isalnum() or c in (' ', '-', '_')).strip()
        return f"{safe_title} - {episode_number:02d}.{extension}"

    def cleanup_partial(self, output_path: Path):
        """
        Clean up partial download files

        Args:
            output_path: Output file path
        """
        # Axel creates .st files for state
        state_file = Path(str(output_path) + ".st")
        if state_file.exists():
            try:
                state_file.unlink()
                logger.debug("download.state_file_removed", path=str(state_file))
            except Exception as e:
                logger.debug("download.state_file_remove_failed", error=str(e))

    def resume_check(self, output_path: Path) -> bool:
        """
        Check if download can be resumed

        Args:
            output_path: Output file path

        Returns:
            bool: True if resume is possible
        """
        state_file = Path(str(output_path) + ".st")
        return state_file.exists() and output_path.exists()


class DownloadError(Exception):
    """Custom exception for download errors"""
    pass
