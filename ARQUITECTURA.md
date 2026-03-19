# Arquitectura Técnica de AI Companion

## Visión General

```
┌─────────────────────────────────────────────────────────────────────┐
│                         APLICACIÓN DE ESCRITORIO                     │
│                         (Electron + React)                           │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Sidebar    │  │   Páginas    │  │   Estado     │               │
│  │              │  │   (React     │  │   (Zustand)  │               │
│  │  - Chats     │  │    Router)   │  │              │               │
│  │  - Personajes│  │              │  │  - Auth      │               │
│  │  - Galería   │  │  - Login     │  │  - Chats     │               │
│  │  - Settings  │  │  - Chat      │  │  - Settings  │               │
│  └──────────────┘  │  - Builder   │  └──────────────┘               │
│                    └──────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                            │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                      RUTAS DE API                              │  │
│  │                                                                 │  │
│  │  /auth        → Registro, Login, JWT                           │  │
│  │  /characters  → CRUD de personajes, System Prompts             │  │
│  │  /chat        → Mensajes, contexto, memoria                     │  │
│  │  /images      → Generación de imágenes                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                      SERVICIOS DE IA                           │  │
│  │                                                                 │  │
│  │  LLMService       → OpenAI, Anthropic, Ollama                  │  │
│  │  ImageService     → SDXL, LoRA, ControlNet                     │  │
│  │  MemoryService    → ChromaDB, Pinecone, Embeddings             │  │
│  │  TTSService       → Edge TTS, Coqui, gTTS                      │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCIA                                 │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  SQLite/     │  │  ChromaDB    │  │  FileSystem  │               │
│  │  PostgreSQL  │  │  (Vector)    │  │  (Assets)    │               │
│  │              │  │              │  │              │               │
│  │  - Users     │  │  - Memories  │  │  - Images    │               │
│  │  - Chats     │  │  - Embeddings│  │  - Audio     │               │
│  │  - Messages  │  │              │  │  - LoRA      │               │
│  │  - Characters│  │              │  │              │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de una Conversación

### 1. Usuario envía mensaje

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Usuario │     │  Frontend   │     │   Backend    │     │    IA    │
│         │     │   (React)   │     │  (FastAPI)   │     │Services  │
└────┬────┘     └──────┬──────┘     └──────┬───────┘     └────┬─────┘
     │                 │                    │                   │
     │ Escribe mensaje │                    │                   │
     │────────────────>│                    │                   │
     │                 │                    │                   │
     │                 │ POST /chat/{id}/   │                   │
     │                 │ message            │                   │
     │                 │───────────────────>│                   │
     │                 │                    │                   │
     │                 │                    │ 1. Guarda mensaje │
     │                 │                    │    en DB          │
     │                 │                    │                   │
     │                 │                    │ 2. Busca memorias │
     │                 │                    │    relevantes     │
     │                 │                    │──────────────────>│
     │                 │                    │                   │
     │                 │                    │ 3. Construye      │
     │                 │                    │    prompt         │
     │                 │                    │                   │
     │                 │                    │ 4. Llama al LLM   │
     │                 │                    │──────────────────>│
     │                 │                    │                   │
     │                 │                    │ 5. Obtiene        │
     │                 │                    │    respuesta      │
     │                 │                    │<──────────────────│
     │                 │                    │                   │
     │                 │                    │ 6. (Opcional)     │
     │                 │                    │    Genera imagen  │
     │                 │                    │──────────────────>│
     │                 │                    │                   │
     │                 │                    │ 7. (Opcional)     │
     │                 │                    │    Genera audio   │
     │                 │                    │──────────────────>│
     │                 │                    │                   │
     │                 │                    │ 8. Guarda         │
     │                 │                    │    respuesta      │
     │                 │                    │                   │
     │                 │ Response           │                   │
     │                 │<───────────────────│                   │
     │                 │                    │                   │
     │  Renderiza      │                    │                   │
     │<────────────────│                    │                   │
     │                 │                    │                   │
```

---

## System Prompt - El "ADN" del Personaje

### Estructura del Prompt

```python
system_prompt = f"""
Actúa como un personaje llamado {nombre}.

INFORMACIÓN BÁSICA:
- Edad: {edad} años
- Descripción: {descripcion}

PERSONALIDAD:
{personalidad}

HISTORIA:
{backstory}

APARIENCIA:
{appearance}

RELACIÓN CON EL USUARIO:
{relationship_type}

INSTRUCCIONES DE COMPORTAMIENTO:
1. Nunca admitas que eres una Inteligencia Artificial
2. Mantén siempre tu personalidad definida
3. Usa un lenguaje natural y conversacional
4. Sé empático/a y emocionalmente responsivo/a
5. Usa emojis ocasionalmente cuando sea apropiado
6. Mantén coherencia con tu historia y personalidad
7. Responde de manera creativa y engaging
8. Usa asteriscos para acciones: *sonríe*

FORMATO DE RESPUESTA:
- Respuestas cortas y naturales (2-4 oraciones)
- Evita lenguaje demasiado formal
- Muestra interés en el usuario
- Haz preguntas para mantener la conversación
"""
```

### Inyección de Contexto

Cuando el usuario envía un mensaje:

```python
# 1. Buscar memorias relevantes
memorias = memory_service.search(
    query=mensaje_usuario,
    user_id=user_id,
    top_k=5
)

# 2. Construir contexto
contexto = "\n".join([
    f"• {m['tipo']}: {m['contenido']}"
    for m in memorias
])

# 3. Inyectar en el system prompt
system_prompt_final = system_prompt + f"""

CONTEXTO DE CONVERSACIONES ANTERIORES:
{contexto}

Usa esta información para responder de manera coherente.
"""
```

---

## Memoria Vectorial - Funcionamiento Interno

### 1. Codificación a Vector

```
Mensaje: "Mi perro se llama Max y tiene 3 años"
                ↓
        [Modelo de Embedding]
        (nomic-embed-text / text-embedding-3-small)
                ↓
Vector: [0.023, -0.045, 0.012, ..., 0.089]  # 768-1536 dimensiones
```

### 2. Almacenamiento en ChromaDB

```python
collection.add(
    ids=["mem_123"],
    embeddings=[[0.023, -0.045, ...]],
    metadatas=[{
        "user_id": 1,
        "character_id": 5,
        "memory_type": "fact",
        "importance": 0.8,
        "content": "Mi perro se llama Max y tiene 3 años"
    }]
)
```

### 3. Búsqueda por Similitud

```
Query: "¿Te acuerdas de mi mascota?"
            ↓
    [Embedding Model]
            ↓
    Vector Query: [0.021, -0.043, ...]
            ↓
    [Búsqueda por Similitud Coseno]
            ↓
    Resultados:
    - "Mi perro se llama Max" (similitud: 0.92)
    - "Tengo un cachorro" (similitud: 0.87)
    - "Max es muy juguetón" (similitud: 0.85)
```

### 4. Fórmula de Similitud

```
similitud_coseno = (A · B) / (||A|| × ||B||)

Donde:
- A, B = vectores
- · = producto punto
- ||A|| = magnitud del vector A

Resultado: 0 (totalmente diferentes) a 1 (idénticos)
```

---

## Generación de Imágenes con LoRA

### Flujo de Generación

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ENTRADA                                                  │
│    Prompt: "Una selfie en la playa al atardecer"            │
│    Personaje: Sofía (con LoRA entrenado)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CONSTRUCCIÓN DEL PROMPT COMPLETO                         │
│    "Una selfie en la playa al atardecer, mujer joven,       │
│     cabello rubio largo, ojos verdes, figura atlética,      │
│     high quality, detailed, professional, 4k"               │
│                                                             │
│    Negative prompt: "ugly, duplicate, low quality..."       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. APLICACIÓN DE LoRA                                       │
│    - Cargar pesos específicos del personaje                 │
│    - Scale: 0.8 (80% de influencia del LoRA)                │
│    - Esto fuerza a la IA a generar facciones consistentes   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PROCESO DE DENOISING (SDXL)                              │
│    a. Generar ruido aleatorio                               │
│    b. Iterativamente "limpiar" el ruido guiado por:         │
│       - El prompt (texto → vectores CLIP)                   │
│       - LoRA (facciones del personaje)                      │
│    c. 30 iteraciones de refinamiento                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. SALIDA                                                   │
│    Imagen 512x512 PNG del personaje en la playa             │
│    Guardada en: /assets/images/{uuid}.png                   │
└─────────────────────────────────────────────────────────────┘
```

### Entrenamiento de LoRA

```python
# Dataset: 20-50 imágenes del personaje
# Resolución: 512x512
# Epochs: 10-20
# Learning rate: 1e-4

# Comando de entrenamiento (kohya-ss)
accelerate launch train_network.py \
  --pretrained_model_name_or_path=runwayml/stable-diffusion-v1-5 \
  --train_data_dir=./dataset/sofia \
  --output_dir=./models/lora/sofia.safetensors \
  --resolution=512 \
  --batch_size=4 \
  --epochs=15 \
  --network_module=networks.lora \
  --network_dim=128 \
  --network_alpha=64
```

---

## Base de Datos - Esquema

```sql
-- Usuarios
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personajes
CREATE TABLE characters (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    personality TEXT,
    backstory TEXT,
    appearance TEXT,
    voice_tone VARCHAR(100),
    relationship_type VARCHAR(50),
    age INTEGER,
    avatar_url VARCHAR(255),
    system_prompt TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_nsfw BOOLEAN DEFAULT FALSE,
    lora_path VARCHAR(255),
    lora_scale FLOAT DEFAULT 0.8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chats
CREATE TABLE chats (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    character_id INTEGER REFERENCES characters(id),
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mensajes
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id),
    sender VARCHAR(20) NOT NULL,  -- 'user' o 'character'
    content TEXT NOT NULL,
    image_url VARCHAR(255),
    audio_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Galería de imágenes
CREATE TABLE character_images (
    id INTEGER PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    image_url VARCHAR(255) NOT NULL,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas rápidas
CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_characters_owner ON characters(owner_id);
```

---

## Seguridad

### Autenticación JWT

```python
# 1. Login
POST /api/v1/auth/login
{
    "username": "usuario",
    "password": "contraseña"
}

# 2. Backend verifica credenciales
hashed = bcrypt.hash(password)
if bcrypt.verify(password, hashed):
    # 3. Generar token
    token = jwt.encode(
        {"sub": username, "user_id": id},
        SECRET_KEY,
        algorithm="HS256",
        expires_in=7 days
    )

# 4. Cliente usa token en headers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 5. Backend valida token en cada request
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload["user_id"]
```

### Hash de Contraseñas

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# Registrar
hashed = pwd_context.hash("contraseña")
# Resultado: $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW

# Login
if pwd_context.verify("contraseña", hashed):
    # Contraseña correcta
```

---

## Optimizaciones de Rendimiento

### 1. Cache de Modelos

```python
# Singleton para modelos de IA
class LLMService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_cache = {}
        return cls._instance
    
    def get_model(self, model_name):
        if model_name not in self.model_cache:
            self.model_cache[model_name] = load_model(model_name)
        return self.model_cache[model_name]
```

### 2. Conexiones de DB

```python
# Pool de conexiones
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)
```

### 3. Búsquedas Vectoriales

```python
# Índices HNSW en ChromaDB
collection.create_index(
    index_params={
        "efConstruction": 200,
        "M": 16
    }
)

# Búsqueda aproximada (más rápida)
results = collection.query(
    query_embeddings=[query],
    n_results=5,
    ef_search=64  # Menor = más rápido, mayor = más preciso
)
```

---

## Escalabilidad

### De Local a Producción

| Componente | Local | Producción |
|------------|-------|------------|
| DB | SQLite | PostgreSQL |
| Vector DB | ChromaDB | Pinecone |
| LLM | Ollama | OpenAI API |
| Imágenes | Replicate | Stability AI |
| Cache | Memoria | Redis |
| Deploy | Local | Docker + K8s |

### Docker Compose (Producción)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/aicompanion
      VECTOR_DB_TYPE: pinecone
      LLM_PROVIDER: openai
    ports:
      - "8000:8000"
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

---

**Documento Técnico v1.0**
