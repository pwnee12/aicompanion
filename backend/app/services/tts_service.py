"""Servicio de Texto a Voz (TTS)"""

import os
import uuid
import asyncio
from typing import Optional, Dict
from loguru import logger
from app.core.config import settings


class TTSService:
    """Servicio para convertir texto a audio"""
    
    def __init__(self):
        self.provider = settings.TTS_PROVIDER
        self.default_voice = settings.TTS_DEFAULT_VOICE
        self.default_rate = settings.TTS_DEFAULT_RATE
        
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Convertir texto a audio
        
        Args:
            text: Texto a convertir
            voice: Voz a usar (ej: "en-US-AriaNeural")
            rate: Velocidad (palabras por minuto)
            save_path: Dónde guardar el audio
        
        Returns:
            Dict con audio_url y duration
        """
        voice = voice or self.default_voice
        rate = rate or self.default_rate
        
        if save_path is None:
            save_path = settings.VOICES_PATH
        
        os.makedirs(save_path, exist_ok=True)
        
        try:
            if self.provider == "edge":
                audio_data = await self._edge_tts(text, voice, rate)
            elif self.provider == "gtts":
                audio_data = await self._gtts(text, voice)
            elif self.provider == "coqui":
                audio_data = await self._coqui_tts(text, voice)
            else:
                raise ValueError(f"Proveedor TTS no válido: {self.provider}")
            
            # Guardar audio
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(save_path, filename)
            
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            # Calcular duración aproximada
            duration = len(text) / (rate * 0.01)  # Estimación rough
            
            return {
                "audio_url": f"/assets/voices/{filename}",
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Error en TTS: {e}")
            raise
    
    async def _edge_tts(self, text: str, voice: str, rate: int) -> bytes:
        """Usar Edge TTS (Microsoft Azure, gratis)"""
        import edge_tts
        
        # Ajustar rate al formato de edge-tts
        rate_str = f"+{rate - 100}%" if rate > 100 else f"{rate - 100}%"
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    async def _gtts(self, text: str, voice: str) -> bytes:
        """Usar Google TTS"""
        from gtts import gTTS
        import io
        
        # Extraer idioma de la voz (ej: "en-US" -> "en")
        lang = voice.split("-")[0] if "-" in voice else "en"
        
        tts = gTTS(text=text, lang=lang)
        
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.read()
    
    async def _coqui_tts(self, text: str, voice: str) -> bytes:
        """Usar Coqui TTS (local, más voces)"""
        try:
            from TTS.api import TTS
            import torch
            import io
            
            # Cargar modelo (singleton)
            if not hasattr(self, 'tts_model'):
                logger.info("Cargando modelo Coqui TTS...")
                self.tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                
                if torch.cuda.is_available():
                    self.tts_model.to("cuda")
            
            # Generar audio
            audio_buffer = io.BytesIO()
            self.tts_model.tts_to_file(text=text, file_path=audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.read()
            
        except ImportError:
            logger.error("Coqui TTS no instalado")
            raise RuntimeError("Coqui TTS no disponible")


# Singleton
tts_service = TTSService()
