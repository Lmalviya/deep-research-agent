# MCP Search Server

A lightweight search-focused MCP (Model Context Protocol) server built using the official MCP Python SDK.

This project is designed for learning and experimentation around:

* MCP servers
* Retrieval systems
* Web search orchestration
* Content extraction pipelines
* Agent tooling

The server currently provides:

* `search` — search the web using SearxNG
* `extract` — extract clean webpage content (coming next)
* `crawl` — recursively crawl webpages (coming next)

---

# Architecture

```text
MCP Client
    ↓
MCP Search Server
    ↓
SearxNG
    ↓
Search Engines
(Google, Brave, DuckDuckGo, etc.)
```

The MCP server does NOT directly scrape Google.
Instead, it uses a self-hosted SearxNG instance as the search provider.

---

# Tech Stack

| Component   | Purpose                   |
| ----------- | ------------------------- |
| MCP SDK     | MCP server implementation |
| FastMCP     | Simplified MCP framework  |
| SearxNG     | Meta search engine        |
| Redis       | SearxNG caching/storage   |
| httpx       | Async HTTP client         |
| trafilatura | Clean webpage extraction  |
| Pydantic    | Validation and schemas    |
| uv          | Python package manager    |

---

# Project Structure

```text
mcp-search-server/
│
├── pyproject.toml
├── README.md
├── .env
│
├── src/
│   └── mcp_search/
│       ├── __init__.py
│       ├── server.py
│       ├── config.py
│       │
│       ├── tools/
│       │   ├── search.py
│       │   ├── extract.py
│       │   └── crawl.py
│       │
│       ├── services/
│       │   ├── searxng.py
│       │   ├── fetcher.py
│       │   ├── extractor.py
│       │   └── crawler.py
│       │
│       ├── models/
│       │   ├── search.py
│       │   ├── extract.py
│       │   └── crawl.py
│       │
│       └── utils/
│           ├── markdown.py
│           └── urls.py
│
└── tests/
```

---

# Prerequisites

Install:

* Python 3.11+
* Docker
* Node.js (for MCP Inspector)
* uv

---

# Install uv

## Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```bash
uv --version
```

---

# Setup SearxNG

Create:

```text
infra/search/docker-compose.yml
```

Example:

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: redis

    restart: unless-stopped

    ports:
      - "6379:6379"

    command: >
      redis-server
      --appendonly yes
      --save 60 1000
      --loglevel warning

    volumes:
      - redis_data:/data

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

    networks:
      - infra-network

  searxng:
    image: searxng/searxng:latest
    container_name: searxng

    restart: unless-stopped

    ports:
      - "8080:8080"

    environment:
      - BASE_URL=http://localhost:8080/
      - INSTANCE_NAME=MySearxNG
      - SEARXNG_REDIS_URL=redis://redis:6379/0

    volumes:
      - ./searxng:/etc/searxng

    networks:
      - infra-network

volumes:
  redis_data:

networks:
  infra-network:
    external: true
```

---

# Create Shared Docker Network

Run once:

```bash
docker network create infra-network
```

---

# Start SearxNG

```bash
docker compose up -d
```

---

# Configure SearxNG JSON API

Edit:

```text
./searxng/settings.yml
```

Ensure:

```yaml
use_default_settings: true

server:
  public_instance: false

search:
  formats:
    - html
    - json

  safe_search: 0

limiter: false
```

Restart:

```bash
docker compose restart searxng
```

---

# Verify SearxNG

Open browser:

```text
http://localhost:8080
```

Test JSON API:

```text
http://localhost:8080/search?q=chatgpt&format=json
```

You should receive JSON results.

---

# Install Project Dependencies

From project root:

```bash
uv sync
```

---

# Environment Variables

Create `.env`:

```env
SEARXNG_BASE_URL=http://localhost:8080
REQUEST_TIMEOUT=30
MAX_SEARCH_RESULTS=5
MAX_CRAWL_PAGES=20
```

---

# Run MCP Server

```bash
uv run mcp-search
```

Expected:

```text
Starting MCP Search Server...
```

The server will then wait silently for MCP client connections.

This is normal behavior.

---

# Test Using MCP Inspector

Install and run Inspector:

```bash
npx @modelcontextprotocol/inspector
```

In the Inspector UI:

## Transport

```text
stdio
```

## Command

```text
uv
```

## Arguments

```text
run mcp-search
```

Connect.

You should now see registered tools such as:

```text
search
```

---

# Example Search Tool Request

Input:

```json
{
  "query": "latest model context protocol updates",
  "limit": 5
}
```

Example Response:

```json
{
  "query": "latest model context protocol updates",
  "results": [
    {
      "title": "...",
      "url": "https://...",
      "snippet": "...",
      "source_engine": "duckduckgo"
    }
  ]
}
```

---

# Current Development Status

## Implemented

* MCP server bootstrap
* Search tool registration
* SearxNG integration
* Typed Pydantic models
* MCP Inspector testing

## Coming Next

* Extract tool
* Crawl tool
* Async parallel fetching
* Markdown extraction
* Result reranking
* URL deduplication
* Caching layer

---

# Important Concepts

## MCP Server

Your MCP server is NOT a web server.

It communicates using the MCP protocol over:

* stdio
* SSE
* streamable HTTP

Currently this project uses:

```text
stdio
```

---

## Why SearxNG?

SearxNG acts as a search abstraction layer.

Instead of directly scraping Google, the MCP server uses:

```text
MCP → SearxNG → Search Engines
```

Benefits:

* multi-engine support
* normalized results
* self-hosted
* no vendor lock-in
* easier maintenance

---

# Troubleshooting

## 403 Forbidden on JSON API

Cause:

* SearxNG JSON API disabled
* limiter enabled

Fix:

* enable JSON format
* disable limiter
* restart container

---

## MCP Server Shows No Output

This is normal.

MCP servers wait for MCP clients and usually communicate silently over stdio.

Use MCP Inspector to interact with the server.

---

## Inspector Cannot Connect

Verify:

```bash
uv run mcp-search
```

runs successfully.

Also verify:

* Python installed
* uv installed
* dependencies synced

---

# Learning Goals

This project is intentionally focused on understanding:

* MCP architecture
* Retrieval systems
* Search orchestration
* Content extraction
* Agent tooling

Rather than building:

* a full search engine
* a vector database platform
* a LangChain-heavy abstraction layer

---

# License

MIT
