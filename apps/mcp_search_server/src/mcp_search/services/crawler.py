from __future__ import annotations

from collections import deque

from urllib.parse import urljoin
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from mcp_search.config import settings
from mcp_search.services.fetcher import fetch_html
from mcp_search.services.extractor import extract_content
from mcp_search.models.extract import ExtractResponse
from mcp_search.services.batch_extractor import batch_extract

from mcp_search.services.batch_crawler import batch_crawl



async def crawl(
    start_url: str,
    max_pages: int | None = None,
    batch_size: int | None = None,
) -> list[ExtractResponse]:
    """
    Simple BFS crawler:
    - starts from a URL
    - extracts links
    - fetches + extracts content
    """

    max_pages = max_pages or settings.max_crawl_pages
    batch_size = batch_size or settings.crawl_batch_size

    return await batch_crawl(
        start_url=start_url,
        max_pages=max_pages,
        batch_size=batch_size,
    )