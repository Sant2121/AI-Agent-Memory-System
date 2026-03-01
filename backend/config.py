from pydantic_settings import BaseSettings
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./memory_system.db"
    
    # LLM API Keys
    openai_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    use_grok: bool = True
    
    # Redis
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    environment: str = "development"
    
    # Memory Configuration
    max_memories_retrieved: int = 5
    memory_similarity_threshold: float = 0.5
    embedding_model: str = "sentence-transformers"
    llm_model: str = "gpt-4o"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["*"]
    
    # Memory Storage
    vector_store_path: str = "./data/vector_store"
    memory_db_path: str = "./data/memories"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
