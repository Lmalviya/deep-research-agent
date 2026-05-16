# 🕵️‍♂️ Deep Research Agent

Autonomous research platform built with LangGraph multi-agent orchestration, custom + third-party MCP servers, and production-grade infrastructure.

## 🏗️ Architecture

- **`apps/ui`**: Next.js + shadcn/ui frontend (Claude-inspired aesthetic).
- **`apps/backend`**: FastAPI gateway + MCP connection manager (PostgreSQL).
- **`brain`**: Orchestration service using LangChain MCP adapters for universal tool access.
- **`infra`**: Shared infrastructure including LiteLLM Proxy, Prometheus, and PostgreSQL.

---

## 🚀 Quick Start (Local Development)

To run the full stack, start the components in this specific order:

### 1. Start the Database
The backend requires the dedicated MCP Postgres instance.
```powershell
docker compose -f infra/docker-compose.yml up -d mcp-postgres
```

### 2. Start the Brain Service
The orchestration layer that connects to remote MCP providers.
```powershell
cd brain
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 3. Start the Backend API
The gateway for UI requests and secret management.
```powershell
cd apps/backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Start the UI
The research dashboard.
```powershell
cd apps/ui
npm run dev
```

---

## 🔗 Port Mapping

| Service | URL |
| :--- | :--- |
| **Frontend UI** | [http://localhost:3000](http://localhost:3000) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **Brain API** | [http://localhost:8001](http://localhost:8001) |
| **Postgres (MCP)** | `localhost:5433` |
| **LiteLLM Proxy** | [http://localhost:4000](http://localhost:4000) |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) |

---

## 🛠️ Features

- **Dynamic MCP Add-ons**: Add GitHub, HuggingFace, or custom servers via the UI.
- **Multi-User Ready**: Isolated MCP configurations per user (Postgres + Encryption).
- **Streaming Orchestration**: Real-time agent progress and tool-usage badges.
- **Production Infrastructure**: Built-in monitoring, proxying, and containerization.
