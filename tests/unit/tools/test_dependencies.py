"""Tests for dependencies module."""

from unittest.mock import AsyncMock, patch

import pytest

from youtube_search_mcp.download.ytdlp_downloader import YtDlpDownloader
from youtube_search_mcp.formatters.json_formatter import JsonFormatter
from youtube_search_mcp.formatters.markdown_formatter import MarkdownFormatter
from youtube_search_mcp.search.ytdlp_provider import YtDlpSearchProvider
from youtube_search_mcp.tools import dependencies


@pytest.fixture(autouse=True)
def reset_dependencies():
    """Reset global dependencies before each test."""
    dependencies._search_provider = None
    dependencies._downloader = None
    dependencies._formatters = {}
    yield
    dependencies._search_provider = None
    dependencies._downloader = None
    dependencies._formatters = {}


class TestEnsureInitialized:
    """Tests for _ensure_initialized function."""

    def test_ensure_initialized_creates_search_provider(self):
        """Test that _ensure_initialized creates search provider."""
        dependencies._ensure_initialized()

        assert dependencies._search_provider is not None
        assert isinstance(dependencies._search_provider, YtDlpSearchProvider)

    def test_ensure_initialized_creates_downloader(self):
        """Test that _ensure_initialized creates downloader."""
        dependencies._ensure_initialized()

        assert dependencies._downloader is not None
        assert isinstance(dependencies._downloader, YtDlpDownloader)

    def test_ensure_initialized_creates_formatters(self):
        """Test that _ensure_initialized creates formatters."""
        dependencies._ensure_initialized()

        assert "json" in dependencies._formatters
        assert "markdown" in dependencies._formatters
        assert isinstance(dependencies._formatters["json"], JsonFormatter)
        assert isinstance(dependencies._formatters["markdown"], MarkdownFormatter)

    def test_ensure_initialized_skips_if_already_initialized(self):
        """Test that _ensure_initialized skips if already initialized."""
        # First initialization
        dependencies._ensure_initialized()
        original_provider = dependencies._search_provider

        # Second call should not reinitialize
        dependencies._ensure_initialized()

        assert dependencies._search_provider is original_provider


class TestGetSearchProvider:
    """Tests for get_search_provider function."""

    def test_get_search_provider_returns_instance(self):
        """Test that get_search_provider returns provider instance."""
        provider = dependencies.get_search_provider()

        assert provider is not None
        assert isinstance(provider, YtDlpSearchProvider)

    def test_get_search_provider_initializes_if_needed(self):
        """Test that get_search_provider initializes if not already done."""
        assert dependencies._search_provider is None

        provider = dependencies.get_search_provider()

        assert provider is not None
        assert dependencies._search_provider is provider

    def test_get_search_provider_returns_same_instance(self):
        """Test that get_search_provider returns same instance (singleton)."""
        provider1 = dependencies.get_search_provider()
        provider2 = dependencies.get_search_provider()

        assert provider1 is provider2


class TestGetDownloader:
    """Tests for get_downloader function."""

    def test_get_downloader_returns_instance(self):
        """Test that get_downloader returns downloader instance."""
        downloader = dependencies.get_downloader()

        assert downloader is not None
        assert isinstance(downloader, YtDlpDownloader)

    def test_get_downloader_initializes_if_needed(self):
        """Test that get_downloader initializes if not already done."""
        assert dependencies._downloader is None

        downloader = dependencies.get_downloader()

        assert downloader is not None
        assert dependencies._downloader is downloader

    def test_get_downloader_returns_same_instance(self):
        """Test that get_downloader returns same instance (singleton)."""
        downloader1 = dependencies.get_downloader()
        downloader2 = dependencies.get_downloader()

        assert downloader1 is downloader2


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_formatter_json(self):
        """Test getting JSON formatter."""
        formatter = dependencies.get_formatter("json")

        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_markdown(self):
        """Test getting Markdown formatter."""
        formatter = dependencies.get_formatter("markdown")

        assert isinstance(formatter, MarkdownFormatter)

    def test_get_formatter_default_is_json(self):
        """Test that default formatter is JSON."""
        formatter = dependencies.get_formatter()

        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_unknown_type_returns_json(self):
        """Test that unknown formatter type returns JSON."""
        formatter = dependencies.get_formatter("unknown")

        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_initializes_if_needed(self):
        """Test that get_formatter initializes if not already done."""
        assert not dependencies._formatters

        formatter = dependencies.get_formatter()

        assert dependencies._formatters
        assert formatter is not None


class TestInitializeDependencies:
    """Tests for initialize_dependencies function."""

    @pytest.mark.asyncio
    async def test_initialize_dependencies_creates_all(self):
        """Test that initialize_dependencies creates all dependencies."""
        with patch.object(YtDlpSearchProvider, "validate_connection", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = True

            await dependencies.initialize_dependencies()

            assert dependencies._search_provider is not None
            assert dependencies._downloader is not None
            assert dependencies._formatters

    @pytest.mark.asyncio
    async def test_initialize_dependencies_validates_provider(self):
        """Test that initialize_dependencies validates the provider."""
        with patch.object(YtDlpSearchProvider, "validate_connection", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = True

            await dependencies.initialize_dependencies()

            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_dependencies_handles_validation_failure(self):
        """Test that initialize_dependencies handles validation failure."""
        with patch.object(YtDlpSearchProvider, "validate_connection", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = False

            # Should not raise, just log warning
            await dependencies.initialize_dependencies()

            assert dependencies._search_provider is not None

    @pytest.mark.asyncio
    async def test_initialize_dependencies_handles_validation_error(self):
        """Test that initialize_dependencies handles validation error."""
        with patch.object(YtDlpSearchProvider, "validate_connection", new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = Exception("Validation error")

            # Should not raise, just log error
            await dependencies.initialize_dependencies()

            assert dependencies._search_provider is not None

