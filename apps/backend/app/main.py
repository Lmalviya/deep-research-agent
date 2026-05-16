import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, AsyncSessionLocal, Base
from app.mcp_manager.catalog import seed_catalog
from app.models import mcp_catalog, user_mcp  # noqa: F401 — ensure models are registered
from app.routers import mcp, chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Host — Backend",
    description="API for managing MCP server configs and routing chat to the Brain service.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mcp.router)
app.include_router(chat.router)

@app.on_event("startup")
async def on_startup():
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Seeding MCP catalog...")
    async with AsyncSessionLocal() as db:
        await seed_catalog(db)

    logger.info("Backend ready.")

@app.get("/health")
async def health():
    return {"status": "ok"}
