import asyncio
from collections import deque

from mcp_search.services.batch_extractor import batch_extract
from mcp_search.services.fetcher import fetch_html
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

async def batch_crawl(
    start_url: str,
    max_pages: int = 20,
    batch_size: int = 5,
) -> list[ExtractResponse]:

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

        # 2. PARALLEL FETCH + EXTRACT
        batch_results = await batch_extract(batch)
        results.extend(batch_results)

        # 3. DISCOVER NEW LINKS (WAVE EXPANSION)
        for url in batch:
            try:
                html = await fetch_html(url)
                links = _extract_links(html, url)

                for link in links:
                    if link not in visited:
                        queue.append(link)

            except Exception:
                continue

    return results