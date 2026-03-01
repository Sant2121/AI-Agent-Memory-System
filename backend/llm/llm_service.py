from typing import List, Optional
from abc import ABC, abstractmethod
import logging
from config import settings

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass


class GrokLLMService(BaseLLMService):
    def __init__(self, api_key: str, model: str = "grok-4-latest"):
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = model
            logger.info(f"✅ Initialized Grok LLM service with model {model}")
        except ImportError:
            logger.warning("OpenAI library not installed, using mock service")
            self.client = None
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Grok API."""
        try:
            if not self.client:
                return self._mock_response(prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant with access to user memory context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with Grok: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return "I understand your question. Based on the context provided, I can help you with this. Please note that this is a mock response since Grok API is not configured."


class OpenAILLMService(BaseLLMService):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI LLM service with model {model}")
        except ImportError:
            logger.warning("OpenAI not installed, using mock service")
            self.client = None
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API."""
        try:
            if not self.client:
                return self._mock_response(prompt)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant with access to user memory context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return "I understand your question. Based on the context provided, I can help you with this. Please note that this is a mock response since OpenAI API is not configured."


class MockLLMService(BaseLLMService):
    def generate_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        return "This is a mock LLM response. Configure OpenAI API key to use real LLM."


def get_llm_service(api_key: Optional[str] = None, model: str = "gpt-4o") -> BaseLLMService:
    """Factory function to get LLM service based on configuration."""
    if settings.use_grok and settings.xai_api_key:
        logger.info("Using Grok LLM service")
        return GrokLLMService(api_key=settings.xai_api_key, model="grok-4-latest")
    elif api_key or settings.openai_api_key:
        logger.info("Using OpenAI LLM service")
        return OpenAILLMService(api_key=api_key or settings.openai_api_key, model=model)
    else:
        logger.warning("No API key provided, using mock LLM service")
        return MockLLMService()
