import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


# ─────────────────────── Catalog ───────────────────────

class McpCatalogRead(BaseModel):
    id: uuid.UUID
    name: str
    transport: str
    endpoint: str
    requires_auth: bool
    auth_hint: Optional[str] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None

    # Injected at request time — not stored in this table
    user_config_id: Optional[uuid.UUID] = None
    is_active: bool = False
    has_token: bool = False

    class Config:
        from_attributes = True


# ─────────────────────── User MCP Config ───────────────────────

class UserMcpConfigCreate(BaseModel):
    """Used when creating a built-in activation OR a custom server."""
    user_id: str
    catalog_id: Optional[uuid.UUID] = None  # Provided for built-ins, None for custom
    name: str
    transport: str  # "SSE" | "Stdio"
    endpoint: str
    auth_token: Optional[str] = None  # Plaintext — backend encrypts before storage
    is_custom: bool = False


class UserMcpConfigUpdate(BaseModel):
    """Used when editing a config. All fields optional."""
    name: Optional[str] = None
    endpoint: Optional[str] = None
    auth_token: Optional[str] = None  # Provide to update, omit to keep existing
    is_active: Optional[bool] = None


class UserMcpConfigRead(BaseModel):
    id: uuid.UUID
    user_id: str
    catalog_id: Optional[uuid.UUID] = None
    name: str
    transport: str
    endpoint: str
    has_token: bool  # True if auth_token_encrypted is not None (never expose the raw token)
    is_active: bool
    is_custom: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────── Chat ───────────────────────

class ChatRequest(BaseModel):
    user_id: str
    query: str
