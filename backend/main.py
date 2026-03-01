from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from config import settings
from database.connection import init_db
from api.routes import chat, memories, health

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agent Memory System",
    description="Persistent memory architecture for AI assistants",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

app.include_router(chat.router)
app.include_router(memories.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully")
        logger.info("AI Agent Memory System started")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Agent Memory System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
