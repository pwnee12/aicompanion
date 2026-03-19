"""Base de datos y modelos SQLAlchemy"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")


class Character(Base):
    """Modelo de personaje"""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    personality = Column(Text)
    backstory = Column(Text)
    appearance = Column(Text)
    voice_tone = Column(String(100))
    relationship_type = Column(String(50))  # friend, romantic, mentor, etc.
    age = Column(Integer)
    avatar_url = Column(String(255))
    system_prompt = Column(Text)  # El "ADN" del personaje
    is_public = Column(Boolean, default=False)
    is_nsfw = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # LoRA config para coherencia visual
    lora_path = Column(String(255))
    lora_scale = Column(Float, default=0.8)
    
    # Relaciones
    owner = relationship("User", back_populates="characters")
    chats = relationship("Chat", back_populates="character", cascade="all, delete-orphan")
    images = relationship("CharacterImage", back_populates="character", cascade="all, delete-orphan")


class Chat(Base):
    """Modelo de conversación"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="chats")
    character = relationship("Character", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    """Modelo de mensaje"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "user" o "character"
    content = Column(Text, nullable=False)
    image_url = Column(String(255))  # URL de imagen generada (si aplica)
    audio_url = Column(String(255))  # URL de audio TTS (si aplica)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    chat = relationship("Chat", back_populates="messages")


class CharacterImage(Base):
    """Galería de imágenes del personaje"""
    __tablename__ = "character_images"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    prompt = Column(Text)  # Prompt usado para generar
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    character = relationship("Character", back_populates="images")


class Memory(Base):
    """Memoria contextual (metadata para vector DB)"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(100))  # ID en la vector DB
    memory_type = Column(String(50))  # "fact", "preference", "event", "emotion"
    importance = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
