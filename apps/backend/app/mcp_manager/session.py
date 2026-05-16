"""
McpSession — manages the lifecycle of a single connection to one MCP server.
For now this is a lightweight wrapper that validates the connection.
Full LangChain tool loading will happen in the Brain service.
"""

import asyncio
import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)


@dataclass
class McpSession:
    config_id: str
    name: str
    transport: str
    endpoint: str
    auth_token: str | None = None

    # Runtime state
    is_connected: bool = False
    error: str | None = None
    discovered_tools: list[str] = field(default_factory=list)

    async def connect(self) -> bool:
        """
        Validate the MCP server is reachable.
        A lightweight health-check via HTTP GET — full tool discovery
        happens in the Brain when the agent is invoked.
        """
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.endpoint, headers=headers)
                # MCP SSE servers typically return 200 or 405 for GET (they expect POST/SSE)
                # We consider anything < 500 as "reachable"
                if response.status_code < 500:
                    self.is_connected = True
                    self.error = None
                    logger.info(f"[McpSession] Connected to {self.name} ({self.endpoint})")
                    return True
                else:
                    self.is_connected = False
                    self.error = f"Server returned HTTP {response.status_code}"
                    return False
        except httpx.ConnectError:
            self.is_connected = False
            self.error = "Connection refused — server may be offline"
            return False
        except httpx.TimeoutException:
            self.is_connected = False
            self.error = "Connection timed out"
            return False
        except Exception as e:
            self.is_connected = False
            self.error = str(e)
            return False

    async def disconnect(self) -> None:
        self.is_connected = False
        logger.info(f"[McpSession] Disconnected from {self.name}")
