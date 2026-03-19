"""Router de generación de imágenes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.schemas import (
    ImageGenerationRequest,
    ImageGenerationResponse
)
from app.core.security import decode_access_token
from fastapi import Header
from loguru import logger

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(
    image_data: ImageGenerationRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Generar imagen con IA
    
    Soporta:
    - Prompt personalizado
    - Personaje con LoRA para coherencia
    - Múltiples providers (Replicate, Stability, Local SD)
    """
    from app.db.database import Character
    from app.services.image_service import image_service
    
    # Verificar autenticación (opcional, se puede usar sin auth)
    user_id = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("user_id")
    
    # Si hay character_id, obtener datos del personaje
    character_data = None
    if image_data.character_id:
        character = db.query(Character).filter(
            Character.id == image_data.character_id
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personaje no encontrado"
            )
        
        character_data = {
            "appearance": character.appearance,
            "lora_path": character.lora_path,
            "lora_scale": character.lora_scale
        }
        
        # Configurar LoRA
        if character.lora_path and image_data.use_lora:
            image_service.set_active_lora(
                character.lora_path,
                image_data.lora_scale
            )
    
    try:
        result = await image_service.generate(
            prompt=image_data.prompt,
            character_data=character_data,
            width=image_data.width,
            height=image_data.height,
            steps=image_data.steps,
            guidance_scale=image_data.guidance_scale,
            negative_prompt=image_data.negative_prompt
        )
        
        # Si hay character_id y user_id, guardar en galería
        if image_data.character_id and user_id:
            from app.db.database import CharacterImage
            
            character_image = CharacterImage(
                character_id=image_data.character_id,
                image_url=result["image_url"],
                prompt=image_data.prompt
            )
            db.add(character_image)
            db.commit()
        
        return ImageGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando imagen: {str(e)}"
        )


@router.get("/character/{character_id}")
async def get_character_images(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Obtener galería de imágenes de un personaje"""
    from app.db.database import CharacterImage
    
    images = db.query(CharacterImage).filter(
        CharacterImage.character_id == character_id
    ).order_by(CharacterImage.created_at.desc()).all()
    
    return images
