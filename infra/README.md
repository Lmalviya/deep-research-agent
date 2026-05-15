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

## 🧪 Testing

### Test API (using NVIDIA example)
```powershell
curl -X POST 'http://localhost:4000/chat/completions' `
  -H 'Content-Type: application/json' `
  -H 'Authorization: Bearer sk-admin-7f2a1b9c3d4e5f6a8b' `
  -d '{"model": "nemotron", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### Test 2: Monitoring Link
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
