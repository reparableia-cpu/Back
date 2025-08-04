from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

ai_assistant_bp = Blueprint("ai_assistant", __name__)

class SimpleAIAssistant:
    """Asistente de IA simplificado sin dependencias externas"""
    
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
            'python_function': '''
def calcular_numeros_primos(limite):
    """
    Calcula todos los números primos hasta un límite dado usando la Criba de Eratóstenes
    
    Args:
        limite (int): El número límite hasta el cual buscar primos
        
    Returns:
        list: Lista de números primos encontrados
    """
    if limite < 2:
        return []
    
    # Crear una lista de números booleanos
    es_primo = [True] * (limite + 1)
    es_primo[0] = es_primo[1] = False
    
    # Aplicar la Criba de Eratóstenes
    for i in range(2, int(limite**0.5) + 1):
        if es_primo[i]:
            for j in range(i*i, limite + 1, i):
                es_primo[j] = False
    
    # Recopilar los números primos
    primos = [i for i in range(2, limite + 1) if es_primo[i]]
    return primos

# Ejemplo de uso
if __name__ == "__main__":
    limite = 100
    primos = calcular_numeros_primos(limite)
    print(f"Números primos hasta {limite}: {primos}")
'''
        }
        
        self.responses = {
            'primos': '''¡Por supuesto! Te ayudo a crear una función para calcular números primos. Aquí tienes una implementación eficiente usando la Criba de Eratóstenes:

```python
def calcular_numeros_primos(limite):
    """
    Calcula todos los números primos hasta un límite dado usando la Criba de Eratóstenes
    
    Args:
        limite (int): El número límite hasta el cual buscar primos
        
    Returns:
        list: Lista de números primos encontrados
    """
    if limite < 2:
        return []
    
    # Crear una lista de números booleanos
    es_primo = [True] * (limite + 1)
    es_primo[0] = es_primo[1] = False
    
    # Aplicar la Criba de Eratóstenes
    for i in range(2, int(limite**0.5) + 1):
        if es_primo[i]:
            for j in range(i*i, limite + 1, i):
                es_primo[j] = False
    
    # Recopilar los números primos
    primos = [i for i in range(2, limite + 1) if es_primo[i]]
    return primos

# Ejemplo de uso
if __name__ == "__main__":
    limite = 100
    primos = calcular_numeros_primos(limite)
    print(f"Números primos hasta {limite}: {primos}")
```

Esta función es muy eficiente para encontrar todos los números primos hasta un límite dado. La Criba de Eratóstenes es uno de los algoritmos más rápidos para esta tarea.

¿Te gustaría que te explique cómo funciona el algoritmo o necesitas ayuda con alguna otra función?''',
            
            'default': '''¡Hola! Soy tu asistente de IA especializado en programación. Puedo ayudarte con:

- Crear funciones y algoritmos en Python, JavaScript, Java, C++
- Explicar conceptos de programación
- Generar código para aplicaciones web (Flask, React)
- Resolver problemas de debugging
- Diseñar arquitecturas de software
- Mejores prácticas de desarrollo

¿En qué puedo ayudarte hoy?'''
        }
    
    def get_ai_response(self, message: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obtiene respuesta simulada de la IA"""
        try:
            # Obtener historial de conversación
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            
            history = self.conversation_history[session_id]
            
            # Generar respuesta basada en palabras clave
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['primo', 'primos', 'prime']):
                ai_response = self.responses['primos']
            elif any(word in message_lower for word in ['flask', 'api', 'servidor']):
                ai_response = f"Te ayudo con Flask. Aquí tienes un ejemplo básico:\n\n```python\n{self.code_templates['flask_api']}\n```"
            elif any(word in message_lower for word in ['react', 'componente', 'frontend']):
                ai_response = f"Te ayudo con React. Aquí tienes un componente de ejemplo:\n\n```jsx\n{self.code_templates['react_component']}\n```"
            elif any(word in message_lower for word in ['hola', 'ayuda', 'help']):
                ai_response = self.responses['default']
            else:
                ai_response = f"Entiendo que preguntas sobre: '{message}'. Como asistente de IA especializado en programación, puedo ayudarte con desarrollo de software, algoritmos, y arquitecturas. ¿Podrías ser más específico sobre qué tipo de código o concepto necesitas?"
            
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
            description_lower = description.lower()
            
            # Generar código basado en descripción
            if 'primo' in description_lower:
                generated_code = self.code_templates['python_function']
            elif 'flask' in description_lower or 'api' in description_lower:
                generated_code = self.code_templates['flask_api']
            elif 'react' in description_lower or 'componente' in description_lower:
                generated_code = self.code_templates['react_component']
            elif language == 'python':
                generated_code = f'''# Código Python generado para: {description}

def main():
    """Función principal"""
    print("Hola, mundo!")
    # Aquí va tu código personalizado
    
    # Ejemplo de procesamiento
    datos = [1, 2, 3, 4, 5]
    resultado = [x * 2 for x in datos]
    print(f"Resultado: {{resultado}}")

if __name__ == "__main__":
    main()
'''
            elif language == 'javascript':
                generated_code = f'''// Código JavaScript generado para: {description}

function main() {{
    console.log("Hola, mundo!");
    
    // Ejemplo de procesamiento
    const datos = [1, 2, 3, 4, 5];
    const resultado = datos.map(x => x * 2);
    console.log("Resultado:", resultado);
}}

main();
'''
            else:
                generated_code = f'''// Código {language} generado para: {description}
// Implementa aquí tu lógica específica

#include <iostream>
using namespace std;

int main() {{
    cout << "Hola, mundo!" << endl;
    return 0;
}}
'''
            
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
ai_assistant = SimpleAIAssistant()

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

