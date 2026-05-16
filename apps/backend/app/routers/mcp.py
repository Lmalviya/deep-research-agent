import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.mcp_manager.catalog import seed_catalog
from app.mcp_manager.crypto import encrypt_token, decrypt_token
from app.mcp_manager.manager import mcp_manager
from app.models.mcp_catalog import McpCatalog
from app.models.user_mcp import UserMcpConfig
from app.models.schemas import (
    McpCatalogRead,
    UserMcpConfigCreate,
    UserMcpConfigRead,
    UserMcpConfigUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp", tags=["MCP"])


# ─────────────────────── Catalog ───────────────────────

@router.get("/catalog", response_model=list[McpCatalogRead])
async def get_catalog(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """
    Returns the full list of available built-in MCP servers,
    annotated with the current user's activation status.
    """
    # Fetch all catalog entries
    catalog_result = await db.execute(select(McpCatalog))
    catalog_items = catalog_result.scalars().all()

    # Fetch this user's existing configs (keyed by catalog_id)
    user_result = await db.execute(
        select(UserMcpConfig).where(UserMcpConfig.user_id == user_id)
    )
    user_configs = {str(c.catalog_id): c for c in user_result.scalars().all() if c.catalog_id}

    response = []
    for item in catalog_items:
        user_config = user_configs.get(str(item.id))
        response.append(
            McpCatalogRead(
                id=item.id,
                name=item.name,
                transport=item.transport,
                endpoint=item.endpoint,
                requires_auth=item.requires_auth,
                auth_hint=item.auth_hint,
                icon_url=item.icon_url,
                description=item.description,
                user_config_id=user_config.id if user_config else None,
                is_active=user_config.is_active if user_config else False,
                has_token=bool(user_config and user_config.auth_token_encrypted) if user_config else False,
            )
        )
    return response


# ─────────────────────── User Configs ───────────────────────

@router.get("/configs", response_model=list[UserMcpConfigRead])
async def list_user_configs(user_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Returns all MCP configs for the given user."""
    result = await db.execute(
        select(UserMcpConfig).where(UserMcpConfig.user_id == user_id)
    )
    configs = result.scalars().all()
    return [_to_read_schema(c) for c in configs]


@router.post("/configs", response_model=UserMcpConfigRead, status_code=201)
async def create_config(body: UserMcpConfigCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a user MCP config.
    - For built-ins: provide catalog_id. Auth token is required if catalog.requires_auth=True.
    - For custom: set is_custom=True, catalog_id=None, and provide all fields manually.
    """
    # Guard: if built-in, check catalog exists and auth requirement
    if body.catalog_id:
        catalog = await db.get(McpCatalog, body.catalog_id)
        if not catalog:
            raise HTTPException(status_code=404, detail="Catalog entry not found")
        if catalog.requires_auth and not body.auth_token:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "AUTH_REQUIRED",
                    "message": f"{catalog.name} requires an auth token.",
                    "auth_hint": catalog.auth_hint,
                },
            )

    # Guard: prevent duplicate built-in activations per user
    if body.catalog_id:
        existing = await db.execute(
            select(UserMcpConfig).where(
                UserMcpConfig.user_id == body.user_id,
                UserMcpConfig.catalog_id == body.catalog_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="You have already added this server.")

    # Encrypt token if provided
    encrypted = encrypt_token(body.auth_token) if body.auth_token else None

    config = UserMcpConfig(
        user_id=body.user_id,
        catalog_id=body.catalog_id,
        name=body.name,
        transport=body.transport,
        endpoint=body.endpoint,
        auth_token_encrypted=encrypted,
        is_active=True,  # Activate immediately on creation
        is_custom=body.is_custom,
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)

    # Kick off connection if active
    if config.is_active:
        await _connect_session(config)

    return _to_read_schema(config)


@router.patch("/configs/{config_id}", response_model=UserMcpConfigRead)
async def update_config(
    config_id: uuid.UUID,
    body: UserMcpConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Edit name, endpoint, auth_token, or toggle is_active for any user config."""
    config = await db.get(UserMcpConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    if body.name is not None:
        config.name = body.name
    if body.endpoint is not None:
        config.endpoint = body.endpoint
    if body.auth_token is not None:
        config.auth_token_encrypted = encrypt_token(body.auth_token)

    reconnect_needed = False

    if body.is_active is not None and body.is_active != config.is_active:
        config.is_active = body.is_active
        reconnect_needed = True

    # If any connection-related field changed, reconnect
    if body.endpoint is not None or body.auth_token is not None:
        reconnect_needed = True

    await db.commit()
    await db.refresh(config)

    if reconnect_needed:
        if config.is_active:
            await _connect_session(config)
        else:
            await mcp_manager.disconnect(str(config.id))

    return _to_read_schema(config)


@router.delete("/configs/{config_id}", status_code=204)
async def delete_config(config_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Permanently delete a custom MCP config. Built-in configs cannot be deleted."""
    config = await db.get(UserMcpConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    if not config.is_custom:
        raise HTTPException(
            status_code=403,
            detail="Built-in server configurations cannot be permanently deleted. You can deactivate them instead.",
        )

    # Disconnect session if running
    await mcp_manager.disconnect(str(config.id))
    await db.delete(config)
    await db.commit()


# ─────────────────────── Helpers ───────────────────────

async def _connect_session(config: UserMcpConfig) -> None:
    """Decrypt token and hand off to McpManager."""
    token = None
    if config.auth_token_encrypted:
        try:
            token = decrypt_token(config.auth_token_encrypted)
        except ValueError:
            logger.error(f"Failed to decrypt token for config {config.id}")
    await mcp_manager.connect(
        config_id=str(config.id),
        name=config.name,
        transport=config.transport,
        endpoint=config.endpoint,
        auth_token=token,
    )


def _to_read_schema(config: UserMcpConfig) -> UserMcpConfigRead:
    return UserMcpConfigRead(
        id=config.id,
        user_id=config.user_id,
        catalog_id=config.catalog_id,
        name=config.name,
        transport=config.transport,
        endpoint=config.endpoint,
        has_token=config.auth_token_encrypted is not None,
        is_active=config.is_active,
        is_custom=config.is_custom,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )
