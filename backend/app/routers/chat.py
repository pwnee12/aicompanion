"""Router de chat - El núcleo de la interacción"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.schemas import (
    ChatCreate,
    ChatResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    MessageResponse
)
from app.core.security import decode_access_token
from fastapi import Header
from datetime import datetime
from loguru import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Crear nueva conversación con un personaje"""
    from app.db.database import Chat
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    # Verificar que el personaje existe
    from app.db.database import Character
    character = db.query(Character).filter(Character.id == chat_data.character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personaje no encontrado"
        )
    
    # Crear chat
    db_chat = Chat(
        user_id=user_id,
        character_id=character.id,
        title=chat_data.title or f"Chat con {character.name}"
    )
    
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    
    return db_chat


@router.get("/", response_model=List[ChatResponse])
async def list_chats(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Listar conversaciones del usuario"""
    from app.db.database import Chat
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at.desc()).all()
    
    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Obtener detalles de una conversación"""
    from app.db.database import Chat
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )
    
    return chat


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Obtener mensajes de una conversación"""
    from app.db.database import Message
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(
        Message.created_at.desc()
    ).limit(limit).all()
    
    return list(reversed(messages))


@router.post("/{chat_id}/message", response_model=ChatMessageResponse)
async def send_message(
    chat_id: int,
    message_data: ChatMessageRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Enviar mensaje y obtener respuesta del personaje
    
    Este es el endpoint principal del chat:
    1. Guarda el mensaje del usuario
    2. Recupera contexto de memoria
    3. Llama al LLM con system prompt + contexto
    4. Genera imagen si se solicita
    5. Genera audio TTS si se solicita
    6. Guarda respuesta del personaje
    """
    from app.db.database import Chat, Message, Character
    from app.services.llm_service import llm_service
    from app.services.memory_service import memory_service
    from app.services.image_service import image_service
    from app.services.tts_service import tts_service
    
    # Verificar autenticación
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    # Obtener chat y personaje
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )
    
    if chat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta conversación"
        )
    
    character = db.query(Character).filter(Character.id == chat.character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personaje no encontrado"
        )
    
    # === PASO 1: Guardar mensaje del usuario ===
    user_message = Message(
        chat_id=chat_id,
        sender="user",
        content=message_data.message
    )
    db.add(user_message)
    db.commit()
    
    # === PASO 2: Obtener contexto de memoria ===
    context = await memory_service.get_context_for_message(
        message=message_data.message,
        user_id=user_id,
        character_id=character.id
    )
    
    # === PASO 3: Construir mensajes para el LLM ===
    # Obtener historial reciente (últimos 10 mensajes)
    recent_messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(
        Message.created_at.desc()
    ).limit(10).all()
    
    # Formatear para LLM
    llm_messages = []
    for msg in reversed(recent_messages):
        role = "user" if msg.sender == "user" else "assistant"
        llm_messages.append({"role": role, "content": msg.content})
    
    # Añadir mensaje actual
    llm_messages.append({"role": "user", "content": message_data.message})
    
    # === PASO 4: Inyectar contexto en el system prompt ===
    system_prompt = character.system_prompt or ""
    
    if context:
        system_prompt += f"\n\nContexto importante de conversaciones anteriores:\n{context}"
    
    logger.info(f"System prompt length: {len(system_prompt)}")
    
    # === PASO 5: Llamar al LLM ===
    try:
        character_response_text = await llm_service.chat(
            messages=llm_messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
    except Exception as e:
        logger.error(f"Error llamando al LLM: {e}")
        # Rollback del mensaje del usuario
        db.delete(user_message)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando respuesta: {str(e)}"
        )
    
    # === PASO 6: Generar imagen si se solicita ===
    image_url = None
    if message_data.generate_image:
        try:
            # Construir prompt para imagen
            image_prompt = message_data.image_prompt or character_response_text
            
            # Si el personaje tiene LoRA, usarlo
            character_data = None
            if character.lora_path:
                character_data = {
                    "appearance": character.appearance,
                    "lora_path": character.lora_path,
                    "lora_scale": character.lora_scale
                }
            
            # Configurar LoRA activo
            if character.lora_path:
                image_service.set_active_lora(character.lora_path, character.lora_scale)
            
            result = await image_service.generate(
                prompt=image_prompt,
                character_data=character_data,
                width=512,
                height=512
            )
            image_url = result["image_url"]
            
        except Exception as e:
            logger.error(f"Error generando imagen: {e}")
            # No fallar el chat, solo no incluir imagen
    
    # === PASO 7: Generar audio TTS si se solicita ===
    audio_url = None
    if message_data.generate_audio:
        try:
            tts_result = await tts_service.synthesize(
                text=character_response_text,
                voice=character.voice_tone
            )
            audio_url = tts_result["audio_url"]
            
        except Exception as e:
            logger.error(f"Error generando audio: {e}")
            # No fallar el chat, solo no incluir audio
    
    # === PASO 8: Guardar respuesta del personaje ===
    character_message = Message(
        chat_id=chat_id,
        sender="character",
        content=character_response_text,
        image_url=image_url,
        audio_url=audio_url
    )
    db.add(character_message)
    
    # Actualizar timestamp del chat
    chat.updated_at = datetime.utcnow()
    
    db.commit()
    
    # === PASO 9: Guardar en memoria (async, no bloquear) ===
    # Guardar hechos importantes mencionados
    # Esto se podría mejorar con NLP para extraer entidades
    try:
        await memory_service.add_memory(
            content=f"Usuario dijo: {message_data.message}",
            user_id=user_id,
            character_id=character.id,
            memory_type="event",
            importance=0.5
        )
    except Exception as e:
        logger.error(f"Error guardando en memoria: {e}")
    
    # === PASO 10: Retornar respuesta ===
    return ChatMessageResponse(
        user_message=MessageResponse(
            id=user_message.id,
            chat_id=chat_id,
            sender="user",
            content=message_data.message,
            created_at=user_message.created_at
        ),
        character_message=MessageResponse(
            id=character_message.id,
            chat_id=chat_id,
            sender="character",
            content=character_response_text,
            image_url=image_url,
            audio_url=audio_url,
            created_at=character_message.created_at
        ),
        context_memories=[context] if context else []
    )


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Eliminar conversación"""
    from app.db.database import Chat
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )
    
    if chat.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta conversación"
        )
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Conversación eliminada correctamente"}
