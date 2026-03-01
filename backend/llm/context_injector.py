from typing import List
from database.models import Memory
import logging

logger = logging.getLogger(__name__)


class ContextInjector:
    def __init__(self, max_memories: int = 5):
        self.max_memories = max_memories
    
    def inject_context(self, query: str, memories: List[Memory]) -> str:
        """Inject memory context into prompt."""
        try:
            if not memories:
                return query
            
            context_section = self._build_context_section(memories)
            injected_prompt = f"{context_section}\n\nUser Query:\n{query}"
            
            return injected_prompt
        except Exception as e:
            logger.error(f"Error injecting context: {e}")
            return query
    
    def _build_context_section(self, memories: List[Memory]) -> str:
        """Build context section from memories."""
        try:
            context_lines = ["Context from Memory:"]
            
            for i, memory in enumerate(memories[:self.max_memories], 1):
                similarity = getattr(memory, 'semantic_similarity', 0.0)
                context_lines.append(f"- {memory.memory_text} (relevance: {similarity:.2f})")
            
            return "\n".join(context_lines)
        except Exception as e:
            logger.error(f"Error building context section: {e}")
            return "Context from Memory:"
    
    def build_system_prompt(self) -> str:
        """Build system prompt for LLM."""
        return """You are a helpful AI assistant with access to user memory context. 
You have been provided with relevant information from past conversations and user preferences.
Use this context to provide personalized, coherent, and relevant responses.
Always acknowledge when you're using information from the user's memory context."""
    
    def build_full_prompt(self, query: str, memories: List[Memory]) -> str:
        """Build complete prompt with system context and memory."""
        context = self._build_context_section(memories)
        full_prompt = f"""{self.build_system_prompt()}

{context}

User Query:
{query}"""
        return full_prompt
