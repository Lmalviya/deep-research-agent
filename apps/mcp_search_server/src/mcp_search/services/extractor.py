import trafilatura

from mcp_search.models.extract import ExtractResponse


def extract_content(url: str, html: str) -> ExtractResponse:
    """
    Extract clean markdown content from raw HTML.
    """
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

    return result