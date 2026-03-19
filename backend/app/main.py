"""Aplicación FastAPI principal"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

from app.core.config import settings
from app.db.database import create_tables
from app.routers import auth, characters, chat, images
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service


# Configurar logging
logger.add(
    "logs/aicompanion_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)

# Crear directorio de logs
os.makedirs("logs", exist_ok=True)


def create_application() -> FastAPI:
    """Crear y configurar la aplicación FastAPI"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API para AI Companion - Compañero virtual con IA",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configurar CORS (para el frontend desktop)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar orígenes
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Inicializar base de datos
    create_tables()
    logger.info("Base de datos inicializada")
    
    # Inicializar servicios de IA
    @app.on_event("startup")
    async def startup_event():
        """Inicializar servicios al arrancar"""
        logger.info("Iniciando servicios de IA...")
        
        try:
            await memory_service.initialize(llm_service)
            logger.info("Servicios de IA inicializados correctamente")
        except Exception as e:
            logger.warning(f"Error inicializando servicios de IA: {e}")
            logger.warning("Los servicios de memoria no estarán disponibles")
    
    # Montar archivos estáticos (imágenes, audios)
    os.makedirs(settings.ASSETS_PATH, exist_ok=True)
    os.makedirs(settings.IMAGES_PATH, exist_ok=True)
    os.makedirs(settings.VOICES_PATH, exist_ok=True)
    os.makedirs(settings.CHARACTERS_PATH, exist_ok=True)
    
    app.mount("/assets", StaticFiles(directory=settings.ASSETS_PATH), name="assets")
    
    # Incluir routers
    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(characters.router, prefix=settings.API_PREFIX)
    app.include_router(chat.router, prefix=settings.API_PREFIX)
    app.include_router(images.router, prefix=settings.API_PREFIX)
    
    # Endpoint de health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    
    # Endpoint raíz
    @app.get("/")
    async def root():
        return {
            "message": f"Bienvenido a {settings.APP_NAME} API",
            "docs": "/docs",
            "version": settings.APP_VERSION
        }
    
    logger.info(f"API {settings.APP_NAME} v{settings.APP_VERSION} lista")
    
    return app


# Crear aplicación
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Iniciando servidor en {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
