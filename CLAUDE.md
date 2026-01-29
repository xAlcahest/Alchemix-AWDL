# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AnimeWorld Downloader is a CLI tool for downloading anime from AnimeWorld.ac with intelligent speed-based connection management. It uses Axel for multi-connection downloads (1-256 connections based on internet speed), supports bilingual UI (Italian/English), and includes SQLite-based tracking.

## Development Commands

### Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python animeworld_dl.py --help

# Install in development mode
pip install -e .
```

### Testing

```bash
# Run component tests
python test_installation.py

# This verifies:
# - Python 3.8+ installed
# - All dependencies available
# - Module imports working
# - Config/database/i18n/logger systems functional
```

### Running the Application

```bash
# First run triggers speed test and config creation
python animeworld_dl.py search "anime name"

# Main commands
python animeworld_dl.py search "query"           # Search for anime
python animeworld_dl.py list "ANIME_URL"         # List episodes
python animeworld_dl.py download "URL" --episodes all
python animeworld_dl.py config --show            # View configuration
python animeworld_dl.py --retest                 # Re-run speed test
```

## Architecture Overview

### Core Design Pattern

The application follows a modular architecture with lazy initialization of heavy components (Axel, scraper, downloader) in the main `AnimeWorldDownloader` class. This ensures the config and database are always available while downloads and scraping are only initialized when needed.

### Module Structure

**animeworld_dl/core/** - Business logic
- `config.py`: TOML configuration with connection tier mapping (10 tiers from <10 Mbps to >1.5 Gbps)
- `speedtest_manager.py`: Speed testing with automatic tier calculation
- `scraper.py`: BeautifulSoup-based HTML parsing for AnimeWorld
- `downloader.py`: Axel wrapper with retry/backoff and resume support
- `database.py`: SQLite3 operations for tracking anime/episodes/downloads

**animeworld_dl/ui/** - User interface
- `i18n.py`: Translation system (TRANSLATIONS dict with IT/EN keys)
- `logger.py`: Rich-based logging with i18n integration

**animeworld_dl/utils/** - Utilities
- `axel_manager.py`: Binary download/management for Windows (x64/ARM64) and Linux (x64/ARM64)

**animeworld_dl.py** - Click-based CLI entry point with commands: search, list, download, config

### Key Data Flow

1. **First Run**: Config doesn't exist → `run_first_time_setup()` → speedtest → calculate connections → save TOML
2. **Search**: User query → `AnimeWorldScraper.search_anime()` → fuzzy matching with RapidFuzz → display results
3. **Download**: Anime URL → scraper gets episodes → `get_video_url()` extracts direct link → `DownloadManager` uses Axel → track in SQLite

### Connection Tier System

The core intelligence is in `config.py:CONNECTION_TIERS` - a list of `(min_mbps, max_mbps, connections)` tuples. When speed test runs, `get_connections_for_speed()` maps the measured speed to connection count (1-256). This is the primary feature differentiating this downloader.

### State Management

- **Config**: TOML at `~/.config/animeworld-dl/config.toml` (loaded at init, saved after changes)
- **Database**: SQLite at `~/.config/animeworld-dl/animeworld.db` (tracks anime metadata, episodes, download status)
- **Logs**: Rich logs to `~/.config/animeworld-dl/logs/animeworld_dl.log`
- **Axel Binaries**: Downloaded to `~/.config/animeworld-dl/bin/` if system Axel unavailable

### Scraper Implementation Notes

The scraper targets AnimeWorld's HTML structure but uses multiple selector fallbacks since the site may change. Key patterns:
- Anime cards: `.film-list .item`, `.anime-card`, `.film-poster`
- Episodes: `.episode-list a`, `.server.active a`, or any `a[href*='/play/']`
- Season detection is heuristic-based (looks for episode number resets or large gaps)

### i18n System

Translations are in `ui/i18n.py:TRANSLATIONS` dict with keys like `"speed_test.starting"`. The logger wraps translation calls automatically - when logging, use `logger.info("key", param=value)` and it formats with i18n.

### Lazy Component Initialization

The main class has `self.axel_manager = None` initially and calls `_init_components()` only when needed (during download/list commands). This prevents:
- Speed test delays on simple config queries
- Axel binary downloads when just viewing help
- Network requests when offline

## Important Implementation Details

### Axel Binary Management

`AxelManager` checks system PATH first, then downloads platform-specific binaries from GitHub releases. Supported: Linux x64/ARM64, Windows x64/ARM64. macOS is excluded (requires Homebrew installation). No checksum verification by design decision.

### Episode Parsing

Episode URLs follow pattern: `/play/anime-name.ANIME_ID/EPISODE_ID`. The scraper extracts IDs via regex `\.([a-zA-Z0-9]+)` and builds episode lists. Video URL extraction tries multiple methods:
1. Look for download link with `a[href*='download']`
2. Parse JavaScript for video URLs with regex patterns
3. Check iframe sources (may need recursive scraping)

### Database Schema

Three main tables:
- `anime`: Stores anime metadata (id, title, url, genres, total_episodes, is_dub)
- `episodes`: Stores episode data (linked to anime via anime_id) with downloaded status
- `download_queue`: Not actively used but available for future batch queuing

Check `is_downloaded()` before downloading to skip completed episodes.

### Error Handling & Retry

`DownloadManager.download_with_retry()` implements exponential backoff: wait 1s, then 2s, then 4s between retries (default 3 attempts). All network operations (speedtest, scraping, downloading) have retry logic.

### File Naming

Three modes in config: `original` (keep server name), `season_episode` (format as "Anime - S01E01.mp4"), `custom` (use template with placeholders). The downloader calls `format_filename()` which handles sanitization and pattern application.

## Configuration Reference

Config is in TOML with sections: `speedtest`, `download`, `network`, `ui`, `search`, `axel`, `logging`, `advanced`. Critical settings:
- `download.parallel_episodes`: 1 = sequential, >1 = parallel episode downloads
- `ui.language`: "en" or "it"
- `search.fuzzy_threshold`: 0-100, lower = more permissive matching
- `axel.use_system_binary`: true = prefer system Axel over downloaded binary

See `config.toml.example` for full reference.

## Modifying Core Systems

### Adding New Languages

1. Add translation dict to `ui/i18n.py:TRANSLATIONS["new_lang"]`
2. Update `I18n.set_language()` validation
3. Add to config options in `core/config.py:DEFAULT_CONFIG`

### Changing Connection Tiers

Modify `core/config.py:CONNECTION_TIERS` list. Format: `(min_speed, max_speed, connections)`. Use `float('inf')` for unlimited max.

### Adding CLI Commands

1. Define command function with `@cli.command()` decorator in `animeworld_dl.py`
2. Add Click options/arguments as needed
3. Access app via `ctx.obj["app"]`
4. Add translations for any new UI strings in `ui/i18n.py`

### Scraper Maintenance

If AnimeWorld changes HTML structure:
1. Update selectors in `scraper.py` (search for `.select()` calls)
2. Test with `search_anime()` and `get_anime_info()`
3. Video URL extraction may need new patterns in `get_video_url()`

## User Data Locations

All user data under `~/.config/animeworld-dl/`:
- `config.toml` - Configuration
- `animeworld.db` - Download tracking database
- `logs/animeworld_dl.log` - Application logs
- `bin/axel` or `bin/axel.exe` - Downloaded Axel binary
- `cache/` - Reserved for future caching

Downloads go to path in `config.download.output_dir` (default: `~/Downloads/AnimeWorld`).

## License & Attribution

This project uses **CC BY-NC-SA 4.0 with Additional Terms** (see LICENSE file). Key requirements:
- Attribution required in source, docs, and UI
- Notification mandatory when code is used/modified/forked
- Non-commercial use only without explicit permission
- Share-alike for all derivatives

When contributing or using this code, review the LICENSE file's notification requirements and attribution guidelines.
