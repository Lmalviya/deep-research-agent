from app.models.mcp_catalog import McpCatalog

BUILT_IN_SERVERS: list[dict] = [
    {
        "name": "GitHub",
        "transport": "SSE",
        "endpoint": "https://api.githubcopilot.com/mcp/",
        "requires_auth": True,
        "auth_hint": "Enter your GitHub Personal Access Token (ghp_...)",
        "icon_url": "https://github.com/favicon.ico",
        "description": "Access GitHub repositories, issues, pull requests, and code search.",
    },
    {
        "name": "HuggingFace",
        "transport": "SSE",
        "endpoint": "https://hf.co/mcp",
        "requires_auth": True,
        "auth_hint": "Enter your HuggingFace API token (hf_...)",
        "icon_url": "https://huggingface.co/favicon.ico",
        "description": "Search models, datasets, and Spaces on HuggingFace Hub.",
    },
    {
        "name": "Brave Search",
        "transport": "SSE",
        "endpoint": "https://mcp.brave.com/v1",
        "requires_auth": True,
        "auth_hint": "Enter your Brave Search API key",
        "icon_url": "https://brave.com/favicon.ico",
        "description": "Real-time internet search via Brave Search API.",
    },
]


async def seed_catalog(db) -> None:
    """Insert built-in servers into mcp_catalog if they don't exist yet (idempotent)."""
    from sqlalchemy import select

    for server_data in BUILT_IN_SERVERS:
        result = await db.execute(
            select(McpCatalog).where(McpCatalog.name == server_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            db.add(McpCatalog(**server_data))

    await db.commit()
