# 🏛️ Infrastructure: LiteLLM Proxy & Monitoring

This directory contains the core infrastructure for the Deep Research Platform. It is designed with a **Bridge Architecture** to ensure high security and centralized monitoring.

## 🏗️ Architecture Overview

*   **LiteLLM Proxy**: Acts as the central gateway for all AI model requests.
*   **PostgreSQL**: A dedicated, isolated database for LiteLLM to store keys and logs.
*   **Prometheus**: A global monitoring service that scrapes performance metrics.

### 🛡️ Network Security
We use two separate networks:
1.  `infra-network` (External): A global bridge for monitoring and cross-service communication.
2.  `litellm-db-internal` (Internal): A private network that isolates the database from the rest of the system.

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

### 1. Prerequisites
Ensure **Docker Desktop** is running on your machine.

### 2. Initialize the Global Network
Run this command once to create the shared communication bridge:
```powershell
docker network create infra-network
```

### 3. Start Global Monitoring
Start the Prometheus stack first:
```powershell
cd infra
docker compose up -d
```

### 4. Start LiteLLM Proxy
Navigate to the litellm directory and start the proxy and its database:
```powershell
cd infra/litellm
docker compose up -d
```

---

## 🧪 Testing the Setup

### Test 1: API Connectivity
Check if the proxy is alive and can handle authentication (replaces the key with the one in your `.env`):
```powershell
curl -X POST 'http://localhost:4000/chat/completions' `
  -H 'Content-Type: application/json' `
  -H 'Authorization: Bearer sk-admin-7f2a1b9c3d4e5f6a8b' `
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello!"}]}'
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
