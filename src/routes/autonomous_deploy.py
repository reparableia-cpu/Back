from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
import os
import subprocess
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional

autonomous_deploy_bp = Blueprint('autonomous_deploy', __name__)

class DeploymentPlanner:
    """Planificador inteligente de despliegues"""
    
    def __init__(self):
        self.deployment_strategies = {
            'simple': {
                'description': 'Despliegue simple para aplicaciones pequeñas',
                'complexity': 'low',
                'downtime': 'minimal',
                'rollback_time': 'fast',
                'use_cases': ['desarrollo', 'prototipado', 'aplicaciones simples']
            },
            'blue_green': {
                'description': 'Despliegue con dos entornos idénticos',
                'complexity': 'medium',
                'downtime': 'zero',
                'rollback_time': 'instant',
                'use_cases': ['producción', 'alta disponibilidad', 'aplicaciones críticas']
            },
            'canary': {
                'description': 'Despliegue gradual a un subconjunto de usuarios',
                'complexity': 'high',
                'downtime': 'zero',
                'rollback_time': 'fast',
                'use_cases': ['aplicaciones de alto tráfico', 'testing en producción']
            },
            'rolling': {
                'description': 'Actualización gradual de instancias',
                'complexity': 'medium',
                'downtime': 'minimal',
                'rollback_time': 'medium',
                'use_cases': ['microservicios', 'aplicaciones distribuidas']
            }
        }
        
        self.cloud_providers = {
            'local': {
                'description': 'Despliegue local para desarrollo',
                'cost': 'free',
                'scalability': 'limited',
                'availability': 'low'
            },
            'docker': {
                'description': 'Contenedorización con Docker',
                'cost': 'low',
                'scalability': 'medium',
                'availability': 'medium'
            },
            'kubernetes': {
                'description': 'Orquestación con Kubernetes',
                'cost': 'medium',
                'scalability': 'high',
                'availability': 'high'
            }
        }
        
        self.application_types = {
            'web_app': {
                'frameworks': ['flask', 'django', 'fastapi', 'express'],
                'requirements': ['web_server', 'database', 'static_files'],
                'recommended_strategy': 'blue_green'
            },
            'api': {
                'frameworks': ['flask', 'fastapi', 'express'],
                'requirements': ['web_server', 'database'],
                'recommended_strategy': 'rolling'
            },
            'microservice': {
                'frameworks': ['flask', 'fastapi', 'express'],
                'requirements': ['container', 'service_discovery', 'load_balancer'],
                'recommended_strategy': 'canary'
            },
            'static_site': {
                'frameworks': ['react', 'vue', 'angular', 'html'],
                'requirements': ['web_server', 'cdn'],
                'recommended_strategy': 'simple'
            }
        }
        
        self.deployment_history = []
    
    def analyze_application(self, app_path: str, app_type: str = None) -> Dict[str, Any]:
        """Analiza una aplicación para determinar sus características"""
        analysis = {
            'path': app_path,
            'type': app_type,
            'framework': None,
            'dependencies': [],
            'database_required': False,
            'static_files': False,
            'docker_ready': False,
            'complexity': 'low'
        }
        
        try:
            # Verificar archivos de configuración
            files_in_path = os.listdir(app_path) if os.path.exists(app_path) else []
            
            # Detectar framework
            if 'app.py' in files_in_path or 'main.py' in files_in_path:
                analysis['framework'] = 'flask'
            elif 'package.json' in files_in_path:
                analysis['framework'] = 'nodejs'
            elif 'index.html' in files_in_path:
                analysis['framework'] = 'static'
            
            # Verificar dependencias
            if 'requirements.txt' in files_in_path:
                try:
                    with open(os.path.join(app_path, 'requirements.txt'), 'r') as f:
                        analysis['dependencies'] = f.read().splitlines()
                except:
                    pass
            
            if 'package.json' in files_in_path:
                try:
                    with open(os.path.join(app_path, 'package.json'), 'r') as f:
                        package_data = json.load(f)
                        analysis['dependencies'] = list(package_data.get('dependencies', {}).keys())
                except:
                    pass
            
            # Verificar base de datos
            db_indicators = ['sqlite', 'postgresql', 'mysql', 'mongodb', 'database']
            analysis['database_required'] = any(
                any(indicator in dep.lower() for indicator in db_indicators)
                for dep in analysis['dependencies']
            )
            
            # Verificar archivos estáticos
            static_dirs = ['static', 'public', 'assets', 'dist', 'build']
            analysis['static_files'] = any(
                os.path.exists(os.path.join(app_path, static_dir))
                for static_dir in static_dirs
            )
            
            # Verificar Docker
            analysis['docker_ready'] = 'Dockerfile' in files_in_path
            
            # Determinar complejidad
            complexity_score = 0
            if analysis['database_required']:
                complexity_score += 2
            if len(analysis['dependencies']) > 10:
                complexity_score += 1
            if analysis['static_files']:
                complexity_score += 1
            
            if complexity_score >= 3:
                analysis['complexity'] = 'high'
            elif complexity_score >= 1:
                analysis['complexity'] = 'medium'
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def recommend_deployment_strategy(self, app_analysis: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Recomienda una estrategia de despliegue basada en el análisis"""
        
        # Obtener requisitos
        availability_req = requirements.get('availability', 'medium')
        performance_req = requirements.get('performance', 'medium')
        budget_req = requirements.get('budget', 'medium')
        complexity_tolerance = requirements.get('complexity_tolerance', 'medium')
        
        # Determinar estrategia basada en tipo de aplicación
        app_type = app_analysis.get('type', 'web_app')
        base_strategy = self.application_types.get(app_type, {}).get('recommended_strategy', 'simple')
        
        # Ajustar estrategia basada en requisitos
        if availability_req == 'high' and complexity_tolerance in ['medium', 'high']:
            if performance_req == 'high':
                strategy = 'canary'
            else:
                strategy = 'blue_green'
        elif availability_req == 'high' and complexity_tolerance == 'low':
            strategy = 'blue_green'
        elif app_analysis.get('complexity') == 'high':
            strategy = 'rolling'
        else:
            strategy = base_strategy
        
        # Seleccionar proveedor
        if budget_req == 'low' or requirements.get('environment') == 'development':
            provider = 'local'
        elif app_analysis.get('docker_ready') and complexity_tolerance in ['medium', 'high']:
            provider = 'kubernetes' if availability_req == 'high' else 'docker'
        else:
            provider = 'docker'
        
        recommendation = {
            'strategy': strategy,
            'provider': provider,
            'strategy_details': self.deployment_strategies[strategy],
            'provider_details': self.cloud_providers[provider],
            'confidence': self._calculate_confidence(app_analysis, requirements, strategy, provider),
            'reasoning': self._generate_reasoning(app_analysis, requirements, strategy, provider)
        }
        
        return recommendation
    
    def _calculate_confidence(self, app_analysis: Dict[str, Any], requirements: Dict[str, Any], 
                            strategy: str, provider: str) -> float:
        """Calcula el nivel de confianza en la recomendación"""
        confidence = 0.5  # Base
        
        # Aumentar confianza si hay información completa
        if app_analysis.get('framework'):
            confidence += 0.1
        if app_analysis.get('dependencies'):
            confidence += 0.1
        if 'complexity' in app_analysis:
            confidence += 0.1
        
        # Ajustar por compatibilidad
        if strategy in ['simple', 'rolling'] and app_analysis.get('complexity') == 'low':
            confidence += 0.1
        if strategy in ['blue_green', 'canary'] and requirements.get('availability') == 'high':
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, app_analysis: Dict[str, Any], requirements: Dict[str, Any], 
                           strategy: str, provider: str) -> List[str]:
        """Genera el razonamiento detrás de la recomendación"""
        reasoning = []
        
        # Razonamiento sobre estrategia
        if strategy == 'simple':
            reasoning.append("Estrategia simple recomendada para aplicación de baja complejidad")
        elif strategy == 'blue_green':
            reasoning.append("Estrategia blue-green para garantizar alta disponibilidad")
        elif strategy == 'canary':
            reasoning.append("Estrategia canary para despliegue gradual y testing en producción")
        elif strategy == 'rolling':
            reasoning.append("Estrategia rolling para aplicaciones distribuidas")
        
        # Razonamiento sobre proveedor
        if provider == 'local':
            reasoning.append("Despliegue local para desarrollo y testing")
        elif provider == 'docker':
            reasoning.append("Docker para portabilidad y aislamiento")
        elif provider == 'kubernetes':
            reasoning.append("Kubernetes para alta escalabilidad y disponibilidad")
        
        # Razonamiento basado en análisis
        if app_analysis.get('database_required'):
            reasoning.append("Base de datos detectada - configuración de persistencia requerida")
        if app_analysis.get('static_files'):
            reasoning.append("Archivos estáticos detectados - configuración de servidor web")
        if app_analysis.get('docker_ready'):
            reasoning.append("Dockerfile encontrado - aplicación lista para contenedorización")
        
        return reasoning
    
    def generate_deployment_config(self, app_analysis: Dict[str, Any], 
                                 recommendation: Dict[str, Any], 
                                 requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Genera la configuración de despliegue"""
        
        config = {
            'deployment_id': f"deploy_{int(time.time())}",
            'application': {
                'name': requirements.get('app_name', 'my-app'),
                'path': app_analysis['path'],
                'framework': app_analysis.get('framework', 'unknown'),
                'type': app_analysis.get('type', 'web_app')
            },
            'strategy': recommendation['strategy'],
            'provider': recommendation['provider'],
            'resources': {
                'cpu': requirements.get('cpu', '1'),
                'memory': requirements.get('memory', '512Mi'),
                'storage': requirements.get('storage', '1Gi'),
                'replicas': requirements.get('replicas', 1)
            },
            'networking': {
                'port': requirements.get('port', 5000),
                'external_access': requirements.get('external_access', True),
                'load_balancer': recommendation['strategy'] in ['blue_green', 'canary']
            },
            'environment': requirements.get('environment', 'development'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Configuración específica por proveedor
        if recommendation['provider'] == 'docker':
            config['docker'] = self._generate_docker_config(app_analysis, config)
        elif recommendation['provider'] == 'kubernetes':
            config['kubernetes'] = self._generate_kubernetes_config(app_analysis, config)
        
        return config
    
    def _generate_docker_config(self, app_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Genera configuración específica para Docker"""
        framework = app_analysis.get('framework', 'unknown')
        
        dockerfile_content = ""
        if framework == 'flask':
            dockerfile_content = f"""
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {config['networking']['port']}

CMD ["python", "app.py"]
"""
        elif framework == 'nodejs':
            dockerfile_content = f"""
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE {config['networking']['port']}

CMD ["npm", "start"]
"""
        elif framework == 'static':
            dockerfile_content = f"""
FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        
        return {
            'dockerfile_content': dockerfile_content.strip(),
            'build_command': f"docker build -t {config['application']['name']} .",
            'run_command': f"docker run -p {config['networking']['port']}:{config['networking']['port']} {config['application']['name']}"
        }
    
    def _generate_kubernetes_config(self, app_analysis: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Genera configuración específica para Kubernetes"""
        
        deployment_yaml = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f"{config['application']['name']}-deployment"
            },
            'spec': {
                'replicas': config['resources']['replicas'],
                'selector': {
                    'matchLabels': {
                        'app': config['application']['name']
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': config['application']['name']
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': config['application']['name'],
                            'image': f"{config['application']['name']}:latest",
                            'ports': [{
                                'containerPort': config['networking']['port']
                            }],
                            'resources': {
                                'requests': {
                                    'cpu': config['resources']['cpu'],
                                    'memory': config['resources']['memory']
                                },
                                'limits': {
                                    'cpu': config['resources']['cpu'],
                                    'memory': config['resources']['memory']
                                }
                            }
                        }]
                    }
                }
            }
        }
        
        service_yaml = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': f"{config['application']['name']}-service"
            },
            'spec': {
                'selector': {
                    'app': config['application']['name']
                },
                'ports': [{
                    'port': 80,
                    'targetPort': config['networking']['port']
                }],
                'type': 'LoadBalancer' if config['networking']['external_access'] else 'ClusterIP'
            }
        }
        
        return {
            'deployment_yaml': yaml.dump(deployment_yaml, default_flow_style=False),
            'service_yaml': yaml.dump(service_yaml, default_flow_style=False),
            'apply_commands': [
                f"kubectl apply -f {config['application']['name']}-deployment.yaml",
                f"kubectl apply -f {config['application']['name']}-service.yaml"
            ]
        }

class DeploymentExecutor:
    """Ejecutor de despliegues"""
    
    def __init__(self):
        self.execution_history = []
    
    def execute_deployment(self, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un despliegue basado en la configuración"""
        
        execution_id = f"exec_{int(time.time())}"
        
        execution_result = {
            'execution_id': execution_id,
            'deployment_id': deployment_config['deployment_id'],
            'status': 'in_progress',
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'provider': deployment_config['provider'],
            'strategy': deployment_config['strategy']
        }
        
        try:
            # Ejecutar pasos según el proveedor
            if deployment_config['provider'] == 'local':
                steps = self._execute_local_deployment(deployment_config)
            elif deployment_config['provider'] == 'docker':
                steps = self._execute_docker_deployment(deployment_config)
            elif deployment_config['provider'] == 'kubernetes':
                steps = self._execute_kubernetes_deployment(deployment_config)
            else:
                steps = [{'step': 'Proveedor no soportado', 'status': 'error'}]
            
            execution_result['steps'] = steps
            execution_result['status'] = 'completed' if all(s['status'] == 'success' for s in steps) else 'failed'
            execution_result['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            execution_result['status'] = 'error'
            execution_result['error'] = str(e)
            execution_result['end_time'] = datetime.now().isoformat()
        
        self.execution_history.append(execution_result)
        return execution_result
    
    def _execute_local_deployment(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ejecuta despliegue local (simulado)"""
        steps = [
            {'step': 'Verificar aplicación local', 'status': 'success', 'message': 'Aplicación verificada'},
            {'step': 'Configurar entorno', 'status': 'success', 'message': 'Entorno configurado'},
            {'step': 'Iniciar aplicación', 'status': 'success', 'message': f"Aplicación disponible en puerto {config['networking']['port']}"}
        ]
        
        for step in steps:
            step['timestamp'] = datetime.now().isoformat()
            time.sleep(1)  # Simular tiempo de ejecución
        
        return steps
    
    def _execute_docker_deployment(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ejecuta despliegue con Docker (simulado)"""
        steps = [
            {'step': 'Generar Dockerfile', 'status': 'success', 'message': 'Dockerfile creado'},
            {'step': 'Construir imagen Docker', 'status': 'success', 'message': f"Imagen {config['application']['name']} construida"},
            {'step': 'Ejecutar contenedor', 'status': 'success', 'message': f"Contenedor ejecutándose en puerto {config['networking']['port']}"},
            {'step': 'Verificar salud del contenedor', 'status': 'success', 'message': 'Contenedor saludable'}
        ]
        
        for step in steps:
            step['timestamp'] = datetime.now().isoformat()
            time.sleep(1)  # Simular tiempo de ejecución
        
        return steps
    
    def _execute_kubernetes_deployment(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ejecuta despliegue con Kubernetes (simulado)"""
        steps = [
            {'step': 'Generar manifiestos Kubernetes', 'status': 'success', 'message': 'Manifiestos YAML generados'},
            {'step': 'Aplicar Deployment', 'status': 'success', 'message': 'Deployment aplicado al cluster'},
            {'step': 'Aplicar Service', 'status': 'success', 'message': 'Service aplicado al cluster'},
            {'step': 'Verificar pods', 'status': 'success', 'message': f"{config['resources']['replicas']} pods ejecutándose"},
            {'step': 'Verificar servicio', 'status': 'success', 'message': 'Servicio disponible externamente'}
        ]
        
        for step in steps:
            step['timestamp'] = datetime.now().isoformat()
            time.sleep(1)  # Simular tiempo de ejecución
        
        return steps

# Instancias globales
deployment_planner = DeploymentPlanner()
deployment_executor = DeploymentExecutor()

@autonomous_deploy_bp.route('/analyze-app', methods=['POST'])
@cross_origin()
def analyze_application():
    """Analiza una aplicación para despliegue"""
    try:
        data = request.get_json()
        app_path = data.get('app_path', '')
        app_type = data.get('app_type')
        
        if not app_path:
            return jsonify({'error': 'Ruta de aplicación requerida'}), 400
        
        analysis = deployment_planner.analyze_application(app_path, app_type)
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Error analizando aplicación: {str(e)}'}), 500

@autonomous_deploy_bp.route('/recommend-strategy', methods=['POST'])
@cross_origin()
def recommend_strategy():
    """Recomienda estrategia de despliegue"""
    try:
        data = request.get_json()
        app_analysis = data.get('app_analysis', {})
        requirements = data.get('requirements', {})
        
        recommendation = deployment_planner.recommend_deployment_strategy(app_analysis, requirements)
        return jsonify(recommendation), 200
        
    except Exception as e:
        return jsonify({'error': f'Error recomendando estrategia: {str(e)}'}), 500

@autonomous_deploy_bp.route('/generate-config', methods=['POST'])
@cross_origin()
def generate_config():
    """Genera configuración de despliegue"""
    try:
        data = request.get_json()
        app_analysis = data.get('app_analysis', {})
        recommendation = data.get('recommendation', {})
        requirements = data.get('requirements', {})
        
        config = deployment_planner.generate_deployment_config(app_analysis, recommendation, requirements)
        return jsonify(config), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generando configuración: {str(e)}'}), 500

@autonomous_deploy_bp.route('/deploy', methods=['POST'])
@cross_origin()
def deploy_application():
    """Ejecuta el despliegue de una aplicación"""
    try:
        data = request.get_json()
        deployment_config = data.get('deployment_config', {})
        
        if not deployment_config:
            return jsonify({'error': 'Configuración de despliegue requerida'}), 400
        
        result = deployment_executor.execute_deployment(deployment_config)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Error ejecutando despliegue: {str(e)}'}), 500

@autonomous_deploy_bp.route('/deployment-history', methods=['GET'])
@cross_origin()
def get_deployment_history():
    """Obtiene el historial de despliegues"""
    try:
        return jsonify({
            'history': deployment_executor.execution_history,
            'count': len(deployment_executor.execution_history),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo historial: {str(e)}'}), 500

@autonomous_deploy_bp.route('/strategies', methods=['GET'])
@cross_origin()
def get_strategies():
    """Obtiene las estrategias de despliegue disponibles"""
    try:
        return jsonify({
            'strategies': deployment_planner.deployment_strategies,
            'providers': deployment_planner.cloud_providers,
            'application_types': deployment_planner.application_types,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo estrategias: {str(e)}'}), 500

