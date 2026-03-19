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
