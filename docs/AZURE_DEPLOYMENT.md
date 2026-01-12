# Azure Deployment Guide

Deploy the POC Web App to Azure Container Apps with your existing PostgreSQL database.

---

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- Docker Desktop (optional - only needed for local builds, see Step 2 Option A)
- Your existing PostgreSQL connection string

---

## Option A: Use Existing PostgreSQL Database

If you already have an Azure PostgreSQL Flexible Server, you just need the connection string:

```
postgresql://<username>:<password>@<server-name>.postgres.database.azure.com:5432/<database-name>?sslmode=require
```

**Example:**

```
postgresql://pocadmin:YourPassword123!@mycompany-postgres.postgres.database.azure.com:5432/poc_webapp?sslmode=require
```

> **Note:** Azure PostgreSQL requires SSL. Add `?sslmode=require` to your connection string.

---

## Option B: Create New PostgreSQL (Skip if using existing)

```powershell
# Create resource group (skip if exists)
az group create -n poc-webapp-rg -l centralindia

# Create PostgreSQL Flexible Server
az postgres flexible-server create `
  -n poc-webapp-postgres `
  -g poc-webapp-rg `
  -l centralindia `
  --admin-user pocadmin `
  --admin-password YourSecurePassword123! `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --public-access 0.0.0.0

# Create the database
az postgres flexible-server db create `
  -g poc-webapp-rg `
  -s poc-webapp-postgres `
  -d poc_webapp
```

---

## Step 1: Create Azure Container Registry

```powershell
# Create resource group (skip if exists)
az group create -n poc-webapp-rg -l centralindia

# Create container registry
az acr create -n pocwebappacr -g poc-webapp-rg --sku Basic

# Enable admin access (needed for Container Apps)
az acr update -n pocwebappacr --admin-enabled true
```

---

## Step 2: Build and Push Docker Images

### Option A: Build Locally (requires Docker)

```powershell
# Login to your registry
az acr login -n pocwebappacr

# Build and push backend
docker build -t pocwebappacr.azurecr.io/backend:v1 ./backend
docker push pocwebappacr.azurecr.io/backend:v1

# Build and push frontend (with Azure target)
docker build --build-arg DEPLOY_TARGET=azure -t pocwebappacr.azurecr.io/frontend:v1 ./frontend
docker push pocwebappacr.azurecr.io/frontend:v1
```

### Option B: Build in Azure Cloud (no Docker required)

If you don't have Docker installed, Azure can build the images directly in the cloud:

```powershell
# Build backend in Azure (uploads source, builds in cloud, pushes to ACR)
az acr build --registry pocwebappacr --image backend:v1 ./backend

# Build frontend in Azure (with Azure target)
az acr build --registry pocwebappacr --image frontend:v1 --build-arg DEPLOY_TARGET=azure ./frontend
```

> **Note:** This uploads your source code to Azure, builds it there, and stores in ACR - all without local Docker.

---

## Step 3: Create Container Apps Environment

```powershell
# Create the environment
az containerapp env create `
  -n poc-env `
  -g poc-webapp-rg `
  -l centralindia
```

---

## Step 4: Deploy Backend

Replace `<YOUR_DATABASE_URL>` with your actual connection string:

```powershell
# Get ACR credentials
$acrPassword = az acr credential show -n pocwebappacr --query "passwords[0].value" -o tsv

# Deploy backend
az containerapp create `
  -n poc-backend `
  -g poc-webapp-rg `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/backend:v1 `
  --target-port 8000 `
  --ingress internal `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword `
  --env-vars DATABASE_URL="<YOUR_DATABASE_URL>" SECRET_KEY="your-production-secret-key"
```

**Example with existing database:**

```powershell
az containerapp create `
  -n poc-backend `
  -g poc-webapp-rg `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/backend:v1 `
  --target-port 8000 `
  --ingress internal `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword `
  --env-vars DATABASE_URL="postgresql://pocadmin:MyPassword@myserver.postgres.database.azure.com:5432/poc_webapp?sslmode=require" SECRET_KEY="change-this-in-production"
```

---

## Step 5: Deploy Frontend

```powershell
# Get backend URL
$backendUrl = az containerapp show -n poc-backend -g poc-webapp-rg --query "properties.configuration.ingress.fqdn" -o tsv

# Deploy frontend
az containerapp create `
  -n poc-frontend `
  -g poc-webapp-rg `
  --environment poc-env `
  --image pocwebappacr.azurecr.io/frontend:v1 `
  --target-port 80 `
  --ingress external `
  --registry-server pocwebappacr.azurecr.io `
  --registry-username pocwebappacr `
  --registry-password $acrPassword
```

---

## Step 6: Get Your App URL

```powershell
az containerapp show -n poc-frontend -g poc-webapp-rg --query "properties.configuration.ingress.fqdn" -o tsv
```

Your app will be available at: `https://poc-frontend.<random>.centralindia.azurecontainerapps.io`

---

## Firewall: Allow Container Apps to Access PostgreSQL

If using Azure PostgreSQL, you need to allow access from Container Apps:

```powershell
# Allow Azure services
az postgres flexible-server firewall-rule create `
  -g poc-webapp-rg `
  -n poc-webapp-postgres `
  -r AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0
```

---

## Troubleshooting

### Check backend logs

```powershell
az containerapp logs show -n poc-backend -g poc-webapp-rg --follow
```

### Check if database is reachable

If you get connection errors, verify:

1. Firewall rules allow Azure services
2. SSL mode is set in connection string
3. Database name exists

### Update environment variables

```powershell
az containerapp update -n poc-backend -g poc-webapp-rg `
  --set-env-vars DATABASE_URL="new-connection-string"
```
