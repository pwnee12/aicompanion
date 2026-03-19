#!/bin/bash

# AI Companion - Docker Deploy Script
# Este script construye y despliega la aplicación con Docker

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar Docker
print_info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Instala Docker Compose primero."
    exit 1
fi

print_success "Docker $(docker --version) detectado"
print_success "Docker Compose $(docker-compose --version) detectado"

# Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning "No se encontró .env, copiando desde .env.docker..."
    cp .env.docker .env
    print_warning "Edita .env con tus claves de API antes de continuar"
    exit 1
fi

# Cargar variables de entorno
set -a
source .env
set +a

# Crear directorios necesarios
print_info "Creando directorios de persistencia..."
mkdir -p backend/assets backend/vector_db backend/logs

# Construir imágenes
print_info "Construyendo imágenes Docker..."
docker-compose build

# Iniciar servicios
print_info "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios inicien..."
sleep 10

# Verificar salud de servicios
print_info "Verificando salud de servicios..."
docker-compose ps

# Mostrar logs del backend
print_info "\nLogs del backend (últimas 20 líneas):"
docker-compose logs --tail=20 backend

print_success "\n======================================="
print_success "¡Deploy completado!"
echo ""
print_info "Frontend: http://localhost:${FRONTEND_PORT:-3000}"
print_info "Backend:  http://localhost:${BACKEND_PORT:-8000}"
print_info "API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
echo ""
print_info "Para ver logs en tiempo real:"
echo "   docker-compose logs -f"
echo ""
print_info "Para detener servicios:"
echo "   docker-compose down"
echo ""
print_info "Para reiniciar:"
echo "   docker-compose restart"
echo "======================================="
