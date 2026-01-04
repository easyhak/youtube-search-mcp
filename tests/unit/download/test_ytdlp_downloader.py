"""Tests for YtDlpDownloader."""

from unittest.mock import MagicMock, patch

import pytest
import yt_dlp

from youtube_search_mcp.core.exceptions import (
    DiskSpaceError,
    DownloadError,
    FFmpegNotFoundError,
    NetworkError,
    VideoNotFoundError,
)
from youtube_search_mcp.download.ytdlp_downloader import YtDlpDownloader
from youtube_search_mcp.models.download_params import DownloadParams, DownloadResult


@pytest.fixture
def downloader():
    """Create YtDlpDownloader instance."""
    return YtDlpDownloader(default_output_dir="test_downloads")


@pytest.fixture
def video_params():
    """Create sample video download parameters."""
    return DownloadParams(
        video_id="dQw4w9WgXcQ",
        quality="high",
        format="mp4",
        download_type="video",
    )


@pytest.fixture
def audio_params():
    """Create sample audio download parameters."""
    return DownloadParams(
        video_id="dQw4w9WgXcQ",
        quality="high",
        format="mp3",
        download_type="audio",
    )


@pytest.fixture
def mock_video_info():
    """Create mock video info from yt-dlp."""
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up",
        "duration": 212,
        "filepath": "test_downloads/Rick Astley - Never Gonna Give You Up.mp4",
        "requested_downloads": [
            {"filepath": "test_downloads/Rick Astley - Never Gonna Give You Up.mp4"}
        ],
    }


class TestYtDlpDownloaderInit:
    """Tests for YtDlpDownloader initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        downloader = YtDlpDownloader()

        assert downloader._default_output_dir == "downloads"
        assert downloader._min_disk_space_mb == 100

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        downloader = YtDlpDownloader(
            default_output_dir="/custom/path",
            min_disk_space_mb=500,
        )

        assert downloader._default_output_dir == "/custom/path"
        assert downloader._min_disk_space_mb == 500


class TestValidateOutputDirectory:
    """Tests for _validate_output_directory method."""

    def test_validate_with_valid_path(self, downloader):
        """Test validation with valid path."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
        ) as mock_validate:
            mock_validate.return_value = (True, "")

            result = downloader._validate_output_directory("/valid/path")

            assert result == "/valid/path"

    def test_validate_with_none_uses_default(self, downloader):
        """Test that None uses default output directory."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
        ) as mock_validate:
            mock_validate.return_value = (True, "")

            result = downloader._validate_output_directory(None)

            assert result == "test_downloads"

    def test_validate_raises_disk_space_error(self, downloader):
        """Test that DiskSpaceError is raised when insufficient space."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
        ) as mock_validate:
            mock_validate.return_value = (False, "Not enough disk space available")

            with pytest.raises(DiskSpaceError):
                downloader._validate_output_directory("/some/path")


class TestExtractFilePath:
    """Tests for _extract_file_path method."""

    def test_extract_from_filepath(self, downloader):
        """Test extracting file path from filepath key."""
        with patch("os.path.exists", return_value=True):
            result = downloader._extract_file_path({"filepath": "/path/to/file.mp4"})

            assert result == "/path/to/file.mp4"

    def test_extract_from_filename(self, downloader):
        """Test extracting file path from filename key."""
        with patch("os.path.exists", return_value=True):
            result = downloader._extract_file_path({"filename": "/path/to/file.mp4"})

            assert result == "/path/to/file.mp4"

    def test_extract_from_requested_downloads(self, downloader):
        """Test extracting file path from requested_downloads."""
        with patch("os.path.exists", return_value=True):
            result = downloader._extract_file_path(
                {"requested_downloads": [{"filepath": "/path/to/file.mp4"}]}
            )

            assert result == "/path/to/file.mp4"

    def test_extract_raises_error_when_not_found(self, downloader):
        """Test that DownloadError is raised when file not found."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(DownloadError):
                downloader._extract_file_path({"filepath": "/nonexistent/file.mp4"})


class TestHandleYtdlpError:
    """Tests for _handle_ytdlp_error method."""

    def test_handle_video_unavailable_error(self, downloader):
        """Test handling video unavailable error."""
        error = yt_dlp.utils.DownloadError("Video unavailable")

        with pytest.raises(VideoNotFoundError):
            downloader._handle_ytdlp_error(error, "test_id")

    def test_handle_private_video_error(self, downloader):
        """Test handling private video error."""
        error = yt_dlp.utils.DownloadError("Private video")

        with pytest.raises(VideoNotFoundError):
            downloader._handle_ytdlp_error(error, "test_id")

    def test_handle_network_error(self, downloader):
        """Test handling network error."""
        error = yt_dlp.utils.DownloadError("Unable to download webpage")

        with pytest.raises(NetworkError):
            downloader._handle_ytdlp_error(error, "test_id")

    def test_handle_connection_error(self, downloader):
        """Test handling connection error."""
        error = yt_dlp.utils.DownloadError("Connection refused")

        with pytest.raises(NetworkError):
            downloader._handle_ytdlp_error(error, "test_id")

    def test_handle_generic_download_error(self, downloader):
        """Test handling generic download error."""
        error = yt_dlp.utils.DownloadError("Some unknown error")

        with pytest.raises(DownloadError):
            downloader._handle_ytdlp_error(error, "test_id")


class TestBuildVideoOptions:
    """Tests for _build_video_options method."""

    def test_build_options_basic(self, downloader, video_params):
        """Test building basic video options."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.get_video_format_string"
        ) as mock_format:
            mock_format.return_value = "bestvideo+bestaudio"

            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
            ) as mock_ffmpeg:
                mock_ffmpeg.return_value = None

                opts = downloader._build_video_options(video_params, "output_dir")

                assert opts["format"] == "bestvideo+bestaudio"
                assert opts["merge_output_format"] == "mp4"
                assert opts["quiet"] is True

    def test_build_options_includes_progress_hook(self, downloader, video_params):
        """Test that progress hook is included in options."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.get_video_format_string"
        ) as mock_format:
            mock_format.return_value = "bestvideo+bestaudio"

            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
            ) as mock_ffmpeg:
                mock_ffmpeg.return_value = None

                opts = downloader._build_video_options(video_params, "output_dir")

                assert "progress_hooks" in opts
                assert len(opts["progress_hooks"]) == 1


class TestBuildAudioOptions:
    """Tests for _build_audio_options method."""

    def test_build_options_basic(self, downloader, audio_params):
        """Test building basic audio options."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.get_audio_format_string"
        ) as mock_format:
            mock_format.return_value = "bestaudio/best"

            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.get_audio_postprocessors"
            ) as mock_pp:
                mock_pp.return_value = [{"key": "FFmpegExtractAudio"}]

                with patch(
                    "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
                ) as mock_ffmpeg:
                    mock_ffmpeg.return_value = None

                    opts = downloader._build_audio_options(audio_params, "output_dir")

                    assert opts["format"] == "bestaudio/best"
                    assert opts["quiet"] is True


class TestDownloadVideo:
    """Tests for download_video method."""

    @pytest.mark.asyncio
    async def test_download_video_success(self, downloader, video_params, mock_video_info):
        """Test successful video download."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.check_ffmpeg_available"
        ):
            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
            ) as mock_validate:
                mock_validate.return_value = (True, "")

                with patch(
                    "youtube_search_mcp.download.ytdlp_downloader.get_video_format_string"
                ):
                    with patch(
                        "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
                    ):
                        with patch("os.path.exists", return_value=True):
                            with patch(
                                "youtube_search_mcp.download.ytdlp_downloader.get_file_size"
                            ) as mock_size:
                                mock_size.return_value = 52428800

                                mock_ydl_instance = MagicMock()
                                mock_ydl_instance.extract_info.return_value = mock_video_info
                                mock_ydl_instance.prepare_filename.return_value = "test.mp4"

                                with patch("yt_dlp.YoutubeDL") as mock_ydl:
                                    mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

                                    result = await downloader.download_video(video_params)

                                    assert isinstance(result, DownloadResult)
                                    assert result.success is True
                                    assert result.video_id == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_download_video_ffmpeg_not_found(self, downloader, video_params):
        """Test download when FFmpeg is not found."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.check_ffmpeg_available"
        ) as mock_check:
            mock_check.side_effect = FFmpegNotFoundError("FFmpeg not found")

            with pytest.raises(FFmpegNotFoundError):
                await downloader.download_video(video_params)

    @pytest.mark.asyncio
    async def test_download_video_not_found(self, downloader, video_params):
        """Test download when video not found."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.check_ffmpeg_available"
        ):
            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
            ) as mock_validate:
                mock_validate.return_value = (True, "")

                with patch(
                    "youtube_search_mcp.download.ytdlp_downloader.get_video_format_string"
                ):
                    with patch(
                        "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
                    ):
                        mock_ydl_instance = MagicMock()
                        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
                            "Video unavailable"
                        )

                        with patch("yt_dlp.YoutubeDL") as mock_ydl:
                            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

                            with pytest.raises(VideoNotFoundError):
                                await downloader.download_video(video_params)


class TestDownloadAudio:
    """Tests for download_audio method."""

    @pytest.mark.asyncio
    async def test_download_audio_success(self, downloader, audio_params, mock_video_info):
        """Test successful audio download."""
        mock_video_info["filepath"] = "test_downloads/audio.mp3"
        mock_video_info["requested_downloads"][0]["filepath"] = "test_downloads/audio.mp3"

        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.check_ffmpeg_available"
        ):
            with patch(
                "youtube_search_mcp.download.ytdlp_downloader.validate_download_path"
            ) as mock_validate:
                mock_validate.return_value = (True, "")

                with patch(
                    "youtube_search_mcp.download.ytdlp_downloader.get_audio_format_string"
                ):
                    with patch(
                        "youtube_search_mcp.download.ytdlp_downloader.get_audio_postprocessors"
                    ) as mock_pp:
                        mock_pp.return_value = []

                        with patch(
                            "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
                        ):
                            with patch("os.path.exists", return_value=True):
                                with patch(
                                    "youtube_search_mcp.download.ytdlp_downloader.get_file_size"
                                ) as mock_size:
                                    mock_size.return_value = 5242880

                                    mock_ydl_instance = MagicMock()
                                    mock_ydl_instance.extract_info.return_value = mock_video_info

                                    with patch("yt_dlp.YoutubeDL") as mock_ydl:
                                        mock_ydl.return_value.__enter__.return_value = (
                                            mock_ydl_instance
                                        )

                                        result = await downloader.download_audio(audio_params)

                                        assert isinstance(result, DownloadResult)
                                        assert result.success is True
                                        assert result.format == "mp3"


class TestGetAvailableFormats:
    """Tests for get_available_formats method."""

    @pytest.mark.asyncio
    async def test_get_formats_success(self, downloader):
        """Test successful format retrieval."""
        mock_info = {
            "title": "Test Video",
            "formats": [
                {"format_id": "22", "ext": "mp4", "resolution": "720p", "filesize": 100000},
                {"format_id": "18", "ext": "mp4", "resolution": "360p", "filesize": 50000},
            ],
        }

        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
        ):
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.return_value = mock_info

            with patch("yt_dlp.YoutubeDL") as mock_ydl:
                mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

                result = await downloader.get_available_formats("dQw4w9WgXcQ")

                assert result["video_id"] == "dQw4w9WgXcQ"
                assert result["title"] == "Test Video"
                assert result["format_count"] == 2

    @pytest.mark.asyncio
    async def test_get_formats_video_not_found(self, downloader):
        """Test format retrieval when video not found."""
        with patch(
            "youtube_search_mcp.download.ytdlp_downloader.get_ffmpeg_path"
        ):
            mock_ydl_instance = MagicMock()
            mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
                "Video unavailable"
            )

            with patch("yt_dlp.YoutubeDL") as mock_ydl:
                mock_ydl.return_value.__enter__.return_value = mock_ydl_instance

                with pytest.raises(VideoNotFoundError):
                    await downloader.get_available_formats("notexistent")

