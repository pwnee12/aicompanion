# AI Companion - Project Context

## Project Overview

**AI Companion** is a desktop virtual companion application similar to Candy.ai, built with **FastAPI** (backend), **React** (frontend), and **Electron** (desktop wrapper). The application provides AI-powered conversations with customizable characters, featuring memory persistence, image generation, and text-to-speech capabilities.

### Core Features

| Feature | Description |
|---------|-------------|
| **Multiple LLM Support** | OpenAI GPT-4, Anthropic Claude, Ollama (local models), or hybrid mode |
| **Image Generation** | Stable Diffusion via Replicate, Stability AI, or local SD with LoRA support |
| **Text-to-Speech** | Edge TTS, Coqui TTS, Google TTS |
| **Vector Memory** | ChromaDB/Pinecone for contextual conversation memory |
| **Character Builder** | Create custom characters with personality, appearance, and backstory |
| **Desktop App** | Cross-platform Electron application (Windows, macOS, Linux) |

---

## Tech Stack

### Backend
- **Framework:** FastAPI 0.109+
- **Database:** SQLite (dev) / PostgreSQL (prod) with SQLAlchemy 2.0
- **Vector DB:** ChromaDB / Pinecone
- **AI Libraries:** openai, anthropic, sentence-transformers, replicate
- **Auth:** JWT with python-jose, bcrypt password hashing
- **Logging:** Loguru

### Frontend
- **UI Framework:** React 18 with Vite
- **State Management:** Zustand
- **Routing:** React Router DOM v6
- **Data Fetching:** TanStack React Query (React Query v5)
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Desktop:** Electron 28

---

## Project Structure

```
aicompanion/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Config, security (config.py, security.py)
│   │   ├── db/                # Database models, connections
│   │   ├── models/            # Pydantic schemas
│   │   ├── routers/           # API routes (auth, characters, chat, images)
│   │   ├── services/          # AI services (llm, memory, image, tts)
│   │   └── main.py            # FastAPI app entry point
│   ├── tests/                 # Pytest tests
│   ├── venv/                  # Python virtual environment
│   ├── .env                   # Environment config (DO NOT COMMIT)
│   ├── .env.example           # Environment template
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Electron + React frontend
│   ├── electron/              # Electron main process
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # App pages (Login, Chat, Builder, etc.)
│   │   ├── services/          # API client services
│   │   ├── store/             # Zustand state stores
│   │   └── App.jsx            # Root component
│   ├── public/                # Static assets
│   ├── electron/              # Electron main process code
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite bundler config
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── .env                   # Frontend environment
│
├── assets/                     # Generated/stored assets
│   ├── characters/            # Character data/avatars
│   ├── images/                # Generated images
│   └── voices/                # Generated audio files
│
├── models/                     # Local AI models
│   ├── lora/                  # LoRA weights for character consistency
│   └── embeddings/            # Embedding models
│
├── logs/                       # Application logs
├── setup.sh                    # Setup script for Linux/Mac
├── README.md                   # User documentation
├── QUICKSTART.md               # Quick setup guide
└── ARQUITECTURA.md             # Technical architecture docs
```

---

## Building and Running

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **(Optional) Ollama** for local LLM: `curl -fsSL https://ollama.ai/install.sh | sh`

### Initial Setup

```bash
# Run setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Or manually:
# 1. Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# 2. Frontend setup
cd ../frontend
npm install
cp .env.example .env
```

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run electron:dev
```

### Production Build

```bash
cd frontend
npm run electron:build
# Executable generated in frontend/dist-electron/
```

### Key Commands

| Command | Description |
|---------|-------------|
| `pip install -r requirements.txt` | Install backend dependencies |
| `npm install` | Install frontend dependencies |
| `uvicorn app.main:app --reload` | Start backend dev server |
| `npm run dev` | Start Vite dev server |
| `npm run electron:dev` | Start Electron app in dev mode |
| `npm run electron:build` | Build Electron app for distribution |
| `pytest` | Run backend tests |

---

## Configuration

### Environment Variables (backend/.env)

```env
# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database
DATABASE_URL=sqlite+aiosqlite:///./aicompanion.db

# Vector DB
VECTOR_DB_TYPE=chroma
CHROMA_DB_PATH=./vector_db

# LLM Provider: openai, anthropic, ollama, hybrid
LLM_PROVIDER=hybrid

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Image Generation: replicate, stability, local_sd
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=r8-...

# TTS: edge, coqui, gtts
TTS_PROVIDER=edge
TTS_DEFAULT_VOICE=en-US-AriaNeural
```

### 100% Local Setup (Free)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download models
ollama pull llama2              # Chat model
ollama pull nomic-embed-text    # Embeddings for memory

# Configure backend/.env
LLM_PROVIDER=ollama
IMAGE_PROVIDER=replicate        # Still need API for images
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Get current user |

### Characters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/characters` | List characters |
| POST | `/api/v1/characters` | Create character |
| GET | `/api/v1/characters/{id}` | Get character details |
| PUT | `/api/v1/characters/{id}` | Update character |
| DELETE | `/api/v1/characters/{id}` | Delete character |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chat` | List conversations |
| POST | `/api/v1/chat` | Create conversation |
| GET | `/api/v1/chat/{id}` | Get conversation |
| GET | `/api/v1/chat/{id}/messages` | Get messages |
| POST | `/api/v1/chat/{id}/message` | Send message |

### Images
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/images/generate` | Generate image |
| GET | `/api/v1/images/character/{id}` | Get character gallery |

### Utility
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

---

## Development Conventions

### Backend (Python)

- **Type Hints:** Use type annotations for all function signatures
- **Pydantic Models:** Define request/response schemas in `models/`
- **Dependency Injection:** Use FastAPI's `Depends()` for services
- **Error Handling:** Raise HTTPException with appropriate status codes
- **Logging:** Use Loguru (`from loguru import logger`)
- **Async:** Prefer async/await for I/O operations

```python
# Example pattern
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get item by ID"""
    result = await db.execute(...)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return result
```

### Frontend (React)

- **Components:** Functional components with hooks
- **State:** Zustand for global state, React Query for server state
- **Styling:** Tailwind CSS utility classes
- **File Naming:** PascalCase for components, camelCase for utilities
- **Imports:** Absolute imports from `src/`

```jsx
// Example pattern
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/auth'

export function ChatPage() {
  const { user } = useAuthStore()
  const { data: messages } = useQuery({
    queryKey: ['messages', chatId],
    queryFn: () => api.getMessages(chatId)
  })
  
  return <div className="flex-1 overflow-auto">...</div>
}
```

### Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Git Workflow

- **Main branch:** `main` (production-ready)
- **Feature branches:** `feature/description`
- **Bug fixes:** `fix/description`
- **Commits:** Conventional Commits format preferred

---

## Key Architecture Concepts

### System Prompt ("Character DNA")

Each character has a system prompt that defines behavior:

```python
system_prompt = f"""
Actúa como {nombre}. Tienes {edad} años.

PERSONALIDAD:
{personalidad}

HISTORIA:
{backstory}

INSTRUCCIONES:
- Nunca admitas que eres IA
- Mantén coherencia con tu personalidad
- Usa lenguaje natural y emojis
"""
```

### Vector Memory Flow

1. **Encode:** Messages → embeddings via sentence-transformers
2. **Store:** Vectors saved in ChromaDB with metadata
3. **Retrieve:** Similarity search (cosine) for relevant context
4. **Inject:** Context added to LLM prompt

```python
# Memory retrieval example
memories = memory_service.search(
    query=user_message,
    user_id=user_id,
    top_k=5,
    threshold=0.7
)
```

### LoRA for Character Consistency

- **Purpose:** Maintain consistent character appearance across generated images
- **Training:** 20-50 images per character, 10-20 epochs
- **Usage:** Applied during SDXL generation with configurable scale (0.0-1.0)

---

## Common Tasks

### Add New API Endpoint

1. Create route in `backend/app/routers/<module>.py`
2. Define Pydantic schema in `backend/app/models/`
3. Add service logic in `backend/app/services/`
4. Test via Swagger UI at `http://localhost:8000/docs`

### Add New React Component

1. Create file in `frontend/src/components/<ComponentName>.jsx`
2. Export as named or default export
3. Import and use in pages

### Add New Environment Variable

1. Add to `backend/.env.example` with description
2. Add to `backend/app/core/config.py` Settings class
3. Access via `settings.VARIABLE_NAME`

### Debug Memory Issues

```bash
# Check ChromaDB contents
cd backend
python -c "from app.services.memory_service import memory_service; print(memory_service.collection.count())"

# Clear vector DB
rm -rf vector_db/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `cd backend && source venv/bin/activate && pip install -r requirements.txt` |
| `npm ERR! dependency` | `cd frontend && rm -rf node_modules package-lock.json && npm install` |
| Port 8000 in use | `lsof -ti:8000 | xargs kill -9` |
| Ollama not responding | `ollama serve` or check `http://localhost:11434` |
| JWT auth fails | Verify `SECRET_KEY` matches in .env |

---

## File References

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app initialization |
| `backend/app/core/config.py` | Settings and environment config |
| `backend/app/services/llm_service.py` | LLM provider abstraction |
| `backend/app/services/memory_service.py` | Vector memory operations |
| `backend/app/routers/chat.py` | Chat endpoints |
| `frontend/src/App.jsx` | React root component |
| `frontend/electron/main.js` | Electron main process |
| `setup.sh` | Automated setup script |

---

## External Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Electron Docs:** https://www.electronjs.org/
- **Ollama:** https://ollama.ai/
- **ChromaDB:** https://docs.trychroma.com/
- **Zustand:** https://github.com/pmndrs/zustand

---

*Last updated: March 2026*
