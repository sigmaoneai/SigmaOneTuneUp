from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import text

from api.routes import agents, phone_numbers, calls, syncro, dashboard, prompts, retellai, eval_tests, onboarding, knowledge_base
from api.database import engine, Base
from api.middleware.logging import LoggingMiddleware

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting SigmaOne TuneUp Backend...")
    
    # Test database connection (don't create tables - use existing schema)
    try:
        async with engine.begin() as conn:
            # Simple connection test
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful - using existing schema")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SigmaOne TuneUp Backend...")

# Create FastAPI app
app = FastAPI(
    title="SigmaOne TuneUp API",
    description="Backend API for RetellAI and SyncroMSP integration with enhanced observability",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(phone_numbers.router, prefix="/api/v1/phone-numbers", tags=["phone-numbers"])
app.include_router(calls.router, prefix="/api/v1/calls", tags=["calls"])
app.include_router(syncro.router, prefix="/api/v1/syncro", tags=["syncro"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["prompts"])
app.include_router(retellai.router, prefix="/api/v1/retellai", tags=["retellai"])
app.include_router(eval_tests.router, prefix="/api/v1/eval-tests", tags=["eval-tests"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge-base", tags=["knowledge-base"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SigmaOne TuneUp API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    ) 