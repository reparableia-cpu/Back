"""
Sistema de Sandbox para ejecución segura de código
"""
import subprocess
import tempfile
import os
import signal
import json
import time
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import docker
from typing import Dict, Any, Optional
import threading
import psutil

sandbox_bp = Blueprint("sandbox", __name__)

class CodeSandbox:
    """Sandbox para ejecución segura de código"""
    
    SUPPORTED_LANGUAGES = {
        'python': {
            'extension': '.py',
            'command': ['python3'],
            'timeout': 30,
            'memory_limit': '128m'
        },
        'javascript': {
            'extension': '.js',
            'command': ['node'],
            'timeout': 30,
            'memory_limit': '128m'
        },
        'bash': {
            'extension': '.sh',
            'command': ['bash'],
            'timeout': 15,
            'memory_limit': '64m'
        }
    }
    
    def __init__(self):
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Verificar si Docker está disponible"""
        try:
            docker.from_env().ping()
            return True
        except:
            return False
    
    def execute_code(self, code: str, language: str, input_data: str = "") -> Dict[str, Any]:
        """Ejecutar código en sandbox"""
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                'success': False,
                'error': f'Lenguaje no soportado: {language}',
                'supported_languages': list(self.SUPPORTED_LANGUAGES.keys())
            }
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        if self.docker_available:
            return self._execute_with_docker(code, language, input_data, lang_config)
        else:
            return self._execute_with_subprocess(code, language, input_data, lang_config)
    
    def _execute_with_docker(self, code: str, language: str, input_data: str, lang_config: Dict) -> Dict[str, Any]:
        """Ejecutar código usando Docker (más seguro)"""
        try:
            client = docker.from_env()
            
            # Imagen base según el lenguaje
            images = {
                'python': 'python:3.11-alpine',
                'javascript': 'node:18-alpine',
                'bash': 'alpine:latest'
            }
            
            image = images.get(language, 'alpine:latest')
            
            # Crear archivo temporal con el código
            with tempfile.NamedTemporaryFile(mode='w', suffix=lang_config['extension'], delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Configurar volumen para el archivo
                volume_mapping = {
                    os.path.dirname(temp_file): {'bind': '/code', 'mode': 'ro'}
                }
                
                # Comando de ejecución
                filename = os.path.basename(temp_file)
                command = lang_config['command'] + [f'/code/{filename}']
                
                # Ejecutar contenedor
                container = client.containers.run(
                    image,
                    command=command,
                    volumes=volume_mapping,
                    stdin_open=True,
                    stdout=True,
                    stderr=True,
                    remove=True,
                    detach=True,
                    mem_limit=lang_config['memory_limit'],
                    network_disabled=True,
                    security_opt=['no-new-privileges:true'],
                    cap_drop=['ALL'],
                    read_only=True,
                    tmpfs={'/tmp': 'noexec,nosuid,size=10m'}
                )
                
                # Enviar input si existe
                if input_data:
                    container.exec_run(f'echo "{input_data}"', stdin=True)
                
                # Esperar resultado con timeout
                try:
                    result = container.wait(timeout=lang_config['timeout'])
                    logs = container.logs(stdout=True, stderr=True).decode('utf-8')
                    
                    return {
                        'success': result['StatusCode'] == 0,
                        'output': logs,
                        'exit_code': result['StatusCode'],
                        'execution_time': None,
                        'language': language
                    }
                
                except docker.errors.ContainerError as e:
                    return {
                        'success': False,
                        'error': 'Error en ejecución del contenedor',
                        'output': str(e),
                        'language': language
                    }
                
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_file)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en Docker: {str(e)}',
                'language': language
            }
    
    def _execute_with_subprocess(self, code: str, language: str, input_data: str, lang_config: Dict) -> Dict[str, Any]:
        """Ejecutar código usando subprocess (menos seguro pero más compatible)"""
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix=lang_config['extension'], delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                start_time = time.time()
                
                # Configurar comando
                command = lang_config['command'] + [temp_file]
                
                # Ejecutar con límites de tiempo y recursos
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )
                
                # Configurar timeout y límites de memoria
                def kill_process():
                    if process.poll() is None:
                        try:
                            if os.name != 'nt':
                                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                            else:
                                process.terminate()
                        except:
                            pass
                
                timer = threading.Timer(lang_config['timeout'], kill_process)
                timer.start()
                
                try:
                    # Ejecutar y obtener resultado
                    stdout, stderr = process.communicate(input=input_data, timeout=lang_config['timeout'])
                    execution_time = time.time() - start_time
                    
                    output = stdout
                    if stderr:
                        output += f"\n--- STDERR ---\n{stderr}"
                    
                    return {
                        'success': process.returncode == 0,
                        'output': output,
                        'exit_code': process.returncode,
                        'execution_time': round(execution_time, 3),
                        'language': language
                    }
                
                except subprocess.TimeoutExpired:
                    process.kill()
                    return {
                        'success': False,
                        'error': f'Timeout: El código tardó más de {lang_config["timeout"]} segundos',
                        'language': language
                    }
                
                finally:
                    timer.cancel()
                    
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_file)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en ejecución: {str(e)}',
                'language': language
            }

# Instancia global del sandbox
code_sandbox = CodeSandbox()

@sandbox_bp.route('/execute', methods=['POST'])
@cross_origin()
def execute_code():
    """Ejecutar código en sandbox"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        code = data.get('code', '').strip()
        language = data.get('language', '').lower()
        input_data = data.get('input', '')
        
        if not code:
            return jsonify({'error': 'El código no puede estar vacío'}), 400
        
        if not language:
            return jsonify({'error': 'Debe especificar un lenguaje'}), 400
        
        # Validar longitud del código
        if len(code) > 10000:  # 10KB máximo
            return jsonify({'error': 'El código es demasiado largo (máximo 10KB)'}), 400
        
        # Filtros básicos de seguridad
        dangerous_patterns = [
            'import os', 'import subprocess', 'import sys',
            'eval(', 'exec(', '__import__',
            'open(', 'file(', 'input(',
            'raw_input(', 'compile(',
            'rm -rf', 'sudo', 'wget', 'curl'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return jsonify({
                    'error': f'Código bloqueado: contiene patrón peligroso "{pattern}"',
                    'security_note': 'El código fue bloqueado por razones de seguridad'
                }), 400
        
        # Ejecutar código
        result = code_sandbox.execute_code(code, language, input_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@sandbox_bp.route('/languages', methods=['GET'])
@cross_origin()
def get_supported_languages():
    """Obtener lenguajes soportados"""
    return jsonify({
        'languages': list(code_sandbox.SUPPORTED_LANGUAGES.keys()),
        'docker_available': code_sandbox.docker_available,
        'configurations': code_sandbox.SUPPORTED_LANGUAGES
    })

@sandbox_bp.route('/health', methods=['GET'])
@cross_origin()
def sandbox_health():
    """Verificar estado del sandbox"""
    return jsonify({
        'status': 'healthy',
        'docker_available': code_sandbox.docker_available,
        'supported_languages': list(code_sandbox.SUPPORTED_LANGUAGES.keys())
    })

@sandbox_bp.route('/examples', methods=['GET'])
@cross_origin()
def get_code_examples():
    """Obtener ejemplos de código para cada lenguaje"""
    examples = {
        'python': '''# Ejemplo Python
print("¡Hola desde el sandbox!")

# Operaciones básicas
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"Números: {numbers}")
print(f"Cuadrados: {squared}")

# Función simple
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(f"Fibonacci de 8: {fibonacci(8)}")
''',
        'javascript': '''// Ejemplo JavaScript
console.log("¡Hola desde el sandbox!");

// Operaciones básicas
const numbers = [1, 2, 3, 4, 5];
const squared = numbers.map(x => x * x);
console.log("Números:", numbers);
console.log("Cuadrados:", squared);

// Función simple
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log(`Fibonacci de 8: ${fibonacci(8)}`);
''',
        'bash': '''#!/bin/bash
# Ejemplo Bash
echo "¡Hola desde el sandbox!"

# Variables
name="Usuario"
echo "Bienvenido, $name"

# Loop simple
echo "Contando del 1 al 5:"
for i in {1..5}; do
    echo "Número: $i"
done

# Fecha actual
echo "Fecha actual: $(date)"
'''
    }
    
    return jsonify({'examples': examples})
