from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Initialized EmbeddingService with model: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding vector."""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embedding vectors."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding texts: {e}")
            raise
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            similarity = max(0.0, min(1.0, similarity))
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def batch_similarity(self, query_embedding: List[float], embeddings: List[List[float]]) -> List[float]:
        """Calculate similarity between query and multiple embeddings."""
        try:
            query_vec = np.array(query_embedding)
            embeddings_array = np.array(embeddings)
            
            query_norm = np.linalg.norm(query_vec)
            if query_norm == 0:
                return [0.0] * len(embeddings)
            
            norms = np.linalg.norm(embeddings_array, axis=1)
            similarities = np.dot(embeddings_array, query_vec) / (norms * query_norm + 1e-8)
            
            return similarities.tolist()
        except Exception as e:
            logger.error(f"Error in batch similarity: {e}")
            return [0.0] * len(embeddings)


embedding_service = EmbeddingService()
