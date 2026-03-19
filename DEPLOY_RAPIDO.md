# 🚀 DEPLOY RÁPIDO - 10 MINUTOS

## Opción Más Fácil: Railway.app

### 1. Crear cuenta en Railway
https://railway.app → Sign up con GitHub

### 2. Deploy del Backend
```
1. Click "New Project"
2. "Deploy from GitHub repo"
3. Selecciona tu repo de aicompanion
4. Railway detecta FastAPI automáticamente
5. Click "Add PostgreSQL"
6. ¡Listo! Backend corriendo
```

### 3. Configurar Variables
En Railway → Variables → Add:
```
SECRET_KEY=mi-clave-segura-1234567890
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://tu-ollama-url.com
IMAGE_PROVIDER=replicate
REPLICATE_API_TOKEN=tu-token
```

### 4. Deploy del Frontend en Vercel
```
1. https://vercel.com → Sign up
2. "Add New Project"
3. Importa tu repo
4. Root Directory: frontend
5. Environment:
   VITE_API_URL=https://tu-backend.railway.app/api/v1
6. Deploy
```

### 5. Crear Usuario
```bash
curl -X POST https://tu-backend.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"pwnee12","email":"pwnee12@email.com","password":"12111211"}'
```

---

## Opción Gratis 90 días: Render

Sigue las instrucciones en `DEPLOY_CLOUD.md`

---

## URLs Finales

```
Frontend: https://aicompanion.vercel.app
Backend:  https://aicompanion.onrender.com
Login:    pwnee12 / 12111211
```

---

## ¿Problemas?

1. **Backend no responde:** Revisa logs en Railway/Render
2. **CORS error:** Agrega frontend URL al backend
3. **Database error:** Verifica DATABASE_URL
4. **IA no funciona:** Configura Ollama o OpenAI

---

## Costos

| Plataforma | Gratis | Después |
|------------|--------|---------|
| Railway | $5 crédito | ~$5/mes |
| Render | 90 días | ~$7/mes |
| Vercel | Siempre | $0/mes |
