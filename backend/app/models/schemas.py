"""Esquemas Pydantic para validación de datos"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# === User Schemas ===
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# === Character Schemas ===
class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None
    voice_tone: Optional[str] = None
    relationship_type: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    is_public: bool = False
    is_nsfw: bool = False
    lora_scale: float = Field(default=0.8, ge=0.0, le=1.0)


class CharacterCreate(CharacterBase):
    """Schema para crear personaje"""
    pass


class CharacterUpdate(BaseModel):
    """Schema para actualizar personaje"""
    name: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    appearance: Optional[str] = None
    voice_tone: Optional[str] = None
    relationship_type: Optional[str] = None
    age: Optional[int] = None
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None
    is_nsfw: Optional[bool] = None
    lora_scale: Optional[float] = None


class CharacterResponse(CharacterBase):
    id: int
    owner_id: int
    avatar_url: Optional[str] = None
    system_prompt: Optional[str] = None
    lora_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# === Chat Schemas ===
class ChatBase(BaseModel):
    title: Optional[str] = None


class ChatCreate(ChatBase):
    character_id: int


class ChatResponse(ChatBase):
    id: int
    user_id: int
    character_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# === Message Schemas ===
class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    sender: str = "user"


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    sender: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessageRequest(BaseModel):
    """Request para enviar mensaje al chat"""
    message: str = Field(..., min_length=1)
    generate_image: bool = False
    generate_audio: bool = False
    image_prompt: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Respuesta del chat"""
    user_message: MessageResponse
    character_message: MessageResponse
    context_memories: List[str] = []


# === Image Schemas ===
class ImageGenerationRequest(BaseModel):
    """Request para generar imagen"""
    prompt: str
    character_id: Optional[int] = None
    width: int = 512
    height: int = 512
    steps: int = 30
    guidance_scale: float = 7.5
    use_lora: bool = True
    lora_scale: float = 0.8
    negative_prompt: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    image_url: str
    prompt: str
    width: int
    height: int
    generation_time: float


# === TTS Schemas ===
class TTSRequest(BaseModel):
    """Request para texto a voz"""
    text: str
    voice: Optional[str] = None
    rate: int = 150


class TTSResponse(BaseModel):
    audio_url: str
    duration: float


# === Memory Schemas ===
class MemoryResponse(BaseModel):
    id: int
    content: str
    memory_type: str
    importance: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# === Auth Schemas ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
