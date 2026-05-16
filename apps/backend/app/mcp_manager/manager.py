"""
McpManager — singleton that maintains active McpSessions for all users.
Sessions are keyed by user_mcp_config.id (UUID string).
"""

import logging
from typing import Dict

from app.mcp_manager.session import McpSession

logger = logging.getLogger(__name__)


class McpManager:
    def __init__(self):
        # { config_id: McpSession }
        self._sessions: Dict[str, McpSession] = {}

    async def connect(
        self,
        config_id: str,
        name: str,
        transport: str,
        endpoint: str,
        auth_token: str | None = None,
    ) -> McpSession:
        """Create or replace a session for a given config_id."""
        # Disconnect existing session if any
        if config_id in self._sessions:
            await self._sessions[config_id].disconnect()

        session = McpSession(
            config_id=config_id,
            name=name,
            transport=transport,
            endpoint=endpoint,
            auth_token=auth_token,
        )
        await session.connect()
        self._sessions[config_id] = session
        return session

    async def disconnect(self, config_id: str) -> None:
        """Disconnect and remove a session."""
        if config_id in self._sessions:
            await self._sessions[config_id].disconnect()
            del self._sessions[config_id]
            logger.info(f"[McpManager] Removed session for config {config_id}")

    def get_session(self, config_id: str) -> McpSession | None:
        return self._sessions.get(config_id)

    def get_active_sessions_for_user(self, user_id: str) -> list[McpSession]:
        """Returns all connected sessions for a given user (for brain invocation)."""
        return [s for s in self._sessions.values() if s.is_connected]

    def get_all_sessions(self) -> dict[str, McpSession]:
        return self._sessions


# Global singleton — imported by routers
mcp_manager = McpManager()
