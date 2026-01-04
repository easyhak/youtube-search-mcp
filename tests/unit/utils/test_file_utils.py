"""Tests for file_utils module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from youtube_search_mcp.core.exceptions import FFmpegNotFoundError
from youtube_search_mcp.utils.file_utils import (
    check_directory_writable,
    check_disk_space,
    check_ffmpeg_available,
    ensure_directory_exists,
    get_ffmpeg_installation_guide,
    get_ffmpeg_path,
    get_file_size,
    get_unique_filename,
    validate_download_path,
)


class TestCheckDiskSpace:
    """Tests for check_disk_space function."""

    def test_check_disk_space_sufficient(self):
        """Test check_disk_space returns True when sufficient space."""
        # Current directory should have some space
        result = check_disk_space(".", 1)  # 1 MB required

        assert result is True

    def test_check_disk_space_insufficient(self):
        """Test check_disk_space returns False when insufficient space."""
        # Request impossibly large amount
        result = check_disk_space(".", 999999999999)  # ~1 petabyte

        assert result is False

    def test_check_disk_space_invalid_path(self):
        """Test check_disk_space returns True on invalid path (fail-safe)."""
        result = check_disk_space("/nonexistent/path/that/does/not/exist", 1)

        assert result is True  # Fail-safe: assume there's enough space


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists function."""

    def test_ensure_directory_creates_dir(self):
        """Test that ensure_directory_exists creates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_subdir")
            assert not os.path.exists(new_dir)

            ensure_directory_exists(new_dir)

            assert os.path.exists(new_dir)

    def test_ensure_directory_existing_dir(self):
        """Test that ensure_directory_exists handles existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise
            ensure_directory_exists(tmpdir)

            assert os.path.exists(tmpdir)

    def test_ensure_directory_creates_nested(self):
        """Test that ensure_directory_exists creates nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "a", "b", "c")

            ensure_directory_exists(new_dir)

            assert os.path.exists(new_dir)


class TestCheckDirectoryWritable:
    """Tests for check_directory_writable function."""

    def test_check_writable_temp_dir(self):
        """Test that temp directory is writable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = check_directory_writable(tmpdir)

            assert result is True

    def test_check_writable_nonexistent_dir(self):
        """Test that nonexistent directory is not writable."""
        result = check_directory_writable("/nonexistent/path")

        assert result is False


class TestGetFileSize:
    """Tests for get_file_size function."""

    def test_get_file_size_existing_file(self):
        """Test getting size of existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello, World!")
            f.flush()
            temp_path = f.name

        # File must be closed before checking size on Windows
        size = get_file_size(temp_path)
        assert size == 13

        # Clean up
        try:
            os.unlink(temp_path)
        except (OSError, PermissionError):
            pass  # Ignore cleanup errors on Windows

    def test_get_file_size_nonexistent_file(self):
        """Test getting size of nonexistent file returns None."""
        result = get_file_size("/nonexistent/file.txt")

        assert result is None


class TestValidateDownloadPath:
    """Tests for validate_download_path function."""

    def test_validate_valid_path(self):
        """Test validate_download_path with valid path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            is_valid, error = validate_download_path(tmpdir, required_mb=1)

            assert is_valid is True
            assert error is None

    def test_validate_creates_directory(self):
        """Test validate_download_path creates directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_download_dir")

            is_valid, error = validate_download_path(new_dir, required_mb=1)

            assert is_valid is True
            assert os.path.exists(new_dir)


class TestGetUniqueFilename:
    """Tests for get_unique_filename function."""

    def test_get_unique_filename_new_file(self):
        """Test get_unique_filename returns original if file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_unique_filename(tmpdir, "test.mp4")

            assert result == "test.mp4"

    def test_get_unique_filename_existing_file(self):
        """Test get_unique_filename appends number if file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing file
            (Path(tmpdir) / "test.mp4").touch()

            result = get_unique_filename(tmpdir, "test.mp4")

            assert result == "test (1).mp4"

    def test_get_unique_filename_multiple_existing(self):
        """Test get_unique_filename handles multiple existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple existing files
            (Path(tmpdir) / "test.mp4").touch()
            (Path(tmpdir) / "test (1).mp4").touch()
            (Path(tmpdir) / "test (2).mp4").touch()

            result = get_unique_filename(tmpdir, "test.mp4")

            assert result == "test (3).mp4"


class TestGetFfmpegInstallationGuide:
    """Tests for get_ffmpeg_installation_guide function."""

    def test_installation_guide_windows(self):
        """Test installation guide for Windows."""
        with patch("platform.system", return_value="Windows"):
            guide = get_ffmpeg_installation_guide()

            assert "Windows" in guide
            assert "choco install ffmpeg" in guide

    def test_installation_guide_macos(self):
        """Test installation guide for macOS."""
        with patch("platform.system", return_value="Darwin"):
            guide = get_ffmpeg_installation_guide()

            assert "macOS" in guide
            assert "brew install ffmpeg" in guide

    def test_installation_guide_linux(self):
        """Test installation guide for Linux."""
        with patch("platform.system", return_value="Linux"):
            guide = get_ffmpeg_installation_guide()

            assert "Linux" in guide
            assert "apt install ffmpeg" in guide


class TestCheckFfmpegAvailable:
    """Tests for check_ffmpeg_available function."""

    def test_check_ffmpeg_not_found(self):
        """Test check_ffmpeg_available raises when ffmpeg not found."""
        with patch("shutil.which", return_value=None):
            with pytest.raises(FFmpegNotFoundError) as exc_info:
                check_ffmpeg_available()

            assert "FFmpeg" in str(exc_info.value)

    def test_check_ffmpeg_found(self):
        """Test check_ffmpeg_available succeeds when ffmpeg found."""
        with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
            # Should not raise
            check_ffmpeg_available()


class TestGetFfmpegPath:
    """Tests for get_ffmpeg_path function."""

    def test_get_ffmpeg_path_normal(self):
        """Test get_ffmpeg_path returns 'ffmpeg' in normal environment."""
        result = get_ffmpeg_path()

        assert result == "ffmpeg"

    def test_get_ffmpeg_path_frozen_windows(self):
        """Test get_ffmpeg_path in frozen Windows environment."""
        with patch.object(__import__("sys"), "frozen", True, create=True):
            with patch.object(__import__("sys"), "_MEIPASS", "/bundled", create=True):
                with patch.object(__import__("sys"), "executable", "C:\\app\\app.exe"):
                    with patch("os.name", "nt"):
                        result = get_ffmpeg_path()

                        assert "ffmpeg" in result

