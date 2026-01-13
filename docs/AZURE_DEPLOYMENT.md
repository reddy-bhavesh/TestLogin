# Azure Container Apps Deployment Guide

Complete guide for deploying the POC Web App to Azure Container Apps with layered security.

## Architecture

```
Internet → Frontend (Nginx + React) → Backend (FastAPI) → PostgreSQL
                    ↓
           Security Layers:
           - CORS (browser-level)
           - API Key (app-level)
           - IP Restrictions (network-level)
```

### Azure Resources

| Resource           | Name              | Purpose                     |
| ------------------ | ----------------- | --------------------------- |
| Resource Group     | `rg-dummy-webapp` | Container for all resources |
| Container Registry | `pocwebappacr`    | Docker image storage        |
| Container Apps Env | `poc-env`         | Hosting environment         |
| Container App      | `poc-frontend`    | React + Nginx proxy         |
| Container App      | `poc-backend`     | FastAPI API server          |

---

## Prerequisites

- Azure CLI installed
- Docker Desktop installed
- Azure Container Registry access
- PostgreSQL database (existing)

---

## Quick Start

### 1. Login

```powershell
az login
docker login pocwebappacr.azurecr.io -u pocwebappacr -p <ACR_PASSWORD>
```

### 2. Build & Push Images

```powershell
# Backend
docker build -t pocwebappacr.azurecr.io/backend:v1 ./backend
docker push pocwebappacr.azurecr.io/backend:v1

# Frontend (with Azure config)
docker build --build-arg DEPLOY_TARGET=azure -t pocwebappacr.azurecr.io/frontend:v1 ./frontend
docker push pocwebappacr.azurecr.io/frontend:v1
```

### 3. Create Environment

```powershell
az containerapp env create -n poc-env -g rg-dummy-webapp -l centralindia
```

### 4. Deploy Backend

```powershell
$acrPassword = az acr credential show -n pocwebappacr --query "passwords[0].value" -o tsv

az containerapp create `
  -n poc-backend -g rg-dummy-webapp `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/backend:v1 `
  --target-port 8000 --ingress external `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword `
  --min-replicas 1 `
  --env-vars DATABASE_URL="<YOUR_DB_URL>" SECRET_KEY="<SECRET>"
```

### 5. Deploy Frontend

```powershell
az containerapp create `
  -n poc-frontend -g rg-dummy-webapp `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/frontend:v1 `
  --target-port 80 --ingress external `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword
```

### 6. Get URLs

```powershell
az containerapp show -n poc-frontend -g rg-dummy-webapp --query "properties.configuration.ingress.fqdn" -o tsv
az containerapp show -n poc-backend -g rg-dummy-webapp --query "properties.configuration.ingress.fqdn" -o tsv
```

---

## Security Configuration

### Layer 1: CORS

**Azure Portal** → `poc-backend` → Networking → CORS:

- Allowed Origins: `https://<frontend-url>`
- Methods: GET, POST, PUT, DELETE, OPTIONS
- Headers: \*
- Credentials: ✅

### Layer 2: API Key

1. Add secret to backend:

```powershell
az containerapp secret set -n poc-backend -g rg-dummy-webapp --secrets api-key="<YOUR_KEY>"
az containerapp update -n poc-backend -g rg-dummy-webapp --set-env-vars API_KEY=secretref:api-key
```

2. Backend validates `X-API-KEY` header on `/api/` routes
3. Frontend nginx injects header on proxy requests

### Layer 3: IP Restrictions

1. Get frontend IPs:

```powershell
az containerapp show -n poc-frontend -g rg-dummy-webapp --query "properties.outboundIpAddresses" -o tsv
```

2. **Azure Portal** → `poc-backend` → Ingress → IP Restrictions:
   - Mode: Allow configured IPs, deny all others
   - Add each frontend IP as allow rule

---

## Updating

```powershell
# Rebuild and push
docker build -t pocwebappacr.azurecr.io/backend:v2 ./backend
docker push pocwebappacr.azurecr.io/backend:v2

# Update container app
az containerapp update -n poc-backend -g rg-dummy-webapp --image pocwebappacr.azurecr.io/backend:v2
```

---

## Troubleshooting

```powershell
# View logs
az containerapp logs show -n poc-backend -g rg-dummy-webapp --tail 50

# Check status
az containerapp revision list -n poc-backend -g rg-dummy-webapp -o table
```

| Issue             | Solution                 |
| ----------------- | ------------------------ |
| 401 Unauthorized  | API key mismatch         |
| 403 Forbidden     | IP not allowed           |
| 404 Not Found     | Check nginx proxy config |
| Container stopped | Set `--min-replicas 1`   |
