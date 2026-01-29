# AnimeWorld Downloader

Advanced CLI downloader for AnimeWorld.ac with intelligent connection management and adaptive speed optimization.

## Features

- **Interactive Menu Mode**: Beautiful menu-driven interface with keyboard navigation
- **Intelligent Speed Test**: Automatic connection speed detection with adaptive Axel connection counts
- **Multi-Architecture Support**: x86_64 and ARM64 for Windows/Linux
- **Custom Progress Bars**: Beautiful ASCII art progress visualization with Rich library
- **Bilingual**: Full Italian + English support (i18n)
- **Resume Support**: Auto-resume interrupted downloads
- **Flexible Episode Selection**: Download by range (1-24), list (1,5,8), or all
- **SQLite Tracking**: Local database for download history
- **Configurable Naming**: Customizable file naming via TOML config
- **Season Detection**: Automatic season detection from HTML parsing
- **Fuzzy Search**: Smart anime title matching

## Connection Tiers

Based on your internet speed, connections are automatically configured:

- **< 10 Mbps**: 1 connection
- **10-20 Mbps**: 2 connections
- **20-100 Mbps**: 4 connections
- **100-200 Mbps**: 8 connections
- **200-300 Mbps**: 16 connections
- **300-400 Mbps**: 24 connections
- **400-500 Mbps**: 32 connections
- **500 Mbps - 1 Gbps**: 64 connections
- **1-1.5 Gbps**: 128 connections
- **> 1.5 Gbps**: 256 connections

## Installation

```bash
pip install -r requirements.txt
python animeworld_dl.py --help
```

## Usage

### Interactive Menu Mode

Simply run without arguments to enter the interactive menu:

```bash
python animeworld_dl.py
```

This launches a user-friendly menu where you can:
- Search and browse anime
- List episodes with download status
- Download with guided prompts
- View configuration and statistics
- Re-test connection speed

### Command-Line Mode

For scripting and automation, use direct commands:

```bash
# Search for an anime
python animeworld_dl.py search "jujutsu kaisen"

# List episodes
python animeworld_dl.py list "https://www.animeworld.ac/play/anime-url"

# Download all episodes
python animeworld_dl.py download "ANIME_URL" --episodes all

# Download specific range
python animeworld_dl.py download "ANIME_URL" --episodes 1-24

# Download specific episodes
python animeworld_dl.py download "ANIME_URL" --episodes 1,5,10,12

# Override connection count
python animeworld_dl.py download "ANIME_URL" --episodes all --connections 64

# Retest your connection
python animeworld_dl.py --retest

# Configure settings
python animeworld_dl.py config --show
```

## Configuration

Configuration file: `~/.config/animeworld-dl/config.toml`

Default configuration is created on first run after speedtest.

## Requirements

- Python 3.8+
- Axel (auto-downloaded if not present)
- Internet connection

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International with Additional Terms

This project requires:
- Attribution in source code, documentation, and user interfaces
- Notification to the author when code is used, modified, or redistributed
- Non-commercial use only (commercial use requires explicit permission)
- Share-alike for all derivatives

See [LICENSE](LICENSE) file for complete terms and contact information.
