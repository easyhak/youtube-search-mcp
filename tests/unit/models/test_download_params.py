"""Tests for DownloadParams and DownloadResult models."""

import pytest
from pydantic import ValidationError

from youtube_search_mcp.models.download_params import DownloadParams, DownloadResult


class TestDownloadParams:
    """Tests for DownloadParams model."""

    def test_download_params_with_required_fields_only(self):
        """Test creating DownloadParams with only required field."""
        params = DownloadParams(video_id="dQw4w9WgXcQ")

        assert params.video_id == "dQw4w9WgXcQ"
        assert params.quality == "best"  # default
        assert params.output_dir is None  # default
        assert params.format == "mp4"  # default
        assert params.download_type == "video"  # default

    def test_download_params_with_all_fields(self):
        """Test creating DownloadParams with all fields."""
        params = DownloadParams(
            video_id="dQw4w9WgXcQ",
            quality="high",
            output_dir="C:\\Users\\Downloads",
            format="webm",
            download_type="video",
        )

        assert params.video_id == "dQw4w9WgXcQ"
        assert params.quality == "high"
        assert params.output_dir == "C:\\Users\\Downloads"
        assert params.format == "webm"
        assert params.download_type == "video"

    def test_download_params_audio_type(self):
        """Test creating DownloadParams for audio download."""
        params = DownloadParams(
            video_id="dQw4w9WgXcQ",
            format="mp3",
            download_type="audio",
        )

        assert params.format == "mp3"
        assert params.download_type == "audio"

    def test_download_params_missing_video_id(self):
        """Test that missing video_id raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadParams()

    def test_download_params_video_id_too_short(self):
        """Test that video_id shorter than 11 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadParams(video_id="short")

    def test_download_params_video_id_too_long(self):
        """Test that video_id longer than 11 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadParams(video_id="toolongvideoid")

    def test_download_params_video_id_exact_length(self):
        """Test video_id with exactly 11 characters."""
        params = DownloadParams(video_id="12345678901")

        assert params.video_id == "12345678901"

    def test_download_params_quality_best(self):
        """Test quality with 'best' value."""
        params = DownloadParams(video_id="dQw4w9WgXcQ", quality="best")

        assert params.quality == "best"

    def test_download_params_quality_high(self):
        """Test quality with 'high' value."""
        params = DownloadParams(video_id="dQw4w9WgXcQ", quality="high")

        assert params.quality == "high"

    def test_download_params_quality_medium(self):
        """Test quality with 'medium' value."""
        params = DownloadParams(video_id="dQw4w9WgXcQ", quality="medium")

        assert params.quality == "medium"

    def test_download_params_quality_low(self):
        """Test quality with 'low' value."""
        params = DownloadParams(video_id="dQw4w9WgXcQ", quality="low")

        assert params.quality == "low"

    def test_download_params_quality_invalid(self):
        """Test that invalid quality value raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadParams(video_id="dQw4w9WgXcQ", quality="ultra")

    def test_download_params_download_type_invalid(self):
        """Test that invalid download_type raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadParams(video_id="dQw4w9WgXcQ", download_type="playlist")

    def test_download_params_model_dump(self):
        """Test converting DownloadParams to dictionary."""
        params = DownloadParams(
            video_id="dQw4w9WgXcQ",
            quality="high",
            format="mp4",
        )
        data = params.model_dump()

        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["quality"] == "high"
        assert data["format"] == "mp4"


class TestDownloadResult:
    """Tests for DownloadResult model."""

    def test_download_result_success(self):
        """Test creating successful DownloadResult."""
        result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Rick Astley - Never Gonna Give You Up",
            file_path="C:\\Users\\Downloads\\video.mp4",
            file_size=52428800,
            duration=212,
            format="mp4",
            quality="high",
        )

        assert result.success is True
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.title == "Rick Astley - Never Gonna Give You Up"
        assert result.file_path == "C:\\Users\\Downloads\\video.mp4"
        assert result.file_size == 52428800
        assert result.duration == 212
        assert result.format == "mp4"
        assert result.quality == "high"
        assert result.error is None

    def test_download_result_failure(self):
        """Test creating failed DownloadResult."""
        result = DownloadResult(
            success=False,
            video_id="invalid1234",
            title="Unknown",
            format="mp4",
            quality="best",
            error="Video not found",
        )

        assert result.success is False
        assert result.error == "Video not found"
        assert result.file_path is None
        assert result.file_size is None

    def test_download_result_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            DownloadResult(
                success=True,
                video_id="dQw4w9WgXcQ",
            )

    def test_download_result_model_dump(self):
        """Test converting DownloadResult to dictionary."""
        result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            format="mp4",
            quality="best",
        )
        data = result.model_dump()

        assert data["success"] is True
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["file_path"] is None

    def test_download_result_large_file_size(self):
        """Test DownloadResult with large file size."""
        result = DownloadResult(
            success=True,
            video_id="largefile12",
            title="Large Video",
            file_size=10737418240,  # 10 GB
            format="mp4",
            quality="best",
        )

        assert result.file_size == 10737418240

    def test_download_result_audio_format(self):
        """Test DownloadResult for audio download."""
        result = DownloadResult(
            success=True,
            video_id="dQw4w9WgXcQ",
            title="Rick Astley - Never Gonna Give You Up",
            file_path="C:\\Users\\Downloads\\audio.mp3",
            file_size=5242880,
            duration=212,
            format="mp3",
            quality="high",
        )

        assert result.format == "mp3"

