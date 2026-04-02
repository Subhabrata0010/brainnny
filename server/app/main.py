"""
Second Brain - Main FastAPI application.
Multi-layer memory engine for LLM chat users.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.snowflake_conn import close_connection, get_snowflake_connection
from app.core.rate_limit import limiter
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

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
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
    logger.info(f"Starting {settings.APP_NAME} v2.0.0...")
    
    # Validate environment variables
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER", 
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
    
    missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        raise RuntimeError(f"Missing required configuration: {', '.join(missing_vars)}")
    
    # Test Snowflake connection
    try:
        conn = get_snowflake_connection()
        logger.info("✓ Snowflake connection established successfully")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Snowflake: {e}")
        raise RuntimeError(f"Snowflake connection failed: {e}")
    
    logger.info(f"✓ {settings.APP_NAME} started successfully")
    logger.info(f"  CORS Origins: {settings.cors_origins_list}")
    logger.info(f"  Debug Mode: {settings.DEBUG}")
    logger.info(f"  Rate Limit: {settings.RATE_LIMIT_PER_MINUTE}/min, {settings.RATE_LIMIT_PER_HOUR}/hr")


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
    """
    Health check endpoint with dependency validation.
    Returns service status and dependency health.
    """
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "2.0.0",
        "dependencies": {}
    }
    
    # Check Snowflake connectivity
    try:
        conn = get_snowflake_connection()
        if conn and not conn.is_closed():
            health_status["dependencies"]["snowflake"] = "connected"
        else:
            health_status["dependencies"]["snowflake"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Snowflake health check failed: {e}")
        health_status["dependencies"]["snowflake"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


# For AWS Lambda deployment with Mangum
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # Mangum not installed for local development
    handler = None