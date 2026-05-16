import trafilatura
import asyncio

from mcp_search.models.extract import ExtractResponse


def extract_content(url: str, html: str) -> ExtractResponse:
    """
    Extract clean markdown content from raw HTML.
    """
    cache_key = _make_key("extract", url)


    extracted = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_formatting=True,
        favor_recall=True,
    )

    if not extracted:
        extracted = ""

    # Try to get title separately (light extraction)
    metadata = trafilatura.metadata.extract_metadata(html)
    title = None

    if metadata:
        title = metadata.title

    result = ExtractResponse(
        url=url,
        title=title,
        content=extracted,
        raw_content_length=len(extracted),
        # author=metadata.author,
        # publish_date=metadata.date,
        # language=metadata.language,
        # quality_score=metadata.quality,
    )
    

    # Fire-and-forget cache write (simple version)
    try:
        async def _cache():
            await redis_client.set(
                cache_key,
                result.model_dump_json(),
                ex=3600,
            )

        asyncio.create_task(_cache())

    except Exception:
        pass

    return result