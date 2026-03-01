from typing import List, Tuple
from database.models import Memory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MemoryRanking:
    def __init__(
        self,
        semantic_weight: float = 0.5,
        recency_weight: float = 0.2,
        importance_weight: float = 0.3
    ):
        self.semantic_weight = semantic_weight
        self.recency_weight = recency_weight
        self.importance_weight = importance_weight
    
    def rank_memories(self, memories: List[Memory]) -> List[Tuple[Memory, float]]:
        """Rank memories based on multiple factors."""
        try:
            ranked = []
            for memory in memories:
                score = self._calculate_score(memory)
                ranked.append((memory, score))
            
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked
        except Exception as e:
            logger.error(f"Error ranking memories: {e}")
            return [(m, 0.0) for m in memories]
    
    def _calculate_score(self, memory: Memory) -> float:
        """Calculate composite score for a memory."""
        semantic_score = self._semantic_score(memory)
        recency_score = self._recency_score(memory)
        importance_score = self._importance_score(memory)
        
        composite_score = (
            self.semantic_weight * semantic_score +
            self.recency_weight * recency_score +
            self.importance_weight * importance_score
        )
        
        return composite_score
    
    def _semantic_score(self, memory: Memory) -> float:
        """Get semantic similarity score (0-1)."""
        return getattr(memory, 'semantic_similarity', 0.5)
    
    def _recency_score(self, memory: Memory) -> float:
        """Calculate recency score based on age."""
        try:
            now = datetime.utcnow()
            age_days = (now - memory.created_at).days
            
            if age_days == 0:
                return 1.0
            elif age_days <= 7:
                return 0.9
            elif age_days <= 30:
                return 0.7
            elif age_days <= 90:
                return 0.5
            else:
                return 0.3
        except Exception as e:
            logger.error(f"Error calculating recency score: {e}")
            return 0.5
    
    def _importance_score(self, memory: Memory) -> float:
        """Get importance score (0-1)."""
        return min(max(memory.importance_score, 0.0), 1.0)
    
    def update_weights(
        self,
        semantic_weight: float = None,
        recency_weight: float = None,
        importance_weight: float = None
    ):
        """Update ranking weights."""
        if semantic_weight is not None:
            self.semantic_weight = semantic_weight
        if recency_weight is not None:
            self.recency_weight = recency_weight
        if importance_weight is not None:
            self.importance_weight = importance_weight
        
        total = self.semantic_weight + self.recency_weight + self.importance_weight
        if total > 0:
            self.semantic_weight /= total
            self.recency_weight /= total
            self.importance_weight /= total
