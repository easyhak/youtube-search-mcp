"""Tests for YtDlpDataParser."""


import pytest

from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails
from youtube_search_mcp.models.video import Video, VideoDetails
from youtube_search_mcp.search.parsers import YtDlpDataParser


@pytest.fixture
def parser():
    """Create YtDlpDataParser instance."""
    return YtDlpDataParser()


class TestParseVideo:
    """Tests for parse_video method."""

    def test_parse_video_complete_data(self, parser):
        """Test parsing video with complete data."""
        data = {
            "id": "dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up",
            "duration": 212,
            "view_count": 1400000000,
            "uploader": "Rick Astley",
            "channel": "Rick Astley Official",
            "upload_date": "20091025",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "timestamp": 1256428800,
            "release_timestamp": 1256428800,
        }
        video = parser.parse_video(data)

        assert isinstance(video, Video)
        assert video.video_id == "dQw4w9WgXcQ"
        assert video.title == "Rick Astley - Never Gonna Give You Up"
        assert video.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert video.duration == 212
        assert video.view_count == 1400000000
        assert video.uploader == "Rick Astley"
        assert video.thumbnail == "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
        assert video.timestamp == 1256428800

    def test_parse_video_minimal_data(self, parser):
        """Test parsing video with minimal data."""
        data = {
            "id": "minimal001",
            "title": "Minimal Video",
        }
        video = parser.parse_video(data)

        assert video.video_id == "minimal001"
        assert video.title == "Minimal Video"
        assert video.duration is None
        assert video.view_count is None
        assert video.uploader is None

    def test_parse_video_missing_id(self, parser):
        """Test parsing video with missing id uses empty string."""
        data = {
            "title": "No ID Video",
        }
        video = parser.parse_video(data)

        assert video.video_id == ""
        assert video.url == "https://youtube.com/watch?v="

    def test_parse_video_missing_title(self, parser):
        """Test parsing video with missing title uses 'Unknown'."""
        data = {
            "id": "notitle1234",
        }
        video = parser.parse_video(data)

        assert video.title == "Unknown"

    def test_parse_video_uploader_fallback_to_channel(self, parser):
        """Test that channel is used when uploader is not available."""
        data = {
            "id": "channel1234",
            "title": "Channel Only Video",
            "channel": "Test Channel",
        }
        video = parser.parse_video(data)

        assert video.uploader == "Test Channel"

    def test_parse_video_with_thumbnails_list(self, parser):
        """Test parsing video with thumbnails list."""
        data = {
            "id": "thumbs12345",
            "title": "Video with Thumbnails",
            "thumbnails": [
                {"url": "https://i.ytimg.com/vi/thumbs12345/default.jpg"},
                {"url": "https://i.ytimg.com/vi/thumbs12345/maxresdefault.jpg"},
            ],
        }
        video = parser.parse_video(data)

        assert video.thumbnail == "https://i.ytimg.com/vi/thumbs12345/maxresdefault.jpg"

    def test_parse_video_timestamp_to_upload_date(self, parser):
        """Test that timestamp is converted to upload_date."""
        data = {
            "id": "timestamp12",
            "title": "Timestamp Video",
            "timestamp": 1700000000,  # Nov 14-15, 2023 depending on timezone
        }
        video = parser.parse_video(data)

        # Date varies by timezone, so just check format
        assert video.upload_date is not None
        assert len(video.upload_date) == 8
        assert video.upload_date.startswith("202311")


class TestParseVideoDetails:
    """Tests for parse_video_details method."""

    def test_parse_video_details_complete(self, parser):
        """Test parsing video details with complete data."""
        data = {
            "id": "dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up",
            "duration": 212,
            "view_count": 1400000000,
            "uploader": "Rick Astley",
            "uploader_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
            "channel": "Rick Astley Official",
            "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "description": "The official video for Never Gonna Give You Up",
            "tags": ["rick astley", "never gonna give you up"],
            "categories": ["Music"],
            "like_count": 15000000,
            "comment_count": 2500000,
            "age_limit": 0,
            "formats": [{"format_id": "22"}, {"format_id": "18"}],
            "timestamp": 1256428800,
        }
        details = parser.parse_video_details(data)

        assert isinstance(details, VideoDetails)
        assert details.video_id == "dQw4w9WgXcQ"
        assert details.uploader_id == "UCuAXFkgsw1L7xaCfnd5JJOw"
        assert details.description == "The official video for Never Gonna Give You Up"
        assert details.tags == ["rick astley", "never gonna give you up"]
        assert details.categories == ["Music"]
        assert details.like_count == 15000000
        assert details.comment_count == 2500000
        assert details.age_limit == 0
        assert details.formats_available == 2

    def test_parse_video_details_minimal(self, parser):
        """Test parsing video details with minimal data."""
        data = {
            "id": "minimal001",
            "title": "Minimal Video",
        }
        details = parser.parse_video_details(data)

        assert details.video_id == "minimal001"
        assert details.tags == []
        assert details.categories == []
        assert details.formats_available == 0

    def test_parse_video_details_fallback_channel_id(self, parser):
        """Test that channel_id is used when uploader_id is not available."""
        data = {
            "id": "channelid12",
            "title": "Channel ID Video",
            "channel_id": "UCtest12345",
        }
        details = parser.parse_video_details(data)

        assert details.uploader_id == "UCtest12345"


class TestParsePlaylist:
    """Tests for parse_playlist method."""

    def test_parse_playlist_complete(self, parser):
        """Test parsing playlist with complete data."""
        data = {
            "id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            "title": "Python Tutorial Playlist",
            "uploader": "Python Channel",
            "channel": "Python Channel",
            "uploader_id": "UCpython",
            "channel_id": "UCpython",
            "playlist_count": 50,
            "n_entries": 50,
            "thumbnail": "https://i.ytimg.com/vi/playlist/default.jpg",
            "description": "Complete Python tutorial series",
            "modified_date": "20240101",
        }
        playlist = parser.parse_playlist(data)

        assert isinstance(playlist, Playlist)
        assert playlist.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert playlist.title == "Python Tutorial Playlist"
        assert playlist.url == "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert playlist.uploader == "Python Channel"
        assert playlist.uploader_id == "UCpython"
        assert playlist.video_count == 50
        assert playlist.thumbnail == "https://i.ytimg.com/vi/playlist/default.jpg"
        assert playlist.description == "Complete Python tutorial series"
        assert playlist.modified_date == "20240101"

    def test_parse_playlist_minimal(self, parser):
        """Test parsing playlist with minimal data."""
        data = {
            "id": "PLminimal",
            "title": "Minimal Playlist",
        }
        playlist = parser.parse_playlist(data)

        assert playlist.playlist_id == "PLminimal"
        assert playlist.title == "Minimal Playlist"
        assert playlist.uploader is None
        assert playlist.video_count is None

    def test_parse_playlist_video_count_fallback(self, parser):
        """Test that n_entries is used when playlist_count is not available."""
        data = {
            "id": "PLtest123",
            "title": "Test Playlist",
            "n_entries": 25,
        }
        playlist = parser.parse_playlist(data)

        assert playlist.video_count == 25

    def test_parse_playlist_uploader_fallback(self, parser):
        """Test that channel is used when uploader is not available."""
        data = {
            "id": "PLchannel",
            "title": "Channel Playlist",
            "channel": "Test Channel",
        }
        playlist = parser.parse_playlist(data)

        assert playlist.uploader == "Test Channel"

    def test_parse_playlist_with_thumbnails_list(self, parser):
        """Test parsing playlist with thumbnails list."""
        data = {
            "id": "PLthumbs",
            "title": "Playlist with Thumbnails",
            "thumbnails": [
                {"url": "https://i.ytimg.com/vi/playlist/small.jpg"},
                {"url": "https://i.ytimg.com/vi/playlist/large.jpg"},
            ],
        }
        playlist = parser.parse_playlist(data)

        assert playlist.thumbnail == "https://i.ytimg.com/vi/playlist/large.jpg"


class TestParsePlaylistDetails:
    """Tests for parse_playlist_details method."""

    def test_parse_playlist_details_complete(self, parser):
        """Test parsing playlist details with complete data."""
        data = {
            "id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            "title": "Python Tutorial Playlist",
            "uploader": "Python Channel",
            "uploader_id": "UCpython",
            "playlist_count": 50,
            "thumbnail": "https://i.ytimg.com/vi/playlist/default.jpg",
            "description": "Complete Python tutorial series",
            "modified_date": "20240101",
            "availability": "public",
            "tags": ["python", "tutorial"],
            "view_count": 100000,
            "entries": [{"id": "video1"}, {"id": "video2"}],
        }
        details = parser.parse_playlist_details(data)

        assert isinstance(details, PlaylistDetails)
        assert details.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert details.availability == "public"
        assert details.tags == ["python", "tutorial"]
        assert details.view_count == 100000

    def test_parse_playlist_details_minimal(self, parser):
        """Test parsing playlist details with minimal data."""
        data = {
            "id": "PLminimal",
            "title": "Minimal Playlist",
        }
        details = parser.parse_playlist_details(data)

        assert details.playlist_id == "PLminimal"
        assert details.availability is None
        assert details.tags == []
        assert details.view_count is None

    def test_parse_playlist_details_video_count_from_entries(self, parser):
        """Test that video_count is calculated from entries when playlist_count not available."""
        data = {
            "id": "PLentries",
            "title": "Entries Playlist",
            "entries": [{"id": "v1"}, {"id": "v2"}, {"id": "v3"}],
        }
        details = parser.parse_playlist_details(data)

        assert details.video_count == 3


class TestExtractThumbnailUrl:
    """Tests for _extract_thumbnail_url helper method."""

    def test_extract_thumbnail_direct_string(self, parser):
        """Test extracting thumbnail from direct string."""
        data = {"thumbnail": "https://i.ytimg.com/vi/test/maxresdefault.jpg"}
        result = parser._extract_thumbnail_url(data)

        assert result == "https://i.ytimg.com/vi/test/maxresdefault.jpg"

    def test_extract_thumbnail_from_thumbnails_list(self, parser):
        """Test extracting thumbnail from thumbnails list (takes last one)."""
        data = {
            "thumbnails": [
                {"url": "https://i.ytimg.com/vi/test/default.jpg"},
                {"url": "https://i.ytimg.com/vi/test/mqdefault.jpg"},
                {"url": "https://i.ytimg.com/vi/test/maxresdefault.jpg"},
            ]
        }
        result = parser._extract_thumbnail_url(data)

        assert result == "https://i.ytimg.com/vi/test/maxresdefault.jpg"

    def test_extract_thumbnail_empty_thumbnails(self, parser):
        """Test extracting thumbnail from empty thumbnails list."""
        data = {"thumbnails": []}
        result = parser._extract_thumbnail_url(data)

        assert result is None

    def test_extract_thumbnail_no_thumbnail(self, parser):
        """Test extracting thumbnail when no thumbnail data."""
        data = {}
        result = parser._extract_thumbnail_url(data)

        assert result is None

    def test_extract_thumbnail_non_string_thumbnail(self, parser):
        """Test extracting thumbnail when thumbnail is not a string."""
        data = {"thumbnail": 12345}
        result = parser._extract_thumbnail_url(data)

        assert result is None

    def test_extract_thumbnail_invalid_thumbnails_entry(self, parser):
        """Test extracting thumbnail with invalid thumbnails entry."""
        data = {"thumbnails": ["not_a_dict"]}
        result = parser._extract_thumbnail_url(data)

        assert result is None


class TestConvertTimestampToDate:
    """Tests for _convert_timestamp_to_date helper method."""

    def test_convert_valid_timestamp(self, parser):
        """Test converting valid Unix timestamp."""
        result = parser._convert_timestamp_to_date(1700000000)  # Nov 14-15, 2023 depending on timezone

        # Date varies by timezone, so just check format
        assert result is not None
        assert len(result) == 8
        assert result.startswith("202311")

    def test_convert_none_timestamp(self, parser):
        """Test converting None timestamp."""
        result = parser._convert_timestamp_to_date(None)

        assert result is None

    def test_convert_zero_timestamp(self, parser):
        """Test converting zero timestamp."""
        result = parser._convert_timestamp_to_date(0)

        assert result is None

    def test_convert_negative_timestamp(self, parser):
        """Test converting negative timestamp (before epoch)."""
        # Negative timestamps can be valid (dates before 1970)
        # Depending on implementation, this might work or fail
        result = parser._convert_timestamp_to_date(-1)
        # The implementation should handle this gracefully
        assert result is None or isinstance(result, str)

    def test_convert_very_large_timestamp(self, parser):
        """Test converting very large timestamp that might cause overflow."""
        # This might cause an OverflowError on some systems
        result = parser._convert_timestamp_to_date(99999999999999)

        assert result is None

    def test_convert_specific_date(self, parser):
        """Test converting timestamp to specific known date."""
        # Jan 1, 2020 00:00:00 UTC = 1577836800
        result = parser._convert_timestamp_to_date(1577836800)

        # Note: actual date depends on timezone
        assert result is not None
        assert result.startswith("2020")

