"""Tests for validators module."""

import pytest

from youtube_search_mcp.core.exceptions import InvalidQueryError
from youtube_search_mcp.utils.validators import (
    sanitize_filename,
    validate_query,
    validate_video_id,
)


class TestValidateVideoId:
    """Tests for validate_video_id function."""

    def test_valid_video_id_standard(self):
        """Test standard 11-character video ID."""
        assert validate_video_id("dQw4w9WgXcQ") is True

    def test_valid_video_id_with_underscores(self):
        """Test video ID containing underscores."""
        assert validate_video_id("abc_def_123") is True

    def test_valid_video_id_with_hyphens(self):
        """Test video ID containing hyphens."""
        assert validate_video_id("abc-def-123") is True

    def test_valid_video_id_mixed_case(self):
        """Test video ID with mixed case letters."""
        assert validate_video_id("AbCdEfGhIjK") is True

    def test_valid_video_id_all_numbers(self):
        """Test video ID with all numbers."""
        assert validate_video_id("12345678901") is True

    def test_invalid_video_id_too_short(self):
        """Test video ID that is too short."""
        assert validate_video_id("abc123") is False

    def test_invalid_video_id_too_long(self):
        """Test video ID that is too long."""
        assert validate_video_id("abc123456789012") is False

    def test_invalid_video_id_empty(self):
        """Test empty video ID."""
        assert validate_video_id("") is False

    def test_invalid_video_id_none(self):
        """Test None video ID."""
        assert validate_video_id(None) is False

    def test_invalid_video_id_special_chars(self):
        """Test video ID with invalid special characters."""
        assert validate_video_id("abc@def#123") is False

    def test_invalid_video_id_spaces(self):
        """Test video ID with spaces."""
        assert validate_video_id("abc def 123") is False

    def test_invalid_video_id_unicode(self):
        """Test video ID with unicode characters."""
        assert validate_video_id("한글영상ID123") is False


class TestValidateQuery:
    """Tests for validate_query function."""

    def test_valid_query_simple(self):
        """Test simple search query."""
        result = validate_query("python tutorial")
        assert result == "python tutorial"

    def test_valid_query_with_whitespace(self):
        """Test query with leading/trailing whitespace."""
        result = validate_query("  python tutorial  ")
        assert result == "python tutorial"

    def test_valid_query_single_char(self):
        """Test single character query."""
        result = validate_query("a")
        assert result == "a"

    def test_valid_query_max_length(self):
        """Test query at maximum length (200 chars)."""
        query = "a" * 200
        result = validate_query(query)
        assert result == query

    def test_valid_query_unicode(self):
        """Test query with unicode characters."""
        result = validate_query("파이썬 튜토리얼")
        assert result == "파이썬 튜토리얼"

    def test_valid_query_special_chars(self):
        """Test query with special characters."""
        result = validate_query("C++ tutorial & guide")
        assert result == "C++ tutorial & guide"

    def test_invalid_query_empty(self):
        """Test empty query raises error."""
        with pytest.raises(InvalidQueryError) as exc_info:
            validate_query("")
        assert "empty" in exc_info.value.message.lower()

    def test_invalid_query_none(self):
        """Test None query raises error."""
        with pytest.raises(InvalidQueryError) as exc_info:
            validate_query(None)
        assert "empty" in exc_info.value.message.lower()

    def test_invalid_query_whitespace_only(self):
        """Test whitespace-only query raises error."""
        with pytest.raises(InvalidQueryError) as exc_info:
            validate_query("   ")
        assert "empty" in exc_info.value.message.lower()

    def test_invalid_query_too_long(self):
        """Test query exceeding maximum length raises error."""
        query = "a" * 201
        with pytest.raises(InvalidQueryError) as exc_info:
            validate_query(query)
        assert "too long" in exc_info.value.message.lower()


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_valid_filename_unchanged(self):
        """Test valid filename remains unchanged."""
        result = sanitize_filename("my_video_file.mp4")
        assert result == "my_video_file.mp4"

    def test_remove_less_than(self):
        """Test removal of < character."""
        result = sanitize_filename("file<name.mp4")
        assert result == "file_name.mp4"

    def test_remove_greater_than(self):
        """Test removal of > character."""
        result = sanitize_filename("file>name.mp4")
        assert result == "file_name.mp4"

    def test_remove_colon(self):
        """Test removal of : character."""
        result = sanitize_filename("file:name.mp4")
        assert result == "file_name.mp4"

    def test_remove_double_quote(self):
        """Test removal of double quote character."""
        result = sanitize_filename('file"name.mp4')
        assert result == "file_name.mp4"

    def test_remove_forward_slash(self):
        """Test removal of / character."""
        result = sanitize_filename("file/name.mp4")
        assert result == "file_name.mp4"

    def test_remove_backslash(self):
        """Test removal of \\ character."""
        result = sanitize_filename("file\\name.mp4")
        assert result == "file_name.mp4"

    def test_remove_pipe(self):
        """Test removal of | character."""
        result = sanitize_filename("file|name.mp4")
        assert result == "file_name.mp4"

    def test_remove_question_mark(self):
        """Test removal of ? character."""
        result = sanitize_filename("file?name.mp4")
        assert result == "file_name.mp4"

    def test_remove_asterisk(self):
        """Test removal of * character."""
        result = sanitize_filename("file*name.mp4")
        assert result == "file_name.mp4"

    def test_remove_multiple_invalid_chars(self):
        """Test removal of multiple invalid characters."""
        result = sanitize_filename("file<>:name?.mp4")
        assert result == "file___name_.mp4"

    def test_strip_leading_periods(self):
        """Test stripping of leading periods."""
        result = sanitize_filename("...filename.mp4")
        assert result == "filename.mp4"

    def test_strip_trailing_periods(self):
        """Test stripping of trailing periods."""
        result = sanitize_filename("filename...")
        assert result == "filename"

    def test_strip_leading_spaces(self):
        """Test stripping of leading spaces."""
        result = sanitize_filename("   filename.mp4")
        assert result == "filename.mp4"

    def test_strip_trailing_spaces(self):
        """Test stripping of trailing spaces."""
        result = sanitize_filename("filename.mp4   ")
        assert result == "filename.mp4"

    def test_empty_after_sanitization(self):
        """Test filename that becomes empty returns 'unnamed'."""
        result = sanitize_filename("...")
        assert result == "unnamed"

    def test_only_invalid_chars(self):
        """Test filename with only invalid characters returns underscores."""
        result = sanitize_filename("<>:\"/\\|?*")
        assert result == "_________"

    def test_unicode_filename(self):
        """Test filename with unicode characters is preserved."""
        result = sanitize_filename("한글파일명.mp4")
        assert result == "한글파일명.mp4"

    def test_real_world_youtube_title(self):
        """Test sanitization of real-world YouTube video title."""
        title = 'Rick Astley - Never Gonna Give You Up (Official Video)'
        result = sanitize_filename(title)
        assert result == 'Rick Astley - Never Gonna Give You Up (Official Video)'

    def test_youtube_title_with_invalid_chars(self):
        """Test YouTube title containing invalid characters."""
        title = 'What is C++? | Programming Tutorial: Part 1/10'
        result = sanitize_filename(title)
        assert result == 'What is C++_ _ Programming Tutorial_ Part 1_10'

