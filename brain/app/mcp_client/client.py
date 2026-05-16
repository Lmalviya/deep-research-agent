"""
Universal MCP Client using LangChain MCP Adapters.

This client:
1. Receives a list of active MCP server configs from the Backend.
2. Creates a MultiServerMCPClient connecting to each via SSE.
3. Loads the tools from all connected servers.
4. Returns the tools list ready for a LangChain agent.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


def build_mcp_server_config(servers: list[dict]) -> dict:
    """
    Convert the Backend's server list into the format expected by MultiServerMCPClient.

    Backend sends:
        [{"config_id": "...", "name": "GitHub", "transport": "SSE", "endpoint": "...", "auth_token": "ghp_..."}]

    MultiServerMCPClient expects:
        {"GitHub": {"transport": "streamable_http", "url": "...", "headers": {"Authorization": "Bearer ..."}}}
    """
    mcp_config = {}
    for server in servers:
        name = server["name"]
        transport = server.get("transport", "SSE").upper()
        endpoint = server["endpoint"]
        auth_token = server.get("auth_token")

        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        # LangChain MCP adapters use "streamable_http" for SSE/HTTP-based servers
        mcp_config[name] = {
            "transport": "streamable_http",
            "url": endpoint,
            "headers": headers,
        }

    return mcp_config


@asynccontextmanager
async def get_mcp_tools(servers: list[dict]) -> AsyncIterator[list[BaseTool]]:
    """
    Context manager that connects to all active MCP servers and yields their tools.
    Cleans up connections on exit.
    """
    if not servers:
        yield []
        return

    mcp_config = build_mcp_server_config(servers)
    logger.info(f"[MCP Client] Connecting to {len(mcp_config)} server(s): {list(mcp_config.keys())}")

    try:
        async with MultiServerMCPClient(mcp_config) as client:
            tools = client.get_tools()
            logger.info(f"[MCP Client] Loaded {len(tools)} tool(s) from {len(mcp_config)} server(s)")
            yield tools
    except Exception as e:
        logger.error(f"[MCP Client] Failed to connect to MCP servers: {e}")
        yield []  # Graceful degradation — agent runs without tools
