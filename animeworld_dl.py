#!/usr/bin/env python3
r"""
    _    _      _                    _           ___        ______  _
   / \  | | ___| |__   ___ _ __ ___ (_)_  __    / \ \      / /  _ \| |
  / _ \ | |/ __| '_ \ / _ \ '_ ` _ \| \ \/ /   / _ \ \ /\ / /| | | | |
 / ___ \| | (__| | | |  __/ | | | | | |>  <   / ___ \ V  V / | |_| | |___
/_/   \_\_|\___|_| |_|\___|_| |_| |_|_/_/\_\ /_/   \_\_/\_/  |____/|_____|

AnimeWorld Downloader - Main CLI Entry Point
Advanced CLI downloader for AnimeWorld.ac with intelligent connection management
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rapidfuzz import fuzz

from animeworld_dl.core.config import Config
from animeworld_dl.core.speedtest_manager import SpeedTester, get_current_timestamp
from animeworld_dl.core.scraper import AlchemixScraper
from animeworld_dl.core.downloader import DownloadManager
from animeworld_dl.core.database import Database
from animeworld_dl.utils.axel_manager import AxelManager
from animeworld_dl.ui.logger import (
    setup_logging, get_logger, console,
    print_header, print_success, print_error, print_warning, print_info
)
from animeworld_dl.ui.i18n import get_i18n

__version__ = "1.0.0"

BANNER = r"""
    _    _      _                    _           ___        ______  _
   / \  | | ___| |__   ___ _ __ ___ (_)_  __    / \ \      / /  _ \| |
  / _ \ | |/ __| '_ \ / _ \ '_ ` _ \| \ \/ /   / _ \ \ /\ / /| | | | |
 / ___ \| | (__| | | |  __/ | | | | | |>  <   / ___ \ V  V / | |_| | |___
/_/   \_\_|\___|_| |_|\___|_| |_| |_|_/_/\_\ /_/   \_\_/\_/  |____/|_____|
"""

logger = get_logger(__name__)


class AlchemixDownloader:
    """Main Alchemix-AWDL application class"""

    def __init__(self):
        self.config_manager = Config()
        self.config = self.config_manager.load()
        self.i18n = get_i18n()

        # Set language
        lang = self.config_manager.get("ui", "language", "en")
        self.i18n.set_language(lang)

        # Setup logging
        log_dir = self.config_manager.get_logs_dir() if self.config_manager.get("logging", "enabled", True) else None
        verbosity = self.config_manager.get("ui", "verbosity", "normal")
        setup_logging(log_dir, verbosity)

        # Initialize database
        db_path = Path(self.config_manager.get("advanced", "database_path", ""))
        self.db = Database(db_path)

        # Initialize components (lazy)
        self.axel_manager: AxelManager = None
        self.scraper: AlchemixScraper = None
        self.downloader: DownloadManager = None

    def _init_components(self):
        """Initialize components lazily"""
        if not self.axel_manager:
            self.axel_manager = AxelManager(self.config_manager.config_dir)
            use_system = self.config_manager.get("axel", "use_system_binary", True)
            self.axel_manager.ensure_axel(use_system)

        if not self.scraper:
            timeout = self.config_manager.get("network", "http_timeout", 10)
            self.scraper = AlchemixScraper(timeout)

        if not self.downloader:
            self.downloader = DownloadManager(self.axel_manager, self.config)

    def run_first_time_setup(self):
        """Run first-time setup with speedtest"""
        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        print_header(self.i18n.get("cli.welcome", version=__version__))

        console.print("Running first-time setup...\n")

        # Run speedtest
        try:
            tester = SpeedTester(self.config_manager.get("speedtest", "timeout", 30))
            download_mbps, upload_mbps, ping = tester.test_with_retry()

            # Calculate connections
            connections = self.config_manager.get_connections_for_speed(download_mbps)

            # Save to config
            self.config["speedtest"]["last_speed_mbps"] = download_mbps
            self.config["speedtest"]["last_test_date"] = get_current_timestamp()
            self.config["speedtest"]["connections"] = connections

            self.config_manager.save()

            print_success(f"Configured {connections} connections for {download_mbps:.2f} Mbps")

        except Exception as e:
            print_warning(f"Speedtest failed: {e}")
            print_info("Using default 4 connections")
            self.config["speedtest"]["connections"] = 4
            self.config_manager.save()

        print_success(self.i18n.get("cli.config_created", path=str(self.config_manager.config_file)))

    def search_anime(self, query: str, fuzzy: bool = True):
        """Search for anime"""
        self._init_components()

        results = self.scraper.search_anime(query)

        if not results:
            print_warning(self.i18n.get("cli.no_results", query=query))
            return None

        # Apply fuzzy matching if enabled
        if fuzzy:
            threshold = self.config_manager.get("search", "fuzzy_threshold", 70)
            scored_results = [
                (result, fuzz.partial_ratio(query.lower(), result["title"].lower()))
                for result in results
            ]
            # Filter by threshold
            results = [r for r, score in scored_results if score >= threshold]

            if not results:
                print_warning(self.i18n.get("cli.no_results", query=query))
                return None

            # Sort by score
            results = [r for r, _ in sorted(scored_results, key=lambda x: x[1], reverse=True)]

        # Display results
        table = Table(title="Search Results")
        table.add_column("#", style="cyan")
        table.add_column("Title", style="bold")
        table.add_column("Type", style="yellow")
        table.add_column("ID", style="dim")

        for idx, anime in enumerate(results[:20], 1):  # Limit to 20
            anime_type = "DUB-ITA" if anime.get("is_dub") else "SUB-ITA"
            table.add_row(str(idx), anime["title"], anime_type, anime["id"])

        console.print(table)

        return results

    def list_episodes(self, anime_url: str):
        """List episodes for an anime"""
        self._init_components()

        anime_info = self.scraper.get_anime_info(anime_url)

        # Save to database
        self.db.add_anime(
            anime_info["id"],
            anime_info["title"],
            url=anime_info["url"],
            description=anime_info["description"],
            genres=anime_info["genres"],
            total_episodes=anime_info["total_episodes"]
        )

        # Display info
        console.print(f"\n[bold cyan]{anime_info['title']}[/bold cyan]")
        console.print(f"Total Episodes: {anime_info['total_episodes']}")
        console.print(f"Genres: {', '.join(anime_info['genres'])}\n")

        if anime_info["description"]:
            console.print(f"[dim]{anime_info['description'][:200]}...[/dim]\n")

        # Display episodes by season
        for season, episodes in anime_info["seasons"].items():
            table = Table(title=f"Season {season}")
            table.add_column("Episode", style="cyan")
            table.add_column("Title", style="bold")
            table.add_column("Downloaded", style="green")

            for ep in episodes:
                # Check if downloaded
                is_downloaded = self.db.is_downloaded(ep["id"])
                status = "✓" if is_downloaded else ""

                table.add_row(str(ep["number"]), ep["title"], status)

            console.print(table)

        return anime_info

    def download_episodes(
        self,
        anime_url: str,
        episodes: str = "all",
        connections: int = None
    ):
        """Download episodes"""
        self._init_components()

        # Get anime info
        anime_info = self.scraper.get_anime_info(anime_url)

        # Parse episode selection
        selected_episodes = self._parse_episode_selection(
            episodes,
            anime_info["episodes"]
        )

        if not selected_episodes:
            print_error("No episodes selected")
            return

        console.print(f"\nDownloading {len(selected_episodes)} episode(s) from {anime_info['title']}\n")

        # Get connections count
        if connections is None:
            connections = self.config_manager.get("speedtest", "connections", 4)

        # Download each episode
        output_dir = Path(self.config_manager.get("download", "output_dir", ""))
        anime_dir = output_dir / anime_info["title"]

        for episode in selected_episodes:
            try:
                # Get video URL
                video_url = self.scraper.get_video_url(episode["url"])

                # Format filename
                filename = self.downloader.format_filename(
                    anime_title=anime_info["title"],
                    episode_number=episode["number"],
                    season=1,  # TODO: detect from seasons
                    pattern=self.config_manager.get("download", "naming_pattern", "original")
                )

                output_path = anime_dir / filename

                # Check if already downloaded
                if self.db.is_downloaded(episode["id"]):
                    print_info(f"Skipping {filename} (already downloaded)")
                    continue

                # Download with retry
                success = self.downloader.download_with_retry(
                    url=video_url,
                    output_path=output_path,
                    connections=connections,
                    max_attempts=self.config_manager.get("download", "retry_attempts", 3),
                    backoff=self.config_manager.get("download", "retry_backoff", True)
                )

                if success:
                    # Mark as downloaded
                    file_size = output_path.stat().st_size if output_path.exists() else 0
                    self.db.mark_downloaded(episode["id"], str(output_path), file_size)
                    print_success(f"Downloaded: {filename}")
                else:
                    print_error(f"Failed to download: {filename}")

            except KeyboardInterrupt:
                print_warning("\nDownload interrupted by user")
                break

            except Exception as e:
                print_error(f"Error downloading {episode['title']}: {e}")
                continue

    def _parse_episode_selection(self, selection: str, episodes: list) -> list:
        """Parse episode selection (all, range, list)"""
        if selection.lower() == "all":
            return episodes

        selected = []

        # Support both comma-separated and range
        parts = selection.split(",")

        for part in parts:
            part = part.strip()

            # Range (e.g., 1-10)
            if "-" in part:
                try:
                    start, end = part.split("-")
                    start, end = int(start), int(end)

                    for ep in episodes:
                        if start <= ep["number"] <= end:
                            selected.append(ep)

                except ValueError:
                    print_warning(f"Invalid range: {part}")
                    continue

            # Single episode
            else:
                try:
                    ep_num = int(part)
                    for ep in episodes:
                        if ep["number"] == ep_num:
                            selected.append(ep)
                            break

                except ValueError:
                    print_warning(f"Invalid episode number: {part}")
                    continue

        return selected

    def show_config(self):
        """Show current configuration"""
        table = Table(title="Configuration")
        table.add_column("Section", style="cyan")
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="green")

        for section, values in self.config.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    table.add_row(section, key, str(value))

        console.print(table)
        console.print(f"\nConfig file: [cyan]{self.config_manager.config_file}[/cyan]")


# CLI Commands

@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--retest", is_flag=True, help="Re-run speed test")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.pass_context
def cli(ctx, retest, interactive):
    """AnimeWorld Downloader - Download anime from AnimeWorld.ac

    Run without arguments to enter interactive menu mode.
    """
    ctx.ensure_object(dict)
    app = AlchemixDownloader()
    ctx.obj["app"] = app

    # First time setup
    if not app.config_manager.exists():
        app.run_first_time_setup()

    # Retest if requested
    if retest:
        tester = SpeedTester()
        download_mbps, _, _ = tester.run_test()
        connections = app.config_manager.get_connections_for_speed(download_mbps)
        app.config["speedtest"]["last_speed_mbps"] = download_mbps
        app.config["speedtest"]["last_test_date"] = get_current_timestamp()
        app.config["speedtest"]["connections"] = connections
        app.config_manager.save()
        print_success(f"Updated: {connections} connections for {download_mbps:.2f} Mbps")

    # If no command is provided, enter interactive mode
    if ctx.invoked_subcommand is None:
        from animeworld_dl.ui.interactive import InteractiveMenu
        menu = InteractiveMenu(app)
        menu.run()


@cli.command()
@click.argument("query")
@click.pass_context
def search(ctx, query):
    """Search for anime"""
    app = ctx.obj["app"]
    app.search_anime(query)


@cli.command()
@click.argument("anime_url")
@click.pass_context
def list(ctx, anime_url):
    """List episodes for an anime"""
    app = ctx.obj["app"]
    app.list_episodes(anime_url)


@cli.command()
@click.argument("anime_url")
@click.option("--episodes", "-e", default="all", help="Episodes to download (all, 1-10, 1,3,5)")
@click.option("--connections", "-c", type=int, help="Override connection count")
@click.pass_context
def download(ctx, anime_url, episodes, connections):
    """Download anime episodes"""
    app = ctx.obj["app"]
    app.download_episodes(anime_url, episodes, connections)


@cli.command()
@click.option("--show", is_flag=True, help="Show current configuration")
@click.pass_context
def config(ctx, show):
    """Manage configuration"""
    app = ctx.obj["app"]

    if show:
        app.show_config()
    else:
        console.print(f"Config file: [cyan]{app.config_manager.config_file}[/cyan]")
        console.print("Use --show to display current configuration")


def main():
    """Entry point"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        print_warning("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
