from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, users, config
from app.models.database import engine, Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="POC Web App API",
    description="Backend API for the React frontend",
    version="1.0.0"
)

# API Key for service-to-service authentication
# In production, use Azure Key Vault or environment secrets
API_KEY = os.environ.get("API_KEY", "")

@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    """Validate API key for all /api/ routes except health check and OPTIONS"""
    path = request.url.path
    
    # Skip validation for:
    # - Non-API routes (static files, etc.)
    # - Health check endpoint (for Azure monitoring)
    # - OPTIONS requests (CORS preflight)
    # - When API_KEY is not configured (local development)
    if (
        not path.startswith("/api/") or
        path == "/api/health" or
        request.method == "OPTIONS" or
        not API_KEY
    ):
        return await call_next(request)
    
    # Validate the API key
    provided_key = request.headers.get("X-API-KEY")
    if provided_key != API_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"}
        )
    
    return await call_next(request)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://poc-frontend.redwater-9e6b81c0.centralindia.azurecontainerapps.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}
