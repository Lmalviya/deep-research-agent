import asyncio

from mcp_search.services.fetcher import fetch_html
from mcp_search.services.extractor import extract_content
from mcp_search.models.extract import ExtractResponse


async def _process_url(url: str) -> ExtractResponse | None:
    try:
        html = await fetch_html(url)
        return extract_content(url, html)
    except Exception:
        return None


async def batch_extract(urls: list[str]) -> list[ExtractResponse]:
    """
    Parallel URL fetch + extract pipeline.
    """

    tasks = [
        _process_url(url)
        for url in urls
    ]

    results = await asyncio.gather(*tasks)

    # filter failed results
    return [r for r in results if r is not None]