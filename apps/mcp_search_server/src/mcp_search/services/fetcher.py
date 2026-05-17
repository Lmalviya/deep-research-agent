import httpx

from mcp_search.config import settings

# Module-level shared client — one connection pool for all outbound HTTP calls.
# httpx.AsyncClient is coroutine-safe; sharing it across calls enables TCP keep-alive
# and avoids the overhead of a fresh TLS handshake on every request.
http_client = httpx.AsyncClient(
    timeout=settings.request_timeout,
    follow_redirects=True,
    headers={
        "User-Agent": settings.user_agent,
        "Accept": "text/html,application/xhtml+xml",
    },
    limits=httpx.Limits(
        max_connections=20,           # total concurrent connections
        max_keepalive_connections=10, # idle keep-alive slots
        keepalive_expiry=30,          # seconds before idle connection is dropped
    ),
)


async def fetch_html(url: str) -> str:
    """
    Fetch raw HTML content from a URL.
    Uses the module-level shared client for connection pool reuse.
    """
    response = await http_client.get(url)
    response.raise_for_status()
    return response.text