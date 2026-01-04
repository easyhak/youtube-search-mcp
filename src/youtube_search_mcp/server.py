"""FastMCP server implementation for YouTube search and download."""

import asyncio

from fastmcp import FastMCP

try:
    from youtube_search_mcp.core.config import get_config
    from youtube_search_mcp.tools.dependencies import initialize_dependencies
    from youtube_search_mcp.tools.download_tools import register_download_tools
    from youtube_search_mcp.tools.playlist_tools import register_playlist_tools
    from youtube_search_mcp.tools.resources import register_resources
    from youtube_search_mcp.tools.search_tools import register_search_tools
    from youtube_search_mcp.tools.utility_tools import register_utility_tools
    from youtube_search_mcp.utils.logger import get_logger, setup_logging
except ImportError:
    from .core.config import get_config
    from .tools.dependencies import initialize_dependencies
    from .tools.download_tools import register_download_tools
    from .tools.playlist_tools import register_playlist_tools
    from .tools.resources import register_resources
    from .tools.search_tools import register_search_tools
    from .tools.utility_tools import register_utility_tools
    from .utils.logger import setup_logging

# Initialize configuration
config = get_config()

# Setup logging
logger = setup_logging(config.log_level)

# Initialize MCP server
mcp = FastMCP(name=config.server_name)

# Initialize dependencies synchronously at module load
logger.info(f"Initializing {config.server_name} v{config.server_version}")
asyncio.run(initialize_dependencies())
logger.info("Dependencies initialized successfully")

# Register all tools and resources
register_search_tools(mcp)
register_playlist_tools(mcp)
register_download_tools(mcp)
register_utility_tools(mcp)
register_resources(mcp)


def run() -> None:
    """Run the MCP server."""
    logger.info(f"Starting MCP server {config.server_name}")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
