# Backend Dockerfile - Optimizado para Railway/Cloud
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema y limpiar caché
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements desde backend/
COPY backend/requirements.txt .

# Instalar dependencias de Python con timeout mayor
ENV PIP_DEFAULT_TIMEOUT=100
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    -r requirements.txt

# Copiar el código de la aplicación desde backend/
COPY backend/app/ ./app/

# Crear directorios para assets y logs
RUN mkdir -p /app/assets /app/logs /app/vector_db

# Exponer puerto
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
