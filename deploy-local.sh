#!/bin/bash

# AI Companion - Deploy Local Rápido
# Este script inicia la aplicación sin Docker

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

echo "🚀 AI Companion - Deploy Local"
echo "======================================="

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no encontrado"
    exit 1
fi
print_success "Python $(python3 --version) detectado"

# Verificar Node.js
print_info "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    print_error "Node.js no encontrado"
    exit 1
fi
print_success "Node.js $(node --version) detectado"

# Configurar Backend
print_info "Configurando backend..."
cd backend

if [ ! -d "venv" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

print_info "Instalando dependencias del backend..."
pip install --quiet -r requirements.txt

if [ ! -f ".env" ]; then
    print_info "Creando .env desde .env.example..."
    cp .env.example .env
fi

cd ..

# Configurar Frontend
print_info "Configurando frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    print_info "Instalando dependencias del frontend..."
    npm install --silent
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

cd ..

# Crear directorios
mkdir -p backend/assets backend/vector_db backend/logs

echo ""
print_success "¡Configuración completada!"
echo ""
echo "======================================="
echo "Para iniciar la aplicación:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend && npm run electron:dev"
echo "======================================="
