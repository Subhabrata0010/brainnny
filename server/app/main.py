"""
Second Brain - Main FastAPI application.
Multi-layer memory engine for LLM chat users.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.snowflake_conn import close_connection
from app.routers import conversation, context, user

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-layer memory engine - stores and retrieves context only",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router)
app.include_router(conversation.router)
app.include_router(context.router)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    logger.info(f"Starting {settings.APP_NAME}...")
    logger.info("Snowflake connection will be established on first use")


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown."""
    logger.info("Shutting down...")
    close_connection()


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": "2.0.0",
        "architecture": "Multi-Layer Memory",
        "layers": ["working_memory", "episodic_memory", "semantic_memory", "conversation_logs"],
        "endpoints": {
            "user": "POST /user/{user_id} - Create or get user profile",
            "store": "POST /conversation - Store conversation messages",
            "retrieve": "POST /retrieve-context - Retrieve memory context",
            "health": "GET /health",
            "docs": "/docs"
        },
        "note": "System stores and retrieves memory only. Does NOT generate AI responses."
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


# For AWS Lambda deployment with Mangum
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # Mangum not installed for local development
    handler = None