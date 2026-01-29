"""
AnimeWorld Downloader - Speed Test Module
Handles internet speed testing and connection optimization
"""

import speedtest
from datetime import datetime
from typing import Tuple, Optional
from ..ui.logger import get_logger

logger = get_logger(__name__)


class SpeedTester:
    """Handles speed testing using speedtest-cli"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.last_result: Optional[Tuple[float, float, float]] = None

    def run_test(self, show_progress: bool = True) -> Tuple[float, float, float]:
        """
        Run speed test and return download, upload, and ping

        Returns:
            Tuple[float, float, float]: (download_mbps, upload_mbps, ping_ms)
        """
        try:
            if show_progress:
                logger.info("speed_test.starting")

            st = speedtest.Speedtest()

            if show_progress:
                logger.info("speed_test.server_select")
            st.get_best_server()

            if show_progress:
                logger.info("speed_test.download")
            download_bps = st.download()
            download_mbps = download_bps / 1_000_000  # Convert to Mbps

            if show_progress:
                logger.info("speed_test.upload")
            upload_bps = st.upload()
            upload_mbps = upload_bps / 1_000_000

            ping = st.results.ping

            self.last_result = (download_mbps, upload_mbps, ping)

            if show_progress:
                logger.success("speed_test.completed",
                             download=f"{download_mbps:.2f}",
                             upload=f"{upload_mbps:.2f}",
                             ping=f"{ping:.2f}")

            return self.last_result

        except Exception as e:
            logger.error("speed_test.failed", error=str(e))
            raise SpeedTestError(f"Speed test failed: {e}")

    def test_with_retry(self, max_attempts: int = 3) -> Tuple[float, float, float]:
        """
        Run speed test with retry logic

        Args:
            max_attempts: Maximum number of retry attempts

        Returns:
            Tuple[float, float, float]: (download_mbps, upload_mbps, ping_ms)
        """
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info("speed_test.attempt", current=attempt, total=max_attempts)
                return self.run_test()
            except Exception as e:
                last_error = e
                if attempt < max_attempts:
                    logger.warning("speed_test.retry", attempt=attempt)
                    continue

        raise SpeedTestError(f"Speed test failed after {max_attempts} attempts: {last_error}")

    def get_speed_tier_info(self, speed_mbps: float) -> dict:
        """
        Get connection tier information for given speed

        Args:
            speed_mbps: Download speed in Mbps

        Returns:
            dict: Tier information including connections and tier name
        """
        from .config import CONNECTION_TIERS

        for min_speed, max_speed, connections in CONNECTION_TIERS:
            if min_speed <= speed_mbps < max_speed:
                # Determine tier name
                if speed_mbps < 20:
                    tier = "very_slow"
                elif speed_mbps < 100:
                    tier = "slow"
                elif speed_mbps < 200:
                    tier = "medium"
                elif speed_mbps < 500:
                    tier = "fast"
                elif speed_mbps < 1000:
                    tier = "very_fast"
                elif speed_mbps < 1500:
                    tier = "gigabit"
                else:
                    tier = "ultra"

                return {
                    "speed_mbps": speed_mbps,
                    "connections": connections,
                    "tier": tier,
                    "min_speed": min_speed,
                    "max_speed": max_speed if max_speed != float('inf') else None
                }

        # Fallback
        return {
            "speed_mbps": speed_mbps,
            "connections": 4,
            "tier": "unknown",
            "min_speed": 0,
            "max_speed": None
        }

    def format_speed(self, mbps: float, include_mbs: bool = True) -> str:
        """
        Format speed for display

        Args:
            mbps: Speed in megabits per second
            include_mbs: Also show megabytes per second

        Returns:
            str: Formatted speed string
        """
        if include_mbs:
            mbs = mbps / 8  # Convert to MB/s
            return f"{mbps:.2f} Mbps ({mbs:.2f} MB/s)"
        return f"{mbps:.2f} Mbps"


class SpeedTestError(Exception):
    """Custom exception for speed test errors"""
    pass


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()
