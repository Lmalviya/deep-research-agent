from mcp.server.fastmcp import FastMCP

from mcp_search.config import settings
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
    mcp = create_server()

    transport = settings.mcp_transport
    print(f"Starting MCP Search Server [transport={transport}]...")

    if transport == "sse":
        print(f"  Listening on http://{settings.mcp_host}:{settings.mcp_port}")
        mcp.run(
            transport="sse",
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
    else:
        mcp.run(transport="stdio")
