"""
AnimeWorld Downloader - Configuration Module
Handles TOML config loading, saving, and defaults
"""

import os
import toml
from pathlib import Path
from typing import Dict, Any, Optional
from platformdirs import user_config_dir

# Default configuration template
DEFAULT_CONFIG = {
    "speedtest": {
        "last_speed_mbps": 0,
        "last_test_date": "",
        "connections": 4,
        "timeout": 30
    },
    "download": {
        "output_dir": str(Path(__file__).parent.parent.parent / "Video_DL"),
        "naming_pattern": "original",  # original, season_episode, custom
        "custom_pattern": "{anime_name} - S{season:02d}E{episode:02d}.{ext}",
        "parallel_episodes": 1,  # Sequential by default
        "retry_attempts": 3,
        "retry_backoff": True,
        "auto_resume": True,
        "check_disk_space": True
    },
    "network": {
        "http_timeout": 10,
        "download_timeout": 0,  # No timeout
        "speed_limit": 0,  # No limit (MB/s)
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "ui": {
        "language": "en",  # en or it
        "verbosity": "normal",  # quiet, normal, verbose, debug
        "show_speed_mbps": True,
        "show_speed_mbs": True,
        "ascii_progress": True
    },
    "search": {
        "fuzzy_threshold": 70,  # 0-100, lower is more permissive
        "prefer_dub": False,
        "prefer_sub": False,
        "ask_preference": True
    },
    "axel": {
        "use_system_binary": True,
        "binary_path": "",  # Auto-detected or custom
        "download_if_missing": True
    },
    "logging": {
        "enabled": True,
        "max_size_mb": 10,
        "backup_count": 5
    },
    "advanced": {
        "check_updates": True,
        "cache_expire_days": 7,
        "database_path": ""  # Auto-set to config dir
    }
}

# Connection tier mapping based on speed (Mbps)
CONNECTION_TIERS = [
    (0, 10, 1),
    (10, 20, 2),
    (20, 100, 4),
    (100, 200, 8),
    (200, 300, 16),
    (300, 400, 24),
    (400, 500, 32),
    (500, 1000, 64),
    (1000, 1500, 128),
    (1500, float('inf'), 256)
]


class Config:
    """Configuration manager for AnimeWorld Downloader"""

    def __init__(self):
        self.config_dir = Path(user_config_dir("animeworld-dl"))
        self.config_file = self.config_dir / "config.toml"
        self.config: Dict[str, Any] = {}
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                self.config = toml.load(self.config_file)
                # Merge with defaults to add any new keys
                self.config = self._merge_with_defaults(self.config)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()
            # Set auto-paths
            self.config["advanced"]["database_path"] = str(self.config_dir / "animeworld.db")

        return self.config

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to ensure all keys exist"""
        merged = DEFAULT_CONFIG.copy()
        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged

    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                toml.dump(self.config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def get_connections_for_speed(self, speed_mbps: float) -> int:
        """Calculate optimal connections based on speed"""
        for min_speed, max_speed, connections in CONNECTION_TIERS:
            if min_speed <= speed_mbps < max_speed:
                return connections
        return 4  # Default fallback

    def exists(self) -> bool:
        """Check if config file exists"""
        return self.config_file.exists()

    def get_logs_dir(self) -> Path:
        """Get logs directory path"""
        logs_dir = self.config_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def get_cache_dir(self) -> Path:
        """Get cache directory path"""
        cache_dir = self.config_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
