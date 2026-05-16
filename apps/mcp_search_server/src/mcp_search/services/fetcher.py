import httpx

from mcp_search.config import settings


async def fetch_html(url: str) -> str:
    """
    Fetch raw HTML content from a URL.
    """

    headers = {
        "User-Agent": settings.user_agent,
        "Accept": "text/html,application/xhtml+xml",
    }

    async with httpx.AsyncClient(
        timeout=settings.request_timeout,
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = await client.get(url)

        response.raise_for_status()

        return response.text