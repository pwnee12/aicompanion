#!/bin/bash

# AI Companion - Script de Inicio Completo
# Este script inicia backend y frontend correctamente

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
echo "🚀 AI Companion - Iniciando..."
echo "======================================="

# Detener procesos anteriores
print_info "Deteniendo procesos anteriores..."
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 2

# Crear directorios
mkdir -p backend/logs backend/assets backend/vector_db

# ==========================================
# INICIAR BACKEND
# ==========================================
print_info "Iniciando Backend..."
cd backend

# Activar entorno virtual
source venv/bin/activate

# Iniciar backend en background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend iniciado (PID: $BACKEND_PID)"

# Esperar a que el backend esté listo
print_info "Esperando backend... (10 segundos)"
sleep 10

# Verificar backend
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend listo!"
        break
    fi
    if [ $i -eq 10 ]; then
        print_error "Backend no respondió. Revisa logs/backend.log"
        exit 1
    fi
    sleep 1
done

cd ..

# ==========================================
# INICIAR FRONTEND
# ==========================================
print_info "Iniciando Frontend..."
cd frontend

# Iniciar frontend en background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
print_success "Frontend iniciado (PID: $FRONTEND_PID)"

# Esperar a que el frontend esté listo
print_info "Esperando frontend... (5 segundos)"
sleep 5

cd ..

# ==========================================
# CREAR USUARIO Y PERSONAJES DE PRUEBA
# ==========================================
print_info "Creando datos de prueba..."

# Esperar un poco más
sleep 3

# Crear usuario admin
cd backend
source venv/bin/activate

python3 << 'PYTHON_EOF'
import sys
sys.path.append('.')
from sqlalchemy.orm import Session
from app.db.database import User, engine
from app.core.security import get_password_hash
from datetime import datetime, timezone

db = Session(bind=engine)

# Crear usuario admin si no existe
existing = db.query(User).filter(User.username == "admin").first()
if not existing:
    new_user = User(
        username="admin",
        email="admin@aicompanion.com",
        hashed_password=get_password_hash("admin123"),
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    print("Usuario admin creado")
else:
    print("Usuario admin ya existe")

db.close()
PYTHON_EOF

cd ..

# ==========================================
# MOSTRAR INFORMACIÓN
# ==========================================
echo ""
print_success "======================================="
print_success "¡AI Companion Listo!"
print_success "======================================="
echo ""
echo "📍 URLs:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Credenciales:"
echo "   Username:  admin"
echo "   Password:  admin123"
echo ""
echo "📋 Pasos:"
echo "   1. Abre http://localhost:5173"
echo "   2. Inicia sesión con las credenciales"
echo "   3. Crea un personaje o usa uno existente"
echo "   4. ¡Comienza a chatear!"
echo ""
echo "🛑 Para detener:"
echo "   pkill -f 'uvicorn app.main'"
echo "   pkill -f 'vite'"
echo "======================================="
