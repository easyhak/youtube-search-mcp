"""Tests for Markdown formatter module."""

import pytest

from youtube_search_mcp.formatters.markdown_formatter import MarkdownFormatter
from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails
from youtube_search_mcp.models.video import Video, VideoDetails


@pytest.fixture
def formatter():
    """Create MarkdownFormatter instance."""
    return MarkdownFormatter()


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
        modified_date="20240101",
        availability="public",
        tags=["python", "tutorial", "programming"],
        view_count=100000,
    )


class TestMarkdownFormatterFormatVideos:
    """Tests for format_videos method."""

    def test_format_single_video(self, formatter, sample_video):
        """Test formatting a single video."""
        result = formatter.format_videos([sample_video])

        assert "# Search Results (1 videos)" in result
        assert "## 1. Rick Astley - Never Gonna Give You Up" in result
        assert "**Video ID**: `dQw4w9WgXcQ`" in result
        assert "**URL**: https://youtube.com/watch?v=dQw4w9WgXcQ" in result
        assert "**Uploader**: Rick Astley" in result

    def test_format_multiple_videos(self, formatter, sample_video):
        """Test formatting multiple videos."""
        video2 = Video(
            video_id="abc123XYZ00",
            title="Second Video",
            url="https://youtube.com/watch?v=abc123XYZ00",
        )
        result = formatter.format_videos([sample_video, video2])

        assert "# Search Results (2 videos)" in result
        assert "## 1." in result
        assert "## 2." in result
        assert "Second Video" in result

    def test_format_empty_video_list(self, formatter):
        """Test formatting empty video list."""
        result = formatter.format_videos([])

        assert "# Search Results (0 videos)" in result

    def test_format_video_duration_with_hours(self, formatter):
        """Test formatting video with duration over an hour."""
        video = Video(
            video_id="longevideo1",
            title="Long Video",
            url="https://youtube.com/watch?v=longevideo1",
            duration=3723,  # 1h 2m 3s
        )
        result = formatter.format_videos([video])

        assert "**Duration**: 1h 2m 3s" in result

    def test_format_video_duration_without_hours(self, formatter):
        """Test formatting video with duration under an hour."""
        video = Video(
            video_id="shortvideo",
            title="Short Video",
            url="https://youtube.com/watch?v=shortvideo",
            duration=212,  # 3m 32s
        )
        result = formatter.format_videos([video])

        assert "**Duration**: 3m 32s" in result

    def test_format_video_view_count_formatted(self, formatter, sample_video):
        """Test that view count is formatted with commas."""
        result = formatter.format_videos([sample_video])

        assert "**Views**: 1,400,000,000" in result

    def test_format_video_upload_date_formatted(self, formatter, sample_video):
        """Test that upload date is formatted correctly."""
        result = formatter.format_videos([sample_video])

        assert "**Upload Date**: 2009-10-25" in result

    def test_format_video_without_optional_fields(self, formatter):
        """Test formatting video without optional fields."""
        video = Video(
            video_id="minimal001",
            title="Minimal Video",
            url="https://youtube.com/watch?v=minimal001",
        )
        result = formatter.format_videos([video])

        assert "**Video ID**: `minimal001`" in result
        assert "**Duration**" not in result
        assert "**Uploader**" not in result


class TestMarkdownFormatterFormatVideoDetails:
    """Tests for format_video_details method."""

    def test_format_video_details_complete(self, formatter, sample_video_details):
        """Test formatting complete video details."""
        result = formatter.format_video_details(sample_video_details)

        assert "# Rick Astley - Never Gonna Give You Up" in result
        assert "## Basic Information" in result
        assert "**Video ID**: `dQw4w9WgXcQ`" in result
        assert "**Uploader**: Rick Astley" in result
        assert "**Channel ID**: `UCuAXFkgsw1L7xaCfnd5JJOw`" in result

    def test_format_video_details_statistics(self, formatter, sample_video_details):
        """Test statistics section in video details."""
        result = formatter.format_video_details(sample_video_details)

        assert "## Statistics" in result
        assert "**Views**: 1,400,000,000" in result
        assert "**Likes**: 15,000,000" in result
        assert "**Comments**: 2,500,000" in result

    def test_format_video_details_description(self, formatter, sample_video_details):
        """Test description section in video details."""
        result = formatter.format_video_details(sample_video_details)

        assert "## Description" in result
        assert "The official video for Never Gonna Give You Up" in result

    def test_format_video_details_long_description_truncated(self, formatter):
        """Test that long descriptions are truncated."""
        details = VideoDetails(
            video_id="longdesc001",
            title="Long Description Video",
            url="https://youtube.com/watch?v=longdesc001",
            description="A" * 600,  # 600 characters
        )
        result = formatter.format_video_details(details)

        assert "A" * 500 in result
        assert "..." in result

    def test_format_video_details_tags(self, formatter, sample_video_details):
        """Test tags section in video details."""
        result = formatter.format_video_details(sample_video_details)

        assert "## Tags" in result
        assert "`rick astley`" in result
        assert "`never gonna give you up`" in result

    def test_format_video_details_many_tags_truncated(self, formatter):
        """Test that more than 20 tags shows truncation message."""
        tags = [f"tag{i}" for i in range(25)]
        details = VideoDetails(
            video_id="manytags001",
            title="Many Tags Video",
            url="https://youtube.com/watch?v=manytags001",
            tags=tags,
        )
        result = formatter.format_video_details(details)

        assert "...and 5 more tags" in result

    def test_format_video_details_categories(self, formatter, sample_video_details):
        """Test categories section in video details."""
        result = formatter.format_video_details(sample_video_details)

        assert "## Categories" in result
        assert "Music" in result

    def test_format_video_details_age_restriction_none(self, formatter, sample_video_details):
        """Test age restriction display when no restriction."""
        result = formatter.format_video_details(sample_video_details)

        assert "**Age Restriction**: No age restriction" in result

    def test_format_video_details_age_restriction_18(self, formatter):
        """Test age restriction display when restricted."""
        details = VideoDetails(
            video_id="restricted1",
            title="Restricted Video",
            url="https://youtube.com/watch?v=restricted1",
            age_limit=18,
        )
        result = formatter.format_video_details(details)

        assert "**Age Restriction**: 18+" in result

    def test_format_video_details_formats_available(self, formatter, sample_video_details):
        """Test available formats display."""
        result = formatter.format_video_details(sample_video_details)

        assert "**Available Formats**: 25" in result


class TestMarkdownFormatterFormatPlaylists:
    """Tests for format_playlists method."""

    def test_format_single_playlist(self, formatter, sample_playlist):
        """Test formatting a single playlist."""
        result = formatter.format_playlists([sample_playlist])

        assert "# Playlist Search Results (1 playlists)" in result
        assert "## 1. Python Tutorial Playlist" in result
        assert "**Playlist ID**: `PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`" in result
        assert "**Creator**: Python Channel" in result
        assert "**Videos**: 50" in result

    def test_format_multiple_playlists(self, formatter, sample_playlist):
        """Test formatting multiple playlists."""
        playlist2 = Playlist(
            playlist_id="PLtest123456",
            title="Second Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
        )
        result = formatter.format_playlists([sample_playlist, playlist2])

        assert "# Playlist Search Results (2 playlists)" in result
        assert "## 1." in result
        assert "## 2." in result

    def test_format_empty_playlist_list(self, formatter):
        """Test formatting empty playlist list."""
        result = formatter.format_playlists([])

        assert "# Playlist Search Results (0 playlists)" in result

    def test_format_playlist_description(self, formatter, sample_playlist):
        """Test playlist description display."""
        result = formatter.format_playlists([sample_playlist])

        assert "**Description**: Complete Python tutorial series" in result

    def test_format_playlist_long_description_truncated(self, formatter):
        """Test that long playlist descriptions are truncated."""
        playlist = Playlist(
            playlist_id="PLlongdesc",
            title="Long Description Playlist",
            url="https://youtube.com/playlist?list=PLlongdesc",
            description="B" * 200,  # 200 characters
        )
        result = formatter.format_playlists([playlist])

        assert "B" * 150 in result
        assert "..." in result


class TestMarkdownFormatterFormatPlaylistDetails:
    """Tests for format_playlist_details method."""

    def test_format_playlist_details_complete(self, formatter, sample_playlist_details):
        """Test formatting complete playlist details."""
        result = formatter.format_playlist_details(sample_playlist_details)

        assert "# Python Tutorial Playlist" in result
        assert "## Basic Information" in result
        assert "**Playlist ID**: `PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf`" in result
        assert "**Creator**: Python Channel" in result
        assert "**Channel ID**: `UCpython`" in result
        assert "**Total Videos**: 50" in result
        assert "**Availability**: public" in result

    def test_format_playlist_details_modified_date(self, formatter, sample_playlist_details):
        """Test modified date formatting."""
        result = formatter.format_playlist_details(sample_playlist_details)

        assert "**Last Modified**: 2024-01-01" in result

    def test_format_playlist_details_statistics(self, formatter, sample_playlist_details):
        """Test statistics section in playlist details."""
        result = formatter.format_playlist_details(sample_playlist_details)

        assert "## Statistics" in result
        assert "**Total Views**: 100,000" in result

    def test_format_playlist_details_tags(self, formatter, sample_playlist_details):
        """Test tags section in playlist details."""
        result = formatter.format_playlist_details(sample_playlist_details)

        assert "## Tags" in result
        assert "`python`" in result
        assert "`tutorial`" in result
        assert "`programming`" in result

    def test_format_playlist_details_description(self, formatter, sample_playlist_details):
        """Test description section in playlist details."""
        result = formatter.format_playlist_details(sample_playlist_details)

        assert "## Description" in result
        assert "Complete Python tutorial series" in result

    def test_format_playlist_details_long_description_truncated(self, formatter):
        """Test that long playlist descriptions are truncated."""
        details = PlaylistDetails(
            playlist_id="PLlongdesc",
            title="Long Description Playlist",
            url="https://youtube.com/playlist?list=PLlongdesc",
            description="C" * 600,  # 600 characters
        )
        result = formatter.format_playlist_details(details)

        assert "C" * 500 in result
        assert "..." in result

    def test_format_playlist_details_many_tags_truncated(self, formatter):
        """Test that more than 20 tags shows truncation message."""
        tags = [f"tag{i}" for i in range(25)]
        details = PlaylistDetails(
            playlist_id="PLmanytags",
            title="Many Tags Playlist",
            url="https://youtube.com/playlist?list=PLmanytags",
            tags=tags,
        )
        result = formatter.format_playlist_details(details)

        assert "...and 5 more tags" in result

