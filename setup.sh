#!/bin/bash

# AI Companion - Script de inicio rápido
# Este script configura y ejecuta la aplicación en modo desarrollo

set -e

echo "🚀 AI Companion - Configuración inicial"
echo "======================================="

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_warning "Python 3 no encontrado. Por favor instala Python 3.10+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "$PYTHON_VERSION detectado"

# Verificar Node.js
print_info "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    print_warning "Node.js no encontrado. Por favor instala Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "$NODE_VERSION detectado"

# Configurar Backend
print_info "Configurando backend..."
cd backend

if [ ! -d "venv" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv venv
fi

print_info "Activando entorno virtual..."
source venv/bin/activate

print_info "Instalando dependencias del backend..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    print_info "Creando archivo .env..."
    cp .env.example .env
    print_warning "Edita backend/.env con tus claves de API"
fi

cd ..

# Configurar Frontend
print_info "Configurando frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_info "Instalando dependencias del frontend..."
    npm install
fi

if [ ! -f ".env" ]; then
    print_info "Creando archivo .env del frontend..."
    cp .env.example .env
fi

cd ..

# Crear directorios necesarios
print_info "Creando directorios de assets..."
mkdir -p assets/images
mkdir -p assets/voices
mkdir -p assets/characters
mkdir -p models/lora
mkdir -p logs

echo ""
echo "======================================="
print_success "¡Configuración completada!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Edita backend/.env con tus claves de API"
echo "   2. (Opcional) Instala Ollama para LLM local: https://ollama.ai"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   cd frontend && npm run electron:dev"
echo ""
echo "======================================="
