"""Servicio de LLM - Soporta múltiples proveedores (híbrido)"""

import httpx
from typing import Optional, List, Dict, Any
from loguru import logger
from app.core.config import settings


class LLMService:
    """Servicio para interactuar con modelos de lenguaje"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> str:
        """
        Enviar mensaje al LLM y obtener respuesta
        
        Args:
            messages: Lista de mensajes [{role: "user|assistant", content: "..."}]
            system_prompt: Instrucción de sistema para el personaje
            temperature: Creatividad (0-1)
            max_tokens: Máximo de tokens en respuesta
            stream: Si True, responde en streaming
        
        Returns:
            Respuesta del modelo como string
        """
        if self.provider == "hybrid":
            # Usar Ollama para desarrollo, OpenAI para producción
            try:
                return await self._ollama_chat(messages, system_prompt, temperature, max_tokens)
            except Exception as e:
                logger.warning(f"Ollama falló, usando OpenAI: {e}")
                if self.openai_api_key:
                    return await self._openai_chat(messages, system_prompt, temperature, max_tokens)
                raise RuntimeError("No hay proveedor LLM disponible")
        
        elif self.provider == "openai":
            return await self._openai_chat(messages, system_prompt, temperature, max_tokens)
        
        elif self.provider == "anthropic":
            return await self._anthropic_chat(messages, system_prompt, temperature, max_tokens)
        
        elif self.provider == "ollama":
            return await self._ollama_chat(messages, system_prompt, temperature, max_tokens)
        
        else:
            raise ValueError(f"Proveedor LLM no válido: {self.provider}")
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Chat con OpenAI GPT"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key no configurada")
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Construir mensajes con system prompt
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        api_messages.extend(messages)
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Chat con Anthropic Claude"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key no configurada")
        
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "system": system_prompt or "",
            "messages": messages
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    async def _ollama_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Chat con Ollama (modelo local)"""
        # Construir prompt con system prompt
        full_prompt = ""
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            full_prompt += f"{role.capitalize()}: {content}\n"
        
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["response"]
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generar embedding para texto"""
        if self.provider == "openai" or self.openai_api_key:
            return await self._openai_embedding(text)
        else:
            return await self._ollama_embedding(text)
    
    async def _openai_embedding(self, text: str) -> List[float]:
        """Generar embedding con OpenAI"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.OPENAI_EMBEDDING_MODEL,
            "input": text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    
    async def _ollama_embedding(self, text: str) -> List[float]:
        """Generar embedding con Ollama"""
        payload = {
            "model": settings.OLLAMA_EMBEDDING_MODEL,
            "prompt": text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/embeddings",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]


# Singleton
llm_service = LLMService()
