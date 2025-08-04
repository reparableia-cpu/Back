from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
import openai
import requests
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

ai_assistant_bp = Blueprint("ai_assistant", __name__)

# Configurar cliente OpenAI
client = openai.OpenAI()

class EnhancedAIAssistant:
    """Asistente de IA mejorado con capacidades de búsqueda en internet"""
    
    def __init__(self):
        self.conversation_history = {}
        self.search_history = []
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
    
    def search_internet(self, query: str) -> Dict[str, Any]:
        """Realiza búsqueda en internet usando DuckDuckGo API"""
        try:
            # Usar DuckDuckGo API para búsquedas
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer información relevante
                results = []
                
                # Abstract (resumen principal)
                if data.get('Abstract'):
                    results.append({
                        'type': 'abstract',
                        'content': data['Abstract'],
                        'source': data.get('AbstractSource', 'DuckDuckGo')
                    })
                
                # Related topics
                if data.get('RelatedTopics'):
                    for topic in data['RelatedTopics'][:3]:  # Limitar a 3 resultados
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append({
                                'type': 'related_topic',
                                'content': topic['Text'],
                                'url': topic.get('FirstURL', '')
                            })
                
                # Answer (respuesta directa)
                if data.get('Answer'):
                    results.append({
                        'type': 'answer',
                        'content': data['Answer'],
                        'source': data.get('AnswerType', 'calculation')
                    })
                
                search_result = {
                    'query': query,
                    'results': results,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
                
                # Guardar en historial
                self.search_history.append(search_result)
                
                return search_result
            else:
                return {
                    'query': query,
                    'error': f'Error en búsqueda: {response.status_code}',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'error'
                }
                
        except Exception as e:
            return {
                'query': query,
                'error': f'Error realizando búsqueda: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def needs_internet_search(self, message: str) -> bool:
        """Determina si un mensaje requiere búsqueda en internet"""
        search_indicators = [
            'busca', 'buscar', 'search', 'encuentra', 'información sobre',
            'qué es', 'quién es', 'cuándo', 'dónde', 'cómo', 'por qué',
            'últimas noticias', 'actualización', 'estado actual',
            'precio de', 'cotización', 'valor actual',
            'definición de', 'significado de'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in search_indicators)
    
    def get_ai_response(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtiene respuesta de la IA con capacidades de búsqueda"""
        try:
            # Obtener historial de conversación
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            history = self.conversation_history[session_id]
            
            # Determinar si necesita búsqueda en internet
            search_results = None
            if self.needs_internet_search(message):
                # Extraer términos de búsqueda del mensaje
                search_query = self._extract_search_terms(message)
                if search_query:
                    search_results = self.search_internet(search_query)
            
            # Preparar mensajes para OpenAI
            system_message = """Eres un asistente de IA especializado en programación y desarrollo de software con acceso a información actualizada de internet. 

Puedes ayudar con:
- Generación de código en Python, JavaScript, React, Flask
- Explicación de conceptos de programación
- Debugging y solución de problemas
- Arquitectura de software
- Mejores prácticas de desarrollo
- Información actualizada sobre tecnologías y tendencias
- Búsquedas y consultas de información en tiempo real

Si tienes información de búsquedas de internet, úsala para proporcionar respuestas más precisas y actualizadas.

Responde de manera clara, concisa y práctica. Si generas código, incluye comentarios explicativos."""

            messages = [{"role": "system", "content": system_message}]
            
            # Agregar historial reciente (últimos 10 mensajes)
            for msg in history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Agregar información de búsqueda si está disponible
            enhanced_message = message
            if search_results and search_results.get('results'):
                search_info = "\n\nInformación encontrada en internet:\n"
                for result in search_results['results'][:3]:  # Limitar a 3 resultados
                    search_info += f"- {result['content']}\n"
                enhanced_message = f"{message}\n{search_info}"
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": enhanced_message})
            
            # Llamar a OpenAI
            response = client.chat.completions.create(
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
            
            result = {
                'response': ai_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # Incluir información de búsqueda si se realizó
            if search_results:
                result['search_performed'] = True
                result['search_query'] = search_results.get('query')
                result['search_results_count'] = len(search_results.get('results', []))
            
            return result
            
        except Exception as e:
            return {
                'error': f'Error al obtener respuesta de IA: {str(e)}',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }
    
    def _extract_search_terms(self, message: str) -> str:
        """Extrae términos de búsqueda del mensaje"""
        # Remover palabras comunes y extraer términos clave
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'está', 'tiene', 'del', 'al'}
        
        # Limpiar el mensaje
        clean_message = re.sub(r'[^\w\s]', ' ', message.lower())
        words = clean_message.split()
        
        # Filtrar palabras de parada y palabras muy cortas
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Tomar las primeras 5 palabras clave
        return ' '.join(keywords[:5])
    
    def generate_code(self, description: str, language: str = 'python', framework: str = None) -> Dict[str, Any]:
        """Genera código basado en descripción con información actualizada"""
        try:
            # Verificar si necesita información actualizada sobre el framework
            search_results = None
            if framework:
                search_query = f"{framework} {language} best practices latest"
                search_results = self.search_internet(search_query)
            
            # Preparar prompt específico para generación de código
            prompt = f"""
            Genera código {language} {'usando ' + framework if framework else ''} para:
            {description}
            
            Requisitos:
            - Código limpio y bien comentado
            - Manejo de errores apropiado
            - Mejores prácticas del lenguaje y framework
            - Funcional y listo para usar
            - Usa las últimas versiones y mejores prácticas
            
            Proporciona solo el código sin explicaciones adicionales.
            """
            
            # Agregar información de búsqueda si está disponible
            if search_results and search_results.get('results'):
                search_info = "\n\nInformación actualizada encontrada:\n"
                for result in search_results['results'][:2]:
                    search_info += f"- {result['content']}\n"
                prompt += search_info
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_code = response.choices[0].message.content
            
            result = {
                'code': generated_code,
                'language': language,
                'framework': framework,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            if search_results:
                result['search_performed'] = True
                result['search_query'] = search_results.get('query')
            
            return result
            
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
    
    def get_search_history(self) -> Dict[str, Any]:
        """Obtiene el historial de búsquedas"""
        return {
            'searches': self.search_history[-10:],  # Últimas 10 búsquedas
            'total_searches': len(self.search_history),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

# Instancia global del asistente
ai_assistant = EnhancedAIAssistant()

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

@ai_assistant_bp.route("/search", methods=["POST"])
@cross_origin()
def search_internet():
    """Endpoint para realizar búsquedas en internet"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Consulta de búsqueda requerida"}), 400
        
        response = ai_assistant.search_internet(query)
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@ai_assistant_bp.route("/search-history", methods=["GET"])
@cross_origin()
def get_search_history():
    """Endpoint para obtener historial de búsquedas"""
    try:
        response = ai_assistant.get_search_history()
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

