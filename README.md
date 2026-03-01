# AI Agent Memory System

A production-ready persistent memory architecture for AI assistants to store, retrieve, and utilize long-term memory across conversations using vector embeddings and semantic search.

## Overview

This system enables AI agents to:
- **Store** user information, preferences, and conversation context as embeddings
- **Retrieve** relevant memories based on semantic similarity
- **Rank** memories by relevance, recency, and importance
- **Inject** context into LLM responses for coherent, personalized interactions

## Architecture

```
User Message
    ↓
Memory Retrieval (Vector Search)
    ↓
Relevant Memories Retrieved
    ↓
LLM Response Generation (with context injection)
    ↓
Memory Update & Storage
```

## Tech Stack

- **Backend**: FastAPI + Python
- **LLM**: OpenAI GPT-4o (abstraction layer for extensibility)
- **Embeddings**: SentenceTransformers (local) + OpenAI embeddings (optional)
- **Vector Database**: FAISS (local) with support for Pinecone/Weaviate
- **Structured Storage**: PostgreSQL
- **Cache**: Redis (optional)
- **Frontend**: React with TailwindCSS
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)
- OpenAI API Key (optional, for GPT-4o)

### Setup

#### 1. Clone and Install Backend
```bash
cd ai-agent-memory-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure Environment
Create `.env` file in the backend directory:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/memory_db

# OpenAI (optional)
OPENAI_API_KEY=your_api_key_here

# Redis (optional)
REDIS_URL=redis://localhost:6379

# App
DEBUG=True
LOG_LEVEL=INFO
```

#### 3. Initialize Database
```bash
cd backend
python -m alembic upgrade head
```

#### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

#### 5. Setup Frontend
```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

### Docker Setup

```bash
docker-compose up --build
```

This will start:
- FastAPI backend on `http://localhost:8000`
- React frontend on `http://localhost:3000`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

## API Endpoints

### Chat
**POST** `/api/chat`
- Send a message and get AI response with memory context
- Request: `{ "user_id": "string", "message": "string" }`
- Response: `{ "response": "string", "memories": [...], "memory_context": "string" }`

### Memories
**GET** `/api/memories`
- Retrieve all stored memories for a user
- Query: `?user_id=string&limit=10`
- Response: `{ "memories": [...], "total": int }`

**DELETE** `/api/memory/{memory_id}`
- Delete a specific memory
- Response: `{ "success": bool, "message": "string" }`

### Health
**GET** `/api/health`
- Check system health
- Response: `{ "status": "healthy", "components": {...} }`

## Project Structure

```
ai-agent-memory-system/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── memories.py
│   │   │   └── health.py
│   │   └── schemas.py
│   ├── memory_engine/
│   │   ├── memory_store.py
│   │   ├── memory_retrieval.py
│   │   ├── memory_ranking.py
│   │   └── memory_update.py
│   ├── embeddings/
│   │   ├── embedding_service.py
│   │   └── vector_store.py
│   ├── llm/
│   │   ├── llm_service.py
│   │   └── context_injector.py
│   ├── database/
│   │   ├── models.py
│   │   ├── connection.py
│   │   └── migrations/
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MemoryPanel.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── public/
├── architecture/
│   └── memory_architecture.md
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── test_memory_engine.py
│   ├── test_embeddings.py
│   └── test_api.py
├── .env.example
├── README.md
└── requirements.txt
```

## Core Features

### 1. Memory Storage
- Automatic extraction of important information from conversations
- Conversion to embeddings using SentenceTransformers
- Storage in PostgreSQL with vector embeddings in FAISS
- Metadata tracking (timestamp, user_id, importance_score)

### 2. Memory Retrieval
- Semantic search using vector similarity
- Top-K retrieval based on cosine similarity
- Efficient FAISS indexing for fast lookups

### 3. Memory Ranking
Memories ranked by:
- **Semantic Similarity**: Cosine distance to query
- **Recency**: Recent memories weighted higher
- **Importance Score**: User-defined or ML-derived importance

### 4. Context Injection
Retrieved memories automatically injected into LLM prompts:
```
Context from memory:
- User is building an AI media authenticity platform
- Prefers detailed technical explanations
- Working with Python and FastAPI

Question: Help design a pitch deck.
```

### 5. Memory Update
Intelligent memory extraction:
- Stores user preferences
- Captures project details
- Records long-term facts
- Filters trivial information

## Testing

Run tests with pytest:
```bash
cd backend
pytest tests/ -v
```

Test coverage includes:
- Memory storage and retrieval
- Embedding generation
- API endpoints
- LLM integration
- Memory ranking logic

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `REDIS_URL` | Redis connection string | Optional |
| `DEBUG` | Debug mode | False |
| `LOG_LEVEL` | Logging level | INFO |
| `EMBEDDING_MODEL` | Model for embeddings | sentence-transformers |
| `LLM_MODEL` | LLM model to use | gpt-4o |
| `MAX_MEMORIES_RETRIEVED` | Max memories per query | 5 |
| `MEMORY_SIMILARITY_THRESHOLD` | Min similarity score | 0.5 |

## Performance Considerations

- **FAISS Indexing**: O(log n) search complexity
- **Batch Processing**: Memories processed in batches for efficiency
- **Caching**: Redis caching for frequently accessed memories
- **Vector Quantization**: Optional for large-scale deployments

## Extensibility

### Add New LLM Providers
Implement `BaseLLMService` in `backend/llm/llm_service.py`:
```python
class AnthropicLLMService(BaseLLMService):
    def generate_response(self, prompt: str) -> str:
        # Implementation
        pass
```

### Add New Vector Stores
Implement `BaseVectorStore` in `backend/embeddings/vector_store.py`:
```python
class PineconeVectorStore(BaseVectorStore):
    def search(self, query_embedding: List[float], top_k: int) -> List[Memory]:
        # Implementation
        pass
```

## Deployment

### Heroku
```bash
git push heroku main
```

### AWS
See `docker/` directory for containerization. Deploy using ECS or Kubernetes.

### Local Testing
```bash
docker-compose up
# Visit http://localhost:3000
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U user -d memory_db -c "SELECT 1"
```

### Memory Retrieval Not Working
- Verify embeddings are generated: Check `memory_embeddings` table
- Check FAISS index: Verify `vector_store.index` file exists
- Review logs: `tail -f logs/app.log`

### API Errors
- Check backend logs: `docker logs backend`
- Verify environment variables: `echo $DATABASE_URL`
- Test endpoint: `curl http://localhost:8000/api/health`

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for usage examples

---

**Built with ❤️ for AI-powered conversations**
