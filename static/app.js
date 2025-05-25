/**
 * ChatLuz - Aplicación de Chat con IA
 * JavaScript para manejar la interfaz de usuario y comunicación con el backend
 */

class ChatLuzApp {
    constructor() {
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.welcomeMessage = document.getElementById('welcomeMessage');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.charCounter = document.getElementById('charCounter');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.errorModal = document.getElementById('errorModal');
        this.errorMessage = document.getElementById('errorMessage');
        this.closeErrorModal = document.getElementById('closeErrorModal');
        
        this.isLoading = false;
        this.maxLength = 2000;
        
        this.initializeEventListeners();
        this.loadConversationHistory();
        this.focusInput();
    }

    initializeEventListeners() {
        // Envío de mensajes
        this.messageForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Nueva conversación
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Contador de caracteres
        this.messageInput.addEventListener('input', () => this.updateCharCounter());
        
        // Enter para enviar (Shift+Enter para nueva línea)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit(e);
            }
        });
        
        // Cerrar modal de error
        this.closeErrorModal.addEventListener('click', () => this.hideErrorModal());
        
        // Auto-resize del input
        this.messageInput.addEventListener('input', () => this.autoResizeInput());
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isLoading) return;
        
        const message = this.messageInput.value.trim();
        if (!message) {
            this.showError('Por favor, escribe un mensaje antes de enviar.');
            return;
        }
        
        if (message.length > this.maxLength) {
            this.showError(`El mensaje es demasiado largo. Máximo ${this.maxLength} caracteres.`);
            return;
        }
        
        try {
            this.setLoading(true);
            this.hideWelcomeMessage();
            
            // Agregar mensaje del usuario
            this.addMessage(message, 'user');
            
            // Limpiar input
            this.messageInput.value = '';
            this.updateCharCounter();
            
            // Mostrar indicador de escritura
            this.showTypingIndicator();
            
            // Enviar mensaje al servidor
            const response = await this.sendMessage(message);
            
            // Ocultar indicador de escritura
            this.hideTypingIndicator();
            
            if (response.success) {
                // Agregar respuesta de la IA
                this.addMessage(response.response, 'ai');
            } else {
                this.showError(response.error || 'Error al enviar el mensaje.');
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.showError('Error de conexión. Por favor, verifica tu conexión a internet.');
        } finally {
            this.setLoading(false);
            this.focusInput();
        }
    }

    async sendMessage(message) {
        const response = await fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start space-x-3 ${type === 'user' ? 'justify-end' : 'justify-start'}`;
        
        const timestamp = new Date().toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="flex flex-col items-end max-w-xs sm:max-w-md lg:max-w-lg">
                    <div class="message-bubble user">
                        <p class="text-sm">${this.formatMessage(content)}</p>
                    </div>
                    <div class="message-timestamp text-right">${timestamp}</div>
                </div>
                <div class="message-avatar user">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar ai">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="flex flex-col max-w-xs sm:max-w-md lg:max-w-lg">
                    <div class="message-bubble ai">
                        <p class="text-sm">${this.formatMessage(content)}</p>
                    </div>
                    <div class="message-timestamp">${timestamp}</div>
                </div>
            `;
        }
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Escapar HTML y convertir enlaces y saltos de línea
        const escaped = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        
        // Convertir saltos de línea a <br>
        const withBreaks = escaped.replace(/\n/g, '<br>');
        
        // Convertir URLs a enlaces (simple)
        const withLinks = withBreaks.replace(
            /(https?:\/\/[^\s<>"]+)/gi,
            '<a href="$1" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">$1</a>'
        );
        
        return withLinks;
    }

    showTypingIndicator() {
        this.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.classList.add('hidden');
    }

    hideWelcomeMessage() {
        if (this.welcomeMessage) {
            this.welcomeMessage.style.display = 'none';
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.messageInput.disabled = loading;
        
        if (loading) {
            this.sendButton.innerHTML = `
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Enviando...</span>
            `;
        } else {
            this.sendButton.innerHTML = `
                <i class="fas fa-paper-plane"></i>
                <span>Enviar</span>
            `;
        }
    }

    updateCharCounter() {
        const currentLength = this.messageInput.value.length;
        this.charCounter.textContent = `${currentLength}/${this.maxLength}`;
        
        if (currentLength > this.maxLength * 0.9) {
            this.charCounter.classList.add('near-limit');
        } else {
            this.charCounter.classList.remove('near-limit');
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    focusInput() {
        setTimeout(() => {
            if (!this.isLoading) {
                this.messageInput.focus();
            }
        }, 100);
    }

    autoResizeInput() {
        // Reset height to calculate new height
        this.messageInput.style.height = 'auto';
        const maxHeight = 120; // Max height in pixels
        const newHeight = Math.min(this.messageInput.scrollHeight, maxHeight);
        this.messageInput.style.height = newHeight + 'px';
    }

    async loadConversationHistory() {
        try {
            this.showLoadingOverlay();
            
            const response = await fetch('/conversation_history');
            const data = await response.json();
            
            if (data.success && data.conversations.length > 0) {
                this.hideWelcomeMessage();
                
                // Cargar mensajes del historial
                data.conversations.forEach(conv => {
                    this.addMessage(conv.user_message, 'user');
                    this.addMessage(conv.ai_response, 'ai');
                });
            }
            
        } catch (error) {
            console.error('Error cargando historial:', error);
            // No mostrar error al usuario, el historial es opcional
        } finally {
            this.hideLoadingOverlay();
        }
    }

    startNewChat() {
        if (confirm('¿Estás seguro de que quieres iniciar una nueva conversación? Se perderá el historial actual.')) {
            window.location.href = '/new_chat';
        }
    }

    showLoadingOverlay() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoadingOverlay() {
        this.loadingOverlay.classList.add('hidden');
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorModal.classList.remove('hidden');
    }

    hideErrorModal() {
        this.errorModal.classList.add('hidden');
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new ChatLuzApp();
});

// Manejar errores globales
window.addEventListener('error', (e) => {
    console.error('Error global:', e.error);
});

// Manejar errores de promesas no capturadas
window.addEventListener('unhandledrejection', (e) => {
    console.error('Promesa rechazada no manejada:', e.reason);
});
