"""
AnimeWorld Downloader - Logger
Rich-based logging system with i18n support
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, DownloadColumn, TransferSpeedColumn
from .i18n import get_i18n

# Global console instance
console = Console()

# Global progress instance (for downloads)
_progress: Optional[Progress] = None


class I18nRichHandler(RichHandler):
    """Rich handler with i18n support"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n = get_i18n()


class Logger:
    """Logger wrapper with i18n and Rich formatting"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.i18n = get_i18n()

    def _format_message(self, key: str, **kwargs) -> str:
        """Format message with i18n"""
        return self.i18n.get(key, **kwargs)

    def debug(self, key: str, **kwargs):
        """Debug level log"""
        msg = self._format_message(key, **kwargs)
        self.logger.debug(msg)

    def info(self, key: str, **kwargs):
        """Info level log"""
        msg = self._format_message(key, **kwargs)
        self.logger.info(msg)

    def warning(self, key: str, **kwargs):
        """Warning level log"""
        msg = self._format_message(key, **kwargs)
        self.logger.warning(msg)

    def error(self, key: str, **kwargs):
        """Error level log"""
        msg = self._format_message(key, **kwargs)
        self.logger.error(msg)

    def success(self, key: str, **kwargs):
        """Success message (info level with green)"""
        msg = self._format_message(key, **kwargs)
        console.print(f"[green]✓[/green] {msg}")

    def critical(self, key: str, **kwargs):
        """Critical level log"""
        msg = self._format_message(key, **kwargs)
        self.logger.critical(msg)


def setup_logging(log_dir: Optional[Path] = None, verbosity: str = "normal"):
    """
    Setup logging system

    Args:
        log_dir: Directory for log files
        verbosity: Verbosity level (quiet, normal, verbose, debug)
    """
    # Map verbosity to log level
    level_map = {
        "quiet": logging.ERROR,
        "normal": logging.WARNING,  # Show only warnings and errors by default
        "verbose": logging.INFO,
        "debug": logging.DEBUG
    }

    level = level_map.get(verbosity, logging.WARNING)

    # Console handler
    console_handler = I18nRichHandler(
        console=console,
        show_time=verbosity == "debug",
        show_path=verbosity == "debug",
        markup=True,
        rich_tracebacks=True
    )
    console_handler.setLevel(level)

    handlers = [console_handler]

    # File handler if log_dir provided
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "animeworld_dl.log"

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        force=True
    )


def get_logger(name: str) -> Logger:
    """Get logger instance"""
    return Logger(name)


def get_progress() -> Progress:
    """Get or create global progress instance"""
    global _progress
    if _progress is None:
        _progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TaskProgressColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True  # Auto-clear completed progress bars
        )
    return _progress


def print_header(text: str):
    """Print a fancy header"""
    console.print(f"\n[bold cyan]{text}[/bold cyan]\n")


def print_success(text: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {text}")


def print_error(text: str):
    """Print error message"""
    console.print(f"[red]✗[/red] {text}")


def print_warning(text: str):
    """Print warning message"""
    console.print(f"[yellow]⚠[/yellow] {text}")


def print_info(text: str):
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {text}")
