import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from embeddings.embedding_service import EmbeddingService
from embeddings.vector_store import VectorStore
import tempfile
import os


class TestEmbeddingService:
    @pytest.fixture
    def embedding_service(self):
        return EmbeddingService()
    
    def test_embed_text(self, embedding_service):
        text = "User is building an AI media authenticity platform"
        embedding = embedding_service.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embed_texts(self, embedding_service):
        texts = [
            "User prefers Python",
            "User works with FastAPI",
            "User is interested in AI"
        ]
        embeddings = embedding_service.embed_texts(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)
    
    def test_similarity(self, embedding_service):
        text1 = "The user is building an AI platform"
        text2 = "The user is developing an AI system"
        text3 = "The weather is sunny today"
        
        emb1 = embedding_service.embed_text(text1)
        emb2 = embedding_service.embed_text(text2)
        emb3 = embedding_service.embed_text(text3)
        
        sim_12 = embedding_service.similarity(emb1, emb2)
        sim_13 = embedding_service.similarity(emb1, emb3)
        
        assert 0 <= sim_12 <= 1
        assert 0 <= sim_13 <= 1
        assert sim_12 > sim_13
    
    def test_batch_similarity(self, embedding_service):
        query = "AI platform"
        candidates = [
            "Building an AI system",
            "Machine learning platform",
            "The weather today"
        ]
        
        query_emb = embedding_service.embed_text(query)
        candidate_embs = embedding_service.embed_texts(candidates)
        
        similarities = embedding_service.batch_similarity(query_emb, candidate_embs)
        
        assert len(similarities) == 3
        assert all(0 <= s <= 1 for s in similarities)


class TestVectorStore:
    @pytest.fixture
    def vector_store(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = VectorStore(dimension=384, index_path=tmpdir)
            yield store
    
    def test_add_vector(self, vector_store):
        embedding = [0.1] * 384
        memory_id = "mem_123"
        
        internal_id = vector_store.add(memory_id, embedding)
        
        assert internal_id == 0
        assert vector_store.get_size() == 1
    
    def test_search_vectors(self, vector_store):
        embeddings = {
            "mem_1": [0.1] * 384,
            "mem_2": [0.1] * 384,
            "mem_3": [0.9] * 384,
        }
        
        for mem_id, emb in embeddings.items():
            vector_store.add(mem_id, emb)
        
        query = [0.1] * 384
        results = vector_store.search(query, top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)
    
    def test_delete_vector(self, vector_store):
        memory_id = "mem_123"
        embedding = [0.1] * 384
        
        vector_store.add(memory_id, embedding)
        assert vector_store.get_size() == 1
        
        vector_store.delete(memory_id)
        assert vector_store.get_size() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
