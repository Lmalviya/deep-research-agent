from mcp.server.fastmcp import FastMCP

from mcp_search.tools.search import register_search_tool
from mcp_search.tools.extract import register_extract_tool
from mcp_search.tools.crawl import register_crawl_tool


def create_server() -> FastMCP:
    mcp = FastMCP(
        name="mcp-search-server",
    )

    # Register tools
    register_search_tool(mcp)
    register_extract_tool(mcp)
    register_crawl_tool(mcp)

    return mcp


def main():
    print("Starting MCP Search Server...")

    mcp = create_server()

    mcp.run()