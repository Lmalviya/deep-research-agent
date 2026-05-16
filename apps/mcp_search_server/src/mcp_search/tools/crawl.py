from mcp.server.fastmcp import FastMCP

from mcp_search.services.crawler import crawl
from mcp_search.models.extract import ExtractResponse


def register_crawl_tool(mcp: FastMCP):
    @mcp.tool(
        name="crawl",
        description=(
            "Crawl a website starting from a URL. "
            "Follows internal links and extracts clean markdown content "
            "from multiple pages."
        ),
    )
    async def crawl_tool(
        start_url: str,
        max_pages: int = 10,
    ) -> list[ExtractResponse]:
        return await crawl(
            start_url=start_url,
            max_pages=max_pages,
        )