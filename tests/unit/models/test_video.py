"""Tests for Video and VideoDetails models."""

import pytest
from pydantic import ValidationError

from youtube_search_mcp.models.video import Video, VideoDetails


class TestVideo:
    """Tests for Video model."""

    def test_video_with_required_fields_only(self):
        """Test creating Video with only required fields."""
        video = Video(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        )

        assert video.video_id == "dQw4w9WgXcQ"
        assert video.title == "Test Video"
        assert video.url == "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert video.duration is None
        assert video.view_count is None
        assert video.uploader is None
        assert video.upload_date is None
        assert video.thumbnail is None

    def test_video_with_all_fields(self):
        """Test creating Video with all fields."""
        video = Video(
            video_id="dQw4w9WgXcQ",
            title="Rick Astley - Never Gonna Give You Up",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
            duration=212,
            view_count=1400000000,
            uploader="Rick Astley",
            upload_date="20091025",
            thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            timestamp=1256428800,
            release_timestamp=1256428800,
        )

        assert video.duration == 212
        assert video.view_count == 1400000000
        assert video.uploader == "Rick Astley"
        assert video.upload_date == "20091025"
        assert video.thumbnail == "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
        assert video.timestamp == 1256428800
        assert video.release_timestamp == 1256428800

    def test_video_missing_required_field(self):
        """Test that missing required field raises ValidationError."""
        with pytest.raises(ValidationError):
            Video(
                title="Test Video",
                url="https://youtube.com/watch?v=test",
            )

    def test_video_model_dump(self):
        """Test converting Video to dictionary."""
        video = Video(
            video_id="test123456",
            title="Test Video",
            url="https://youtube.com/watch?v=test123456",
            duration=100,
        )
        data = video.model_dump()

        assert data["video_id"] == "test123456"
        assert data["title"] == "Test Video"
        assert data["duration"] == 100
        assert data["view_count"] is None

    def test_video_model_json(self):
        """Test converting Video to JSON."""
        video = Video(
            video_id="test123456",
            title="Test Video",
            url="https://youtube.com/watch?v=test123456",
        )
        json_str = video.model_dump_json()

        assert "test123456" in json_str
        assert "Test Video" in json_str

    def test_video_unicode_title(self):
        """Test Video with unicode characters in title."""
        video = Video(
            video_id="korean12345",
            title="한글 제목 테스트",
            url="https://youtube.com/watch?v=korean12345",
        )

        assert video.title == "한글 제목 테스트"

    def test_video_zero_duration(self):
        """Test Video with zero duration (livestreams)."""
        video = Video(
            video_id="livestream1",
            title="Live Stream",
            url="https://youtube.com/watch?v=livestream1",
            duration=0,
        )

        assert video.duration == 0

    def test_video_large_view_count(self):
        """Test Video with very large view count."""
        video = Video(
            video_id="viral123456",
            title="Viral Video",
            url="https://youtube.com/watch?v=viral123456",
            view_count=10000000000,
        )

        assert video.view_count == 10000000000


class TestVideoDetails:
    """Tests for VideoDetails model."""

    def test_video_details_with_required_fields_only(self):
        """Test creating VideoDetails with only required fields."""
        details = VideoDetails(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            url="https://youtube.com/watch?v=dQw4w9WgXcQ",
        )

        assert details.video_id == "dQw4w9WgXcQ"
        assert details.tags == []
        assert details.categories == []
        assert details.formats_available == 0

    def test_video_details_with_all_fields(self):
        """Test creating VideoDetails with all fields."""
        details = VideoDetails(
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
            tags=["rick astley", "never gonna give you up", "80s music"],
            categories=["Music"],
            like_count=15000000,
            comment_count=2500000,
            age_limit=0,
            formats_available=25,
        )

        assert details.uploader_id == "UCuAXFkgsw1L7xaCfnd5JJOw"
        assert details.description == "The official video for Never Gonna Give You Up"
        assert len(details.tags) == 3
        assert "rick astley" in details.tags
        assert details.categories == ["Music"]
        assert details.like_count == 15000000
        assert details.comment_count == 2500000
        assert details.age_limit == 0
        assert details.formats_available == 25

    def test_video_details_inherits_from_video(self):
        """Test that VideoDetails inherits from Video."""
        details = VideoDetails(
            video_id="test123456",
            title="Test Video",
            url="https://youtube.com/watch?v=test123456",
        )

        assert isinstance(details, Video)

    def test_video_details_with_empty_tags(self):
        """Test VideoDetails with explicit empty tags."""
        details = VideoDetails(
            video_id="notags12345",
            title="Video Without Tags",
            url="https://youtube.com/watch?v=notags12345",
            tags=[],
        )

        assert details.tags == []

    def test_video_details_with_age_restriction(self):
        """Test VideoDetails with age restriction."""
        details = VideoDetails(
            video_id="restricted1",
            title="Age Restricted Video",
            url="https://youtube.com/watch?v=restricted1",
            age_limit=18,
        )

        assert details.age_limit == 18

    def test_video_details_model_dump(self):
        """Test converting VideoDetails to dictionary."""
        details = VideoDetails(
            video_id="test123456",
            title="Test Video",
            url="https://youtube.com/watch?v=test123456",
            tags=["tag1", "tag2"],
            like_count=1000,
        )
        data = details.model_dump()

        assert data["tags"] == ["tag1", "tag2"]
        assert data["like_count"] == 1000
        assert data["categories"] == []

    def test_video_details_long_description(self):
        """Test VideoDetails with long description."""
        long_desc = "A" * 5000
        details = VideoDetails(
            video_id="longdesc123",
            title="Long Description Video",
            url="https://youtube.com/watch?v=longdesc123",
            description=long_desc,
        )

        assert details.description == long_desc
        assert len(details.description) == 5000

    def test_video_details_multiple_categories(self):
        """Test VideoDetails with multiple categories."""
        details = VideoDetails(
            video_id="multicats12",
            title="Multi Category Video",
            url="https://youtube.com/watch?v=multicats12",
            categories=["Music", "Entertainment", "Comedy"],
        )

        assert len(details.categories) == 3

