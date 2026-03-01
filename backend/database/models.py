from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    memory_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    importance_score = Column(Float, default=0.5)
    recency_score = Column(Float, default=1.0)
    semantic_similarity = Column(Float, default=0.0)
    category = Column(String, default="general")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="memories")
    
    __table_args__ = (
        Index("idx_user_id_created_at", "user_id", "created_at"),
        Index("idx_user_id_category", "user_id", "category"),
    )


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    role = Column(String)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)
    retrieved_memories = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")


class MemoryRetrievalLog(Base):
    __tablename__ = "memory_retrieval_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    query = Column(Text, nullable=False)
    retrieved_memory_ids = Column(JSON, default=list)
    scores = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_retrieval_log_user_created", "user_id", "created_at"),
    )
