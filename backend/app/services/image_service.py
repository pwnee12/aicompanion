"""Servicio de generación de imágenes con Stable Diffusion y LoRA"""

import os
import uuid
import time
import asyncio
import httpx
from typing import Optional, Dict, Any
from PIL import Image
from loguru import logger
from app.core.config import settings


class ImageGenerationService:
    """Servicio para generar imágenes con IA"""
    
    def __init__(self):
        self.provider = settings.IMAGE_PROVIDER
        self.replicate_token = settings.REPLICATE_API_TOKEN
        self.stability_key = settings.STABILITY_API_KEY
        self.use_lora = settings.SD_USE_LORA
        self.lora_path = settings.SD_LORA_PATH
        
    async def generate(
        self,
        prompt: str,
        character_data: Optional[Dict[str, Any]] = None,
        width: int = 512,
        height: int = 512,
        steps: int = 30,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generar imagen a partir de prompt
        
        Args:
            prompt: Descripción de la imagen
            character_data: Datos del personaje para coherencia (LoRA)
            width: Ancho de imagen
            height: Alto de imagen
            steps: Pasos de denoising
            guidance_scale: Qué tanto seguir el prompt
            negative_prompt: Lo que NO debe aparecer
            save_path: Dónde guardar la imagen
        
        Returns:
            Dict con image_url, prompt, dimensions, generation_time
        """
        start_time = time.time()
        
        # Construir prompt completo
        full_prompt = self._build_prompt(prompt, character_data)
        
        # Negative prompt por defecto para mejor calidad
        if not negative_prompt:
            negative_prompt = "ugly, duplicate, low quality, blurry, distorted, deformed"
        
        try:
            if self.provider == "replicate":
                image_data = await self._replicate_generate(
                    full_prompt, negative_prompt, width, height, steps, guidance_scale
                )
            elif self.provider == "stability":
                image_data = await self._stability_generate(
                    full_prompt, negative_prompt, width, height, steps, guidance_scale
                )
            elif self.provider == "local_sd":
                image_data = await self._local_sd_generate(
                    full_prompt, negative_prompt, width, height, steps, guidance_scale,
                    character_data
                )
            else:
                raise ValueError(f"Proveedor de imágenes no válido: {self.provider}")
            
            # Guardar imagen
            image_url = await self._save_image(image_data, save_path)
            
            generation_time = time.time() - start_time
            
            return {
                "image_url": image_url,
                "prompt": full_prompt,
                "width": width,
                "height": height,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"Error generando imagen: {e}")
            raise
    
    def _build_prompt(
        self,
        base_prompt: str,
        character_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construir prompt completo con detalles del personaje"""
        full_prompt = base_prompt
        
        if character_data:
            # Añadir apariencia del personaje
            appearance = character_data.get("appearance", "")
            if appearance:
                full_prompt += f", {appearance}"
            
            # Añadir estilo de ropa si existe
            clothing = character_data.get("clothing_style", "")
            if clothing:
                full_prompt += f", wearing {clothing}"
        
        # Mejorar calidad
        full_prompt += ", high quality, detailed, professional, 4k"
        
        return full_prompt
    
    async def _replicate_generate(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance_scale: float
    ) -> bytes:
        """Generar imagen usando Replicate API (SDXL, etc.)"""
        if not self.replicate_token:
            raise ValueError("Replicate API token no configurado")
        
        headers = {
            "Authorization": f"Bearer {self.replicate_token}",
            "Content-Type": "application/json"
        }
        
        # Usar SDXL con soporte para LoRA
        payload = {
            "version": "ac732df83cea7fff18b8472b5d3e0b3c66d428fd",  # SDXL versión
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "num_inference_steps": steps,
                "guidance_scale": guidance_scale
            }
        }
        
        # Añadir LoRA si está configurado
        if self.use_lora and hasattr(self, 'active_lora'):
            payload["input"]["lora_weights_scale"] = self.active_lora.get("scale", 0.8)
            payload["input"]["lora_path"] = self.active_lora.get("path", "")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Crear predicción
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            prediction = response.json()
            
            # Esperar a que termine
            while prediction["status"] not in ["succeeded", "failed", "canceled"]:
                await asyncio.sleep(2)
                response = await client.get(prediction["urls"]["get"], headers=headers)
                prediction = response.json()
            
            if prediction["status"] == "succeeded":
                image_url = prediction["output"][0]
                # Descargar imagen
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                return img_response.content
            else:
                raise RuntimeError(f"Generación falló: {prediction.get('error', 'Unknown error')}")
    
    async def _stability_generate(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance_scale: float
    ) -> bytes:
        """Generar imagen usando Stability AI API"""
        if not self.stability_key:
            raise ValueError("Stability AI API key no configurada")
        
        headers = {
            "Authorization": f"Bearer {self.stability_key}",
            "Accept": "image/*"
        }
        
        data = {
            "text_prompts[0][text]": prompt,
            "text_prompts[0][weight]": 1.0,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": guidance_scale
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            return response.content
    
    async def _local_sd_generate(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance_scale: float,
        character_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generar imagen usando Stable Diffusion local con LoRA"""
        try:
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            import torch
            
            # Cargar modelo (singleton - debería estar en caché)
            if not hasattr(self, 'pipeline'):
                logger.info("Cargando modelo Stable Diffusion...")
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    settings.SD_MODEL_ID,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipeline.scheduler.config
                )
                
                # Cargar LoRA si existe
                if self.use_lora and character_data and character_data.get("lora_path"):
                    logger.info(f"Cargando LoRA: {character_data['lora_path']}")
                    self.pipeline.load_lora_weights(
                        character_data["lora_path"],
                        adapter_name="character"
                    )
                    self.pipeline.set_adapters(["character"], [character_data.get("lora_scale", 0.8)])
                
                if torch.cuda.is_available():
                    self.pipeline = self.pipeline.to("cuda")
                else:
                    self.pipeline = self.pipeline.to("cpu")
            
            # Generar imagen
            image = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            ).images[0]
            
            # Convertir a bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except ImportError as e:
            logger.error(f"Dependencias de imagen local no instaladas: {e}")
            raise RuntimeError("Stable Diffusion local no disponible. Usa API cloud.")
    
    async def _save_image(self, image_data: bytes, save_path: Optional[str] = None) -> str:
        """Guardar imagen y retornar URL"""
        if save_path is None:
            save_path = settings.IMAGES_PATH
        
        os.makedirs(save_path, exist_ok=True)
        
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(save_path, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # Retornar ruta relativa (el frontend construirá URL completa)
        return f"/assets/images/{filename}"
    
    def set_active_lora(self, lora_path: str, scale: float = 0.8):
        """Configurar LoRA activo para generación"""
        self.active_lora = {"path": lora_path, "scale": scale}
        logger.info(f"LoRA activo: {lora_path} (scale: {scale})")


# Singleton
image_service = ImageGenerationService()
