from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import ChatRequest, ChatResponse, MemoryResponse
from database.connection import get_db
from database.models import User, Message, Conversation
from memory_engine.memory_store import MemoryStore
from memory_engine.memory_retrieval import MemoryRetrieval
from memory_engine.memory_ranking import MemoryRanking
from llm.llm_service import get_llm_service
from llm.context_injector import ContextInjector
from config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

llm_service = get_llm_service()
context_injector = ContextInjector(max_memories=settings.max_memories_retrieved)
memory_ranking = MemoryRanking()

logger.info(f"LLM Service initialized: {type(llm_service).__name__}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process user message, retrieve relevant memories, and generate response.
    """
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            user = User(id=request.user_id, username=request.user_id, email=f"{request.user_id}@example.com")
            db.add(user)
            db.commit()
        
        memory_store = MemoryStore(db)
        memory_retrieval = MemoryRetrieval(db)
        
        memories = []
        memory_context = ""
        
        if request.retrieve_memories:
            memories = memory_retrieval.retrieve_memories(
                user_id=request.user_id,
                query=request.message,
                top_k=request.top_k,
                similarity_threshold=settings.memory_similarity_threshold
            )
            
            ranked_memories = memory_ranking.rank_memories(memories)
            memories = [m[0] for m in ranked_memories]
            
            for memory in memories:
                memory_store.increment_access_count(memory.id)
            
            memory_context = context_injector._build_context_section(memories)
        
        full_prompt = context_injector.build_full_prompt(request.message, memories)
        response_text = llm_service.generate_response(full_prompt)
        
        conversation = db.query(Conversation).filter(
            Conversation.user_id == request.user_id
        ).order_by(Conversation.created_at.desc()).first()
        
        if not conversation:
            conversation = Conversation(user_id=request.user_id, title="Default Conversation")
            db.add(conversation)
            db.commit()
        
        message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            retrieved_memories=[m.id for m in memories]
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        memory_responses = [
            MemoryResponse.from_orm(m) for m in memories
        ]
        
        return ChatResponse(
            response=response_text,
            memories=memory_responses,
            memory_context=memory_context,
            message_id=message.id
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/store-memory")
async def store_memory_from_chat(
    user_id: str,
    memory_text: str,
    category: str = "general",
    importance_score: float = 0.5,
    db: Session = Depends(get_db)
):
    """
    Manually store a memory from chat context.
    """
    try:
        memory_store = MemoryStore(db)
        memory = memory_store.store_memory(
            user_id=user_id,
            memory_text=memory_text,
            category=category,
            importance_score=importance_score
        )
        return MemoryResponse.from_orm(memory)
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
