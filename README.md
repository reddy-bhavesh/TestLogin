# POC Web Application

React + Python web app with PostgreSQL database for Azure deployment.

## Quick Start

```bash
# Start all services (PostgreSQL + Backend + Frontend)
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
```

### PostgreSQL Credentials (Local Dev)

| Setting  | Value         |
| -------- | ------------- |
| Database | `poc_webapp`  |
| User     | `pocuser`     |
| Password | `pocpassword` |
| Port     | `5432`        |

### First User = Admin

The first user to register automatically becomes an admin.

## Pages

| Page    | Path      | Description                 |
| ------- | --------- | --------------------------- |
| Login   | `/login`  | Login/Register              |
| Profile | `/forms`  | Edit user profile           |
| Config  | `/config` | Admin settings (admin only) |

## Audit Logging

### Backend (Python)

- JSON-formatted logs to stdout using `python-json-logger`
- Azure Container Apps captures these automatically to Log Analytics
- Logs include: `Admin_User`, `Action`, `Target_Tenant`, `Target_User`

### Frontend (React)

- Application Insights SDK for browser events
- Set `VITE_APP_INSIGHTS_CONNECTION_STRING` env var to enable

### KQL Query for Azure Log Analytics

```kql
ContainerAppConsoleLogs_CL
| extend d = parse_json(Log_s)
| project Time = TimeGenerated,
    Admin = tostring(d.Admin_User),
    Action = tostring(d.Action),
    Target = tostring(d.Target_User)
| where isnotempty(Admin)
| order by Time desc
```

## Azure Deployment

```bash
# 1. Create resources
az group create -n poc-webapp-rg -l centralindia
az acr create -n pocwebappacr -g poc-webapp-rg --sku Basic

# 2. Create Azure PostgreSQL
az postgres flexible-server create \
  -n poc-webapp-postgres -g poc-webapp-rg -l centralindia \
  --admin-user pocadmin --admin-password YourSecurePassword123! \
  --sku-name Standard_B1ms --tier Burstable

# 3. Build & push images
az acr login -n pocwebappacr
docker build -t pocwebappacr.azurecr.io/backend:v1 ./backend
docker build -t pocwebappacr.azurecr.io/frontend:v1 ./frontend
docker push pocwebappacr.azurecr.io/backend:v1
docker push pocwebappacr.azurecr.io/frontend:v1

# 4. Deploy to Container Apps (logs auto-route to Log Analytics)
az containerapp env create -n poc-env -g poc-webapp-rg -l centralindia
az containerapp create -n poc-backend -g poc-webapp-rg --environment poc-env \
  --image pocwebappacr.azurecr.io/backend:v1 --target-port 8000 --ingress internal \
  --env-vars DATABASE_URL="postgresql://pocadmin:YourSecurePassword123!@poc-webapp-postgres.postgres.database.azure.com:5432/poc_webapp"
az containerapp create -n poc-frontend -g poc-webapp-rg --environment poc-env \
  --image pocwebappacr.azurecr.io/frontend:v1 --target-port 80 --ingress external
```

## Tech Stack

- **Frontend**: React 18 + Vite + Application Insights
- **Backend**: Python FastAPI + JSON Logging
- **Database**: PostgreSQL 16
- **Auth**: JWT tokens
- **Logging**: Azure Log Analytics (immutable audit trail)
