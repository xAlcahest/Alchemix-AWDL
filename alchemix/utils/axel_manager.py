"""
AnimeWorld Downloader - Axel Binary Manager
Handles downloading, managing, and executing Axel binaries
"""

import os
import platform
import shutil
import subprocess
import requests
from pathlib import Path
from typing import Optional, Tuple
from ..ui.logger import get_logger

logger = get_logger(__name__)

# GitHub releases for Axel
AXEL_GITHUB_REPO = "axel-download-accelerator/axel"
AXEL_VERSION = "2.17.11"  # Latest stable version

# Binary URLs (we'll construct these based on platform)
BINARY_URLS = {
    "linux-x86_64": f"https://github.com/{AXEL_GITHUB_REPO}/releases/download/v{AXEL_VERSION}/axel-{AXEL_VERSION}-linux-amd64",
    "linux-aarch64": f"https://github.com/{AXEL_GITHUB_REPO}/releases/download/v{AXEL_VERSION}/axel-{AXEL_VERSION}-linux-arm64",
    "windows-x86_64": f"https://github.com/{AXEL_GITHUB_REPO}/releases/download/v{AXEL_VERSION}/axel-{AXEL_VERSION}-win64.exe",
    "windows-aarch64": f"https://github.com/{AXEL_GITHUB_REPO}/releases/download/v{AXEL_VERSION}/axel-{AXEL_VERSION}-win-arm64.exe",
}


class AxelManager:
    """Manages Axel binary installation and execution"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.bin_dir = config_dir / "bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        self.axel_path: Optional[Path] = None

    def get_platform_info(self) -> Tuple[str, str]:
        """
        Get platform and architecture information

        Returns:
            Tuple[str, str]: (platform, architecture)
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Normalize platform
        if system == "linux":
            plat = "linux"
        elif system == "windows":
            plat = "windows"
        elif system == "darwin":
            # macOS uses system Axel or can install via homebrew
            plat = "macos"
        else:
            plat = "unknown"

        # Normalize architecture
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
        elif machine in ["aarch64", "arm64"]:
            arch = "aarch64"
        elif machine in ["armv7l", "armv7"]:
            arch = "armv7"
        else:
            arch = "unknown"

        return plat, arch

    def find_system_axel(self) -> Optional[Path]:
        """
        Find Axel in system PATH

        Returns:
            Optional[Path]: Path to system Axel or None
        """
        axel_path = shutil.which("axel")
        if axel_path:
            logger.info("axel.found_system", path=axel_path)
            return Path(axel_path)
        return None

    def get_binary_url(self) -> Optional[str]:
        """
        Get download URL for current platform

        Returns:
            Optional[str]: Download URL or None if unsupported
        """
        plat, arch = self.get_platform_info()

        if plat == "macos":
            logger.info("axel.macos_detected")
            return None  # macOS should use system or homebrew

        key = f"{plat}-{arch}"
        url = BINARY_URLS.get(key)

        if not url:
            logger.warning("axel.unsupported_platform", platform=plat, arch=arch)

        return url

    def download_binary(self, url: str, force: bool = False) -> Path:
        """
        Download Axel binary from URL

        Args:
            url: Download URL
            force: Force download even if exists

        Returns:
            Path: Path to downloaded binary
        """
        plat, _ = self.get_platform_info()
        binary_name = "axel.exe" if plat == "windows" else "axel"
        binary_path = self.bin_dir / binary_name

        if binary_path.exists() and not force:
            logger.info("axel.binary_exists", path=str(binary_path))
            return binary_path

        logger.info("axel.downloading", url=url)

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(binary_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            logger.debug("axel.download_progress", percent=f"{percent:.1f}")

            # Make executable on Unix-like systems
            if plat != "windows":
                os.chmod(binary_path, 0o755)

            logger.success("axel.downloaded", path=str(binary_path))
            return binary_path

        except Exception as e:
            logger.error("axel.download_failed", error=str(e))
            if binary_path.exists():
                binary_path.unlink()
            raise AxelError(f"Failed to download Axel binary: {e}")

    def ensure_axel(self, use_system: bool = True) -> Path:
        """
        Ensure Axel is available

        Args:
            use_system: Try to use system Axel first

        Returns:
            Path: Path to Axel binary

        Raises:
            AxelError: If Axel cannot be found or installed
        """
        # Try system Axel first if requested
        if use_system:
            system_axel = self.find_system_axel()
            if system_axel:
                self.axel_path = system_axel
                return system_axel

        # Check for downloaded binary
        plat, _ = self.get_platform_info()
        binary_name = "axel.exe" if plat == "windows" else "axel"
        binary_path = self.bin_dir / binary_name

        if binary_path.exists():
            self.axel_path = binary_path
            return binary_path

        # Need to download
        url = self.get_binary_url()
        if not url:
            if plat == "macos":
                raise AxelError("Please install Axel via Homebrew: brew install axel")
            else:
                raise AxelError(f"Unsupported platform: {plat}")

        # Download binary
        binary_path = self.download_binary(url)
        self.axel_path = binary_path
        return binary_path

    def get_version(self) -> Optional[str]:
        """
        Get Axel version

        Returns:
            Optional[str]: Version string or None
        """
        if not self.axel_path:
            return None

        try:
            result = subprocess.run(
                [str(self.axel_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse version from output
            output = result.stdout or result.stderr
            if "Axel" in output:
                # Extract version number
                parts = output.split()
                for i, part in enumerate(parts):
                    if part == "version" and i + 1 < len(parts):
                        return parts[i + 1]
            return output.strip().split('\n')[0]
        except Exception as e:
            logger.warning("axel.version_check_failed", error=str(e))
            return None

    def build_command(self, url: str, output: str, connections: int, **kwargs) -> list:
        """
        Build Axel command arguments

        Args:
            url: Download URL
            output: Output file path
            connections: Number of connections
            **kwargs: Additional options

        Returns:
            list: Command arguments
        """
        if not self.axel_path:
            raise AxelError("Axel not initialized")

        cmd = [
            str(self.axel_path),
            "-n", str(connections),
            "-o", output,
        ]

        # Add optional arguments
        if kwargs.get("quiet", False):
            cmd.append("-q")

        if kwargs.get("verbose", False):
            cmd.append("-v")

        if "user_agent" in kwargs:
            cmd.extend(["-U", kwargs["user_agent"]])

        if "speed_limit" in kwargs and kwargs["speed_limit"] > 0:
            # Axel uses bytes/second for speed limit
            limit_bytes = int(kwargs["speed_limit"] * 1024 * 1024)
            cmd.extend(["-s", str(limit_bytes)])

        if "max_redirect" in kwargs:
            cmd.extend(["-m", str(kwargs["max_redirect"])])

        # URL must be last
        cmd.append(url)

        return cmd


class AxelError(Exception):
    """Custom exception for Axel-related errors"""
    pass
