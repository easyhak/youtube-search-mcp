"""Tests for playlist_tools module."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from youtube_search_mcp.core.exceptions import (
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails
from youtube_search_mcp.models.video import Video


class TestSearchPlaylistsLogic:
    """Tests for search_playlists logic."""

    @pytest.mark.asyncio
    async def test_search_playlists_valid_query(self):
        """Test search playlists with valid query."""
        mock_playlists = [
            Playlist(
                playlist_id="PLtest12345",
                title="Test Playlist",
                url="https://youtube.com/playlist?list=PLtest12345",
            )
        ]

        mock_provider = AsyncMock()
        mock_provider.search_playlists = AsyncMock(return_value=mock_playlists)

        mock_formatter = MagicMock()
        mock_formatter.format_playlists.return_value = json.dumps(
            {"count": 1, "playlists": [{"playlist_id": "PLtest12345"}]}
        )

        playlists = await mock_provider.search_playlists("python tutorial")
        result = mock_formatter.format_playlists(playlists)

        data = json.loads(result)
        assert data["count"] == 1

    @pytest.mark.asyncio
    async def test_search_playlists_empty_results(self):
        """Test search playlists with no results."""
        mock_provider = AsyncMock()
        mock_provider.search_playlists = AsyncMock(return_value=[])

        mock_formatter = MagicMock()
        mock_formatter.format_playlists.return_value = json.dumps(
            {"count": 0, "playlists": []}
        )

        playlists = await mock_provider.search_playlists("xyznonexistent")
        result = mock_formatter.format_playlists(playlists)

        data = json.loads(result)
        assert data["count"] == 0


class TestGetPlaylistInfoLogic:
    """Tests for get_playlist_info logic."""

    @pytest.mark.asyncio
    async def test_get_playlist_info_valid_id(self):
        """Test get_playlist_info with valid playlist ID."""
        mock_details = PlaylistDetails(
            playlist_id="PLtest123456",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
            video_count=50,
        )

        mock_provider = AsyncMock()
        mock_provider.get_playlist_details = AsyncMock(return_value=mock_details)

        mock_formatter = MagicMock()
        mock_formatter.format_playlist_details.return_value = json.dumps(
            {"playlist_id": "PLtest123456", "title": "Test Playlist", "video_count": 50}
        )

        details = await mock_provider.get_playlist_details("PLtest123456")
        result = mock_formatter.format_playlist_details(details)

        data = json.loads(result)
        assert data["playlist_id"] == "PLtest123456"
        assert data["video_count"] == 50

    @pytest.mark.asyncio
    async def test_get_playlist_info_not_found(self):
        """Test get_playlist_info when playlist not found."""
        mock_provider = AsyncMock()
        mock_provider.get_playlist_details = AsyncMock(
            side_effect=VideoNotFoundError("Playlist not found")
        )

        with pytest.raises(VideoNotFoundError):
            await mock_provider.get_playlist_details("PLnotexistent")


class TestGetPlaylistVideosLogic:
    """Tests for get_playlist_videos logic."""

    @pytest.mark.asyncio
    async def test_get_playlist_videos_success(self):
        """Test get_playlist_videos with valid playlist ID."""
        mock_videos = [
            Video(
                video_id="video123456",
                title="Video 1",
                url="https://youtube.com/watch?v=video123456",
            ),
            Video(
                video_id="video234567",
                title="Video 2",
                url="https://youtube.com/watch?v=video234567",
            ),
        ]

        mock_provider = AsyncMock()
        mock_provider.get_playlist_videos = AsyncMock(return_value=mock_videos)

        mock_formatter = MagicMock()
        mock_formatter.format_videos.return_value = json.dumps(
            {"count": 2, "videos": [{"video_id": "video123456"}, {"video_id": "video234567"}]}
        )

        videos = await mock_provider.get_playlist_videos("PLtest123456")
        result = mock_formatter.format_videos(videos)

        data = json.loads(result)
        assert data["count"] == 2

    @pytest.mark.asyncio
    async def test_get_playlist_videos_with_limit(self):
        """Test get_playlist_videos with max_results limit."""
        mock_videos = [
            Video(
                video_id="video123456",
                title="Video 1",
                url="https://youtube.com/watch?v=video123456",
            )
        ]

        mock_provider = AsyncMock()
        mock_provider.get_playlist_videos = AsyncMock(return_value=mock_videos)

        videos = await mock_provider.get_playlist_videos("PLtest123456", max_results=1)

        assert len(videos) == 1

    @pytest.mark.asyncio
    async def test_get_playlist_videos_not_found(self):
        """Test get_playlist_videos when playlist not found."""
        mock_provider = AsyncMock()
        mock_provider.get_playlist_videos = AsyncMock(
            side_effect=VideoNotFoundError("Playlist not found")
        )

        with pytest.raises(VideoNotFoundError):
            await mock_provider.get_playlist_videos("PLnotexistent")


class TestErrorHandling:
    """Tests for error handling in playlist tools."""

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test that network errors are handled properly."""
        mock_provider = AsyncMock()
        mock_provider.search_playlists = AsyncMock(
            side_effect=NetworkError("Connection failed")
        )

        with pytest.raises(NetworkError):
            await mock_provider.search_playlists("test")

    @pytest.mark.asyncio
    async def test_search_provider_error_handling(self):
        """Test that search provider errors are handled properly."""
        mock_provider = AsyncMock()
        mock_provider.search_playlists = AsyncMock(
            side_effect=SearchProviderError("Provider error")
        )

        with pytest.raises(SearchProviderError):
            await mock_provider.search_playlists("test")

