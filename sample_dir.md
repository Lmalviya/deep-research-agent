# Mono-Repo Directory Structure: Multi-Agent Research Platform

## High-Level Overview

```text
deep-research-platform/
│
├── apps/
│   ├── orchestrator/           # LangGraph multi-agent app (shallow for now)
│   ├── doc-mcp-server/         # ★ YOUR CUSTOM MCP SERVER (deep dive below)
│   └── web/                    # Next.js dashboard (shallow for now)
│
├── packages/                   # Shared Python/JS code across apps
│   ├── py-shared/              # Common schemas, base classes, utilities
│   └── js-shared/              # Shared TypeScript types for the UI
│
├── infra/                      # Docker, K8s, IaC (Terraform etc.)
│   ├── docker-compose.yml      # Full local dev stack
│   └── k8s/                    # Kubernetes manifests (prod)
│
├── docs/                       # Architecture docs, ADRs
├── scripts/                    # Dev helper scripts
├── pyproject.toml              # Root uv workspace config
└── .env.example
```

---

## Deep Dive: `apps/doc-mcp-server/` — The Custom MCP Server

This is a standalone FastAPI service that exposes document processing capabilities as MCP tools.
It is **stateless** — it receives a request, does the heavy lifting, and returns a result.

```text
apps/doc-mcp-server/
│
├── Dockerfile
├── pyproject.toml
├── .env.example                      # VECTOR_DB_URL, EMBED_MODEL, etc.
│
└── src/
    ├── main.py                       # FastAPI app — mounts the MCP SSE router
    │
    ├── server.py                     # MCP Server instance definition
    │                                 # Registers all tools with the MCP SDK
    │
    ├── tools/                        # ★ Each file = one logical MCP Tool group
    │   ├── __init__.py               # Imports and registers all tools
    │   ├── document_loader.py        # Tool: load_document()
    │   ├── chunker.py                # Tool: chunk_text()
    │   ├── table_extractor.py        # Tool: extract_tables()
    │   ├── image_extractor.py        # Tool: extract_images()
    │   ├── embedder.py               # Tool: generate_embeddings()
    │   └── vector_indexer.py         # Tool: upsert_to_vector_db()
    │
    ├── core/                         # Business logic — NOT exposed as MCP tools
    │   ├── parsers/                  # Raw file parsing logic
    │   │   ├── pdf_parser.py         # PyMuPDF / pdfplumber
    │   │   ├── docx_parser.py        # python-docx
    │   │   └── image_parser.py       # OCR with Tesseract / EasyOCR
    │   ├── chunking/                 # Chunking strategies
    │   │   ├── character_splitter.py
    │   │   └── semantic_splitter.py
    │   ├── embedding/                # Embedding model clients
    │   │   └── embed_client.py       # OpenAI / local HuggingFace adapter
    │   └── vector_db/                # Vector DB client
    │       └── qdrant_client.py
    │
    ├── schemas/                      # Pydantic input/output schemas for each tool
    │   ├── document.py               # LoadDocumentInput, LoadDocumentOutput
    │   ├── chunk.py                  # ChunkInput, ChunkOutput
    │   ├── embed.py                  # EmbedInput, EmbedOutput
    │   └── index.py                  # IndexInput, IndexOutput
    │
    └── config.py                     # Settings via pydantic-settings
```

---

## Deep Dive: `apps/orchestrator/src/clients/` — The MCP Client

The orchestrator is a LangGraph app. It **consumes** MCP servers — your custom one + third-party ones.
The `clients/` sub-directory is where all MCP communication is centralized.

```text
apps/orchestrator/src/clients/
│
├── __init__.py
│
├── base_mcp_client.py            # Abstract base: connect(), list_tools(), call_tool()
│                                 # Handles SSE vs stdio transport transparently
│
├── doc_processing_client.py      # Client for YOUR doc-mcp-server
│                                 # Typed wrappers: load_doc(), chunk(), embed()
│
├── brave_search_client.py        # Client for Brave Search MCP (3rd party)
│
├── memory_client.py              # Client for Memory/Graph MCP (3rd party)
│
└── tool_registry.py              # ★ Central registry
                                  # Discovers tools from all connected MCP servers
                                  # Converts them into LangChain-compatible Tool objects
                                  # so LangGraph agents can call them
```

---

## Key Design Decisions to Discuss

| Concern | Decision | Reason |
|---|---|---|
| **Transport** | SSE (HTTP) for your server | Easy to deploy behind a load balancer; stdio is only for local CLI tools |
| **Auth** | API Key header (`X-API-Key`) on the MCP server | Simple, stateless, works with any infra |
| **State in MCP Server** | None — purely stateless | Allows horizontal scaling; state lives in orchestrator |
| **What stays in MCP Server** | File parsing, chunking, embedding, VDB writes | CPU/GPU heavy, needs its own container resources |
| **What stays in Orchestrator** | Routing, retries, agent state, job tracking | Logic decisions, not data processing |
| **Schemas** | Pydantic models for all tool inputs/outputs | Type safety, auto-generated MCP tool descriptions |
