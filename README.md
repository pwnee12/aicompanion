# AI Companion

Aplicación de compañero virtual con IA, similar a Candy.ai. Construida con FastAPI, React y Electron.

## 🚀 Características

### Sistema de IA
- **LLMs Múltiples**: Soporte para OpenAI GPT-4, Anthropic Claude, y modelos locales con Ollama
- **Generación de Imágenes**: Stable Diffusion con soporte LoRA para coherencia de personajes
- **Texto a Voz (TTS)**: Edge TTS, Coqui TTS, Google TTS
- **Memoria Contextual**: Base de datos vectorial (ChromaDB/Pinecone) para recordar conversaciones

### Funcionalidades
- **Character Builder**: Crea personajes con personalidad, apariencia e historia personalizada
- **Chat Continuo**: Interfaz tipo mensajería con historial persistente
- **Galería Multimedia**: Álbum de imágenes generadas por personaje
- **Directorio**: Explora personajes públicos de la comunidad
- **Sin Censura**: Control total sobre los filtros de contenido

## 📁 Estructura del Proyecto

```
aicompanion/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints de la API
│   │   ├── core/              # Configuración y seguridad
│   │   ├── db/                # Modelos y conexión DB
│   │   ├── models/            # Esquemas Pydantic
│   │   ├── routers/           # Rutas de la API
│   │   ├── services/          # Servicios de IA
│   │   └── main.py            # Punto de entrada
│   └── requirements.txt
│
├── frontend/                   # Aplicación Electron + React
│   ├── electron/              # Código Electron
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   ├── pages/             # Páginas de la app
│   │   ├── services/          # Servicios API
│   │   ├── store/             # Estado (Zustand)
│   │   └── App.jsx
│   └── package.json
│
├── assets/                     # Archivos generados
│   ├── characters/
│   ├── images/
│   └── voices/
│
└── models/                     # Modelos de IA locales
    ├── lora/
    └── embeddings/
```

## 🛠️ Instalación

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- (Opcional) Ollama para LLM local
- (Opcional) GPU NVIDIA para Stable Diffusion local

### 1. Clonar el repositorio
```bash
git clone <repo-url>
cd aicompanion
```

### 2. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env

# Editar .env con tus claves de API
# - OPENAI_API_KEY (opcional)
# - ANTHROPIC_API_KEY (opcional)
# - REPLICATE_API_TOKEN (para imágenes)
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar configuración
cp .env.example .env
```

### 4. (Opcional) Configurar Ollama para LLM Local

```bash
# Instalar Ollama desde https://ollama.ai

# Descargar modelo
ollama pull llama2

# Descargar modelo de embeddings
ollama pull nomic-embed-text

# El servidor se inicia automáticamente en http://localhost:11434
```

## 🚀 Ejecución

### Modo Desarrollo

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

### Modo Producción

**Build del Frontend:**
```bash
cd frontend
npm run electron:build
```

El ejecutable se generará en `frontend/dist-electron/`

## 📖 Uso

### 1. Registrar Usuario
- Abre la aplicación
- Ve a "Regístrate"
- Crea tu cuenta

### 2. Crear Personaje
- Ve a "Personajes" → "Nuevo Personaje"
- Completa:
  - **Información básica**: Nombre, edad, descripción
  - **Personalidad**: Rasgos, historia, motivaciones
  - **Apariencia**: Descripción física para generación de imágenes
  - **Configuración**: Relación, tono de voz, opciones de contenido

### 3. Chatear
- Haz clic en "Chatear" en un personaje
- Escribe mensajes
- Opcional: Activa "Generar imagen" o "Generar audio"

### 4. Memoria Contextual
- El sistema recuerda automáticamente detalles importantes
- Pregunta sobre conversaciones pasadas
- La IA inyecta contexto relevante en cada respuesta

## 🔧 Configuración de APIs

### OpenAI
```env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4-turbo-preview
```

### Anthropic
```env
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Ollama (Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Híbrido (Recomendado)
```env
LLM_PROVIDER=hybrid
# Usa Ollama local, fallback a OpenAI si falla
OPENAI_API_KEY=sk-...
```

### Imágenes - Replicate
```env
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=r8-...
```

### Imágenes - Stability AI
```env
IMAGE_PROVIDER=stability
STABILITY_API_KEY=st-...
```

## 🧪 Testing

```bash
cd backend
pytest
```

## 📝 Endpoints de la API

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual

### Personajes
- `GET /api/v1/characters` - Listar personajes
- `POST /api/v1/characters` - Crear personaje
- `GET /api/v1/characters/{id}` - Obtener personaje
- `PUT /api/v1/characters/{id}` - Actualizar personaje
- `DELETE /api/v1/characters/{id}` - Eliminar personaje

### Chat
- `GET /api/v1/chat` - Listar conversaciones
- `POST /api/v1/chat` - Crear conversación
- `GET /api/v1/chat/{id}` - Obtener conversación
- `GET /api/v1/chat/{id}/messages` - Obtener mensajes
- `POST /api/v1/chat/{id}/message` - Enviar mensaje

### Imágenes
- `POST /api/v1/images/generate` - Generar imagen
- `GET /api/v1/images/character/{id}` - Galería del personaje

## 🧠 Arquitectura de IA

### System Prompt
Cada personaje tiene un "ADN" textual que define su comportamiento:
```
Actúa como [nombre]. Tienes [edad] años.
Personalidad: [rasgos]
Historia: [backstory]
Relación con el usuario: [tipo]

Instrucciones:
- Nunca admitas que eres IA
- Mantén coherencia con tu personalidad
- Usa lenguaje natural y emojis
```

### Memoria Vectorial
1. Los mensajes se convierten a embeddings
2. Se guardan en ChromaDB con metadata
3. En cada mensaje nuevo, se buscan recuerdos similares
4. El contexto relevante se inyecta en el LLM

### Coherencia Visual (LoRA)
- Cada personaje puede tener un modelo LoRA entrenado
- LoRA restringe la generación a las facciones del personaje
- Scale controla la intensidad (0.0 - 1.0)

## ⚠️ Consideraciones

### Seguridad
- Cambia `SECRET_KEY` en producción
- Usa HTTPS para la API
- No compartas claves de API

### Rendimiento
- Usa GPU para Stable Diffusion local
- ChromaDB es suficiente para uso personal
- Pinecone para escalabilidad en producción

### Costos
- OpenAI: ~$0.01-0.03 por conversación
- Replicate: ~$0.002-0.01 por imagen
- Ollama: Gratis (usa tu hardware)

## 📄 Licencia

MIT License

## 🙏 Créditos

Inspirado en Candy.ai y proyectos similares de AI companions.

---

**Hecho con ❤️ usando FastAPI, React y Electron**
