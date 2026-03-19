"""Servicio de memoria contextual con base de datos vectorial"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings


class MemoryService:
    """
    Servicio de memoria contextual usando base de datos vectorial
    
    Funcionamiento:
    1. Convierte mensajes/emociones a vectores (embeddings)
    2. Guarda en ChromaDB/Pinecone con metadata
    3. Busca por similitud cuando el usuario pregunta algo
    4. Inyecta contexto relevante en el LLM
    """
    
    def __init__(self):
        self.db_type = settings.VECTOR_DB_TYPE
        self.client = None
        self.collection = None
        self._initialized = False
        
    async def initialize(self, llm_service):
        """Inicializar conexión a vector DB"""
        if self._initialized:
            return
        
        try:
            if self.db_type == "chroma":
                await self._init_chroma()
            elif self.db_type == "pinecone":
                await self._init_pinecone()
            
            self.llm_service = llm_service
            self._initialized = True
            logger.info(f"Vector DB ({self.db_type}) inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando vector DB: {e}")
            raise
    
    async def _init_chroma(self):
        """Inicializar ChromaDB local"""
        import chromadb
        from chromadb.config import Settings
        
        # Crear cliente persistente
        chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )
        
        # Crear o obtener colección
        self.collection = chroma_client.get_or_create_collection(
            name="ai_companion_memories",
            metadata={"hnsw:space": "cosine"}  # Similitud coseno
        )
        
        logger.info("ChromaDB inicializado")
    
    async def _init_pinecone(self):
        """Inicializar Pinecone (cloud)"""
        from pinecone import Pinecone
        
        if not settings.PINECONE_API_KEY:
            raise ValueError("Pinecone API key no configurada")
        
        pc = Pinecone(
            api_key=settings.PINECONE_API_KEY,
            environment=settings.PINECONE_ENVIRONMENT
        )
        
        # Crear o obtener índice
        index_name = "ai-companion-memories"
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine"
            )
        
        self.collection = pc.Index(index_name)
        logger.info("Pinecone inicializado")
    
    async def add_memory(
        self,
        content: str,
        user_id: int,
        character_id: Optional[int] = None,
        memory_type: str = "fact",
        importance: float = 0.5
    ) -> Dict[str, Any]:
        """
        Añadir recuerdo a la base de datos vectorial
        
        Args:
            content: Contenido del recuerdo (texto)
            user_id: ID del usuario
            character_id: ID del personaje (opcional)
            memory_type: Tipo (fact, preference, event, emotion)
            importance: Importancia (0-1)
        
        Returns:
            Dict con memory_id y status
        """
        if not self._initialized:
            await self.initialize()
        
        # Generar embedding
        embedding = await self.llm_service.generate_embedding(content)
        
        # Crear metadata
        metadata = {
            "user_id": user_id,
            "character_id": character_id or 0,
            "memory_type": memory_type,
            "importance": importance,
            "content": content  # Guardar texto original también
        }
        
        # Generar ID único
        memory_id = f"mem_{user_id}_{character_id or 0}_{asyncio.get_event_loop().time()}"
        
        # Guardar en vector DB
        if self.db_type == "chroma":
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
        elif self.db_type == "pinecone":
            self.collection.upsert(
                vectors=[(memory_id, embedding, metadata)]
            )
        
        logger.info(f"Memoria añadida: {memory_id} (tipo: {memory_type})")
        
        return {
            "memory_id": memory_id,
            "status": "success"
        }
    
    async def search_memories(
        self,
        query: str,
        user_id: int,
        character_id: Optional[int] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Buscar recuerdos relevantes por similitud
        
        Args:
            query: Pregunta o texto de búsqueda
            user_id: ID del usuario
            character_id: ID del personaje
            top_k: Cuántos recuerdos retornar
            similarity_threshold: Mínimo de similitud

        Returns:
            Lista de recuerdos relevantes
        """
        if not self._initialized:
            await self.initialize()

        # Generar embedding de la query
        try:
            query_embedding = await self.llm_service.generate_embedding(query)
        except Exception as e:
            logger.warning(f"No se pudo generar embedding: {e}")
            return []  # Retornar vacío si falla el embedding
        
        # Buscar en vector DB
        if self.db_type == "chroma":
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2  # Pedir más para filtrar después
            )
            
            # Procesar resultados
            memories = []
            for i, id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if "distances" in results else 0
                similarity = 1 - distance  # Convertir distancia a similitud
                
                if similarity >= similarity_threshold:
                    metadata = results["metadatas"][0][i]
                    memories.append({
                        "id": id,
                        "content": metadata.get("content", ""),
                        "memory_type": metadata.get("memory_type", "fact"),
                        "importance": metadata.get("importance", 0.5),
                        "similarity": similarity
                    })
        
        elif self.db_type == "pinecone":
            # Filtrar por user_id
            filter_dict = {"user_id": user_id}
            if character_id:
                filter_dict["character_id"] = character_id
            
            results = self.collection.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            memories = []
            for match in results["matches"]:
                if match["score"] >= similarity_threshold:
                    metadata = match["metadata"]
                    memories.append({
                        "id": match["id"],
                        "content": metadata.get("content", ""),
                        "memory_type": metadata.get("memory_type", "fact"),
                        "importance": metadata.get("importance", 0.5),
                        "similarity": match["score"]
                    })
        
        # Ordenar por importancia y similitud
        memories.sort(key=lambda x: x["similarity"] * x["importance"], reverse=True)
        
        logger.info(f"Búsqueda de memorias: {len(memories)} resultados encontrados")
        
        return memories[:top_k]  # Retornar top_k después de filtrar
    
    async def get_context_for_message(
        self,
        message: str,
        user_id: int,
        character_id: Optional[int] = None
    ) -> str:
        """
        Obtener contexto inyectable para el LLM

        Esto es lo que se "susurra" al bot en cada mensaje:
        - Recuerdos relevantes del usuario
        - Preferencias guardadas
        - Eventos importantes

        Args:
            message: Mensaje actual del usuario
            user_id: ID del usuario
            character_id: ID del personaje

        Returns:
            String con contexto para inyectar en el system prompt
        """
        try:
            memories = await self.search_memories(
                query=message,
                user_id=user_id,
                character_id=character_id,
                top_k=settings.MEMORY_TOP_K,
                similarity_threshold=settings.MEMORY_SIMILARITY_THRESHOLD
            )
        except Exception as e:
            logger.warning(f"Error buscando memorias: {e}")
            memories = []
        
        if not memories:
            return ""
        
        # Construir contexto
        context_parts = []
        
        for mem in memories:
            if mem["memory_type"] == "fact":
                context_parts.append(f"• Hecho: {mem['content']}")
            elif mem["memory_type"] == "preference":
                context_parts.append(f"• Preferencia: {mem['content']}")
            elif mem["memory_type"] == "event":
                context_parts.append(f"• Evento pasado: {mem['content']}")
            elif mem["memory_type"] == "emotion":
                context_parts.append(f"• Emoción recordada: {mem['content']}")
        
        context = "\n".join(context_parts)
        
        logger.info(f"Contexto generado: {len(context)} caracteres")
        
        return context
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Eliminar un recuerdo"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if self.db_type == "chroma":
                self.collection.delete(ids=[memory_id])
            elif self.db_type == "pinecone":
                self.collection.delete(ids=[memory_id])
            
            logger.info(f"Memoria eliminada: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando memoria: {e}")
            return False
    
    async def get_all_memories(
        self,
        user_id: int,
        character_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtener todos los recuerdos de un usuario"""
        # Nota: Esto puede ser lento en grandes volúmenes
        # En producción, usar paginación o filtros más eficientes
        if not self._initialized:
            await self.initialize()
        
        # Implementación simplificada - en producción usar filtros nativos
        all_memories = []
        
        # ChromaDB no tiene un método simple "get all with filter"
        # Esto es una implementación básica
        if self.db_type == "chroma":
            # Obtener todo (puede ser mucho)
            results = self.collection.get(include=["metadatas"])
            
            for i, metadata in enumerate(results["metadatas"]):
                if metadata.get("user_id") == user_id:
                    if character_id is None or metadata.get("character_id") == character_id:
                        all_memories.append({
                            "id": results["ids"][i],
                            "content": metadata.get("content", ""),
                            "memory_type": metadata.get("memory_type", "fact"),
                            "importance": metadata.get("importance", 0.5)
                        })
        
        return all_memories


# Singleton
memory_service = MemoryService()
