from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.schemas import MemoryCreate, MemoryUpdate, MemoryResponse, MemoriesListResponse
from database.connection import get_db
from database.models import Memory
from memory_engine.memory_store import MemoryStore
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["memories"])


@router.get("/memories", response_model=MemoriesListResponse)
async def get_memories(
    user_id: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve all memories for a user.
    """
    try:
        query = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        )
        
        if category:
            query = query.filter(Memory.category == category)
        
        memories = query.order_by(Memory.created_at.desc()).limit(limit).all()
        
        return MemoriesListResponse(
            memories=[MemoryResponse.from_orm(m) for m in memories],
            total=len(memories)
        )
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific memory by ID.
    """
    try:
        memory = db.query(Memory).filter(
            Memory.id == memory_id,
            Memory.is_active == True
        ).first()
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return MemoryResponse.from_orm(memory)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memories", response_model=MemoryResponse)
async def create_memory(
    user_id: str = Query(...),
    memory: MemoryCreate = None,
    db: Session = Depends(get_db)
):
    """
    Create a new memory.
    """
    try:
        memory_store = MemoryStore(db)
        stored_memory = memory_store.store_memory(
            user_id=user_id,
            memory_text=memory.memory_text,
            category=memory.category,
            importance_score=memory.importance_score,
            tags=memory.tags
        )
        return MemoryResponse.from_orm(stored_memory)
    except Exception as e:
        logger.error(f"Error creating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing memory.
    """
    try:
        memory_store = MemoryStore(db)
        updated_memory = memory_store.update_memory(
            memory_id=memory_id,
            memory_text=memory_update.memory_text,
            importance_score=memory_update.importance_score,
            category=memory_update.category,
            tags=memory_update.tags
        )
        
        if not updated_memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return MemoryResponse.from_orm(updated_memory)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str, db: Session = Depends(get_db)):
    """
    Delete a memory.
    """
    try:
        memory_store = MemoryStore(db)
        success = memory_store.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return {"success": True, "message": "Memory deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/stats/{user_id}")
async def get_memory_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Get memory statistics for a user.
    """
    try:
        total_memories = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).count()
        
        categories = db.query(Memory.category).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).distinct().all()
        
        avg_importance = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).with_entities(db.func.avg(Memory.importance_score)).scalar()
        
        return {
            "total_memories": total_memories,
            "categories": [c[0] for c in categories],
            "average_importance": float(avg_importance) if avg_importance else 0.0
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
