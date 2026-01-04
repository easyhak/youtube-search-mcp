"""Tests for YtDlpSearchProvider."""

from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from youtube_search_mcp.core.exceptions import (
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails
from youtube_search_mcp.models.search_params import SearchParams
from youtube_search_mcp.models.video import Video, VideoDetails
from youtube_search_mcp.search.ytdlp_provider import YtDlpSearchProvider


@pytest.fixture
def provider():
    """Create YtDlpSearchProvider instance."""
    return YtDlpSearchProvider()


@pytest.fixture
def mock_video_data():
    """Sample video data from yt-dlp."""
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "duration": 212,
        "view_count": 1400000000,
        "uploader": "Rick Astley",
        "channel": "Rick Astley Official",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "timestamp": 1256428800,
    }


@pytest.fixture
def mock_playlist_data():
    """Sample playlist data from yt-dlp."""
    return {
        "id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        "title": "Python Tutorial Playlist",
        "uploader": "Python Channel",
        "playlist_count": 50,
        "thumbnail": "https://i.ytimg.com/vi/playlist/default.jpg",
    }


class TestYtDlpSearchProviderInit:
    """Tests for YtDlpSearchProvider initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        provider = YtDlpSearchProvider()

        assert provider._max_results_default == 10
        assert provider._timeout == 30
        assert provider._retries == 3

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        provider = YtDlpSearchProvider(
            max_results_default=20,
            timeout=60,
            retries=5,
        )

        assert provider._max_results_default == 20
        assert provider._timeout == 60
        assert provider._retries == 5

    def test_build_ydl_options(self, provider):
        """Test that ydl options are built correctly."""
        opts = provider._ydl_opts

        assert opts["quiet"] is True
        assert opts["no_warnings"] is True
        assert opts["skip_download"] is True
        assert opts["socket_timeout"] == 30


class TestErrorClassification:
    """Tests for error classification methods."""

    def test_is_network_error_timeout(self, provider):
        """Test network error detection for timeout."""
        assert provider._is_network_error("Connection timeout")

    def test_is_network_error_unable_to_download(self, provider):
        """Test network error detection for download error."""
        assert provider._is_network_error("Unable to download webpage")

    def test_is_network_error_connection(self, provider):
        """Test network error detection for connection error."""
        assert provider._is_network_error("Connection refused")

    def test_is_network_error_false(self, provider):
        """Test that unrelated errors are not classified as network errors."""
        assert not provider._is_network_error("Video unavailable")

    def test_is_video_unavailable_private(self, provider):
        """Test video unavailable detection for private video."""
        assert provider._is_video_unavailable("Private video")

    def test_is_video_unavailable_removed(self, provider):
        """Test video unavailable detection for removed video."""
        assert provider._is_video_unavailable("Video has been removed")

    def test_is_video_unavailable_false(self, provider):
        """Test that unrelated errors are not classified as unavailable."""
        assert not provider._is_video_unavailable("Network timeout")


class TestSearch:
    """Tests for search method."""

    @pytest.mark.asyncio
    async def test_search_success(self, provider, mock_video_data):
        """Test successful video search."""
        mock_entries = [mock_video_data, mock_video_data]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            params = SearchParams(query="never gonna give you up", max_results=5)
            results = await provider.search(params)

            assert len(results) == 2
            assert all(isinstance(v, Video) for v in results)
            assert results[0].video_id == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_search_empty_results(self, provider):
        """Test search with no results."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": []}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            params = SearchParams(query="xyznonexistent123", max_results=5)
            results = await provider.search(params)

            assert results == []

    @pytest.mark.asyncio
    async def test_search_network_error(self, provider):
        """Test search with network error."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Unable to download webpage: connection timeout"
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            params = SearchParams(query="test", max_results=5)

            with pytest.raises(NetworkError):
                await provider.search(params)

    @pytest.mark.asyncio
    async def test_search_provider_error(self, provider):
        """Test search with general provider error."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Some unknown error"
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            params = SearchParams(query="test", max_results=5)

            with pytest.raises(SearchProviderError):
                await provider.search(params)


class TestGetVideoDetails:
    """Tests for get_video_details method."""

    @pytest.mark.asyncio
    async def test_get_video_details_success(self, provider, mock_video_data):
        """Test successful video details retrieval."""
        mock_video_data["description"] = "Test description"
        mock_video_data["tags"] = ["tag1", "tag2"]
        mock_video_data["formats"] = [{"format_id": "22"}]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = mock_video_data

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            details = await provider.get_video_details("dQw4w9WgXcQ")

            assert isinstance(details, VideoDetails)
            assert details.video_id == "dQw4w9WgXcQ"
            assert details.title == "Rick Astley - Never Gonna Give You Up"

    @pytest.mark.asyncio
    async def test_get_video_details_not_found(self, provider):
        """Test video details when video not found."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Video unavailable"
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with pytest.raises(VideoNotFoundError):
                await provider.get_video_details("notexistent")

    @pytest.mark.asyncio
    async def test_get_video_details_network_error(self, provider):
        """Test video details with network error."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Connection timeout"
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with pytest.raises(NetworkError):
                await provider.get_video_details("dQw4w9WgXcQ")


class TestValidateConnection:
    """Tests for validate_connection method."""

    @pytest.mark.asyncio
    async def test_validate_connection_success(self, provider, mock_video_data):
        """Test successful connection validation."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": [mock_video_data]}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            result = await provider.validate_connection()

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_connection_failure(self, provider):
        """Test failed connection validation."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = Exception("Connection failed")

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            result = await provider.validate_connection()

            assert result is False


class TestSearchPlaylists:
    """Tests for search_playlists method."""

    @pytest.mark.asyncio
    async def test_search_playlists_success(self, provider, mock_playlist_data):
        """Test successful playlist search."""
        mock_entries = [
            {"_type": "playlist", **mock_playlist_data},
        ]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            results = await provider.search_playlists("python tutorial", max_results=5)

            assert len(results) == 1
            assert all(isinstance(p, Playlist) for p in results)

    @pytest.mark.asyncio
    async def test_search_playlists_empty_results(self, provider):
        """Test playlist search with no results."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": []}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            results = await provider.search_playlists("xyznonexistent123", max_results=5)

            assert results == []


class TestExecutePlaylistSearch:
    """Tests for _execute_playlist_search method."""

    def test_execute_playlist_search_success(self, provider):
        """Test playlist search with mocked yt-dlp response."""
        mock_entries = [
            {
                "_type": "playlist",
                "id": "PL123",
                "title": "Test Playlist 1",
                "uploader": "Test Channel",
                "url": "https://youtube.com/playlist?list=PL123",
            },
            {
                "_type": "url",
                "ie_key": "YoutubeTab",
                "id": "PL456",
                "title": "Test Playlist 2",
                "url": "https://youtube.com/playlist?list=PL456",
            },
            {
                "_type": "video",
                "id": "video1",
                "title": "Not a playlist",
            },
        ]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            results = provider._execute_playlist_search("test query", max_results=5)

            assert len(results) == 2
            assert results[0]["id"] == "PL123"
            assert results[1]["id"] == "PL456"

    def test_execute_playlist_search_fallback(self, provider):
        """Test fallback mechanism when URL search fails."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = [
            Exception("Search URL failed"),
            {"entries": [{"_type": "playlist", "id": "fallback_pl"}]},
        ]

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            results = provider._execute_playlist_search("test query", max_results=5)

            assert mock_ydl_instance.extract_info.call_count == 2
            assert len(results) == 1
            assert results[0]["id"] == "fallback_pl"


class TestGetPlaylistDetails:
    """Tests for get_playlist_details method."""

    @pytest.mark.asyncio
    async def test_get_playlist_details_success(self, provider, mock_playlist_data):
        """Test successful playlist details retrieval."""
        mock_playlist_data["availability"] = "public"
        mock_playlist_data["tags"] = ["python", "tutorial"]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = mock_playlist_data

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            details = await provider.get_playlist_details("PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")

            assert isinstance(details, PlaylistDetails)
            assert details.title == "Python Tutorial Playlist"

    @pytest.mark.asyncio
    async def test_get_playlist_details_not_found(self, provider):
        """Test playlist details when playlist not found."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Video unavailable"
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with pytest.raises(VideoNotFoundError):
                await provider.get_playlist_details("PLnotexistent")


class TestGetPlaylistVideos:
    """Tests for get_playlist_videos method."""

    @pytest.mark.asyncio
    async def test_get_playlist_videos_success(self, provider, mock_video_data):
        """Test successful playlist videos retrieval."""
        mock_entries = [mock_video_data, mock_video_data]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            videos = await provider.get_playlist_videos("PLtest123456")

            assert len(videos) == 2
            assert all(isinstance(v, Video) for v in videos)

    @pytest.mark.asyncio
    async def test_get_playlist_videos_with_limit(self, provider, mock_video_data):
        """Test playlist videos with max_results limit."""
        mock_entries = [mock_video_data, mock_video_data, mock_video_data]

        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {"entries": mock_entries}

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            videos = await provider.get_playlist_videos("PLtest123456", max_results=2)

            assert len(videos) == 2

    @pytest.mark.asyncio
    async def test_get_playlist_videos_not_found(self, provider):
        """Test playlist videos when playlist not found."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Video unavailable"  # Must match the unavailable pattern
        )

        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

            with pytest.raises(VideoNotFoundError):
                await provider.get_playlist_videos("PLnotexistent")

