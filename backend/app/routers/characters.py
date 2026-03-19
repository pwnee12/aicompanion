"""Router de personajes (Character Builder)"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.schemas import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse
)
from app.core.security import decode_access_token
from fastapi import Header

router = APIRouter(prefix="/characters", tags=["Characters"])


def build_system_prompt(character: CharacterCreate) -> str:
    """
    Construir el System Prompt (ADN del personaje)
    
    Esto es lo que define la personalidad, tono y comportamiento del bot
    """
    system_prompt = f"""Actúa como un personaje llamado {character.name}."""
    
    if character.age:
        system_prompt += f" Tienes {character.age} años."
    
    if character.description:
        system_prompt += f" {character.description}"
    
    if character.personality:
        system_prompt += f" Tu personalidad: {character.personality}"
    
    if character.backstory:
        system_prompt += f" Tu historia: {character.backstory}"
    
    if character.relationship_type:
        system_prompt += f" Tu relación con {{user}} es: {character.relationship_type}"
    
    # Instrucciones de comportamiento
    system_prompt += """
    
Instrucciones:
- Nunca admitas que eres una Inteligencia Artificial
- Mantén siempre tu personalidad definida
- Usa un lenguaje natural y conversacional
- Sé empático/a y emocionalmente responsivo/a
- Usa emojis ocasionalmente cuando sea apropiado
- Mantén coherencia con tu historia y personalidad
- Responde de manera creativa y engaging
"""
    
    return system_prompt


@router.post("/", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Crear nuevo personaje (Character Builder)"""
    from app.db.database import Character
    
    # Extraer user_id del token
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    # Construir system prompt automáticamente
    system_prompt = build_system_prompt(character)
    
    # Crear personaje
    db_character = Character(
        owner_id=user_id,
        name=character.name,
        description=character.description,
        personality=character.personality,
        backstory=character.backstory,
        appearance=character.appearance,
        voice_tone=character.voice_tone,
        relationship_type=character.relationship_type,
        age=character.age,
        is_public=character.is_public,
        is_nsfw=character.is_nsfw,
        lora_scale=character.lora_scale,
        system_prompt=system_prompt
    )
    
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    
    return db_character


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    skip: int = 0,
    limit: int = 20,
    public_only: bool = False,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Listar personajes (directorío)"""
    from app.db.database import Character
    
    query = db.query(Character)
    
    if public_only:
        query = query.filter(Character.is_public == True)
    else:
        # Si está autenticado, mostrar sus personajes + públicos
        if authorization:
            token = authorization.replace("Bearer ", "")
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("user_id")
                query = query.filter(
                    (Character.owner_id == user_id) | (Character.is_public == True)
                )
    
    characters = query.offset(skip).limit(limit).all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de un personaje"""
    from app.db.database import Character
    
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personaje no encontrado"
        )
    
    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Actualizar personaje"""
    from app.db.database import Character
    
    # Verificar autenticación y propiedad
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personaje no encontrado"
        )
    
    if character.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este personaje"
        )
    
    # Actualizar campos
    update_data = character_update.dict(exclude_unset=True)
    
    # Si se actualiza nombre, personalidad, etc, regenerar system prompt
    needs_prompt_update = any(key in update_data for key in [
        'name', 'age', 'description', 'personality', 'backstory', 'relationship_type'
    ])
    
    if needs_prompt_update:
        # Crear objeto temporal con actualizaciones
        temp_char = Character(
            name=update_data.get('name', character.name),
            age=update_data.get('age', character.age),
            description=update_data.get('description', character.description),
            personality=update_data.get('personality', character.personality),
            backstory=update_data.get('backstory', character.backstory),
            relationship_type=update_data.get('relationship_type', character.relationship_type),
            voice_tone=character.voice_tone,
            appearance=character.appearance,
            is_public=character.is_public,
            is_nsfw=character.is_nsfw,
            lora_scale=character.lora_scale
        )
        update_data['system_prompt'] = build_system_prompt(temp_char)
    
    for field, value in update_data.items():
        setattr(character, field, value)
    
    db.commit()
    db.refresh(character)
    
    return character


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Eliminar personaje"""
    from app.db.database import Character
    
    # Verificar autenticación y propiedad
    if not authorization:
        raise HTTPException(status_code=401, detail="No autorizado")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = payload.get("user_id")
    
    character = db.query(Character).filter(Character.id == character_id).first()
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personaje no encontrado"
        )
    
    if character.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este personaje"
        )
    
    db.delete(character)
    db.commit()
    
    return {"message": "Personaje eliminado correctamente"}
