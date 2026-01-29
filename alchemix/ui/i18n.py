"""
AnimeWorld Downloader - i18n (Internationalization)
Translations for Italian and English
"""

TRANSLATIONS = {
    "en": {
        # Speed test
        "speed_test.starting": "Starting speed test...",
        "speed_test.server_select": "Selecting best server...",
        "speed_test.download": "Testing download speed...",
        "speed_test.upload": "Testing upload speed...",
        "speed_test.completed": "Speed test completed: {download} Mbps down, {upload} Mbps up, {ping} ms ping",
        "speed_test.failed": "Speed test failed: {error}",
        "speed_test.attempt": "Attempt {current}/{total}...",
        "speed_test.retry": "Retrying speed test (attempt {attempt})...",

        # Axel
        "axel.found_system": "Found system Axel at: {path}",
        "axel.macos_detected": "macOS detected - please install Axel via Homebrew",
        "axel.unsupported_platform": "Unsupported platform: {platform}/{arch}",
        "axel.binary_exists": "Axel binary already exists: {path}",
        "axel.downloading": "Downloading Axel binary from {url}...",
        "axel.download_progress": "Download progress: {percent}%",
        "axel.downloaded": "Axel binary downloaded: {path}",
        "axel.download_failed": "Failed to download Axel: {error}",
        "axel.version_check_failed": "Failed to check Axel version: {error}",

        # Scraper
        "scraper.searching": "Searching for: {query}",
        "scraper.search_complete": "Found {count} results",
        "scraper.search_failed": "Search failed: {error}",
        "scraper.fetching_info": "Fetching anime info from {url}",
        "scraper.info_fetched": "Loaded '{title}' with {episodes} episodes",
        "scraper.info_failed": "Failed to fetch anime info: {error}",
        "scraper.episode_parse_error": "Error parsing episode: {error}",
        "scraper.extracting_video": "Extracting video URL from {url}",
        "scraper.video_found": "Video URL found: {url}",
        "scraper.video_extraction_failed": "Failed to extract video URL: {error}",
        "scraper.iframe_found": "Found iframe source: {src}",
        "scraper.card_parse_error": "Error parsing anime card: {error}",

        # Download
        "download.starting": "Starting download: {filename}",
        "download.completed": "Download completed: {filename}",
        "download.failed": "Download failed: {error}",
        "download.retrying": "Retrying download (attempt {attempt}/{max_attempts})...",
        "download.resumed": "Resuming download: {filename}",
        "download.disk_space_low": "Warning: Low disk space ({available} GB available)",
        "download.disk_space_check": "Checking disk space...",

        # CLI
        "cli.welcome": "AnimeWorld Downloader v{version}",
        "cli.config_created": "Configuration created at: {path}",
        "cli.no_results": "No results found for: {query}",
        "cli.select_anime": "Select an anime:",
        "cli.select_episodes": "Select episodes to download:",
        "cli.select_quality": "Select quality:",
        "cli.select_sub_dub": "Select Sub-ITA or Dub-ITA:",

        # Errors
        "error.no_video_url": "Could not find video download URL",
        "error.invalid_episode_range": "Invalid episode range: {range}",
        "error.config_load_failed": "Failed to load configuration: {error}",

        # General
        "general.yes": "Yes",
        "general.no": "No",
        "general.cancel": "Cancel",
        "general.continue": "Continue",
        "general.sub_ita": "Sub-ITA",
        "general.dub_ita": "Dub-ITA",
    },
    "it": {
        # Speed test
        "speed_test.starting": "Avvio speed test...",
        "speed_test.server_select": "Selezione del miglior server...",
        "speed_test.download": "Test velocità download...",
        "speed_test.upload": "Test velocità upload...",
        "speed_test.completed": "Speed test completato: {download} Mbps down, {upload} Mbps up, {ping} ms ping",
        "speed_test.failed": "Speed test fallito: {error}",
        "speed_test.attempt": "Tentativo {current}/{total}...",
        "speed_test.retry": "Nuovo tentativo speed test ({attempt})...",

        # Axel
        "axel.found_system": "Axel di sistema trovato: {path}",
        "axel.macos_detected": "macOS rilevato - installa Axel tramite Homebrew",
        "axel.unsupported_platform": "Piattaforma non supportata: {platform}/{arch}",
        "axel.binary_exists": "Binary Axel già esistente: {path}",
        "axel.downloading": "Download binary Axel da {url}...",
        "axel.download_progress": "Progresso download: {percent}%",
        "axel.downloaded": "Binary Axel scaricato: {path}",
        "axel.download_failed": "Download Axel fallito: {error}",
        "axel.version_check_failed": "Controllo versione Axel fallito: {error}",

        # Scraper
        "scraper.searching": "Ricerca: {query}",
        "scraper.search_complete": "Trovati {count} risultati",
        "scraper.search_failed": "Ricerca fallita: {error}",
        "scraper.fetching_info": "Caricamento info anime da {url}",
        "scraper.info_fetched": "Caricato '{title}' con {episodes} episodi",
        "scraper.info_failed": "Caricamento info anime fallito: {error}",
        "scraper.episode_parse_error": "Errore parsing episodio: {error}",
        "scraper.extracting_video": "Estrazione URL video da {url}",
        "scraper.video_found": "URL video trovato: {url}",
        "scraper.video_extraction_failed": "Estrazione URL video fallita: {error}",
        "scraper.iframe_found": "Trovato iframe: {src}",
        "scraper.card_parse_error": "Errore parsing scheda anime: {error}",

        # Download
        "download.starting": "Avvio download: {filename}",
        "download.completed": "Download completato: {filename}",
        "download.failed": "Download fallito: {error}",
        "download.retrying": "Nuovo tentativo download ({attempt}/{max_attempts})...",
        "download.resumed": "Ripresa download: {filename}",
        "download.disk_space_low": "Attenzione: Spazio disco basso ({available} GB disponibili)",
        "download.disk_space_check": "Controllo spazio disco...",

        # CLI
        "cli.welcome": "AnimeWorld Downloader v{version}",
        "cli.config_created": "Configurazione creata in: {path}",
        "cli.no_results": "Nessun risultato per: {query}",
        "cli.select_anime": "Seleziona un anime:",
        "cli.select_episodes": "Seleziona episodi da scaricare:",
        "cli.select_quality": "Seleziona qualità:",
        "cli.select_sub_dub": "Seleziona Sub-ITA o Dub-ITA:",

        # Errors
        "error.no_video_url": "Impossibile trovare URL download video",
        "error.invalid_episode_range": "Range episodi non valido: {range}",
        "error.config_load_failed": "Caricamento configurazione fallito: {error}",

        # General
        "general.yes": "Sì",
        "general.no": "No",
        "general.cancel": "Annulla",
        "general.continue": "Continua",
        "general.sub_ita": "Sub-ITA",
        "general.dub_ita": "Dub-ITA",
    }
}


class I18n:
    """Internationalization helper"""

    def __init__(self, language: str = "en"):
        self.language = language if language in TRANSLATIONS else "en"

    def get(self, key: str, **kwargs) -> str:
        """
        Get translated string

        Args:
            key: Translation key (e.g., "speed_test.starting")
            **kwargs: Format arguments

        Returns:
            str: Translated and formatted string
        """
        text = TRANSLATIONS[self.language].get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

    def set_language(self, language: str):
        """Set active language"""
        if language in TRANSLATIONS:
            self.language = language


# Global instance
_i18n = I18n()


def get_i18n() -> I18n:
    """Get global i18n instance"""
    return _i18n


def t(key: str, **kwargs) -> str:
    """Shorthand for translation"""
    return _i18n.get(key, **kwargs)
