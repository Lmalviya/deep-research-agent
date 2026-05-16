from mcp.server.fastmcp import FastMCP

from mcp_search.services.fetcher import fetch_html
from mcp_search.services.extractor import extract_content
from mcp_search.models.extract import ExtractResponse


def register_extract_tool(mcp: FastMCP):
    @mcp.tool(
        name="extract",
        description=(
            "Extract clean markdown content from a webpage URL. "
            "Fetches the page and returns structured readable content."
        ),
    )
    async def extract(url: str) -> ExtractResponse:
        html = await fetch_html(url)
        result = extract_content(url, html)
        return result