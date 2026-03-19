import os
from pydantic_settings import BaseSettings
from typing import Optional, Literal


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # App Info
    APP_NAME: str = "AI Companion"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aicompanion.db"
    # Para PostgreSQL en producción:
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/aicompanion"
    
    # Vector Database
    VECTOR_DB_TYPE: Literal["chroma", "pinecone"] = "chroma"
    CHROMA_DB_PATH: str = "./vector_db"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    
    # LLM Settings
    LLM_PROVIDER: Literal["openai", "anthropic", "ollama", "hybrid"] = "hybrid"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # Image Generation
    IMAGE_PROVIDER: Literal["stability", "replicate", "local_sd"] = "replicate"
    STABILITY_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    
    # Local Stable Diffusion
    SD_MODEL_ID: str = "runwayml/stable-diffusion-v1-5"
    SD_USE_LORA: bool = True
    SD_LORA_PATH: Optional[str] = "./models/lora"
    
    # Image Settings
    IMAGE_DEFAULT_WIDTH: int = 512
    IMAGE_DEFAULT_HEIGHT: int = 512
    IMAGE_DEFAULT_STEPS: int = 30
    IMAGE_DEFAULT_GUIDANCE: float = 7.5
    
    # TTS Settings
    TTS_PROVIDER: Literal["edge", "coqui", "gtts"] = "edge"
    TTS_DEFAULT_VOICE: str = "en-US-AriaNeural"
    TTS_DEFAULT_RATE: int = 150
    
    # File Storage
    ASSETS_PATH: str = "./assets"
    IMAGES_PATH: str = "./assets/images"
    VOICES_PATH: str = "./assets/voices"
    CHARACTERS_PATH: str = "./assets/characters"
    
    # Memory Settings
    MEMORY_TOP_K: int = 5  # Número de recuerdos a recuperar
    MEMORY_SIMILARITY_THRESHOLD: float = 0.7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
