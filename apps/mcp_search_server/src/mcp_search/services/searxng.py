import httpx

from mcp_search.config import settings
from mcp_search.models.search import SearchResponse
from mcp_search.models.search import SearchResult


async def search_searxng(
    query: str,
    limit: int | None = None,
) -> SearchResponse:
    limit = limit or settings.max_search_results

    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        headers={
            "User-Agent": settings.user_agent,
        },
    ) as client:
        response = await client.get(
            f"{settings.searxng_base_url}/search",
            params={
                "q": query,
                "format": "json",
            },
        )
        response.raise_for_status()
        data = response.json()

    results: list[SearchResult] = []

    for item in data.get("results", [])[:limit]:
        url = item.get("url")
        if not url:
            continue

        try:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("content", ""),
                    source_engine=item.get("engine"),
                )
            )
        except Exception:
            continue

    return SearchResponse(
        query=query,
        results=results,
    )