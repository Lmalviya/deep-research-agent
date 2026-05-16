"""
Brain service entry point.

POST /invoke — accepts a query + active server list, streams agent response via SSE.
"""

import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.mcp_client.client import get_mcp_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Brain — Orchestration Service",
    description="LangChain-powered agent that uses active MCP tools to answer queries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvokeRequest(BaseModel):
    query: str
    servers: list[dict]  # List from Backend: [{config_id, name, transport, endpoint, auth_token}]


@app.post("/invoke")
async def invoke(body: InvokeRequest):
    """
    Accepts a query and list of active MCP servers.
    Connects to the servers, loads tools, runs a LangChain ReAct agent, streams the result.
    """

    async def event_stream():
        try:
            async with get_mcp_tools(body.servers) as tools:
                tool_names = [t.name for t in tools]
                logger.info(f"[Brain] Running agent with tools: {tool_names}")

                # ── Placeholder agent response ──
                # TODO: Replace this with a real LangChain ReAct agent in the next phase.
                # This is intentionally simple — the architecture is the goal right now.
                yield f"data: {json.dumps({'type': 'tool_info', 'tools': tool_names})}\n\n"
                yield f"data: {json.dumps({'type': 'token', 'content': f'Connected to {len(tools)} tool(s). '})}\n\n"
                yield f"data: {json.dumps({'type': 'token', 'content': f'Query received: {body.query}'})}\n\n"
                yield f"data: {json.dumps({'type': 'token', 'content': ' (Agent logic will be added in the next phase.)'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"[Brain] Error during invocation: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
async def health():
    return {"status": "ok"}
