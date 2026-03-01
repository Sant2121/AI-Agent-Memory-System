import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from database.models import Base, User, Memory
from database.connection import SessionLocal
from memory_engine.memory_store import MemoryStore
from memory_engine.memory_retrieval import MemoryRetrieval
from memory_engine.memory_ranking import MemoryRanking


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(test_db):
    user = User(id="test_user_1", username="testuser", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    return user


class TestMemoryStore:
    def test_store_memory(self, test_db, test_user):
        store = MemoryStore(test_db)
        
        memory = store.store_memory(
            user_id=test_user.id,
            memory_text="User is building an AI platform",
            category="project",
            importance_score=0.8
        )
        
        assert memory.id is not None
        assert memory.user_id == test_user.id
        assert memory.memory_text == "User is building an AI platform"
        assert memory.category == "project"
        assert memory.importance_score == 0.8
        assert memory.embedding is not None
    
    def test_get_memory(self, test_db, test_user):
        store = MemoryStore(test_db)
        
        stored = store.store_memory(
            user_id=test_user.id,
            memory_text="Test memory",
            category="general"
        )
        
        retrieved = store.get_memory(stored.id)
        assert retrieved is not None
        assert retrieved.memory_text == "Test memory"
    
    def test_get_user_memories(self, test_db, test_user):
        store = MemoryStore(test_db)
        
        for i in range(3):
            store.store_memory(
                user_id=test_user.id,
                memory_text=f"Memory {i}",
                category="general"
            )
        
        memories = store.get_user_memories(test_user.id)
        assert len(memories) == 3
    
    def test_delete_memory(self, test_db, test_user):
        store = MemoryStore(test_db)
        
        memory = store.store_memory(
            user_id=test_user.id,
            memory_text="To be deleted",
            category="general"
        )
        
        success = store.delete_memory(memory.id)
        assert success is True
        
        deleted = test_db.query(Memory).filter(Memory.id == memory.id).first()
        assert deleted.is_active is False
    
    def test_update_memory(self, test_db, test_user):
        store = MemoryStore(test_db)
        
        memory = store.store_memory(
            user_id=test_user.id,
            memory_text="Original text",
            importance_score=0.5
        )
        
        updated = store.update_memory(
            memory_id=memory.id,
            memory_text="Updated text",
            importance_score=0.9
        )
        
        assert updated.memory_text == "Updated text"
        assert updated.importance_score == 0.9


class TestMemoryRetrieval:
    def test_retrieve_memories(self, test_db, test_user):
        store = MemoryStore(test_db)
        retrieval = MemoryRetrieval(test_db)
        
        store.store_memory(
            user_id=test_user.id,
            memory_text="User is building an AI platform",
            category="project"
        )
        store.store_memory(
            user_id=test_user.id,
            memory_text="User prefers Python",
            category="preference"
        )
        
        results = retrieval.retrieve_memories(
            user_id=test_user.id,
            query="AI platform",
            top_k=5
        )
        
        assert len(results) > 0
        assert all(m.user_id == test_user.id for m in results)
    
    def test_retrieve_by_category(self, test_db, test_user):
        store = MemoryStore(test_db)
        retrieval = MemoryRetrieval(test_db)
        
        store.store_memory(
            user_id=test_user.id,
            memory_text="Project info",
            category="project"
        )
        store.store_memory(
            user_id=test_user.id,
            memory_text="User preference",
            category="preference"
        )
        
        results = retrieval.retrieve_memories_by_category(
            user_id=test_user.id,
            category="project"
        )
        
        assert len(results) == 1
        assert results[0].category == "project"


class TestMemoryRanking:
    def test_rank_memories(self, test_db, test_user):
        store = MemoryStore(test_db)
        ranking = MemoryRanking()
        
        memories = []
        for i in range(3):
            mem = store.store_memory(
                user_id=test_user.id,
                memory_text=f"Memory {i}",
                importance_score=0.3 + (i * 0.2)
            )
            mem.semantic_similarity = 0.5 + (i * 0.1)
            memories.append(mem)
        
        ranked = ranking.rank_memories(memories)
        
        assert len(ranked) == 3
        assert all(isinstance(r, tuple) and len(r) == 2 for r in ranked)
        assert all(r[1] >= 0 for r in ranked)
    
    def test_update_weights(self):
        ranking = MemoryRanking()
        
        ranking.update_weights(
            semantic_weight=0.6,
            recency_weight=0.2,
            importance_weight=0.2
        )
        
        total = ranking.semantic_weight + ranking.recency_weight + ranking.importance_weight
        assert abs(total - 1.0) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
