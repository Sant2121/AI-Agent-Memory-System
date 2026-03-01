from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    memory_text: str
    category: str = "general"
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = []


class MemoryUpdate(BaseModel):
    memory_text: Optional[str] = None
    category: Optional[str] = None
    importance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class MemoryResponse(BaseModel):
    id: str
    user_id: str
    memory_text: str
    importance_score: float
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    access_count: int
    semantic_similarity: Optional[float] = None
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: str
    message: str
    retrieve_memories: bool = True
    top_k: int = 5


class ChatResponse(BaseModel):
    response: str
    memories: List[MemoryResponse]
    memory_context: str
    message_id: str


class MemoriesListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int


class HealthResponse(BaseModel):
    status: str
    components: dict
    timestamp: datetime


class MemoryExtractionRequest(BaseModel):
    text: str
    user_id: str


class MemoryExtractionResponse(BaseModel):
    extracted_memories: List[MemoryCreate]
    confidence_scores: List[float]
