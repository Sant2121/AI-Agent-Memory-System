from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Memory, User
from embeddings.embedding_service import embedding_service
from embeddings.vector_store import vector_store
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self, db: Session):
        self.db = db
    
    def store_memory(
        self,
        user_id: str,
        memory_text: str,
        category: str = "general",
        importance_score: float = 0.5,
        tags: List[str] = None
    ) -> Memory:
        """Store a new memory with embedding."""
        try:
            embedding = embedding_service.embed_text(memory_text)
            
            memory = Memory(
                user_id=user_id,
                memory_text=memory_text,
                embedding=embedding,
                importance_score=importance_score,
                category=category,
                tags=tags or []
            )
            
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
            vector_store.add(memory.id, embedding)
            
            logger.info(f"Stored memory {memory.id} for user {user_id}")
            return memory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing memory: {e}")
            raise
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a specific memory."""
        try:
            return self.db.query(Memory).filter(Memory.id == memory_id).first()
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return None
    
    def get_user_memories(self, user_id: str, limit: int = 100) -> List[Memory]:
        """Get all memories for a user."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.is_active == True
            ).order_by(Memory.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving user memories: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Soft delete a memory."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.is_active = False
                self.db.commit()
                vector_store.delete(memory_id)
                logger.info(f"Deleted memory {memory_id}")
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting memory: {e}")
            return False
    
    def update_memory(
        self,
        memory_id: str,
        memory_text: Optional[str] = None,
        importance_score: Optional[float] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Memory]:
        """Update a memory."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return None
            
            if memory_text:
                memory.memory_text = memory_text
                memory.embedding = embedding_service.embed_text(memory_text)
                vector_store.delete(memory_id)
                vector_store.add(memory_id, memory.embedding)
            
            if importance_score is not None:
                memory.importance_score = importance_score
            
            if category:
                memory.category = category
            
            if tags is not None:
                memory.tags = tags
            
            memory.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(memory)
            
            logger.info(f"Updated memory {memory_id}")
            return memory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating memory: {e}")
            return None
    
    def get_memories_by_category(self, user_id: str, category: str) -> List[Memory]:
        """Get memories by category."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.category == category,
                Memory.is_active == True
            ).order_by(Memory.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error retrieving memories by category: {e}")
            return []
    
    def increment_access_count(self, memory_id: str):
        """Increment access count and update last accessed time."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.access_count += 1
                memory.last_accessed = datetime.utcnow()
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating access count: {e}")
