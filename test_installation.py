#!/usr/bin/env python3
"""
Test script to verify AnimeWorld Downloader installation and components
"""

import sys
from pathlib import Path

print("=" * 60)
print("AnimeWorld Downloader - Component Test")
print("=" * 60)

# Test 1: Python version
print("\n[1/8] Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"✗ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

# Test 2: Dependencies
print("\n[2/8] Checking dependencies...")
required_packages = [
    "requests",
    "bs4",
    "lxml",
    "speedtest",
    "rich",
    "toml",
    "click",
    "rapidfuzz",
    "platformdirs"
]

missing = []
for package in required_packages:
    try:
        if package == "bs4":
            import bs4
        elif package == "speedtest":
            import speedtest
        else:
            __import__(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - MISSING")
        missing.append(package)

if missing:
    print(f"\n✗ Missing packages: {', '.join(missing)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Module imports
print("\n[3/8] Testing module imports...")
try:
    from animeworld_dl.core.config import Config
    print("  ✓ config")

    from animeworld_dl.core.speedtest_manager import SpeedTester
    print("  ✓ speedtest_manager")

    from animeworld_dl.core.scraper import AnimeWorldScraper
    print("  ✓ scraper")

    from animeworld_dl.core.downloader import DownloadManager
    print("  ✓ downloader")

    from animeworld_dl.core.database import Database
    print("  ✓ database")

    from animeworld_dl.utils.axel_manager import AxelManager
    print("  ✓ axel_manager")

    from animeworld_dl.ui.logger import get_logger
    print("  ✓ logger")

    from animeworld_dl.ui.i18n import get_i18n
    print("  ✓ i18n")

except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 4: Config system
print("\n[4/8] Testing configuration system...")
try:
    config = Config()
    config.load()
    print("  ✓ Config loaded")

    connections = config.get_connections_for_speed(100)
    print(f"  ✓ Connection calculation: {connections} for 100 Mbps")

except Exception as e:
    print(f"  ✗ Config test failed: {e}")
    sys.exit(1)

# Test 5: i18n system
print("\n[5/8] Testing i18n system...")
try:
    i18n = get_i18n()
    en_msg = i18n.get("speed_test.starting")
    print(f"  ✓ English: {en_msg}")

    i18n.set_language("it")
    it_msg = i18n.get("speed_test.starting")
    print(f"  ✓ Italian: {it_msg}")

except Exception as e:
    print(f"  ✗ i18n test failed: {e}")
    sys.exit(1)

# Test 6: Logger
print("\n[6/8] Testing logger...")
try:
    logger = get_logger("test")
    logger.debug("test.message")
    print("  ✓ Logger initialized")

except Exception as e:
    print(f"  ✗ Logger test failed: {e}")
    sys.exit(1)

# Test 7: Database
print("\n[7/8] Testing database...")
try:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    db = Database(db_path)

    # Test adding anime
    db.add_anime("test123", "Test Anime", url="http://test.com", total_episodes=12)

    # Test retrieving
    anime = db.get_anime("test123")
    assert anime["title"] == "Test Anime"

    # Test adding episode
    db.add_episode("ep1", "test123", 1, title="Episode 1")

    # Test stats
    stats = db.get_download_stats()

    db.close()
    db_path.unlink()  # Clean up

    print("  ✓ Database operations working")

except Exception as e:
    print(f"  ✗ Database test failed: {e}")
    if 'db_path' in locals() and db_path.exists():
        db_path.unlink()
    sys.exit(1)

# Test 8: Axel detection
print("\n[8/8] Testing Axel availability...")
try:
    import shutil
    axel_path = shutil.which("axel")
    if axel_path:
        print(f"  ✓ System Axel found: {axel_path}")
    else:
        print("  ⚠ System Axel not found (will be auto-downloaded)")

except Exception as e:
    print(f"  ⚠ Axel check warning: {e}")

# Summary
print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nYou can now run the downloader:")
print("  python animeworld_dl.py --help")
print("\nFor first-time setup:")
print("  python animeworld_dl.py search \"anime name\"")
print("=" * 60)
