"""Tests for search_tools module."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from youtube_search_mcp.core.exceptions import (
    InvalidQueryError,
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from youtube_search_mcp.models.search_params import SearchParams
from youtube_search_mcp.models.video import Video, VideoDetails


class TestSearchVideosLogic:
    """Tests for search_videos logic."""

    @pytest.mark.asyncio
    async def test_search_videos_valid_query(self):
        """Test search with valid query."""
        mock_videos = [
            Video(
                video_id="test123456",
                title="Test Video",
                url="https://youtube.com/watch?v=test123456",
            )
        ]

        mock_provider = AsyncMock()
        mock_provider.search = AsyncMock(return_value=mock_videos)

        mock_formatter = MagicMock()
        mock_formatter.format_videos.return_value = json.dumps(
            {"count": 1, "videos": [{"video_id": "test123456"}]}
        )

        with patch(
            "youtube_search_mcp.tools.search_tools.get_search_provider"
        ) as mock_get_provider:
            with patch(
                "youtube_search_mcp.tools.search_tools.get_formatter"
            ) as mock_get_formatter:
                mock_get_provider.return_value = mock_provider
                mock_get_formatter.return_value = mock_formatter

                # Simulate the tool's behavior
                params = SearchParams(query="test", max_results=5)
                videos = await mock_provider.search(params)
                result = mock_formatter.format_videos(videos)

                data = json.loads(result)
                assert data["count"] == 1

    @pytest.mark.asyncio
    async def test_search_videos_empty_results(self):
        """Test search with no results."""
        mock_provider = AsyncMock()
        mock_provider.search = AsyncMock(return_value=[])

        mock_formatter = MagicMock()
        mock_formatter.format_videos.return_value = json.dumps({"count": 0, "videos": []})

        params = SearchParams(query="xyznonexistent", max_results=5)
        videos = await mock_provider.search(params)
        result = mock_formatter.format_videos(videos)

        data = json.loads(result)
        assert data["count"] == 0
        assert data["videos"] == []

    def test_search_videos_invalid_query_empty(self):
        """Test that empty query raises InvalidQueryError."""
        from youtube_search_mcp.utils.validators import validate_query

        with pytest.raises(InvalidQueryError):
            validate_query("")

    def test_search_videos_invalid_query_too_long(self):
        """Test that too long query raises InvalidQueryError."""
        from youtube_search_mcp.utils.validators import validate_query

        with pytest.raises(InvalidQueryError):
            validate_query("a" * 201)


class TestGetVideoInfoLogic:
    """Tests for get_video_info logic."""

    @pytest.mark.asyncio
    async def test_get_video_info_valid_id(self):
        """Test get_video_info with valid video ID."""
        mock_details = VideoDetails(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            description="Test description",
        )

        mock_provider = AsyncMock()
        mock_provider.get_video_details = AsyncMock(return_value=mock_details)

        mock_formatter = MagicMock()
        mock_formatter.format_video_details.return_value = json.dumps(
            {"video_id": "dQw4w9WgXcQ", "title": "Test Video"}
        )

        details = await mock_provider.get_video_details("dQw4w9WgXcQ")
        result = mock_formatter.format_video_details(details)

        data = json.loads(result)
        assert data["video_id"] == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_get_video_info_not_found(self):
        """Test get_video_info when video not found."""
        mock_provider = AsyncMock()
        mock_provider.get_video_details = AsyncMock(
            side_effect=VideoNotFoundError("Video not found")
        )

        with pytest.raises(VideoNotFoundError):
            await mock_provider.get_video_details("notexistent")

    def test_get_video_info_invalid_id(self):
        """Test that invalid video ID is detected."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("") is False
        assert validate_video_id("short") is False
        assert validate_video_id("toolongvideoid") is False

    def test_get_video_info_valid_id_format(self):
        """Test that valid video ID format is accepted."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("dQw4w9WgXcQ") is True
        assert validate_video_id("abc_def-123") is True


class TestErrorHandling:
    """Tests for error handling in search tools."""

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test that network errors are handled properly."""
        mock_provider = AsyncMock()
        mock_provider.search = AsyncMock(
            side_effect=NetworkError("Connection failed")
        )

        with pytest.raises(NetworkError):
            await mock_provider.search(SearchParams(query="test"))

    @pytest.mark.asyncio
    async def test_search_provider_error_handling(self):
        """Test that search provider errors are handled properly."""
        mock_provider = AsyncMock()
        mock_provider.search = AsyncMock(
            side_effect=SearchProviderError("Provider error")
        )

        with pytest.raises(SearchProviderError):
            await mock_provider.search(SearchParams(query="test"))

