import json

from mcp_search.config import settings
from mcp_search.models.search import SearchResponse
from mcp_search.models.search import SearchResult
from mcp_search.services.cache import redis_client, _make_key
from mcp_search.services.fetcher import http_client


async def search_searxng(
    query: str,
    limit: int | None = None,
) -> SearchResponse:
    limit = limit or settings.max_search_results

    # 1. CHECK CACHE FIRST
    cache_key = _make_key("search", f"{query}:{limit}")
    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        return SearchResponse.model_validate(data)
        
    # 2. CALL SEARXNG
    response = await http_client.get(
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

    output = SearchResponse(query=query, results=results)

    # 3. STORE CACHE (5 min TTL)
    await redis_client.set(
        cache_key,
        output.model_dump_json(),
        ex=300,
    )
    return output