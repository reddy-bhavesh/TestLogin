# POC Web Application

React + Python web app with MySQL database for Azure deployment.

## Quick Start

```bash
# Start all services (MySQL + Backend + Frontend)
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - MySQL: localhost:3306
```

### MySQL Credentials (Local Dev)

| Setting  | Value         |
| -------- | ------------- |
| Database | `poc_webapp`  |
| User     | `pocuser`     |
| Password | `pocpassword` |

### First User = Admin

The first user to register automatically becomes an admin.

## Pages

| Page    | Path      | Description                 |
| ------- | --------- | --------------------------- |
| Login   | `/login`  | Login/Register              |
| Profile | `/forms`  | Edit user profile           |
| Config  | `/config` | Admin settings (admin only) |

## Azure Deployment

```bash
# 1. Create resources
az group create -n poc-webapp-rg -l centralindia
az acr create -n pocwebappacr -g poc-webapp-rg --sku Basic

# 2. Create Azure MySQL
az mysql flexible-server create \
  -n poc-webapp-mysql -g poc-webapp-rg -l centralindia \
  --admin-user pocadmin --admin-password YourSecurePassword123!

# 3. Build & push images
az acr login -n pocwebappacr
docker build -t pocwebappacr.azurecr.io/backend:v1 ./backend
docker build -t pocwebappacr.azurecr.io/frontend:v1 ./frontend
docker push pocwebappacr.azurecr.io/backend:v1
docker push pocwebappacr.azurecr.io/frontend:v1

# 4. Deploy to Container Apps
az containerapp env create -n poc-env -g poc-webapp-rg -l centralindia
az containerapp create -n poc-backend -g poc-webapp-rg --environment poc-env \
  --image pocwebappacr.azurecr.io/backend:v1 --target-port 8000 --ingress internal \
  --env-vars DATABASE_URL="mysql+pymysql://pocadmin:YourSecurePassword123!@poc-webapp-mysql.mysql.database.azure.com:3306/poc_webapp"
az containerapp create -n poc-frontend -g poc-webapp-rg --environment poc-env \
  --image pocwebappacr.azurecr.io/frontend:v1 --target-port 80 --ingress external
```

## Tech Stack

- **Frontend**: React 18 + Vite
- **Backend**: Python FastAPI
- **Database**: MySQL 8.0
- **Auth**: JWT tokens
