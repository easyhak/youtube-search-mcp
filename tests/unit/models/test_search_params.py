"""Tests for SearchParams model."""

import pytest
from pydantic import ValidationError

from youtube_search_mcp.models.search_params import SearchParams


class TestSearchParams:
    """Tests for SearchParams model."""

    def test_search_params_with_required_fields_only(self):
        """Test creating SearchParams with only required field."""
        params = SearchParams(query="python tutorial")

        assert params.query == "python tutorial"
        assert params.max_results == 10  # default
        assert params.sort_by == "relevance"  # default

    def test_search_params_with_all_fields(self):
        """Test creating SearchParams with all fields."""
        params = SearchParams(
            query="python tutorial",
            max_results=25,
            sort_by="upload_date",
        )

        assert params.query == "python tutorial"
        assert params.max_results == 25
        assert params.sort_by == "upload_date"

    def test_search_params_missing_query(self):
        """Test that missing query raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams()

    def test_search_params_empty_query(self):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams(query="")

    def test_search_params_query_too_long(self):
        """Test that query exceeding 200 chars raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams(query="a" * 201)

    def test_search_params_query_max_length(self):
        """Test query at maximum length (200 chars)."""
        params = SearchParams(query="a" * 200)

        assert len(params.query) == 200

    def test_search_params_max_results_minimum(self):
        """Test max_results at minimum value (1)."""
        params = SearchParams(query="test", max_results=1)

        assert params.max_results == 1

    def test_search_params_max_results_maximum(self):
        """Test max_results at maximum value (50)."""
        params = SearchParams(query="test", max_results=50)

        assert params.max_results == 50

    def test_search_params_max_results_too_low(self):
        """Test that max_results below 1 raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams(query="test", max_results=0)

    def test_search_params_max_results_too_high(self):
        """Test that max_results above 50 raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams(query="test", max_results=51)

    def test_search_params_sort_by_relevance(self):
        """Test sort_by with relevance value."""
        params = SearchParams(query="test", sort_by="relevance")

        assert params.sort_by == "relevance"

    def test_search_params_sort_by_upload_date(self):
        """Test sort_by with upload_date value."""
        params = SearchParams(query="test", sort_by="upload_date")

        assert params.sort_by == "upload_date"

    def test_search_params_sort_by_view_count(self):
        """Test sort_by with view_count value."""
        params = SearchParams(query="test", sort_by="view_count")

        assert params.sort_by == "view_count"

    def test_search_params_sort_by_rating(self):
        """Test sort_by with rating value."""
        params = SearchParams(query="test", sort_by="rating")

        assert params.sort_by == "rating"

    def test_search_params_sort_by_invalid(self):
        """Test that invalid sort_by value raises ValidationError."""
        with pytest.raises(ValidationError):
            SearchParams(query="test", sort_by="invalid_sort")

    def test_search_params_model_dump(self):
        """Test converting SearchParams to dictionary."""
        params = SearchParams(
            query="python tutorial",
            max_results=20,
            sort_by="view_count",
        )
        data = params.model_dump()

        assert data["query"] == "python tutorial"
        assert data["max_results"] == 20
        assert data["sort_by"] == "view_count"

    def test_search_params_unicode_query(self):
        """Test SearchParams with unicode characters in query."""
        params = SearchParams(query="파이썬 튜토리얼")

        assert params.query == "파이썬 튜토리얼"

    def test_search_params_special_chars_query(self):
        """Test SearchParams with special characters in query."""
        params = SearchParams(query="C++ tutorial & guide")

        assert params.query == "C++ tutorial & guide"

    def test_search_params_model_json(self):
        """Test converting SearchParams to JSON."""
        params = SearchParams(query="test query", max_results=15)
        json_str = params.model_dump_json()

        assert "test query" in json_str
        assert "15" in json_str

