# Azure Container Apps Deployment - Complete Walkthrough

Comprehensive guide for deploying the POC Web App to Azure Container Apps with layered security.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Azure Container Apps Environment                   │
│                                                                       │
│  ┌─────────────────────┐         ┌─────────────────────┐             │
│  │   Frontend          │         │    Backend          │             │
│  │   (External)        │────────▶│    (External)       │             │
│  │   - React + Nginx   │  HTTPS  │   - FastAPI         │             │
│  └─────────────────────┘         └─────────────────────┘             │
│          ▲                               │                           │
└──────────┼───────────────────────────────┼───────────────────────────┘
           │                               │
      Internet                        PostgreSQL
```

### Components

| Resource                   | Purpose                     |
| -------------------------- | --------------------------- |
| Resource Group             | Container for all resources |
| Container Registry         | Docker image storage        |
| Container Apps Environment | Hosting environment         |
| Frontend Container App     | React + Nginx proxy         |
| Backend Container App      | FastAPI API server          |

---

## Step 1: Azure Login & Setup

### Login to Azure

```powershell
# Placeholder
az login

# Example
az login
```

### Login to Container Registry

```powershell
# Placeholder
az acr login -n <ACR_NAME>

# Example
az acr login -n pocwebappacr
```

---

## Step 2: Build Docker Images

### Backend Image

```powershell
# Placeholder
docker build -t <ACR_NAME>.azurecr.io/backend:<VERSION> ./backend
docker push <ACR_NAME>.azurecr.io/backend:<VERSION>

# Example
docker build -t pocwebappacr.azurecr.io/backend:v1 ./backend
docker push pocwebappacr.azurecr.io/backend:v1
```

### Frontend Image

```powershell
# Placeholder
docker build --build-arg DEPLOY_TARGET=azure -t <ACR_NAME>.azurecr.io/frontend:<VERSION> ./frontend
docker push <ACR_NAME>.azurecr.io/frontend:<VERSION>

# Example
docker build --build-arg DEPLOY_TARGET=azure -t pocwebappacr.azurecr.io/frontend:v1 ./frontend
docker push pocwebappacr.azurecr.io/frontend:v1
```

---

## Step 3: Create Container Apps Environment

```powershell
# Placeholder
az containerapp env create -n <ENV_NAME> -g <RESOURCE_GROUP> -l <LOCATION>

# Example
az containerapp env create -n poc-env -g rg-dummy-webapp -l centralindia
```

---

## Step 4: Deploy Backend

### 4.1 Get ACR Credentials

```powershell
# Placeholder
$acrPassword = az acr credential show -n <ACR_NAME> --query "passwords[0].value" -o tsv

# Example
$acrPassword = az acr credential show -n pocwebappacr --query "passwords[0].value" -o tsv
```

### 4.2 Deploy Backend Container

```powershell
# Placeholder
az containerapp create `
  -n <BACKEND_APP> -g <RESOURCE_GROUP> `
  --environment <ENV_NAME> `
  --image <ACR_NAME>.azurecr.io/backend:<VERSION> `
  --target-port 8000 --ingress external `
  --registry-server <ACR_NAME>.azurecr.io `
  --registry-username <ACR_NAME> `
  --registry-password $acrPassword `
  --min-replicas 1 `
  --env-vars DATABASE_URL="<DB_CONNECTION_STRING>" SECRET_KEY="<SECRET>"

# Example
az containerapp create `
  -n poc-backend -g rg-dummy-webapp `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/backend:v1 `
  --target-port 8000 --ingress external `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword `
  --min-replicas 1 `
  --env-vars DATABASE_URL="<YOUR_DB_URL>" SECRET_KEY="<YOUR_SECRET>"
```

---

## Step 5: Deploy Frontend

```powershell
# Placeholder
az containerapp create `
  -n <FRONTEND_APP> -g <RESOURCE_GROUP> `
  --environment <ENV_NAME> `
  --image <ACR_NAME>.azurecr.io/frontend:<VERSION> `
  --target-port 80 --ingress external `
  --registry-server <ACR_NAME>.azurecr.io `
  --registry-username <ACR_NAME> `
  --registry-password $acrPassword

# Example
az containerapp create `
  -n poc-frontend -g rg-dummy-webapp `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/frontend:v1 `
  --target-port 80 --ingress external `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword
```

---

## Step 6: Security Configuration

### Layer 1: CORS (Azure Portal)

Navigate to: **Backend App** → Networking → CORS

| Setting         | Value                           |
| --------------- | ------------------------------- |
| Allowed Origins | `https://<frontend-url>`        |
| Credentials     | ✅                              |
| Methods         | GET, POST, PUT, DELETE, OPTIONS |
| Headers         | \*                              |

### Layer 2: API Key

1. Add secret to backend:

```powershell
# Placeholder
az containerapp secret set -n <BACKEND_APP> -g <RESOURCE_GROUP> --secrets api-key="<YOUR_API_KEY>"
az containerapp update -n <BACKEND_APP> -g <RESOURCE_GROUP> --set-env-vars API_KEY=secretref:api-key

# Example
az containerapp secret set -n poc-backend -g rg-dummy-webapp --secrets api-key="poc-webapp-secure-api-key-2026"
az containerapp update -n poc-backend -g rg-dummy-webapp --set-env-vars API_KEY=secretref:api-key
```

2. Backend validates `X-API-KEY` header on `/api/` routes
3. Nginx injects header on proxy requests

### Layer 3: IP Restrictions

```powershell
# Placeholder
az containerapp show -n <FRONTEND_APP> -g <RESOURCE_GROUP> --query "properties.outboundIpAddresses" -o tsv

# Example
az containerapp show -n poc-frontend -g rg-dummy-webapp --query "properties.outboundIpAddresses" -o tsv
```

**Azure Portal**: Backend → Ingress → IP Restrictions → Add each IP as allow rule

---

## Step 7: Verify Deployment

### Get App URLs

```powershell
# Placeholder
az containerapp show -n <APP_NAME> -g <RESOURCE_GROUP> --query "properties.configuration.ingress.fqdn" -o tsv

# Example (Frontend)
az containerapp show -n poc-frontend -g rg-dummy-webapp --query "properties.configuration.ingress.fqdn" -o tsv

# Example (Backend)
az containerapp show -n poc-backend -g rg-dummy-webapp --query "properties.configuration.ingress.fqdn" -o tsv
```

---

## Updating the Application

```powershell
# Placeholder
docker build -t <ACR_NAME>.azurecr.io/<APP>:<NEW_VERSION> ./<APP>
docker push <ACR_NAME>.azurecr.io/<APP>:<NEW_VERSION>
az containerapp update -n <APP_NAME> -g <RESOURCE_GROUP> --image <ACR_NAME>.azurecr.io/<APP>:<NEW_VERSION>

# Example (Backend)
docker build -t pocwebappacr.azurecr.io/backend:v2 ./backend
docker push pocwebappacr.azurecr.io/backend:v2
az containerapp update -n poc-backend -g rg-dummy-webapp --image pocwebappacr.azurecr.io/backend:v2
```

---

## Troubleshooting

### View Logs

```powershell
# Placeholder
az containerapp logs show -n <APP_NAME> -g <RESOURCE_GROUP> --tail 50

# Example
az containerapp logs show -n poc-backend -g rg-dummy-webapp --tail 50
```

### Check Status

```powershell
# Placeholder
az containerapp revision list -n <APP_NAME> -g <RESOURCE_GROUP> -o table

# Example
az containerapp revision list -n poc-backend -g rg-dummy-webapp -o table
```

---

## Summary

| Layer           | Protection        | Configuration              |
| --------------- | ----------------- | -------------------------- |
| CORS            | Browser-level     | Azure Portal               |
| API Key         | Application-level | Backend middleware + nginx |
| IP Restrictions | Network-level     | Azure Portal ingress rules |
