import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from database.models import Base, User
from database.connection import get_db
from main import app


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    return TestClient(app)


@pytest.fixture
def test_user_id():
    return "test_user_123"


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "timestamp" in data


class TestChatEndpoint:
    def test_chat_endpoint(self, client, test_user_id):
        response = client.post("/api/chat", json={
            "user_id": test_user_id,
            "message": "Hello, I'm building an AI platform",
            "retrieve_memories": True,
            "top_k": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "memories" in data
        assert "memory_context" in data
        assert "message_id" in data
    
    def test_chat_without_memory_retrieval(self, client, test_user_id):
        response = client.post("/api/chat", json={
            "user_id": test_user_id,
            "message": "Hello",
            "retrieve_memories": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["memories"]) == 0


class TestMemoriesEndpoint:
    def test_get_memories_empty(self, client, test_user_id):
        response = client.get(f"/api/memories?user_id={test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["memories"]) == 0
    
    def test_create_memory(self, client, test_user_id):
        response = client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "User is building an AI platform",
            "category": "project",
            "importance_score": 0.8,
            "tags": ["ai", "platform"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["memory_text"] == "User is building an AI platform"
        assert data["category"] == "project"
        assert data["importance_score"] == 0.8
        assert "id" in data
    
    def test_get_memories_after_create(self, client, test_user_id):
        client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "Test memory",
            "category": "general"
        })
        
        response = client.get(f"/api/memories?user_id={test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["memories"]) == 1
    
    def test_get_memory_by_id(self, client, test_user_id):
        create_response = client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "Test memory",
            "category": "general"
        })
        memory_id = create_response.json()["id"]
        
        response = client.get(f"/api/memories/{memory_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == memory_id
        assert data["memory_text"] == "Test memory"
    
    def test_update_memory(self, client, test_user_id):
        create_response = client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "Original",
            "importance_score": 0.5
        })
        memory_id = create_response.json()["id"]
        
        response = client.put(f"/api/memories/{memory_id}", json={
            "memory_text": "Updated",
            "importance_score": 0.9
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["memory_text"] == "Updated"
        assert data["importance_score"] == 0.9
    
    def test_delete_memory(self, client, test_user_id):
        create_response = client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "To delete",
            "category": "general"
        })
        memory_id = create_response.json()["id"]
        
        response = client.delete(f"/api/memories/{memory_id}")
        assert response.status_code == 200
        
        get_response = client.get(f"/api/memories?user_id={test_user_id}")
        assert get_response.json()["total"] == 0
    
    def test_get_memory_stats(self, client, test_user_id):
        client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "Memory 1",
            "category": "project",
            "importance_score": 0.8
        })
        client.post(f"/api/memories?user_id={test_user_id}", json={
            "memory_text": "Memory 2",
            "category": "preference",
            "importance_score": 0.6
        })
        
        response = client.get(f"/api/memories/stats/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total_memories"] == 2
        assert len(data["categories"]) == 2
        assert data["average_importance"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
