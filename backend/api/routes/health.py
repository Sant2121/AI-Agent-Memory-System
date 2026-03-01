from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.schemas import HealthResponse
from database.connection import get_db
from embeddings.vector_store import vector_store
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Check system health and component status.
    """
    try:
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_status = "unhealthy"
        
        vector_store_status = "healthy"
        try:
            vector_store_size = vector_store.get_size()
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            vector_store_status = "unhealthy"
            vector_store_size = 0
        
        return HealthResponse(
            status="healthy" if db_status == "healthy" and vector_store_status == "healthy" else "degraded",
            components={
                "database": db_status,
                "vector_store": vector_store_status,
                "vector_store_size": vector_store_size
            },
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": str(e)},
            timestamp=datetime.utcnow()
        )
