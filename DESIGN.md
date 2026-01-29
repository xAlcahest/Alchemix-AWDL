# AnimeWorld Downloader - Design Decisions

This document records all the design decisions made during development based on user requirements.

## Configuration

1. **Config Format**: TOML (more readable for humans)
2. **Config Path**: `~/.config/animeworld-dl/` (XDG standard)
3. **Speedtest Tool**: speedtest-cli (Ookla) - official and reliable
4. **UI Type**: CLI with Rich library for colored output and progress bars

## Speed Test & Network

5. **Speedtest Failure Handling**: Default to 4 connections (safe default)
6. **Connection Tiers (200-500 Mbps)**: Gradual scaling (16/24/32 connections)
7. **Axel Source**: GitHub releases for binary downloads
8. **System Axel**: Use system-installed Axel if available
9. **Supported Architectures**: x86_64 and ARM64 for Windows/Linux
10. **Download Fallback**: No fallback - show error if Axel fails
11. **Checksum Verification**: No checksum verification for binaries

## User Interface

12. **Progress Display**: Real-time stats (speed, ETA, percentage)
13. **Language**: Bilingual support (Italian + English) with i18n
14. **Verbosity**: Normal level by default with custom progress bars
15. **Speed Display**: Show both Mbps and MB/s

## Episode Management

16. **Episode Selection**: Support all methods (range, list, all, specific)
17. **Download Resume**: Auto-resume enabled by default
18. **File Naming**: Original filename from server by default, customizable in TOML
19. **Directory Structure**: Auto-detect seasons from HTML parsing
20. **Search Type**: Fuzzy matching for flexible anime search
21. **Quality Selection**: Single quality per episode (no multi-quality)
22. **Server Selection**: Server is episode-specific, not selectable

## Download Settings

23. **Sub vs Dub**: Always ask user preference
24. **Batch Download**: CLI-only, no GUI
25. **Concurrent Downloads**: Both sequential and parallel, configurable in TOML
26. **Local Database**: SQLite for tracking downloads and metadata
27. **Metadata Saving**: No metadata saved (video files only)
28. **Rate Limiting**: No speed limit by default

## CLI Features

29. **CLI Overrides**: Support --connections, --speed-limit, --output-dir, --verbose/--quiet
30. **Speed Retest**: Command flag --retest for manual speedtest
31. **CLI Commands**: search, download, list, config
32. **Interrupt Handling**: Save state and allow resume on Ctrl+C
33. **Disk Space Check**: Always check before download

## Advanced Features

34. **Error Retry**: Retry with exponential backoff
35. **Connection Tiers**:
    - < 10 Mbps: 1 connection
    - 10-20 Mbps: 2 connections
    - 20-100 Mbps: 4 connections
    - 100-200 Mbps: 8 connections
    - 200-300 Mbps: 16 connections
    - 300-400 Mbps: 24 connections
    - 400-500 Mbps: 32 connections
    - 500-1000 Mbps: 64 connections
    - 1-1.5 Gbps: 128 connections
    - >1.5 Gbps: 256 connections
36. **Multi-Anime Queue**: Sequential download (one anime at a time)
37. **Logging**: File logging enabled to ~/.config/animeworld-dl/logs/
38. **Update Check**: Check for updates on startup
39. **Timeouts**: Default balanced (speedtest: 30s, HTTP: 10s, download: unlimited)
40. **Config Versioning**: No versioning system

## Technical Implementation

- **Python Version**: 3.8+
- **HTTP Library**: requests with BeautifulSoup4 for scraping
- **Download Tool**: Axel (multi-connection download accelerator)
- **Database**: SQLite3 for local tracking
- **Progress Bars**: Rich library with custom ASCII styling
- **CLI Framework**: Click for command-line interface
- **Fuzzy Search**: RapidFuzz for flexible title matching

## File Organization

```
AnimeWorldDownloader/
├── animeworld_dl/           # Main package
│   ├── core/                # Core functionality
│   │   ├── config.py        # TOML configuration management
│   │   ├── database.py      # SQLite database operations
│   │   ├── downloader.py    # Download manager with retry logic
│   │   ├── scraper.py       # AnimeWorld website scraper
│   │   └── speedtest_manager.py  # Speed testing with tiers
│   ├── ui/                  # User interface
│   │   ├── i18n.py          # Internationalization (IT/EN)
│   │   └── logger.py        # Rich-based logging
│   └── utils/               # Utilities
│       └── axel_manager.py  # Axel binary management
├── animeworld_dl.py         # Main CLI entry point
├── config.toml.example      # Example configuration
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── README.md                # Project documentation
├── QUICKSTART.md            # Quick start guide
└── LICENSE                  # MIT License

Configuration: ~/.config/animeworld-dl/config.toml
Database: ~/.config/animeworld-dl/animeworld.db
Logs: ~/.config/animeworld-dl/logs/
Binaries: ~/.config/animeworld-dl/bin/
```

## Future Enhancements (Not Implemented)

The following features were considered but not implemented:
- GUI interface (deliberately CLI-only)
- Multiple quality selection (site provides single quality)
- Metadata embedding in video files
- Cloud sync capabilities
- Notification system
- Scheduled downloads UI
- Video format conversion
- Subtitle management

## Notes

- macOS support via system Axel (install via Homebrew)
- Auto-resume uses Axel's .st state files
- Season detection is heuristic-based from episode patterns
- Fuzzy search threshold of 70 balances precision and recall
- Database enables future features like watch history tracking
