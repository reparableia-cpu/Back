from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
import openai
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

ai_assistant_bp = Blueprint("ai_assistant", __name__)

# Configurar cliente OpenAI (inicialización diferida)
client = None

def get_openai_client():
    global client
    if client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")
        client = openai.OpenAI(api_key=api_key)
    return client

class AIAssistant:
    """Asistente de IA con capacidades de chat y generación de código"""
    
    def __init__(self):
        self.conversation_history = {}
        self.code_templates = {
            'flask_api': '''
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        return jsonify({'message': 'GET request received'})
    else:
        data = request.get_json()
        return jsonify({'received': data, 'processed': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
''',
            'react_component': '''
import React, { useState, useEffect } from 'react';

const MyComponent = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await fetch('/api/data');
            const result = await response.json();
            setData(result);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Cargando...</div>;

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Mi Componente</h2>
            <div className="bg-gray-100 p-4 rounded">
                {data ? JSON.stringify(data, null, 2) : 'No hay datos'}
            </div>
        </div>
    );
};

export default MyComponent;
''',
            'python_script': '''
#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

def main():
    """Función principal del script"""
    print("Iniciando script...")
    
    # Tu código aquí
    data = {
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    }
    
    print(f"Resultado: {json.dumps(data, indent=2)}")

if __name__ == '__main__':
    main()
'''
        }
    
    def get_ai_response(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtiene respuesta de la IA usando OpenAI"""
        try:
            # Obtener historial de conversación
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            history = self.conversation_history[session_id]
            
            # Preparar mensajes para OpenAI
            messages = [
                {
                    "role": "system",
                    "content": """Eres un asistente de IA especializado en programación y desarrollo de software. 
                    Puedes ayudar con:
                    - Generación de código en Python, JavaScript, React, Flask
                    - Explicación de conceptos de programación
                    - Debugging y solución de problemas
                    - Arquitectura de software
                    - Mejores prácticas de desarrollo
                    
                    Responde de manera clara, concisa y práctica. Si generas código, incluye comentarios explicativos."""
                }
            ]
            
            # Agregar historial reciente (últimos 10 mensajes)
            for msg in history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": message})
            
            # Llamar a OpenAI
            response = get_openai_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Guardar en historial
            history.append({"role": "user", "content": message, "timestamp": datetime.now().isoformat()})
            history.append({"role": "assistant", "content": ai_response, "timestamp": datetime.now().isoformat()})
            
            # Mantener solo los últimos 20 mensajes
            if len(history) > 20:
                history = history[-20:]
            
            self.conversation_history[session_id] = history
            
            return {
                'response': ai_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': f'Error al obtener respuesta de IA: {str(e)}',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def generate_code(self, description: str, language: str = 'python', framework: str = None) -> Dict[str, Any]:
        """Genera código basado en descripción"""
        try:
            # Preparar prompt específico para generación de código
            prompt = f"""
            Genera código {language} {'usando ' + framework if framework else ''} para:
            {description}
            
            Requisitos:
            - Código limpio y bien comentado
            - Manejo de errores apropiado
            - Mejores prácticas del lenguaje
            - Funcional y listo para usar
            
            Proporciona solo el código sin explicaciones adicionales.
            """
            
            response = get_openai_client().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_code = response.choices[0].message.content
            
            return {
                'code': generated_code,
                'language': language,
                'framework': framework,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'error': f'Error generando código: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def get_code_template(self, template_type: str) -> Dict[str, Any]:
        """Obtiene plantilla de código predefinida"""
        if template_type in self.code_templates:
            return {
                'template': self.code_templates[template_type],
                'type': template_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        else:
            return {
                'error': f'Plantilla {template_type} no encontrada',
                'available_templates': list(self.code_templates.keys()),
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }

# Instancia global del asistente
ai_assistant = AIAssistant()

@ai_assistant_bp.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    """Endpoint para chatear con el asistente de IA"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', f'session_{int(time.time())}')
        context = data.get('context', {})
        
        if not message:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        response = ai_assistant.get_ai_response(message, session_id, context)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@ai_assistant_bp.route("/generate-code", methods=["POST"])
@cross_origin()
def generate_code():
    """Endpoint para generar código"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        language = data.get('language', 'python')
        framework = data.get('framework')
        
        if not description:
            return jsonify({"error": "Descripción requerida"}), 400
        
        response = ai_assistant.generate_code(description, language, framework)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@ai_assistant_bp.route("/templates", methods=["GET"])
@cross_origin()
def get_templates():
    """Endpoint para obtener plantillas disponibles"""
    try:
        templates = list(ai_assistant.code_templates.keys())
        return jsonify({
            'templates': templates,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@ai_assistant_bp.route("/template/<template_type>", methods=["GET"])
@cross_origin()
def get_template(template_type):
    """Endpoint para obtener una plantilla específica"""
    try:
        response = ai_assistant.get_code_template(template_type)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@ai_assistant_bp.route("/conversation/<session_id>", methods=["GET"])
@cross_origin()
def get_conversation(session_id):
    """Endpoint para obtener historial de conversación"""
    try:
        history = ai_assistant.conversation_history.get(session_id, [])
        return jsonify({
            'session_id': session_id,
            'history': history,
            'message_count': len(history),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

