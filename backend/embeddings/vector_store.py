from typing import List, Tuple, Optional
import faiss
import numpy as np
import os
import json
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "./data/vector_store"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.id_map = {}
        self.reverse_id_map = {}
        self.counter = 0
        
        os.makedirs(index_path, exist_ok=True)
        self.index_file = os.path.join(index_path, "faiss.index")
        self.id_map_file = os.path.join(index_path, "id_map.json")
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        try:
            if os.path.exists(self.index_file):
                self.index = faiss.read_index(self.index_file)
                with open(self.id_map_file, 'r') as f:
                    data = json.load(f)
                    self.id_map = {int(k): v for k, v in data['id_map'].items()}
                    self.reverse_id_map = {v: int(k) for k, v in data['id_map'].items()}
                    self.counter = data['counter']
                logger.info(f"Loaded existing FAISS index with {len(self.id_map)} vectors")
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
        except Exception as e:
            logger.error(f"Error loading/creating index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
    
    def add(self, memory_id: str, embedding: List[float]) -> int:
        """Add embedding to vector store."""
        try:
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)
            
            internal_id = self.counter
            self.id_map[internal_id] = memory_id
            self.reverse_id_map[memory_id] = internal_id
            self.counter += 1
            
            self._save_index()
            return internal_id
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            raise
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar vectors."""
        try:
            query_vector = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))
            
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx in self.id_map:
                    memory_id = self.id_map[idx]
                    similarity = 1 / (1 + distance)
                    results.append((memory_id, float(similarity)))
            
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete(self, memory_id: str):
        """Delete embedding from vector store."""
        try:
            if memory_id in self.reverse_id_map:
                internal_id = self.reverse_id_map[memory_id]
                del self.id_map[internal_id]
                del self.reverse_id_map[memory_id]
                self._save_index()
                logger.info(f"Deleted memory {memory_id} from vector store")
        except Exception as e:
            logger.error(f"Error deleting from vector store: {e}")
    
    def _save_index(self):
        """Save index to disk."""
        try:
            faiss.write_index(self.index, self.index_file)
            with open(self.id_map_file, 'w') as f:
                json.dump({
                    'id_map': {str(k): v for k, v in self.id_map.items()},
                    'counter': self.counter
                }, f)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def get_size(self) -> int:
        """Get number of vectors in store."""
        return self.index.ntotal if self.index else 0


vector_store = VectorStore()
