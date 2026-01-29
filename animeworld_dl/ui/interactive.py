"""
AnimeWorld Downloader - Interactive Menu
Rich-based interactive menu system
"""

from typing import Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from .i18n import get_i18n

console = Console()
i18n = get_i18n()


class InteractiveMenu:
    """Interactive menu for AnimeWorld Downloader"""

    BANNER = """
    _    _      _                    _           ___        ______  _
   / \  | | ___| |__   ___ _ __ ___ (_)_  __    / \ \      / /  _ \| |
  / _ \ | |/ __| '_ \ / _ \ '_ ` _ \| \ \/ /   / _ \ \ /\ / /| | | | |
 / ___ \| | (__| | | |  __/ | | | | | |>  <   / ___ \ V  V / | |_| | |___
/_/   \_\_|\___|_| |_|\___|_| |_| |_|_/_/\_\ /_/   \_\_/\_/  |____/|_____|
"""

    def __init__(self, app):
        """
        Initialize interactive menu

        Args:
            app: AnimeWorldDownloader instance
        """
        self.app = app
        self.running = True

    def show_banner(self):
        """Display the application banner"""
        console.print(f"[bold cyan]{self.BANNER}[/bold cyan]")
        console.print(f"[dim]v{self.app.__class__.__module__.split('.')[-1]}[/dim]\n")

    def show_main_menu(self):
        """Display main menu"""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")

        menu_items = [
            ("1", "Search anime"),
            ("2", "List episodes"),
            ("3", "Download episodes"),
            ("4", "View configuration"),
            ("5", "Re-test connection speed"),
            ("6", "View download statistics"),
            ("0", "Exit")
        ]

        for key, label in menu_items:
            table.add_row(f"[{key}]", label)

        panel = Panel(
            table,
            title="[bold]Alchemix-AWDL - Main Menu[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

        console.print(panel)

    def get_choice(self) -> str:
        """Get user menu choice"""
        return Prompt.ask(
            "\n[bold cyan]Enter choice[/bold cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="0"
        )

    def handle_search(self):
        """Handle anime search"""
        console.print("\n[bold cyan]═══ Search Anime ═══[/bold cyan]\n")
        query = Prompt.ask("[yellow]Enter anime name[/yellow]")

        if not query:
            console.print("[red]Search cancelled[/red]")
            return

        results = self.app.search_anime(query)

        if results:
            choice = IntPrompt.ask(
                "\n[yellow]Select anime number (0 to cancel)[/yellow]",
                default=0
            )

            if 0 < choice <= len(results):
                selected = results[choice - 1]
                self.handle_anime_selected(selected)

    def handle_anime_selected(self, anime: dict):
        """Handle anime selection from search results"""
        console.print(f"\n[bold green]Selected:[/bold green] {anime['title']}\n")

        actions = Table.grid(padding=(0, 2))
        actions.add_column(style="cyan", justify="right")
        actions.add_column(style="white")

        actions.add_row("[1]", "List episodes")
        actions.add_row("[2]", "Download all episodes")
        actions.add_row("[3]", "Download specific episodes")
        actions.add_row("[0]", "Back to main menu")

        console.print(actions)

        choice = Prompt.ask(
            "\n[bold cyan]Choose action[/bold cyan]",
            choices=["0", "1", "2", "3"],
            default="0"
        )

        if choice == "1":
            self.app.list_episodes(anime["url"])
        elif choice == "2":
            self.handle_download(anime["url"], "all")
        elif choice == "3":
            episodes = Prompt.ask("[yellow]Enter episodes (e.g., 1-24 or 1,5,10)[/yellow]")
            if episodes:
                self.handle_download(anime["url"], episodes)

    def handle_list(self):
        """Handle episode listing"""
        console.print("\n[bold cyan]═══ List Episodes ═══[/bold cyan]\n")
        url = Prompt.ask("[yellow]Enter anime URL[/yellow]")

        if not url:
            console.print("[red]Cancelled[/red]")
            return

        anime_info = self.app.list_episodes(url)

        if anime_info:
            console.print("\n[bold]What would you like to do?[/bold]")
            console.print("[1] Download all episodes")
            console.print("[2] Download specific episodes")
            console.print("[0] Back to menu")

            choice = Prompt.ask(
                "\n[bold cyan]Choose action[/bold cyan]",
                choices=["0", "1", "2"],
                default="0"
            )

            if choice == "1":
                self.handle_download(url, "all")
            elif choice == "2":
                episodes = Prompt.ask("[yellow]Enter episodes (e.g., 1-24 or 1,5,10)[/yellow]")
                if episodes:
                    self.handle_download(url, episodes)

    def handle_download(self, url: str = None, episodes: str = None):
        """Handle download"""
        console.print("\n[bold cyan]═══ Download Episodes ═══[/bold cyan]\n")

        if not url:
            url = Prompt.ask("[yellow]Enter anime URL[/yellow]")

        if not url:
            console.print("[red]Download cancelled[/red]")
            return

        if not episodes:
            console.print("\n[bold]Episode selection:[/bold]")
            console.print("[1] All episodes")
            console.print("[2] Specific range (e.g., 1-24)")
            console.print("[3] Specific episodes (e.g., 1,5,10)")
            console.print("[0] Cancel")

            choice = Prompt.ask(
                "\n[bold cyan]Choose option[/bold cyan]",
                choices=["0", "1", "2", "3"],
                default="1"
            )

            if choice == "0":
                return
            elif choice == "1":
                episodes = "all"
            else:
                episodes = Prompt.ask("[yellow]Enter episodes[/yellow]")

        if not episodes:
            console.print("[red]Download cancelled[/red]")
            return

        # Ask for connection override
        use_custom = Prompt.ask(
            f"\n[yellow]Override connections? (current: {self.app.config.get('speedtest', 'connections', 4)})[/yellow]",
            choices=["y", "n"],
            default="n"
        )

        connections = None
        if use_custom == "y":
            connections = IntPrompt.ask(
                "[yellow]Enter number of connections[/yellow]",
                default=self.app.config.get('speedtest', 'connections', 4)
            )

        # Start download
        self.app.download_episodes(url, episodes, connections)

        console.print("\n[bold green]Download completed![/bold green]")
        Prompt.ask("\nPress Enter to continue")

    def handle_config(self):
        """Handle configuration view"""
        console.print("\n[bold cyan]═══ Configuration ═══[/bold cyan]\n")
        self.app.show_config()
        console.print(f"\n[dim]Edit config at: {self.app.config_manager.config_file}[/dim]")
        Prompt.ask("\nPress Enter to continue")

    def handle_speedtest(self):
        """Handle speedtest"""
        console.print("\n[bold cyan]═══ Connection Speed Test ═══[/bold cyan]\n")

        confirm = Prompt.ask(
            "[yellow]Run speed test? This may take a minute[/yellow]",
            choices=["y", "n"],
            default="y"
        )

        if confirm == "y":
            from ..core.speedtest_manager import SpeedTester, get_current_timestamp

            tester = SpeedTester()
            download_mbps, upload_mbps, ping = tester.run_test()

            connections = self.app.config_manager.get_connections_for_speed(download_mbps)

            # Update config
            self.app.config["speedtest"]["last_speed_mbps"] = download_mbps
            self.app.config["speedtest"]["last_test_date"] = get_current_timestamp()
            self.app.config["speedtest"]["connections"] = connections
            self.app.config_manager.save()

            console.print(f"\n[bold green]Speed test completed![/bold green]")
            console.print(f"Download: {download_mbps:.2f} Mbps")
            console.print(f"Upload: {upload_mbps:.2f} Mbps")
            console.print(f"Ping: {ping:.2f} ms")
            console.print(f"\n[cyan]Configured {connections} connections[/cyan]")

        Prompt.ask("\nPress Enter to continue")

    def handle_stats(self):
        """Handle statistics view"""
        console.print("\n[bold cyan]═══ Download Statistics ═══[/bold cyan]\n")

        stats = self.app.db.get_download_stats()

        table = Table(show_header=False, box=None)
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")

        table.add_row("Total Anime:", str(stats.get('total_anime', 0)))
        table.add_row("Total Episodes:", str(stats.get('total_episodes', 0)))
        table.add_row("Downloaded:", str(stats.get('downloaded_episodes', 0)))
        table.add_row("Pending:", str(stats.get('pending_episodes', 0)))
        table.add_row("Total Size:", f"{stats.get('total_size_gb', 0):.2f} GB")

        console.print(table)
        Prompt.ask("\nPress Enter to continue")

    def run(self):
        """Run the interactive menu loop"""
        self.show_banner()

        while self.running:
            console.clear()
            self.show_banner()
            self.show_main_menu()

            choice = self.get_choice()

            try:
                if choice == "0":
                    console.print("\n[bold cyan]Goodbye![/bold cyan]\n")
                    self.running = False
                elif choice == "1":
                    self.handle_search()
                elif choice == "2":
                    self.handle_list()
                elif choice == "3":
                    self.handle_download()
                elif choice == "4":
                    self.handle_config()
                elif choice == "5":
                    self.handle_speedtest()
                elif choice == "6":
                    self.handle_stats()

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Operation cancelled[/yellow]")
                Prompt.ask("\nPress Enter to continue")
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {e}")
                Prompt.ask("\nPress Enter to continue")
