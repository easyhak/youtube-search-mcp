"""Dependency injection for MCP tools."""

from ..core.config import get_config
from ..core.interfaces import Downloader, ResultFormatter, SearchProvider
from ..download.ytdlp_downloader import YtDlpDownloader
from ..formatters.json_formatter import JsonFormatter
from ..formatters.markdown_formatter import MarkdownFormatter
from ..search.ytdlp_provider import YtDlpSearchProvider
from ..utils.logger import get_logger

# Initialize configuration
config = get_config()
logger = get_logger(__name__)

# Global dependency instances
_search_provider: SearchProvider | None = None
_downloader: Downloader | None = None
_formatters: dict[str, ResultFormatter] = {}


async def initialize_dependencies() -> None:
    """Initialize all service dependencies."""
    global _search_provider, _downloader, _formatters

    logger.info(f"Initializing dependencies for {config.server_name}")

    # Initialize search provider
    _search_provider = YtDlpSearchProvider(
        max_results_default=config.default_max_results,
        timeout=config.search_timeout,
        retries=config.max_retries,
    )

    # Initialize downloader
    _downloader = YtDlpDownloader(
        default_output_dir=config.download_dir, min_disk_space_mb=config.min_disk_space_mb
    )

    # Initialize formatters
    _formatters = {"json": JsonFormatter(), "markdown": MarkdownFormatter()}

    # Validate provider is working
    try:
        is_valid = await _search_provider.validate_connection()
        if is_valid:
            logger.info("Search provider validated successfully")
        else:
            logger.warning("Search provider validation failed")
    except Exception as e:
        logger.error(f"Error validating search provider: {e}")


def get_search_provider() -> SearchProvider:
    """
    Get the search provider instance.

    Returns:
        SearchProvider instance

    Raises:
        RuntimeError: If search provider is not initialized
    """
    if _search_provider is None:
        raise RuntimeError("Search provider not initialized. Call initialize_dependencies() first.")
    return _search_provider


def get_downloader() -> Downloader:
    """
    Get the downloader instance.

    Returns:
        Downloader instance

    Raises:
        RuntimeError: If downloader is not initialized
    """
    if _downloader is None:
        raise RuntimeError("Downloader not initialized. Call initialize_dependencies() first.")
    return _downloader


def get_formatter(format_type: str = "json") -> ResultFormatter:
    """
    Get formatter by type.

    Args:
        format_type: Type of formatter ("json" or "markdown")

    Returns:
        ResultFormatter instance (defaults to JSON if type not found)
    """
    return _formatters.get(format_type, _formatters["json"])
