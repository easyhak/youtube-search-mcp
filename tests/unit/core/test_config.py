"""Tests for config module."""

import os
from unittest.mock import patch

import pytest

from youtube_search_mcp.core import config
from youtube_search_mcp.core.config import Config, get_config, get_package_metadata, reset_config


@pytest.fixture(autouse=True)
def reset_config_fixture():
    """Reset config before and after each test."""
    reset_config()
    get_package_metadata.cache_clear()
    yield
    reset_config()
    get_package_metadata.cache_clear()


class TestConfig:
    """Tests for Config class."""

    def test_config_default_values(self):
        """Test that Config has correct default values."""
        cfg = Config()

        assert cfg.default_max_results == 10
        assert cfg.max_results_limit == 50
        assert cfg.search_timeout == 30
        assert cfg.max_retries == 3
        assert cfg.download_dir == "downloads"
        assert cfg.default_video_quality == "high"
        assert cfg.default_audio_quality == "high"
        assert cfg.default_video_format == "mp4"
        assert cfg.default_audio_format == "mp3"
        assert cfg.min_disk_space_mb == 100
        assert cfg.log_level == "INFO"
        assert cfg.default_format == "json"

    def test_config_env_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {"YT_MCP_DEFAULT_MAX_RESULTS": "25"}):
            cfg = Config()
            assert cfg.default_max_results == 25

    def test_config_env_variable_download_dir(self):
        """Test that download_dir can be set via env variable."""
        with patch.dict(os.environ, {"YT_MCP_DOWNLOAD_DIR": "/custom/downloads"}):
            cfg = Config()
            assert cfg.download_dir == "/custom/downloads"

    def test_config_env_variable_log_level(self):
        """Test that log_level can be set via env variable."""
        with patch.dict(os.environ, {"YT_MCP_LOG_LEVEL": "DEBUG"}):
            cfg = Config()
            assert cfg.log_level == "DEBUG"


class TestExpandDownloadDir:
    """Tests for expand_download_dir validator."""

    def test_expand_home_tilde(self):
        """Test expansion of ~ to home directory."""
        cfg = Config(download_dir="~/downloads")

        assert "~" not in cfg.download_dir
        assert cfg.download_dir.endswith("downloads")

    def test_expand_env_variable_unix_style(self):
        """Test expansion of $HOME style env variable."""
        with patch.dict(os.environ, {"MY_VAR": "/custom/path"}):
            cfg = Config(download_dir="$MY_VAR/downloads")

            assert cfg.download_dir == "/custom/path/downloads"

    def test_expand_empty_string(self):
        """Test that empty string remains empty."""
        cfg = Config(download_dir="")

        assert cfg.download_dir == ""

    def test_expand_relative_path_unchanged(self):
        """Test that relative paths without variables are unchanged."""
        cfg = Config(download_dir="downloads")

        assert cfg.download_dir == "downloads"


class TestConfigGetters:
    """Tests for Config getter methods."""

    def test_get_existing_key(self):
        """Test get method with existing key."""
        cfg = Config()

        result = cfg.get("default_max_results")

        assert result == 10

    def test_get_nonexistent_key_returns_default(self):
        """Test get method with nonexistent key returns default."""
        cfg = Config()

        result = cfg.get("nonexistent_key", "default_value")

        assert result == "default_value"

    def test_get_int_existing_key(self):
        """Test get_int method with existing key."""
        cfg = Config()

        result = cfg.get_int("default_max_results")

        assert result == 10
        assert isinstance(result, int)

    def test_get_int_nonexistent_key(self):
        """Test get_int method with nonexistent key returns default."""
        cfg = Config()

        result = cfg.get_int("nonexistent_key", 99)

        assert result == 99

    def test_get_str_existing_key(self):
        """Test get_str method with existing key."""
        cfg = Config()

        result = cfg.get_str("log_level")

        assert result == "INFO"
        assert isinstance(result, str)

    def test_get_str_nonexistent_key(self):
        """Test get_str method with nonexistent key returns default."""
        cfg = Config()

        result = cfg.get_str("nonexistent_key", "default_str")

        assert result == "default_str"


class TestGetConfig:
    """Tests for get_config function."""

    def test_get_config_returns_config_instance(self):
        """Test that get_config returns a Config instance."""
        cfg = get_config()

        assert isinstance(cfg, Config)

    def test_get_config_returns_same_instance(self):
        """Test that get_config returns same instance (singleton)."""
        cfg1 = get_config()
        cfg2 = get_config()

        assert cfg1 is cfg2

    def test_get_config_creates_new_after_reset(self):
        """Test that get_config creates new instance after reset."""
        cfg1 = get_config()
        reset_config()
        cfg2 = get_config()

        # Should be different instances after reset
        assert cfg1 is not cfg2


class TestResetConfig:
    """Tests for reset_config function."""

    def test_reset_config_clears_instance(self):
        """Test that reset_config clears the singleton instance."""
        get_config()  # Create instance
        reset_config()

        # After reset, _config should be None
        assert config._config is None

    def test_reset_config_allows_new_instance(self):
        """Test that reset allows creating new instance with different values."""
        cfg1 = get_config()
        original_results = cfg1.default_max_results

        reset_config()

        with patch.dict(os.environ, {"YT_MCP_DEFAULT_MAX_RESULTS": "99"}):
            cfg2 = get_config()
            assert cfg2.default_max_results == 99
            assert cfg2.default_max_results != original_results


class TestGetPackageMetadata:
    """Tests for get_package_metadata function."""

    def test_get_package_metadata_returns_dict(self):
        """Test that get_package_metadata returns a dictionary."""
        metadata = get_package_metadata()

        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert "version" in metadata

    def test_get_package_metadata_has_name(self):
        """Test that metadata has a name."""
        metadata = get_package_metadata()

        assert metadata["name"]
        assert isinstance(metadata["name"], str)

    def test_get_package_metadata_has_version(self):
        """Test that metadata has a version."""
        metadata = get_package_metadata()

        assert metadata["version"]
        assert isinstance(metadata["version"], str)

    def test_get_package_metadata_cached(self):
        """Test that get_package_metadata is cached."""
        metadata1 = get_package_metadata()
        metadata2 = get_package_metadata()

        # Should return same object (cached)
        assert metadata1 is metadata2

    def test_get_package_metadata_fallback(self):
        """Test that metadata falls back when package not found."""
        get_package_metadata.cache_clear()

        with patch("importlib.metadata.distribution") as mock_dist:
            from importlib.metadata import PackageNotFoundError

            mock_dist.side_effect = PackageNotFoundError("not found")

            metadata = get_package_metadata()

            assert metadata["name"] == "youtube-search-mcp-dev"
            assert metadata["version"] == "1.0.0"


class TestConfigServerSettings:
    """Tests for server settings from package metadata."""

    def test_server_name_set(self):
        """Test that server_name is set from package metadata."""
        cfg = Config()

        assert cfg.server_name
        assert isinstance(cfg.server_name, str)

    def test_server_version_set(self):
        """Test that server_version is set from package metadata."""
        cfg = Config()

        assert cfg.server_version
        assert isinstance(cfg.server_version, str)

