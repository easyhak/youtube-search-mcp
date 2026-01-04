"""Tests for Playlist and PlaylistDetails models."""

import pytest
from pydantic import ValidationError

from youtube_search_mcp.models.playlist import Playlist, PlaylistDetails


class TestPlaylist:
    """Tests for Playlist model."""

    def test_playlist_with_required_fields_only(self):
        """Test creating Playlist with only required fields."""
        playlist = Playlist(
            playlist_id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
        )

        assert playlist.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert playlist.title == "Test Playlist"
        assert playlist.url == "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        assert playlist.uploader is None
        assert playlist.uploader_id is None
        assert playlist.video_count is None
        assert playlist.thumbnail is None
        assert playlist.description is None

    def test_playlist_with_all_fields(self):
        """Test creating Playlist with all fields."""
        playlist = Playlist(
            playlist_id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            title="Python Tutorial Playlist",
            url="https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            uploader="Python Channel",
            uploader_id="UCpython",
            video_count=50,
            thumbnail="https://i.ytimg.com/vi/playlist/default.jpg",
            description="Complete Python tutorial series",
            modified_date="20240101",
        )

        assert playlist.uploader == "Python Channel"
        assert playlist.uploader_id == "UCpython"
        assert playlist.video_count == 50
        assert playlist.thumbnail == "https://i.ytimg.com/vi/playlist/default.jpg"
        assert playlist.description == "Complete Python tutorial series"
        assert playlist.modified_date == "20240101"

    def test_playlist_missing_required_field(self):
        """Test that missing required field raises ValidationError."""
        with pytest.raises(ValidationError):
            Playlist(
                title="Test Playlist",
                url="https://youtube.com/playlist?list=PLtest",
            )

    def test_playlist_model_dump(self):
        """Test converting Playlist to dictionary."""
        playlist = Playlist(
            playlist_id="PLtest123",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123",
            video_count=10,
        )
        data = playlist.model_dump()

        assert data["playlist_id"] == "PLtest123"
        assert data["video_count"] == 10
        assert data["uploader"] is None

    def test_playlist_model_json(self):
        """Test converting Playlist to JSON."""
        playlist = Playlist(
            playlist_id="PLtest123",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123",
        )
        json_str = playlist.model_dump_json()

        assert "PLtest123" in json_str
        assert "Test Playlist" in json_str

    def test_playlist_unicode_title(self):
        """Test Playlist with unicode characters in title."""
        playlist = Playlist(
            playlist_id="PLkorean123",
            title="파이썬 튜토리얼",
            url="https://youtube.com/playlist?list=PLkorean123",
        )

        assert playlist.title == "파이썬 튜토리얼"

    def test_playlist_zero_video_count(self):
        """Test Playlist with zero videos (empty playlist)."""
        playlist = Playlist(
            playlist_id="PLempty1234",
            title="Empty Playlist",
            url="https://youtube.com/playlist?list=PLempty1234",
            video_count=0,
        )

        assert playlist.video_count == 0

    def test_playlist_large_video_count(self):
        """Test Playlist with large video count."""
        playlist = Playlist(
            playlist_id="PLlarge1234",
            title="Large Playlist",
            url="https://youtube.com/playlist?list=PLlarge1234",
            video_count=5000,
        )

        assert playlist.video_count == 5000


class TestPlaylistDetails:
    """Tests for PlaylistDetails model."""

    def test_playlist_details_with_required_fields_only(self):
        """Test creating PlaylistDetails with only required fields."""
        details = PlaylistDetails(
            playlist_id="PLtest123456",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
        )

        assert details.playlist_id == "PLtest123456"
        assert details.availability is None
        assert details.tags == []
        assert details.view_count is None

    def test_playlist_details_with_all_fields(self):
        """Test creating PlaylistDetails with all fields."""
        details = PlaylistDetails(
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

        assert details.availability == "public"
        assert len(details.tags) == 3
        assert "python" in details.tags
        assert details.view_count == 100000

    def test_playlist_details_inherits_from_playlist(self):
        """Test that PlaylistDetails inherits from Playlist."""
        details = PlaylistDetails(
            playlist_id="PLtest123456",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
        )

        assert isinstance(details, Playlist)

    def test_playlist_details_availability_values(self):
        """Test PlaylistDetails with different availability values."""
        public = PlaylistDetails(
            playlist_id="PLpublic123",
            title="Public Playlist",
            url="https://youtube.com/playlist?list=PLpublic123",
            availability="public",
        )
        assert public.availability == "public"

        unlisted = PlaylistDetails(
            playlist_id="PLunlist123",
            title="Unlisted Playlist",
            url="https://youtube.com/playlist?list=PLunlist123",
            availability="unlisted",
        )
        assert unlisted.availability == "unlisted"

        private = PlaylistDetails(
            playlist_id="PLprivate12",
            title="Private Playlist",
            url="https://youtube.com/playlist?list=PLprivate12",
            availability="private",
        )
        assert private.availability == "private"

    def test_playlist_details_with_empty_tags(self):
        """Test PlaylistDetails with explicit empty tags."""
        details = PlaylistDetails(
            playlist_id="PLnotags123",
            title="Playlist Without Tags",
            url="https://youtube.com/playlist?list=PLnotags123",
            tags=[],
        )

        assert details.tags == []

    def test_playlist_details_model_dump(self):
        """Test converting PlaylistDetails to dictionary."""
        details = PlaylistDetails(
            playlist_id="PLtest123456",
            title="Test Playlist",
            url="https://youtube.com/playlist?list=PLtest123456",
            tags=["tag1", "tag2"],
            view_count=1000,
        )
        data = details.model_dump()

        assert data["tags"] == ["tag1", "tag2"]
        assert data["view_count"] == 1000
        assert data["availability"] is None

    def test_playlist_details_large_view_count(self):
        """Test PlaylistDetails with large view count."""
        details = PlaylistDetails(
            playlist_id="PLpopular12",
            title="Popular Playlist",
            url="https://youtube.com/playlist?list=PLpopular12",
            view_count=50000000,
        )

        assert details.view_count == 50000000

    def test_playlist_details_many_tags(self):
        """Test PlaylistDetails with many tags."""
        tags = [f"tag{i}" for i in range(50)]
        details = PlaylistDetails(
            playlist_id="PLmanytags1",
            title="Many Tags Playlist",
            url="https://youtube.com/playlist?list=PLmanytags1",
            tags=tags,
        )

        assert len(details.tags) == 50

