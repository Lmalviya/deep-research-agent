from mcp.server.fastmcp import FastMCP

from mcp_search.models.search import SearchResponse
from mcp_search.services.searxng import search_searxng


def register_search_tool(mcp: FastMCP):
    @mcp.tool(
        name="search",
        description=(
            "Search the web and return relevant search results "
            "with titles, URLs, and snippets."
        ),
    )
    async def search(query: str, limit: int = 10) -> SearchResponse:
        return await search_searxng(
            query=query,
            limit=limit,
        )