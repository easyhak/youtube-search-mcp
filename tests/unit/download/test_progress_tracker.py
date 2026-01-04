"""Tests for progress_tracker module."""

from unittest.mock import MagicMock

from youtube_search_mcp.download.progress_tracker import (
    ProgressTracker,
    create_progress_hook,
)


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_progress_tracker_init(self):
        """Test ProgressTracker initialization."""
        tracker = ProgressTracker("test_video")

        assert tracker.video_id == "test_video"
        assert tracker.total_bytes is None
        assert tracker.downloaded_bytes == 0
        assert tracker.speed is None
        assert tracker.eta is None

    def test_progress_tracker_with_callback(self):
        """Test ProgressTracker with callback."""
        callback = MagicMock()
        tracker = ProgressTracker("test_video", callback=callback)

        assert tracker.callback is callback

    def test_progress_tracker_hook_downloading(self):
        """Test hook with downloading status."""
        tracker = ProgressTracker("test_video")

        d = {
            "status": "downloading",
            "total_bytes": 1000000,
            "downloaded_bytes": 500000,
            "speed": 100000,
            "eta": 5,
            "_percent_str": "50.0%",
            "_speed_str": "100.0KiB/s",
            "_eta_str": "00:05",
        }

        tracker.hook(d)

        assert tracker.total_bytes == 1000000
        assert tracker.downloaded_bytes == 500000
        assert tracker.speed == 100000
        assert tracker.eta == 5

    def test_progress_tracker_hook_finished(self):
        """Test hook with finished status."""
        callback = MagicMock()
        tracker = ProgressTracker("test_video", callback=callback)

        d = {
            "status": "finished",
            "filename": "/path/to/video.mp4",
        }

        tracker.hook(d)

        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args["status"] == "finished"
        assert call_args["filename"] == "/path/to/video.mp4"

    def test_progress_tracker_hook_error(self):
        """Test hook with error status."""
        callback = MagicMock()
        tracker = ProgressTracker("test_video", callback=callback)

        d = {
            "status": "error",
            "error": "Download failed",
        }

        tracker.hook(d)

        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args["status"] == "error"
        assert call_args["error"] == "Download failed"


class TestCreateProgressHook:
    """Tests for create_progress_hook function."""

    def test_create_progress_hook_returns_callable(self):
        """Test that create_progress_hook returns a callable."""
        hook = create_progress_hook("test_video")

        assert callable(hook)

    def test_progress_hook_downloading_status(self):
        """Test progress hook with downloading status."""
        hook = create_progress_hook("test_video")

        info = {
            "status": "downloading",
            "_percent_str": "50.0%",
            "_speed_str": "1.5MiB/s",
            "_eta_str": "00:30",
        }

        # Should not raise
        hook(info)

    def test_progress_hook_finished_status(self):
        """Test progress hook with finished status."""
        hook = create_progress_hook("test_video")

        info = {
            "status": "finished",
            "filename": "test_video.mp4",
        }

        # Should not raise
        hook(info)

    def test_progress_hook_error_status(self):
        """Test progress hook with error status."""
        hook = create_progress_hook("test_video")

        info = {
            "status": "error",
        }

        # Should not raise
        hook(info)
