"""Common mock objects for testing."""

from unittest.mock import AsyncMock, MagicMock


def create_mock_ydl_instance(return_value=None, side_effect=None):
    """Create a mock yt-dlp YoutubeDL instance."""
    mock_instance = MagicMock()
    if side_effect:
        mock_instance.extract_info.side_effect = side_effect
    else:
        mock_instance.extract_info.return_value = return_value
    return mock_instance


def create_mock_search_provider(search_result=None, video_details=None, playlists=None):
    """Create a mock SearchProvider instance."""
    mock_provider = MagicMock()
    mock_provider.search = AsyncMock(return_value=search_result or [])
    mock_provider.get_video_details = AsyncMock(return_value=video_details)
    mock_provider.search_playlists = AsyncMock(return_value=playlists or [])
    mock_provider.get_playlist_details = AsyncMock(return_value=None)
    mock_provider.get_playlist_videos = AsyncMock(return_value=[])
    mock_provider.validate_connection = AsyncMock(return_value=True)
    return mock_provider


def create_mock_downloader(download_result=None):
    """Create a mock Downloader instance."""
    mock_downloader = MagicMock()
    mock_downloader.download_video = AsyncMock(return_value=download_result)
    mock_downloader.download_audio = AsyncMock(return_value=download_result)
    return mock_downloader


def create_mock_formatter():
    """Create a mock ResultFormatter instance."""
    mock_formatter = MagicMock()
    mock_formatter.format_videos.return_value = '{"count": 0, "videos": []}'
    mock_formatter.format_video_details.return_value = "{}"
    mock_formatter.format_playlists.return_value = '{"count": 0, "playlists": []}'
    mock_formatter.format_playlist_details.return_value = "{}"
    return mock_formatter

