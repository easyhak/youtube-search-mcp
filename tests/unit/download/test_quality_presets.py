"""Tests for quality_presets module."""


from youtube_search_mcp.download.quality_presets import (
    get_audio_format_string,
    get_audio_postprocessors,
    get_video_format_string,
)


class TestGetVideoFormatString:
    """Tests for get_video_format_string function."""

    def test_get_video_format_best(self):
        """Test video format string for 'best' quality."""
        result = get_video_format_string("best")

        assert result is not None
        assert isinstance(result, str)
        assert "best" in result or "bestvideo" in result

    def test_get_video_format_high(self):
        """Test video format string for 'high' quality."""
        result = get_video_format_string("high")

        assert result is not None
        assert "1080" in result or "720" in result or "best" in result

    def test_get_video_format_medium(self):
        """Test video format string for 'medium' quality."""
        result = get_video_format_string("medium")

        assert result is not None

    def test_get_video_format_low(self):
        """Test video format string for 'low' quality."""
        result = get_video_format_string("low")

        assert result is not None

    def test_get_video_format_unknown(self):
        """Test video format string for unknown quality defaults to best."""
        result = get_video_format_string("unknown")

        assert result is not None


class TestGetAudioFormatString:
    """Tests for get_audio_format_string function."""

    def test_get_audio_format_best(self):
        """Test audio format string for 'best' quality."""
        result = get_audio_format_string("best")

        assert result is not None
        assert isinstance(result, str)

    def test_get_audio_format_high(self):
        """Test audio format string for 'high' quality."""
        result = get_audio_format_string("high")

        assert result is not None

    def test_get_audio_format_medium(self):
        """Test audio format string for 'medium' quality."""
        result = get_audio_format_string("medium")

        assert result is not None

    def test_get_audio_format_low(self):
        """Test audio format string for 'low' quality."""
        result = get_audio_format_string("low")

        assert result is not None


class TestGetAudioPostprocessors:
    """Tests for get_audio_postprocessors function."""

    def test_get_audio_postprocessors_mp3(self):
        """Test audio postprocessors for mp3 format."""
        result = get_audio_postprocessors("mp3")

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(p.get("key") == "FFmpegExtractAudio" for p in result)

    def test_get_audio_postprocessors_m4a(self):
        """Test audio postprocessors for m4a format."""
        result = get_audio_postprocessors("m4a")

        assert isinstance(result, list)

    def test_get_audio_postprocessors_opus(self):
        """Test audio postprocessors for opus format."""
        result = get_audio_postprocessors("opus")

        assert isinstance(result, list)

    def test_get_audio_postprocessors_wav(self):
        """Test audio postprocessors for wav format."""
        result = get_audio_postprocessors("wav")

        assert isinstance(result, list)

