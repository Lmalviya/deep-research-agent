import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class McpCatalog(Base):
    """Global catalog of built-in MCP servers. Seeded at startup. Users cannot modify these."""

    __tablename__ = "mcp_catalog"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    transport: Mapped[str] = mapped_column(String(10), nullable=False)  # "SSE" | "Stdio"
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auth_hint: Mapped[str | None] = mapped_column(Text, nullable=True)  # User-facing hint for token
    icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
