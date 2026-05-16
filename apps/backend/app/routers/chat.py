import json
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.mcp_manager.crypto import decrypt_token
from app.models.schemas import ChatRequest
from app.models.user_mcp import UserMcpConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def chat(body: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts a user query, builds the list of active MCP server configs for that user,
    and streams the Brain's SSE response back to the UI.
    """
    # Fetch all active configs for this user
    result = await db.execute(
        select(UserMcpConfig).where(
            UserMcpConfig.user_id == body.user_id,
            UserMcpConfig.is_active == True,  # noqa: E712
        )
    )
    active_configs = result.scalars().all()

    if not active_configs:
        raise HTTPException(
            status_code=400,
            detail="No active MCP servers. Please add at least one server in the sidebar.",
        )

    # Build the server list for the Brain (decrypt tokens here — Brain never touches DB)
    servers = []
    for config in active_configs:
        token = None
        if config.auth_token_encrypted:
            try:
                token = decrypt_token(config.auth_token_encrypted)
            except ValueError:
                logger.warning(f"Could not decrypt token for config {config.id}, skipping.")
                continue

        servers.append(
            {
                "config_id": str(config.id),
                "name": config.name,
                "transport": config.transport,
                "endpoint": config.endpoint,
                "auth_token": token,
            }
        )

    brain_payload = {
        "query": body.query,
        "servers": servers,
    }

    async def event_stream():
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{settings.brain_url}/invoke",
                json=brain_payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                if response.status_code != 200:
                    error = await response.aread()
                    yield f"data: {json.dumps({'error': error.decode()})}\n\n"
                    return
                async for chunk in response.aiter_text():
                    yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")
