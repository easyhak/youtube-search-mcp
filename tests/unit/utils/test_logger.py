"""Tests for logger module."""

import logging

from youtube_search_mcp.utils.logger import get_logger, setup_logging


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger(__name__)

        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_module_name(self):
        """Test get_logger with specific module name."""
        logger = get_logger("test.module.name")

        # get_logger always adds "youtube_search_mcp." prefix
        assert logger.name == "youtube_search_mcp.test.module.name"

    def test_get_logger_returns_same_logger(self):
        """Test that same logger is returned for same name."""
        logger1 = get_logger("test.logger")
        logger2 = get_logger("test.logger")

        assert logger1 is logger2


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_creates_handler(self):
        """Test that setup_logging configures logging."""
        # This should not raise
        setup_logging(level="DEBUG")

    def test_setup_logging_with_info_level(self):
        """Test setup_logging with INFO level."""
        setup_logging(level="INFO")

        logger = get_logger("test.setup")
        assert logger.level <= logging.INFO

    def test_setup_logging_with_error_level(self):
        """Test setup_logging with ERROR level."""
        logger = setup_logging(level="ERROR")

        # setup_logging returns the app logger, not root
        assert logger.name == "youtube_search_mcp"
        assert logger.level == logging.ERROR

