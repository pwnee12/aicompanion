#!/bin/bash

# AI Companion - Preparar para Deploy en la Nube
# Este script prepara todo para subir a GitHub y deployar

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

cd /home/ibrahim/Documents/QWEN/aicompanion/aicompanion

echo "======================================="
echo "🚀 Preparando Deploy en la Nube"
echo "======================================="
echo ""

# 1. Verificar Git
print_info "Verificando Git..."
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado"
    exit 1
fi
print_success "Git instalado"

# 2. Inicializar repositorio si no existe
if [ ! -d ".git" ]; then
    print_info "Inicializando repositorio Git..."
    git init
fi

# 3. Crear .gitignore seguro
print_info "Creando .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
*.db
*.sqlite
.env
.env.local
.env.*.local
vector_db/
logs/
*.log

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist-electron/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Generated assets
assets/images/
assets/voices/
models/lora/*.pt
models/lora/*.safetensors
EOF
print_success ".gitignore creado"

# 4. Verificar archivos de deploy
print_info "Verificando archivos de deploy..."
files_ok=true

if [ ! -f "render.yaml" ]; then
    print_error "Falta render.yaml"
    files_ok=false
fi

if [ ! -f "frontend/vercel.json" ]; then
    print_error "Falta frontend/vercel.json"
    files_ok=false
fi

if [ ! -f "backend/Dockerfile" ]; then
    print_error "Falta backend/Dockerfile"
    files_ok=false
fi

if [ "$files_ok" = true ]; then
    print_success "Archivos de deploy verificados"
fi

# 5. Crear archivo de instrucciones
print_info "Generando instrucciones..."
cat > DEPLOY_INSTRUCTIONS.md << 'EOF'
# 📤 Instrucciones para Deploy

## Paso 1: Subir a GitHub

```bash
# Agregar todos los archivos
git add .

# Commit
git commit -m "Ready for cloud deploy"

# Crear repositorio en GitHub y hacer push
git remote add origin https://github.com/TU-USUARIO/aicompanion.git
git branch -M main
git push -u origin main
```

## Paso 2: Deploy en Render (Backend)

1. Ve a https://render.com
2. Sign in con GitHub
3. New → PostgreSQL
   - Name: `aicompanion-db`
   - Database: `aicompanion`
   - User: `aicompanion`
   - Password: (genera una y guárdala)
   - Region: Oregon
4. New → Web Service
   - Conecta tu repo de GitHub
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Agrega Environment Variables:
   ```
   SECRET_KEY=tu-clave-segura-de-32-caracteres
   DATABASE_URL=(la que genera Render automáticamente)
   LLM_PROVIDER=ollama
   IMAGE_PROVIDER=replicate
   REPLICATE_API_TOKEN=tu-token
   TTS_PROVIDER=edge
   ```
6. Deploy y espera ~5 minutos

## Paso 3: Deploy en Vercel (Frontend)

1. Ve a https://vercel.com
2. Sign in con GitHub
3. Add New Project
4. Importa tu repositorio
5. Root Directory: `frontend`
6. Environment Variables:
   ```
   VITE_API_URL=https://tu-backend-en-render.onrender.com/api/v1
   ```
7. Deploy y espera ~2 minutos

## Paso 4: Crear Usuario

```bash
BACKEND_URL="https://tu-backend.onrender.com"

curl -X POST "$BACKEND_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "pwnee12",
    "email": "pwnee12@email.com",
    "password": "12111211"
  }'
```

## Paso 5: Crear Personajes

Usa el script `create_characters.py` o hazlo manual vía API.

## ¡Listo!

Frontend: https://tu-app.vercel.app
Backend: https://tu-backend.onrender.com
EOF
print_success "Instrucciones generadas"

# 6. Mostrar resumen
echo ""
print_success "======================================="
print_success "¡Proyecto listo para deploy!"
print_success "======================================="
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1️⃣  Subir a GitHub:"
echo "   git add ."
echo "   git commit -m 'Ready for deploy'"
echo "   git remote add origin https://github.com/TU-USUARIO/aicompanion.git"
echo "   git push -u origin main"
echo ""
echo "2️⃣  Deploy en Render:"
echo "   https://render.com → New Web Service"
echo "   Conecta tu repo y configura variables"
echo ""
echo "3️⃣  Deploy en Vercel:"
echo "   https://vercel.com → Add Project"
echo "   Root: frontend"
echo ""
echo "📖 Instrucciones completas en: DEPLOY_INSTRUCTIONS.md"
echo ""
echo "======================================="
