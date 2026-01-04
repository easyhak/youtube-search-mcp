"""Tests for JSON formatter module."""

import json

import pytest

from youtube_search_mcp.formatters.json_formatter import JsonFormatter
from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails
from youtube_search_mcp.models.video import Video, VideoDetails


@pytest.fixture
def formatter():
    """Create JsonFormatter instance."""
    return JsonFormatter()


@pytest.fixture
def sample_video():
    """Create a sample Video instance."""
    return Video(
        video_id="dQw4w9WgXcQ",
        title="Rick Astley - Never Gonna Give You Up",
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        duration=212,
        view_count=1400000000,
        uploader="Rick Astley",
        upload_date="20091025",
        thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    )


@pytest.fixture
def sample_video_details():
    """Create a sample VideoDetails instance."""
    return VideoDetails(
        video_id="dQw4w9WgXcQ",
        title="Rick Astley - Never Gonna Give You Up",
        url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        duration=212,
        view_count=1400000000,
        uploader="Rick Astley",
        uploader_id="UCuAXFkgsw1L7xaCfnd5JJOw",
        upload_date="20091025",
        thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        description="The official video for Never Gonna Give You Up",
        tags=["rick astley", "never gonna give you up"],
        categories=["Music"],
        like_count=15000000,
        comment_count=2500000,
        age_limit=0,
        formats_available=25,
    )


@pytest.fixture
def sample_playlist():
    """Create a sample Playlist instance."""
    return Playlist(
        playlist_id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        title="Python Tutorial Playlist",
        url="https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        uploader="Python Channel",
        uploader_id="UCpython",
        video_count=50,
        thumbnail="https://i.ytimg.com/vi/playlist/default.jpg",
        description="Complete Python tutorial series",
    )


@pytest.fixture
def sample_playlist_details():
    """Create a sample PlaylistDetails instance."""
    return PlaylistDetails(
        playlist_id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        title="Python Tutorial Playlist",
        url="https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        uploader="Python Channel",
        uploader_id="UCpython",
        video_count=50,
        thumbnail="https://i.ytimg.com/vi/playlist/default.jpg",
        description="Complete Python tutorial series",
        availability="public",
        tags=["python", "tutorial", "programming"],
        view_count=100000,
    )


class TestJsonFormatterFormatVideos:
    """Tests for format_videos method."""

    def test_format_single_video(self, formatter, sample_video):
        """Test formatting a single video."""
        result = formatter.format_videos([sample_video])
        data = json.loads(result)

        assert data["count"] == 1
        assert len(data["videos"]) == 1
        assert data["videos"][0]["video_id"] == "dQw4w9WgXcQ"
        assert data["videos"][0]["title"] == "Rick Astley - Never Gonna Give You Up"

    def test_format_multiple_videos(self, formatter, sample_video):
        """Test formatting multiple videos."""
        video2 = Video(
            video_id="abc123XYZ00",
            title="Second Video",
            url="https://youtube.com/watch?v=abc123XYZ00",
        )
        result = formatter.format_videos([sample_video, video2])
        data = json.loads(result)

        assert data["count"] == 2
        assert len(data["videos"]) == 2

    def test_format_empty_video_list(self, formatter):
        """Test formatting empty video list."""
        result = formatter.format_videos([])
        data = json.loads(result)

        assert data["count"] == 0
        assert data["videos"] == []

    def test_format_video_with_none_values(self, formatter):
        """Test formatting video with None values."""
        video = Video(
            video_id="minimal001",
            title="Minimal Video",
            url="https://youtube.com/watch?v=minimal001",
            duration=None,
            view_count=None,
            uploader=None,
        )
        result = formatter.format_videos([video])
        data = json.loads(result)

        assert data["count"] == 1
        assert data["videos"][0]["duration"] is None
        assert data["videos"][0]["view_count"] is None
        assert data["videos"][0]["uploader"] is None

    def test_format_video_unicode_title(self, formatter):
        """Test formatting video with unicode characters in title."""
        video = Video(
            video_id="korean12345",
            title="한글 제목 테스트",
            url="https://youtube.com/watch?v=korean12345",
        )
        result = formatter.format_videos([video])
        data = json.loads(result)

        assert data["videos"][0]["title"] == "한글 제목 테스트"

    def test_format_video_json_structure(self, formatter, sample_video):
        """Test that JSON output is properly indented."""
        result = formatter.format_videos([sample_video])

        # Check that it's indented (has newlines and spaces)
        assert "\n" in result
        assert "  " in result


class TestJsonFormatterFormatVideoDetails:
    """Tests for format_video_details method."""

    def test_format_video_details_complete(self, formatter, sample_video_details):
        """Test formatting complete video details."""
        result = formatter.format_video_details(sample_video_details)
        data = json.loads(result)

        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["title"] == "Rick Astley - Never Gonna Give You Up"
        assert data["description"] == "The official video for Never Gonna Give You Up"
        assert data["tags"] == ["rick astley", "never gonna give you up"]
        assert data["like_count"] == 15000000
        assert data["formats_available"] == 25

    def test_format_video_details_minimal(self, formatter):
        """Test formatting video details with minimal data."""
        details = VideoDetails(
            video_id="minimal001",
            title="Minimal Video",
            url="https://youtube.com/watch?v=minimal001",
        )
        result = formatter.format_video_details(details)
        data = json.loads(result)

        assert data["video_id"] == "minimal001"
        assert data["tags"] == []
        assert data["categories"] == []


class TestJsonFormatterFormatPlaylists:
    """Tests for format_playlists method."""

    def test_format_single_playlist(self, formatter, sample_playlist):
        """Test formatting a single playlist."""
        result = formatter.format_playlists([sample_playlist])
        data = json.loads(result)

        assert data["count"] == 1
        assert len(data["playlists"]) == 1
        assert data["playlists"][0]["playlist_id"] == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert data["playlists"][0]["title"] == "Python Tutorial Playlist"

    def test_format_multiple_playlists(self, formatter, sample_playlist):
        """Test formatting multiple playlists."""
        playlist2 = Playlist(
            playlist_id="PLtest123456",
            title="Second Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
        )
        result = formatter.format_playlists([sample_playlist, playlist2])
        data = json.loads(result)

        assert data["count"] == 2
        assert len(data["playlists"]) == 2

    def test_format_empty_playlist_list(self, formatter):
        """Test formatting empty playlist list."""
        result = formatter.format_playlists([])
        data = json.loads(result)

        assert data["count"] == 0
        assert data["playlists"] == []


class TestJsonFormatterFormatPlaylistDetails:
    """Tests for format_playlist_details method."""

    def test_format_playlist_details_complete(self, formatter, sample_playlist_details):
        """Test formatting complete playlist details."""
        result = formatter.format_playlist_details(sample_playlist_details)
        data = json.loads(result)

        assert data["playlist_id"] == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert data["title"] == "Python Tutorial Playlist"
        assert data["availability"] == "public"
        assert data["tags"] == ["python", "tutorial", "programming"]
        assert data["view_count"] == 100000

    def test_format_playlist_details_minimal(self, formatter):
        """Test formatting playlist details with minimal data."""
        details = PlaylistDetails(
            playlist_id="PLminimal",
            title="Minimal Playlist",
            url="https://youtube.com/playlist?list=PLminimal",
        )
        result = formatter.format_playlist_details(details)
        data = json.loads(result)

        assert data["playlist_id"] == "PLminimal"
        assert data["tags"] == []
        assert data["availability"] is None

