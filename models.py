from datetime import datetime
from app import db
from sqlalchemy.sql import func

class Conversation(db.Model):
    """Modelo para almacenar conversaciones del chatbot"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.user_message[:50]}...>'
    
    def to_dict(self):
        """Convierte la conversación a diccionario para JSON"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'timestamp': self.timestamp.isoformat()
        }

class ChatSession(db.Model):
    """Modelo para gestionar sesiones de chat"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    last_activity = db.Column(db.DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f'<ChatSession {self.session_id}>'
    
    def update_activity(self):
        """Actualiza la última actividad de la sesión"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
