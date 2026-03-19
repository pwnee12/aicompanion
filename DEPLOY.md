# AI Companion - Guía de Deploy con Docker

## Requisitos Previos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **8GB+ RAM** (recomendado 16GB)
- **20GB+** espacio en disco

---

## Instalación Rápida

### 1. Clonar y Configurar

```bash
cd aicompanion

# Copiar configuración de entorno
cp .env.docker .env

# Editar .env con tus claves de API
nano .env
# o
code .env
```

### 2. Configurar Variables de Entorno

Edita `.env` con tus claves:

```env
# Security - Genera una clave única
SECRET_KEY=$(openssl rand -hex 32)

# LLM Provider
LLM_PROVIDER=hybrid
OPENAI_API_KEY=sk-tu-clave-aqui
ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui

# Imágenes
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=r8-tu-clave-aqui
```

### 3. Deploy

```bash
# Ejecutar script de deploy
chmod +x deploy.sh
./deploy.sh

# O manualmente:
docker-compose build
docker-compose up -d
```

### 4. Verificar

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs -f backend

# Probar API
curl http://localhost:8000/health
```

**Acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Ver estado
docker-compose ps

# Reconstruir
docker-compose build --no-cache

# Escalar (si necesitas más instancias)
docker-compose up -d --scale backend=2
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar también volúmenes (¡pierde datos!)
docker-compose down -v

# Eliminar imágenes
docker-compose down --rmi all

# Limpieza completa de Docker
docker system prune -a
```

### Acceso a Contenedores

```bash
# Shell en backend
docker-compose exec backend bash

# Shell en frontend
docker-compose exec frontend sh

# Ver variables de entorno
docker-compose exec backend env

# Ver base de datos
docker-compose exec backend ls -la /app/
```

---

## Configuración para Producción

### 1. Security Hardening

```env
# Generar SECRET_KEY segura
SECRET_KEY=$(openssl rand -hex 32)

# Desactivar debug
DEBUG=false

# Usar PostgreSQL en vez de SQLite
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/aicompanion
```

### 2. Base de Datos PostgreSQL (Opcional)

Agrega al `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: aicompanion-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: aicompanion
      POSTGRES_PASSWORD: ${DB_PASSWORD:-securepassword}
      POSTGRES_DB: aicompanion
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - aicompanion-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aicompanion"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
```

### 3. Nginx Reverse Proxy (Opcional)

Para dominio personalizado con SSL:

```yaml
# Agregar al docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    container_name: aicompanion-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - aicompanion-network
```

### 4. SSL con Let's Encrypt

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx

# Obtener certificado
certbot --nginx -d tudominio.com

# Auto-renewal
certbot renew --dry-run
```

---

## Deploy en VPS/Cloud

### DigitalOcean Droplet

```bash
# Conectar al servidor
ssh root@tu-server-ip

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose-plugin

# Clonar repositorio
git clone https://github.com/tu-user/aicompanion.git
cd aicompanion

# Configurar y deploy
cp .env.docker .env
# Editar .env...
docker-compose up -d
```

### AWS EC2

```bash
# Security Group: abrir puertos 22, 80, 443, 3000, 8000

# Instalar Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user

# Instalar Docker Compose
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy
git clone <repo>
cd aicompanion
docker-compose up -d
```

### Google Cloud Run

```bash
# Build y push a GCR
gcloud builds submit --tag gcr.io/PROJECT-ID/aicompanion

# Deploy
gcloud run deploy aicompanion \
  --image gcr.io/PROJECT-ID/aicompanion \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Monitoreo

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Contenedores
docker-compose ps
```

### Logs

```bash
# Logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100 backend

# Logs de hoy
docker-compose logs --since=24h backend

# Guardar logs
docker-compose logs > logs.txt
```

### Métricas

```bash
# Uso de recursos
docker stats

# Uso de disco
docker system df

# Inspeccionar contenedor
docker inspect aicompanion-backend
```

---

## Troubleshooting

### Contenedor no inicia

```bash
# Ver logs de error
docker-compose logs backend

# Verificar variables de entorno
docker-compose exec backend env | grep OPENAI

# Probar conexión
docker-compose exec backend curl http://localhost:8000/health
```

### Error de base de datos

```bash
# Eliminar y recrear volumen (¡pierde datos!)
docker-compose down -v
docker-compose up -d
```

### Error de memoria

```bash
# Limitar memoria en docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Ollama no conecta desde Docker

```bash
# Asegurar extra_hosts en docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"

# O usar red host
network_mode: host
```

---

## Backup y Restore

### Backup

```bash
# Backup de base de datos
docker-compose exec backend tar -czf /tmp/backup.tar.gz /app

# Copiar backup localmente
docker-compose cp backend:/tmp/backup.tar.gz ./backup.tar.gz

# Backup de vectores
tar -czf vector_db_backup.tar.gz backend/vector_db/
```

### Restore

```bash
# Copiar backup al contenedor
docker-compose cp ./backup.tar.gz backend:/tmp/

# Restaurar
docker-compose exec backend tar -xzf /tmp/backup.tar.gz -C /
```

---

## Actualización

```bash
# Pull de cambios
git pull

# Reconstruir y reiniciar
docker-compose build --no-cache
docker-compose up -d

# O solo reiniciar (sin cambios de código)
docker-compose restart
```

---

## Costos Estimados (Cloud)

| Provider | Instancia | RAM | Costo/mes |
|----------|-----------|-----|-----------|
| DigitalOcean | Basic | 4GB | $24 |
| AWS | t3.medium | 4GB | $30 |
| GCP | e2-medium | 4GB | $25 |
| Railway | Standard | 4GB | $20 |

**Nota:** Costos de APIs (OpenAI, Replicate) son adicionales.

---

## Soporte

- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **Issues:** Reporta bugs en GitHub Issues

---

*Última actualización: Marzo 2026*
