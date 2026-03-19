# 🚀 Deploy en la Nube - AI Companion

## Arquitectura Recomendada

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │    Render       │
│   (Frontend)    │ ──────► │   (Backend)     │
│   React + Vite  │  API    │   FastAPI       │
│   Gratis        │         │   + PostgreSQL  │
└─────────────────┘         └─────────────────┘
         │                          │
         └──────────┬───────────────┘
                    │
              ┌─────▼──────┐
              │  Ollama    │
              │  (Opcional)│
              └────────────┘
```

## Costos Estimados

| Servicio | Plan | Costo |
|----------|------|-------|
| Vercel | Hobby | **$0/mes** |
| Render | Free | **$0/mes** |
| Render | PostgreSQL | **$0/mes** (90 días) |
| **TOTAL** | | **$0/mes** (gratis) |

---

## 📋 PASO A PASO

### PARTE 1: Preparar el Proyecto

#### 1.1 Crear repositorio en GitHub

```bash
cd /home/ibrahim/Documents/QWEN/aicompanion/aicompanion

# Inicializar git si no existe
git init

# Crear .gitignore seguro
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
venv/
*.db
.env
.env.local
vector_db/
logs/
*.log

# Node
node_modules/
dist/
dist-electron/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF

# Agregar archivos
git add .
git commit -m "Initial commit - AI Companion"

# Crear repositorio en GitHub y hacer push
# Sigue las instrucciones de GitHub para conectar tu repo
```

#### 1.2 Estructura para Deploy

```
aicompanion/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile          ← Ya creado
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── render.yaml             ← Nuevo (configuración Render)
└── vercel.json             ← Nuevo (configuración Vercel)
```

---

### PARTE 2: Backend en Render

#### 2.1 Crear cuenta en Render
1. Ve a https://render.com
2. Click en **"Get Started for Free"**
3. Regístrate con GitHub (recomendado) o email

#### 2.2 Crear Base de Datos PostgreSQL

1. En Render Dashboard, click **"New"** → **"PostgreSQL"**
2. Configura:
   - **Name:** `aicompanion-db`
   - **Database:** `aicompanion`
   - **User:** `aicompanion`
   - **Password:** (genera una segura, guárdala)
   - **Region:** `Oregon` (más cerca de México)
   - **Free Tier:** ✅ Seleccionado

3. Click **"Create Database"**
4. **Guarda las credenciales** que aparecen:
   - `DATABASE_URL` (interno)
   - `DATABASE_URL_EXTERNAL` (para tu app)

#### 2.3 Crear Web Service (Backend)

1. Click **"New"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configura:

```
Name: aicompanion-backend
Region: Oregon
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000
```

4. **Environment Variables** (click "Add Environment Variable"):

```
SECRET_KEY=cambia-esto-por-una-clave-segura-de-32-caracteres
DATABASE_URL=postgresql://aicompanion:PASSWORD@HOST:5432/aicompanion
VECTOR_DB_TYPE=chroma
CHROMA_DB_PATH=./vector_db

# LLM - Opción 1: Ollama (gratis pero necesita servicio externo)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://tu-ollama-url.com

# LLM - Opción 2: OpenAI (pago pero fácil)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-tu-clave-aqui

# Imágenes
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=r8-tu-clave-aqui

# TTS
TTS_PROVIDER=edge
TTS_DEFAULT_VOICE=es-ES-ElviraNeural

# API
API_HOST=0.0.0.0
API_PORT=10000
DEBUG=false
```

5. **Instance Type:** `Free`
6. Click **"Create Web Service"**

#### 2.4 Esperar el Deploy

- El build tomará ~5-10 minutos
- Verás los logs en tiempo real
- Cuando diga **"Live"** está listo

#### 2.5 Obtener URL del Backend

- En el dashboard de Render verás: `https://aicompanion-backend.onrender.com`
- **Guarda esta URL** - la necesita el frontend

---

### PARTE 3: Frontend en Vercel

#### 3.1 Crear cuenta en Vercel

1. Ve a https://vercel.com
2. Click **"Sign Up"**
3. Conecta con GitHub

#### 3.2 Importar Proyecto

1. Click **"Add New Project"**
2. Importa tu repositorio de GitHub
3. Configura:

```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

4. **Root Directory:** `frontend`

#### 3.3 Environment Variables

Click **"Environment Variables"** → **"Add Variable"**:

```
VITE_API_URL=https://aicompanion-backend.onrender.com/api/v1
```

5. Click **"Deploy"**

#### 3.4 Esperar el Deploy

- Build tomará ~2-3 minutos
- Verás una URL como: `https://aicompanion-xyz.vercel.app`

---

### PARTE 4: Configurar CORS en Backend

En Render, ve a **"Environment Variables"** y agrega:

```
ALLOWED_ORIGINS=https://aicompanion-xyz.vercel.app,https://aicompanion.onrender.com
```

---

### PARTE 5: Crear Usuario y Personajes

Una vez desplegado:

```bash
# URL de tu backend en Render
BACKEND_URL="https://aicompanion-backend.onrender.com"

# Crear usuario
curl -X POST "$BACKEND_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "pwnee12",
    "email": "pwnee12@email.com",
    "password": "12111211"
  }'

# Crear personajes (usa el script que ya tenemos)
```

---

## 🎯 CONFIGURACIÓN DE ARCHIVOS

### `render.yaml` (raíz del proyecto)

```yaml
services:
  - type: web
    name: aicompanion-backend
    env: python
    region: oregon
    plan: free
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 10000"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: aicompanion-db
          property: connectionString
      - key: LLM_PROVIDER
        value: ollama
      - key: IMAGE_PROVIDER
        value: replicate
      - key: TTS_PROVIDER
        value: edge

databases:
  - name: aicompanion-db
    databaseName: aicompanion
    user: aicompanion
    plan: free
```

### `vercel.json` (en frontend/)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### `backend/Dockerfile` (actualizado para Render)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorios
RUN mkdir -p assets logs vector_db

EXPOSE 10000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

---

## 🔄 ALTERNATIVA: Railway.app (Más Fácil)

### Railway es más simple que Render:

1. Ve a https://railway.app
2. Click **"Start a New Project"**
3. **"Deploy from GitHub repo"**
4. Selecciona tu repositorio
5. Railway detecta automáticamente FastAPI
6. Agrega PostgreSQL con un click
7. Configura variables de entorno
8. ¡Listo!

**Ventajas:**
- Más fácil que Render
- $5 crédito gratis
- Deploy automático

**Desventajas:**
- Después de $5 es pago
- Menos control que Render

---

## 🆓 OPCIÓN 100% GRATIS: Ollama en Hugging Face Spaces

Para tener IA local gratis:

1. Ve a https://huggingface.co/spaces
2. Crea un Space con Docker
3. Deploy Ollama con tu modelo
4. Usa la URL en tu backend

```dockerfile
# Dockerfile para Ollama en Hugging Face
FROM ollama/ollama:latest

RUN ollama pull dolphin-llama3:8b

EXPOSE 11434

CMD ["ollama", "serve"]
```

---

## 📊 COMPARACIÓN DE PLATAFORMAS

| Plataforma | Facilidad | Gratis | Recomendado |
|------------|-----------|--------|-------------|
| **Render + Vercel** | Media | ✅ 90 días | ⭐⭐⭐⭐⭐ |
| **Railway** | Fácil | ✅ $5 crédito | ⭐⭐⭐⭐ |
| **Fly.io** | Media | ✅ Limitado | ⭐⭐⭐ |
| **AWS Free Tier** | Difícil | ✅ 12 meses | ⭐⭐⭐ |
| **Heroku** | Fácil | ❌ | ⭐⭐ |

---

## 🎯 MI RECOMENDACIÓN

**Para empezar (100% gratis):**
1. **Backend:** Render Free Tier (90 días)
2. **Frontend:** Vercel Hobby (siempre gratis)
3. **DB:** Render PostgreSQL (90 días gratis)
4. **IA:** Ollama en Hugging Face Spaces (gratis)

**Después de 90 días:**
- Opción A: Pagar Render (~$7/mes)
- Opción B: Mover a Railway (~$5/mes)
- Opción C: VPS propio (DigitalOcean ~$6/mes)

---

## 📞 SOPORTE

Si tienes problemas:

1. **Render Logs:** Dashboard → Logs
2. **Vercel Logs:** Project → Deployments → View Logs
3. **Debug local:** `./start.sh` y prueba antes de deploy

---

## ✅ CHECKLIST PRE-DEPLOY

- [ ] Código en GitHub
- [ ] `.env` NO subido a GitHub
- [ ] `DATABASE_URL` configurado
- [ ] `SECRET_KEY` generado
- [ ] API keys agregadas (OpenAI/Replicate si usas)
- [ ] CORS configurado
- [ ] Tests locales passing
- [ ] Usuario admin creado

---

**¿Listo para deploy?** Sigue los pasos arriba o dime si necesitas ayuda con algo específico.
