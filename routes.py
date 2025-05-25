import uuid
import json
import logging
from flask import render_template, request, session, jsonify, redirect, url_for
from app import app
from chat_service import chat_service

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Página principal del chatbot"""
    # Generar o recuperar session_id
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    """Endpoint para enviar mensajes al chatbot"""
    try:
        # Obtener el mensaje del usuario
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Mensaje no proporcionado'
            }), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'El mensaje no puede estar vacío'
            }), 400
        
        # Obtener session_id
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Generar respuesta usando el servicio de chat
        ai_response = chat_service.generate_response(user_message, session_id)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error en send_message: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@app.route('/conversation_history')
def conversation_history():
    """Obtiene el historial de conversación de la sesión actual"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': True,
                'conversations': []
            })
        
        conversations = chat_service.get_conversation_history(session_id)
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({
            'success': False,
            'error': 'Error obteniendo historial'
        }), 500

@app.route('/new_chat')
def new_chat():
    """Inicia una nueva conversación"""
    # Limpiar la sesión actual
    session.pop('session_id', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return render_template('index.html'), 500
