from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from database.models import Memory, MemoryRetrievalLog
from embeddings.embedding_service import embedding_service
from embeddings.vector_store import vector_store
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MemoryRetrieval:
    def __init__(self, db: Session):
        self.db = db
    
    def retrieve_memories(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Memory]:
        """Retrieve relevant memories based on query."""
        try:
            query_embedding = embedding_service.embed_text(query)
            
            vector_results = vector_store.search(query_embedding, top_k=top_k * 2)
            
            memories = []
            for memory_id, similarity_score in vector_results:
                memory = self.db.query(Memory).filter(
                    Memory.id == memory_id,
                    Memory.user_id == user_id,
                    Memory.is_active == True
                ).first()
                
                if memory and similarity_score >= similarity_threshold:
                    memory.semantic_similarity = similarity_score
                    memories.append(memory)
            
            self._log_retrieval(user_id, query, [m.id for m in memories], [m.semantic_similarity for m in memories])
            
            logger.info(f"Retrieved {len(memories)} memories for user {user_id}")
            return memories[:top_k]
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []
    
    def retrieve_memories_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 10
    ) -> List[Memory]:
        """Retrieve memories by category."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.category == category,
                Memory.is_active == True
            ).order_by(Memory.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving memories by category: {e}")
            return []
    
    def retrieve_recent_memories(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Memory]:
        """Retrieve recent memories."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.is_active == True
            ).order_by(Memory.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving recent memories: {e}")
            return []
    
    def retrieve_important_memories(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Memory]:
        """Retrieve important memories."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.is_active == True
            ).order_by(Memory.importance_score.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving important memories: {e}")
            return []
    
    def retrieve_frequently_accessed(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Memory]:
        """Retrieve frequently accessed memories."""
        try:
            return self.db.query(Memory).filter(
                Memory.user_id == user_id,
                Memory.is_active == True
            ).order_by(Memory.access_count.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error retrieving frequently accessed memories: {e}")
            return []
    
    def _log_retrieval(self, user_id: str, query: str, memory_ids: List[str], scores: List[float]):
        """Log memory retrieval for analytics."""
        try:
            log = MemoryRetrievalLog(
                user_id=user_id,
                query=query,
                retrieved_memory_ids=memory_ids,
                scores=scores
            )
            self.db.add(log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging retrieval: {e}")
