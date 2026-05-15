# 🏛️ Infrastructure: LiteLLM Proxy & Monitoring

This directory contains the production-grade infrastructure for the Deep Research Platform. It features a **Bridge Architecture** that isolates sensitive database traffic while providing global observability.

## 🏗️ Architecture Overview

*   **LiteLLM Proxy**: The central gateway for all AI requests.
*   **PostgreSQL**: An isolated database (`litellm-db`) for persistence.
*   **Prometheus**: Global monitoring that scrapes performance metrics.

### 🛡️ Network Security
1.  **`infra-network` (Global)**: The bridge connecting Prometheus to LiteLLM.
2.  **`litellm-db-internal` (Private)**: An isolated network for LiteLLM-to-DB traffic only.

---

## 📂 Directory Structure

```text
infra/
├── README.md              # You are here
├── docker-compose.yml     # Global Monitoring (Prometheus)
├── prometheus.yml         # Monitoring configuration
└── litellm/
    ├── .env               # Secrets (Master Keys, API Keys)
    ├── config.yaml        # Model Routing & DB Logic
    └── docker-compose.yml # LiteLLM & Postgres services
```

---

## 🤖 Supported Models (Ready to use)

| Provider | Proxy Model Name | Internal Engine | Type |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `gpt-4o` | `gpt-4o` (Load Balanced) | Chat |
| **Anthropic** | `smart-model` | `claude-3-5-sonnet` (Fallback to gpt-4o) | Chat |
| **NVIDIA** | `nemotron` | `nvidia_nim/meta/llama-3.1-8b-instruct` | Chat |
| **OpenAI** | `text-embedding` | `text-embedding-3-small` | **Embedding** |

---

## 🚀 Setup Instructions

### 1. Initialize Networking
Run this once to create the global communication bridge:
```powershell
docker network create infra-network
```

### 2. Configure Secrets
Edit `infra/litellm/.env` and add your real API keys for the providers you want to use.

### 3. Start the Stack
```powershell
# Start Monitoring
cd infra
docker compose up -d

# Start LiteLLM Proxy
cd litellm
docker compose up -d
```

---

## 🖥️ Admin UI Dashboard

LiteLLM includes a built-in dashboard for managing keys and tracking usage.

*   **URL**: [http://localhost:4000/ui](http://localhost:4000/ui)
*   **Authentication**: Use the `LITELLM_MASTER_KEY` from your `.env` file to log in.

### Key Features:
*   **Virtual Keys**: Create specific keys with budgets and expiration dates.
*   **Spend Tracking**: Real-time monitoring of costs across all providers.
*   **Playground**: Test models directly in the browser.
*   **Audit Logs**: View every request and response passing through the proxy.

---

## 🧪 Testing

### Test 1: Chat Completions (Chat)
```powershell
curl -X POST 'http://localhost:4000/chat/completions' `
  -H 'Content-Type: application/json' `
  -H 'Authorization: Bearer sk-admin-7f2a1b9c3d4e5f6a8b' `
  -d '{"model": "nemotron", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Test 2: Text Embeddings (Vector)
```powershell
curl -X POST 'http://localhost:4000/embeddings' `
  -H 'Content-Type: application/json' `
  -H 'Authorization: Bearer sk-admin-7f2a1b9c3d4e5f6a8b' `
  -d '{"model": "text-embedding", "input": "The quick brown fox jumps over the lazy dog"}'
```

### Test 3: Monitoring Link
1.  **Metrics Check**: Run `curl http://localhost:4000/metrics`. You should see a list of performance stats.
2.  **Dashboard Check**: Open [http://localhost:9090/targets](http://localhost:9090/targets). The `litellm` target should be **UP** (Green).

---

## 🛠️ Maintenance

### Viewing Logs
If you encounter issues, check the proxy logs:
```powershell
docker logs litellm-proxy --tail 100 -f
```

### Stopping the Stack
```powershell
# Stop everything
docker compose -f infra/docker-compose.yml down
docker compose -f infra/litellm/docker-compose.yml down
```
