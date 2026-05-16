import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserMcpConfig(Base):
    """Per-user MCP server config. Links a user to a catalog entry (built-in) or defines a custom server."""

    __tablename__ = "user_mcp_config"

    __table_args__ = (
        # A user can only activate each catalog entry once
        UniqueConstraint("user_id", "catalog_id", name="uq_user_catalog"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The user who owns this config — using a plain string (localStorage UUID for now, real auth later)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    # FK to mcp_catalog — NULL if this is a fully custom server
    catalog_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mcp_catalog.id", ondelete="SET NULL"), nullable=True
    )

    # Server definition — inherits defaults from catalog but can be overridden
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    transport: Mapped[str] = mapped_column(String(10), nullable=False)  # "SSE" | "Stdio"
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)

    # Auth token — encrypted at application layer via Fernet before storage
    auth_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship (optional — for eager loading)
    catalog: Mapped["McpCatalog | None"] = relationship("McpCatalog", lazy="joined")  # noqa: F821
