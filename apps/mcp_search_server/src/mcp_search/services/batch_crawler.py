import asyncio
from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from mcp_search.services.fetcher import fetch_html
from mcp_search.services.extractor import extract_content
from mcp_search.services.cache import cache_extract_result
from mcp_search.models.extract import ExtractResponse


# def _is_valid_url(url: str, base_domain: str) -> bool:
#     try:
#         parsed = urlparse(url)
#         return bool(parsed.scheme in ("http", "https") and parsed.netloc)
#     except Exception:
#         return False


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        links.append(full_url)

    return links


def _get_root_domain(url: str) -> str:
    """
    Extract the registerable root domain from a URL.
    e.g. 'https://docs.python.org/3/' -> 'python.org'
    """
    netloc = urlparse(url).netloc.split(":")[0]  # strip port
    parts = netloc.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else netloc


def _is_same_root_domain(url: str, root_domain: str) -> bool:
    """
    Return True if url belongs to root_domain or any of its subdomains.
    e.g. root_domain='python.org' matches 'docs.python.org' and 'python.org'.
    Only http/https links are allowed.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        netloc = parsed.netloc.split(":")[0]
        return netloc == root_domain or netloc.endswith(f".{root_domain}")
    except Exception:
        return False


async def _fetch_extract_links(
    url: str,
) -> tuple[ExtractResponse | None, list[str]]:
    """
    Fetch a page once, then:
      - extract its readable content
      - discover outgoing links
    Returns both so the caller never needs a second fetch.
    """
    try:
        html = await fetch_html(url)
        result = extract_content(url, html)
        # Fire-and-forget cache write
        asyncio.create_task(cache_extract_result(str(result.url), result.model_dump_json()))
        links = _extract_links(html, url)
        return result, links
    except Exception:
        return None, []


async def batch_crawl(
    start_url: str,
    max_pages: int = 20,
    batch_size: int = 5,
) -> list[ExtractResponse]:

    root_domain = _get_root_domain(start_url)

    visited: set[str] = set()
    queue: deque[str] = deque([start_url])
    results: list[ExtractResponse] = []

    while queue and len(visited) < max_pages:

        # 1. BUILD ONE WAVE (BATCH)
        batch: list[str] = []
        while queue and len(batch) < batch_size:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)
            batch.append(url)

        if not batch:
            break

        # 2. FETCH + EXTRACT + LINK-DISCOVERY — one pass, fully parallel
        outcomes = await asyncio.gather(
            *[_fetch_extract_links(url) for url in batch]
        )

        for result, links in outcomes:
            if result is not None:
                results.append(result)
            for link in links:
                if link not in visited and _is_same_root_domain(link, root_domain):
                    queue.append(link)

    return results