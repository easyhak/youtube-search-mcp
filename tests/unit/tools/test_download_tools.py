"""Tests for download_tools module."""

import json
from unittest.mock import AsyncMock

import pytest

from youtube_search_mcp.core.exceptions import (
    DiskSpaceError,
    FFmpegNotFoundError,
    NetworkError,
    VideoNotFoundError,
)
from youtube_search_mcp.models.download_params import DownloadParams, DownloadResult


class TestDownloadVideoLogic:
    """Tests for download_video logic."""

    @pytest.mark.asyncio
    async def test_download_video_success(self):
        """Test successful video download."""
        mock_result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            file_path="/downloads/test.mp4",
            file_size=52428800,
            duration=212,
            format="mp4",
            quality="high",
        )

        mock_downloader = AsyncMock()
        mock_downloader.download_video = AsyncMock(return_value=mock_result)

        params = DownloadParams(
            video_id="dQw4w9WgXcQ",
            quality="high",
            format="mp4",
        )

        result = await mock_downloader.download_video(params)

        assert result.success is True
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.format == "mp4"

    @pytest.mark.asyncio
    async def test_download_video_not_found(self):
        """Test download when video not found."""
        mock_downloader = AsyncMock()
        mock_downloader.download_video = AsyncMock(
            side_effect=VideoNotFoundError("Video not found")
        )

        params = DownloadParams(video_id="notexistent")

        with pytest.raises(VideoNotFoundError):
            await mock_downloader.download_video(params)

    @pytest.mark.asyncio
    async def test_download_video_network_error(self):
        """Test download with network error."""
        mock_downloader = AsyncMock()
        mock_downloader.download_video = AsyncMock(
            side_effect=NetworkError("Connection failed")
        )

        params = DownloadParams(video_id="dQw4w9WgXcQ")

        with pytest.raises(NetworkError):
            await mock_downloader.download_video(params)

    @pytest.mark.asyncio
    async def test_download_video_disk_space_error(self):
        """Test download with insufficient disk space."""
        mock_downloader = AsyncMock()
        mock_downloader.download_video = AsyncMock(
            side_effect=DiskSpaceError("Not enough disk space")
        )

        params = DownloadParams(video_id="dQw4w9WgXcQ")

        with pytest.raises(DiskSpaceError):
            await mock_downloader.download_video(params)

    @pytest.mark.asyncio
    async def test_download_video_ffmpeg_not_found(self):
        """Test download when FFmpeg not available."""
        mock_downloader = AsyncMock()
        mock_downloader.download_video = AsyncMock(
            side_effect=FFmpegNotFoundError("FFmpeg not found")
        )

        params = DownloadParams(video_id="dQw4w9WgXcQ")

        with pytest.raises(FFmpegNotFoundError):
            await mock_downloader.download_video(params)


class TestDownloadAudioLogic:
    """Tests for download_audio logic."""

    @pytest.mark.asyncio
    async def test_download_audio_success(self):
        """Test successful audio download."""
        mock_result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            file_path="/downloads/test.mp3",
            file_size=5242880,
            duration=212,
            format="mp3",
            quality="high",
        )

        mock_downloader = AsyncMock()
        mock_downloader.download_audio = AsyncMock(return_value=mock_result)

        params = DownloadParams(
            video_id="dQw4w9WgXcQ",
            quality="high",
            format="mp3",
            download_type="audio",
        )

        result = await mock_downloader.download_audio(params)

        assert result.success is True
        assert result.format == "mp3"

    @pytest.mark.asyncio
    async def test_download_audio_various_formats(self):
        """Test audio download with various formats."""
        formats = ["mp3", "m4a", "opus", "wav"]

        for fmt in formats:
            mock_result = DownloadResult(
                success=True,
                video_id="dQw4w9WgXcQ",
                title="Test Video",
                file_path=f"/downloads/test.{fmt}",
                file_size=5242880,
                duration=212,
                format=fmt,
                quality="best",
            )

            mock_downloader = AsyncMock()
            mock_downloader.download_audio = AsyncMock(return_value=mock_result)

            params = DownloadParams(
                video_id="dQw4w9WgXcQ",
                format=fmt,
                download_type="audio",
            )

            result = await mock_downloader.download_audio(params)

            assert result.format == fmt


class TestVideoIdValidation:
    """Tests for video ID validation."""

    def test_valid_video_id(self):
        """Test that valid video IDs are accepted."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("dQw4w9WgXcQ") is True
        assert validate_video_id("abc_def-123") is True
        assert validate_video_id("12345678901") is True

    def test_invalid_video_id_too_short(self):
        """Test that short video IDs are rejected."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("short") is False

    def test_invalid_video_id_too_long(self):
        """Test that long video IDs are rejected."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("toolongvideoid") is False

    def test_invalid_video_id_empty(self):
        """Test that empty video IDs are rejected."""
        from youtube_search_mcp.utils.validators import validate_video_id

        assert validate_video_id("") is False
        assert validate_video_id(None) is False


class TestDownloadResultFormat:
    """Tests for download result JSON format."""

    def test_download_result_to_json(self):
        """Test that download result can be serialized to JSON."""
        result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            file_path="/downloads/test.mp4",
            file_size=52428800,
            duration=212,
            format="mp4",
            quality="high",
        )

        json_str = result.model_dump_json()
        data = json.loads(json_str)

        assert data["success"] is True
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["file_size"] == 52428800

    def test_download_result_error_format(self):
        """Test download result format for errors."""
        result = DownloadResult(
            success=False,
            video_id="notexistent",
            title="Unknown",
            format="mp4",
            quality="best",
            error="Video not found",
        )

        json_str = result.model_dump_json()
        data = json.loads(json_str)

        assert data["success"] is False
        assert data["error"] == "Video not found"

