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


def _is_valid_url(url: str, base_domain: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        links.append(full_url)

    return links


async def crawl(
    start_url: str,
    max_pages: int | None = None,
) -> list[ExtractResponse]:
    """
    Simple BFS crawler:
    - starts from a URL
    - extracts links
    - fetches + extracts content
    """

    max_pages = max_pages or settings.max_crawl_pages

    visited: set[str] = set()
    queue: deque[str] = deque([start_url])

    results: list[ExtractResponse] = []

    while queue and len(results) < max_pages:
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        try:
            html = await fetch_html(url)
            extracted = extract_content(url, html)
            results.append(extracted)

            # Extract new links for crawling
            links = _extract_links(html, url)

            for link in links:
                if link not in visited:
                    queue.append(link)

        except Exception:
            continue

    return results