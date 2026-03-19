# AI Companion - Guía de Configuración Rápida

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Instalar dependencias del sistema

**Linux:**
```bash
# Python y pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Node.js (usando nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Windows:**
```powershell
# Usando Chocolatey
choco install python3 nodejs-lts

# O descarga desde:
# Python: https://python.org
# Node.js: https://nodejs.org
```

**macOS:**
```bash
# Usando Homebrew
brew install python3 node
```

### Paso 2: Clonar y configurar

```bash
# Ejecutar script de configuración
chmod +x setup.sh
./setup.sh
```

### Paso 3: Configurar claves de API

Edita `backend/.env`:

```env
# Para usar OpenAI (recomendado)
OPENAI_API_KEY=sk-tu-clave-aqui
LLM_PROVIDER=hybrid

# Para generación de imágenes
REPLICATE_API_TOKEN=r8-tu-clave-aqui

# O usa modelos locales (gratis)
LLM_PROVIDER=ollama
```

### Paso 4: (Opcional) Instalar Ollama para IA local

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelos
ollama pull llama2
ollama pull nomic-embed-text
```

### Paso 5: Iniciar la aplicación

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run electron:dev
```

¡Listo! La aplicación se abrirá automáticamente.

---

## 🔑 Obtener Claves de API

### OpenAI (Para LLM)
1. Ve a https://platform.openai.com
2. Crea una cuenta
3. API Keys → Create new secret key
4. Copia la clave que empieza con `sk-`

**Costo:** ~$0.01-0.03 por conversación larga

### Replicate (Para Imágenes)
1. Ve a https://replicate.com
2. Inicia sesión con GitHub
3. Account → API tokens
4. Copia tu token

**Costo:** ~$0.002-0.01 por imagen

### Stability AI (Alternativa para Imágenes)
1. Ve a https://platform.stability.ai
2. Crea una cuenta
3. API Keys → Generate new key

**Costo:** Similar a Replicate

---

## 🆓 Configuración 100% Gratis (Local)

Si no quieres pagar APIs, usa modelos locales:

### 1. Instalar Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Descargar modelos
```bash
ollama pull llama2              # Para chat
ollama pull nomic-embed-text    # Para memoria
```

### 3. Configurar backend/.env
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Para imágenes, usa Replicate (no hay opción local fácil)
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=xxx
```

**Nota:** Stable Diffusion local requiere GPU NVIDIA con 8GB+ VRAM

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'xxx'"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "npm ERR! Could not resolve dependency"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: "Ollama no responde"
```bash
# Verificar que Ollama está corriendo
ollama list

# Si no, iniciarlo
ollama serve
```

### Error: "Port 8000 already in use"
```bash
# Matar proceso en puerto 8000
lsof -ti:8000 | xargs kill -9

# O cambia el puerto en backend/.env
API_PORT=8001
```

### La aplicación no se abre
```bash
# Verifica que el backend esté corriendo
curl http://localhost:8000/health

# Debería responder: {"status": "healthy", ...}
```

---

## 📊 Requisitos del Sistema

### Mínimos
- CPU: 4 cores
- RAM: 8GB
- Almacenamiento: 10GB
- Sin GPU requerida (usando APIs cloud)

### Recomendados
- CPU: 8 cores
- RAM: 16GB
- Almacenamiento: 20GB SSD
- GPU: NVIDIA RTX 3060+ (para IA local)

---

## 🎯 Próximos Pasos

1. **Crea tu primer personaje**
   - Ve a Personajes → Nuevo Personaje
   - Configura nombre, personalidad, apariencia
   - Guarda y comienza a chatear

2. **Prueba la memoria contextual**
   - En un chat, menciona un dato importante
   - En otro mensaje, pregunta sobre ese dato
   - ¡La IA debería recordarlo!

3. **Genera imágenes**
   - Activa "Generar imagen" en el chat
   - La IA creará una imagen basada en el contexto
   - Revisa la galería del personaje

4. **Personaliza la configuración**
   - Ve a Configuración
   - Ajusta tema, idioma, opciones de IA

---

## 📞 Soporte

- **Documentación:** Ver README.md
- **Issues:** Reporta bugs en GitHub Issues
- **Discusiones:** Pregunta en GitHub Discussions

---

**¡Disfruta de tu AI Companion! 🎉**
