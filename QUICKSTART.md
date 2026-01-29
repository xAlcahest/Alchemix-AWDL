# AnimeWorld Downloader - Quick Start Guide

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install from source

```bash
# Clone or download the repository
cd AnimeWorldDownloader

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### First Run

The first time you run the downloader, it will:
1. Run a speed test to determine your connection speed
2. Configure optimal connection count based on your speed
3. Create configuration file at `~/.config/animeworld-dl/config.toml`

```bash
python animeworld_dl.py --help
```

## Basic Usage

### Search for Anime

```bash
python animeworld_dl.py search "jujutsu kaisen"
```

This will display a table with search results including title, type (Sub-ITA/Dub-ITA), and ID.

### List Episodes

```bash
python animeworld_dl.py list "https://www.animeworld.ac/play/princession-orchestra.lffQh"
```

This shows all available episodes organized by season.

### Download Episodes

**Download all episodes:**
```bash
python animeworld_dl.py download "https://www.animeworld.ac/play/princession-orchestra.lffQh" --episodes all
```

**Download specific range:**
```bash
python animeworld_dl.py download "https://www.animeworld.ac/play/jujutsu-kaisen-3.eFv9F" --episodes 1-24
```

**Download specific episodes:**
```bash
python animeworld_dl.py download "https://www.animeworld.ac/play/frieren.abc123" --episodes 1,5,10,12
```

**Override connection count:**
```bash
python animeworld_dl.py download "https://www.animeworld.ac/play/anime.id" --episodes all --connections 64
```

### Configuration

**View current configuration:**
```bash
python animeworld_dl.py config --show
```

**Edit configuration:**
```bash
# The config file is at ~/.config/animeworld-dl/config.toml
# Edit it with your favorite text editor

nano ~/.config/animeworld-dl/config.toml
```

### Re-test Connection Speed

```bash
python animeworld_dl.py --retest
```

This will re-run the speed test and update your connection configuration.

## Configuration Options

Edit `~/.config/animeworld-dl/config.toml` to customize:

### Download Settings

```toml
[download]
output_dir = "/home/user/Downloads/AnimeWorld"  # Download location
naming_pattern = "original"  # original, season_episode, custom
custom_pattern = "{anime_name} - S{season:02d}E{episode:02d}.{ext}"
parallel_episodes = 1  # Number of episodes to download simultaneously
auto_resume = true  # Auto-resume interrupted downloads
```

### Naming Patterns

- `original`: Keep original filename from server
- `season_episode`: Format as "Anime Name - S01E01.mp4"
- `custom`: Use your custom pattern with placeholders

### Network Settings

```toml
[network]
http_timeout = 10  # HTTP request timeout in seconds
speed_limit = 0  # Download speed limit in MB/s (0 = unlimited)
```

### UI Settings

```toml
[ui]
language = "en"  # en or it
verbosity = "normal"  # quiet, normal, verbose, debug
```

### Search Settings

```toml
[search]
fuzzy_threshold = 70  # Fuzzy search sensitivity (0-100)
ask_preference = true  # Ask for Sub-ITA or Dub-ITA preference
```

## Connection Tiers

The downloader automatically configures connection count based on your speed:

| Speed Range | Connections |
|-------------|-------------|
| < 10 Mbps | 1 |
| 10-20 Mbps | 2 |
| 20-100 Mbps | 4 |
| 100-200 Mbps | 8 |
| 200-300 Mbps | 16 |
| 300-400 Mbps | 24 |
| 400-500 Mbps | 32 |
| 500-1000 Mbps | 64 |
| 1-1.5 Gbps | 128 |
| > 1.5 Gbps | 256 |

## Troubleshooting

### Axel not found

If Axel is not installed on your system:

**Linux (Debian/Ubuntu):**
```bash
sudo apt install axel
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install axel
```

**macOS:**
```bash
brew install axel
```

**Windows:**
The downloader will automatically download the Axel binary for Windows.

### Speed test fails

If the speed test fails, the downloader will default to 4 connections. You can:
1. Manually set connections in config.toml
2. Try re-running with `--retest`
3. Use `--connections N` flag to override

### Downloads fail

1. Check your internet connection
2. Verify the anime URL is correct
3. Check if the video is still available on AnimeWorld
4. Try with fewer connections: `--connections 4`

### Permission errors

Make sure you have write permissions to the download directory:
```bash
chmod 755 ~/Downloads/AnimeWorld
```

## Advanced Usage

### Download Multiple Anime

Create a bash script to download multiple anime:

```bash
#!/bin/bash

python animeworld_dl.py download "URL1" --episodes all
python animeworld_dl.py download "URL2" --episodes all
python animeworld_dl.py download "URL3" --episodes 1-12
```

### Scheduling Downloads

Use cron to schedule downloads:

```bash
# Edit crontab
crontab -e

# Add line to run at 2 AM daily
0 2 * * * cd /path/to/AnimeWorldDownloader && python animeworld_dl.py download "URL" --episodes all
```

## Logs

Logs are stored at: `~/.config/animeworld-dl/logs/animeworld_dl.log`

View recent logs:
```bash
tail -f ~/.config/animeworld-dl/logs/animeworld_dl.log
```

## Database

Download history is stored in SQLite database at:
`~/.config/animeworld-dl/animeworld.db`

You can query it with any SQLite client to see statistics.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## License

MIT License - See LICENSE file for details.
