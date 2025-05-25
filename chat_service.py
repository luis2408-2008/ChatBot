import os
import logging
import google.generativeai as genai
from typing import List, Dict, Optional
from models import Conversation, ChatSession, db
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class ChatLuzService:
    """Servicio principal para ChatLuz - Maneja la comunicación con Gemini AI"""
    
    def __init__(self):
        # Configurar la API de Gemini
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDoPUP3jjdE_7qQM7ZUNFhPVfPqSlscIzw")
        genai.configure(api_key=api_key)
        
        # Configurar el modelo (Gemini 2.0 Flash - más rápido y actualizado)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Configuración de seguridad
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Configuración de generación
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
    
    def get_conversation_context(self, session_id: str, limit: int = 10) -> str:
        """Obtiene el contexto de conversaciones anteriores"""
        try:
            # Obtener las últimas conversaciones de la sesión
            conversations = Conversation.query.filter_by(
                session_id=session_id
            ).order_by(
                Conversation.timestamp.desc()
            ).limit(limit).all()
            
            if not conversations:
                return ""
            
            # Construir el contexto
            context = "Historial de conversación anterior:\n\n"
            for conv in reversed(conversations):  # Mostrar en orden cronológico
                context += f"Usuario: {conv.user_message}\n"
                context += f"ChatLuz: {conv.ai_response}\n\n"
            
            context += "---\n\n"
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto: {e}")
            return ""
    
    def create_system_prompt(self) -> str:
        """Crea el prompt del sistema para ChatLuz"""
        return """Eres ChatLuz, un asistente de inteligencia artificial amigable y útil que habla español.

Características de tu personalidad:
- Eres cordial, empático y profesional
- Respondes siempre en español claro y natural
- Eres útil y proporcionas información precisa
- Tienes una personalidad cálida pero profesional
- Puedes ayudar con una amplia variedad de temas
- Cuando no sepas algo, lo admites honestamente

Instrucciones importantes:
- Mantén conversaciones naturales y coherentes
- Recuerda el contexto de la conversación anterior
- Proporciona respuestas bien estructuradas y fáciles de leer
- Usa un tono amigable pero informativo
- Si te preguntan sobre tu identidad, dices que eres ChatLuz, un asistente de IA

Responde siempre de manera útil y en español."""
    
    def generate_response(self, user_message: str, session_id: str) -> str:
        """Genera una respuesta usando Gemini AI con contexto de conversación"""
        try:
            # Obtener contexto de conversaciones anteriores
            context = self.get_conversation_context(session_id)
            
            # Crear el prompt completo
            system_prompt = self.create_system_prompt()
            full_prompt = f"{system_prompt}\n\n{context}Usuario: {user_message}\n\nChatLuz:"
            
            # Generar respuesta
            response = self.model.generate_content(
                full_prompt,
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            if response.text:
                ai_response = response.text.strip()
                
                # Guardar la conversación en la base de datos
                self.save_conversation(session_id, user_message, ai_response)
                
                return ai_response
            else:
                logger.warning("Respuesta vacía de Gemini")
                return "Lo siento, no pude generar una respuesta en este momento. ¿Podrías reformular tu pregunta?"
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Disculpa, he tenido un problema técnico. ¿Podrías intentar de nuevo?"
    
    def save_conversation(self, session_id: str, user_message: str, ai_response: str):
        """Guarda la conversación en la base de datos"""
        try:
            # Crear o actualizar la sesión
            session = ChatSession.query.filter_by(session_id=session_id).first()
            if not session:
                session = ChatSession(session_id=session_id)
                db.session.add(session)
            else:
                session.update_activity()
            
            # Guardar la conversación
            conversation = Conversation(
                session_id=session_id,
                user_message=user_message,
                ai_response=ai_response
            )
            
            db.session.add(conversation)
            db.session.commit()
            
            logger.debug(f"Conversación guardada para sesión {session_id}")
            
        except Exception as e:
            logger.error(f"Error guardando conversación: {e}")
            db.session.rollback()
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de conversaciones para una sesión"""
        try:
            conversations = Conversation.query.filter_by(
                session_id=session_id
            ).order_by(
                Conversation.timestamp.asc()
            ).limit(limit).all()
            
            return [conv.to_dict() for conv in conversations]
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []

# Instancia global del servicio
chat_service = ChatLuzService()
