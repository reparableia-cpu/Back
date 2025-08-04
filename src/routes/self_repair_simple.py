from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import queue
import random
import os

self_repair_bp = Blueprint('self_repair', __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleSystemMonitor:
    """Monitor del sistema simplificado sin dependencias externas"""
    
    def __init__(self):
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'response_times': [],
            'error_count': 0,
            'request_count': 0
        }
        self.thresholds = {
            'max_cpu_usage': 80.0,
            'max_memory_usage': 85.0,
            'max_disk_usage': 90.0,
            'max_response_time': 5.0,
            'max_error_rate': 0.1
        }
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Inicia el monitoreo del sistema"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Monitoreo del sistema iniciado")
    
    def stop_monitoring(self):
        """Detiene el monitoreo del sistema"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("Monitoreo del sistema detenido")
    
    def _monitor_loop(self):
        """Bucle principal de monitoreo con métricas simuladas"""
        while self.monitoring:
            try:
                # Simular métricas del sistema
                cpu_percent = random.uniform(10, 70)  # CPU entre 10-70%
                memory_percent = random.uniform(20, 60)  # Memoria entre 20-60%
                disk_percent = random.uniform(15, 50)  # Disco entre 15-50%
                
                # Almacenar métricas
                self.metrics['cpu_usage'].append({
                    'value': cpu_percent,
                    'timestamp': datetime.now().isoformat()
                })
                self.metrics['memory_usage'].append({
                    'value': memory_percent,
                    'timestamp': datetime.now().isoformat()
                })
                self.metrics['disk_usage'].append({
                    'value': disk_percent,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Mantener solo las últimas 100 mediciones
                for metric_type in ['cpu_usage', 'memory_usage', 'disk_usage']:
                    if len(self.metrics[metric_type]) > 100:
                        self.metrics[metric_type] = self.metrics[metric_type][-100:]
                
                time.sleep(10)  # Monitorear cada 10 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo: {str(e)}")
                time.sleep(5)
    
    def record_request_metric(self, response_time: float, is_error: bool = False):
        """Registra métricas de peticiones"""
        self.metrics['response_times'].append({
            'value': response_time,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.metrics['response_times']) > 100:
            self.metrics['response_times'] = self.metrics['response_times'][-100:]
        
        self.metrics['request_count'] += 1
        if is_error:
            self.metrics['error_count'] += 1
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtiene las métricas actuales del sistema"""
        current_metrics = {}
        
        # CPU actual
        if self.metrics['cpu_usage']:
            current_metrics['cpu_usage'] = self.metrics['cpu_usage'][-1]['value']
        else:
            current_metrics['cpu_usage'] = random.uniform(10, 50)
        
        # Memoria actual
        if self.metrics['memory_usage']:
            current_metrics['memory_usage'] = self.metrics['memory_usage'][-1]['value']
        else:
            current_metrics['memory_usage'] = random.uniform(20, 60)
        
        # Disco actual
        if self.metrics['disk_usage']:
            current_metrics['disk_usage'] = self.metrics['disk_usage'][-1]['value']
        else:
            current_metrics['disk_usage'] = random.uniform(15, 40)
        
        # Tiempo de respuesta promedio
        if self.metrics['response_times']:
            avg_response_time = sum(m['value'] for m in self.metrics['response_times']) / len(self.metrics['response_times'])
            current_metrics['avg_response_time'] = avg_response_time
        else:
            current_metrics['avg_response_time'] = random.uniform(0.1, 2.0)
        
        # Tasa de errores
        if self.metrics['request_count'] > 0:
            current_metrics['error_rate'] = self.metrics['error_count'] / self.metrics['request_count']
        else:
            current_metrics['error_rate'] = 0
        
        current_metrics['total_requests'] = self.metrics['request_count']
        current_metrics['total_errors'] = self.metrics['error_count']
        current_metrics['timestamp'] = datetime.now().isoformat()
        
        return current_metrics
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detecta anomalías en las métricas del sistema"""
        anomalies = []
        current_metrics = self.get_current_metrics()
        
        # Verificar CPU
        if current_metrics['cpu_usage'] > self.thresholds['max_cpu_usage']:
            anomalies.append({
                'type': 'high_cpu_usage',
                'severity': 'high' if current_metrics['cpu_usage'] > 90 else 'medium',
                'value': current_metrics['cpu_usage'],
                'threshold': self.thresholds['max_cpu_usage'],
                'description': f'Uso de CPU ({current_metrics["cpu_usage"]:.1f}%) excede el umbral',
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar memoria
        if current_metrics['memory_usage'] > self.thresholds['max_memory_usage']:
            anomalies.append({
                'type': 'high_memory_usage',
                'severity': 'high' if current_metrics['memory_usage'] > 95 else 'medium',
                'value': current_metrics['memory_usage'],
                'threshold': self.thresholds['max_memory_usage'],
                'description': f'Uso de memoria ({current_metrics["memory_usage"]:.1f}%) excede el umbral',
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar disco
        if current_metrics['disk_usage'] > self.thresholds['max_disk_usage']:
            anomalies.append({
                'type': 'high_disk_usage',
                'severity': 'high',
                'value': current_metrics['disk_usage'],
                'threshold': self.thresholds['max_disk_usage'],
                'description': f'Uso de disco ({current_metrics["disk_usage"]:.1f}%) excede el umbral',
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar tiempo de respuesta
        if current_metrics['avg_response_time'] > self.thresholds['max_response_time']:
            anomalies.append({
                'type': 'high_response_time',
                'severity': 'medium',
                'value': current_metrics['avg_response_time'],
                'threshold': self.thresholds['max_response_time'],
                'description': f'Tiempo de respuesta promedio ({current_metrics["avg_response_time"]:.2f}s) excede el umbral',
                'timestamp': datetime.now().isoformat()
            })
        
        # Verificar tasa de errores
        if current_metrics['error_rate'] > self.thresholds['max_error_rate']:
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'value': current_metrics['error_rate'],
                'threshold': self.thresholds['max_error_rate'],
                'description': f'Tasa de errores ({current_metrics["error_rate"]:.2%}) excede el umbral',
                'timestamp': datetime.now().isoformat()
            })
        
        return anomalies

class SimpleRepairEngine:
    """Motor de reparación automática simplificado"""
    
    def __init__(self):
        self.repair_actions = {
            'high_cpu_usage': [
                {
                    'action': 'restart_high_cpu_processes',
                    'description': 'Reiniciar procesos con alto uso de CPU',
                    'risk': 'medium',
                    'estimated_time': 30
                },
                {
                    'action': 'optimize_system_processes',
                    'description': 'Optimizar procesos del sistema',
                    'risk': 'low',
                    'estimated_time': 60
                }
            ],
            'high_memory_usage': [
                {
                    'action': 'clear_memory_cache',
                    'description': 'Limpiar caché de memoria',
                    'risk': 'low',
                    'estimated_time': 10
                },
                {
                    'action': 'restart_memory_intensive_processes',
                    'description': 'Reiniciar procesos que consumen mucha memoria',
                    'risk': 'medium',
                    'estimated_time': 30
                }
            ],
            'high_disk_usage': [
                {
                    'action': 'clean_temporary_files',
                    'description': 'Limpiar archivos temporales',
                    'risk': 'low',
                    'estimated_time': 15
                },
                {
                    'action': 'compress_old_logs',
                    'description': 'Comprimir logs antiguos',
                    'risk': 'low',
                    'estimated_time': 20
                }
            ],
            'high_response_time': [
                {
                    'action': 'optimize_database_queries',
                    'description': 'Optimizar consultas de base de datos',
                    'risk': 'low',
                    'estimated_time': 45
                },
                {
                    'action': 'restart_web_server',
                    'description': 'Reiniciar servidor web',
                    'risk': 'medium',
                    'estimated_time': 15
                }
            ],
            'high_error_rate': [
                {
                    'action': 'check_application_logs',
                    'description': 'Revisar logs de aplicación para errores',
                    'risk': 'low',
                    'estimated_time': 10
                },
                {
                    'action': 'restart_application_services',
                    'description': 'Reiniciar servicios de aplicación',
                    'risk': 'medium',
                    'estimated_time': 20
                }
            ]
        }
        self.repair_history = []
    
    def generate_repair_plan(self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un plan de reparación para una anomalía"""
        anomaly_type = anomaly['type']
        available_actions = self.repair_actions.get(anomaly_type, [])
        
        if not available_actions:
            return {
                'anomaly_id': f"anomaly_{int(time.time())}",
                'type': anomaly_type,
                'actions': [],
                'status': 'no_actions_available',
                'message': f'No hay acciones de reparación disponibles para {anomaly_type}'
            }
        
        # Priorizar acciones por riesgo (bajo primero) y tiempo
        sorted_actions = sorted(available_actions, key=lambda x: (x['risk'] == 'high', x['estimated_time']))
        
        repair_plan = {
            'anomaly_id': f"anomaly_{int(time.time())}",
            'type': anomaly_type,
            'severity': anomaly['severity'],
            'actions': sorted_actions,
            'recommended_action': sorted_actions[0] if sorted_actions else None,
            'total_estimated_time': sum(action['estimated_time'] for action in sorted_actions),
            'timestamp': datetime.now().isoformat(),
            'status': 'plan_generated'
        }
        
        return repair_plan
    
    def execute_repair_action(self, action: Dict[str, Any], anomaly_type: str) -> Dict[str, Any]:
        """Ejecuta una acción de reparación (simulado)"""
        execution_id = f"exec_{int(time.time())}"
        
        logger.info(f"Ejecutando acción de reparación: {action['action']}")
        
        # Simular ejecución de la acción
        execution_result = {
            'execution_id': execution_id,
            'action': action['action'],
            'description': action['description'],
            'anomaly_type': anomaly_type,
            'status': 'in_progress',
            'start_time': datetime.now().isoformat(),
            'steps': []
        }
        
        # Simular pasos de ejecución
        steps = self._get_execution_steps(action['action'])
        for step in steps:
            time.sleep(0.5)  # Simular tiempo de ejecución más rápido
            execution_result['steps'].append({
                'step': step,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            })
            logger.info(f"Paso completado: {step}")
        
        execution_result['status'] = 'completed'
        execution_result['end_time'] = datetime.now().isoformat()
        execution_result['success'] = True
        execution_result['message'] = f'Acción {action["action"]} ejecutada exitosamente'
        
        self.repair_history.append(execution_result)
        
        return execution_result
    
    def _get_execution_steps(self, action: str) -> List[str]:
        """Obtiene los pasos de ejecución para una acción"""
        steps_map = {
            'restart_high_cpu_processes': [
                'Identificar procesos con alto uso de CPU',
                'Verificar criticidad de procesos',
                'Reiniciar procesos no críticos',
                'Monitorear uso de CPU post-reinicio'
            ],
            'clear_memory_cache': [
                'Verificar uso actual de memoria',
                'Limpiar caché del sistema',
                'Liberar memoria no utilizada',
                'Verificar mejora en uso de memoria'
            ],
            'clean_temporary_files': [
                'Identificar archivos temporales',
                'Verificar seguridad de eliminación',
                'Eliminar archivos temporales',
                'Verificar espacio liberado'
            ],
            'optimize_database_queries': [
                'Analizar consultas lentas',
                'Identificar oportunidades de optimización',
                'Aplicar optimizaciones',
                'Verificar mejora en rendimiento'
            ],
            'check_application_logs': [
                'Acceder a logs de aplicación',
                'Buscar patrones de error',
                'Identificar causas raíz',
                'Generar reporte de errores'
            ]
        }
        
        return steps_map.get(action, ['Ejecutar acción', 'Verificar resultado'])

# Instancias globales
system_monitor = SimpleSystemMonitor()
repair_engine = SimpleRepairEngine()

@self_repair_bp.route('/start-monitoring', methods=['POST'])
@cross_origin()
def start_monitoring():
    """Inicia el monitoreo del sistema"""
    try:
        system_monitor.start_monitoring()
        return jsonify({
            'status': 'success',
            'message': 'Monitoreo del sistema iniciado',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error iniciando monitoreo: {str(e)}'}), 500

@self_repair_bp.route('/stop-monitoring', methods=['POST'])
@cross_origin()
def stop_monitoring():
    """Detiene el monitoreo del sistema"""
    try:
        system_monitor.stop_monitoring()
        return jsonify({
            'status': 'success',
            'message': 'Monitoreo del sistema detenido',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error deteniendo monitoreo: {str(e)}'}), 500

@self_repair_bp.route('/metrics', methods=['GET'])
@cross_origin()
def get_metrics():
    """Obtiene las métricas actuales del sistema"""
    try:
        metrics = system_monitor.get_current_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo métricas: {str(e)}'}), 500

@self_repair_bp.route('/anomalies', methods=['GET'])
@cross_origin()
def detect_anomalies():
    """Detecta anomalías en el sistema"""
    try:
        anomalies = system_monitor.detect_anomalies()
        return jsonify({
            'anomalies': anomalies,
            'count': len(anomalies),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error detectando anomalías: {str(e)}'}), 500

@self_repair_bp.route('/repair-plan', methods=['POST'])
@cross_origin()
def generate_repair_plan():
    """Genera un plan de reparación para una anomalía"""
    try:
        data = request.get_json()
        anomaly = data.get('anomaly')
        
        if not anomaly:
            return jsonify({'error': 'Anomalía requerida'}), 400
        
        repair_plan = repair_engine.generate_repair_plan(anomaly)
        return jsonify(repair_plan), 200
    except Exception as e:
        return jsonify({'error': f'Error generando plan de reparación: {str(e)}'}), 500

@self_repair_bp.route('/execute-repair', methods=['POST'])
@cross_origin()
def execute_repair():
    """Ejecuta una acción de reparación"""
    try:
        data = request.get_json()
        action = data.get('action')
        anomaly_type = data.get('anomaly_type')
        
        if not action or not anomaly_type:
            return jsonify({'error': 'Acción y tipo de anomalía requeridos'}), 400
        
        result = repair_engine.execute_repair_action(action, anomaly_type)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Error ejecutando reparación: {str(e)}'}), 500

@self_repair_bp.route('/repair-history', methods=['GET'])
@cross_origin()
def get_repair_history():
    """Obtiene el historial de reparaciones"""
    try:
        return jsonify({
            'history': repair_engine.repair_history,
            'count': len(repair_engine.repair_history),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Error obteniendo historial: {str(e)}'}), 500

@self_repair_bp.route('/auto-repair', methods=['POST'])
@cross_origin()
def auto_repair():
    """Ejecuta un ciclo completo de detección y reparación automática"""
    try:
        # Detectar anomalías
        anomalies = system_monitor.detect_anomalies()
        
        if not anomalies:
            return jsonify({
                'status': 'success',
                'message': 'No se detectaron anomalías',
                'anomalies_detected': 0,
                'repairs_executed': 0,
                'timestamp': datetime.now().isoformat()
            }), 200
        
        repair_results = []
        
        for anomaly in anomalies:
            # Generar plan de reparación
            repair_plan = repair_engine.generate_repair_plan(anomaly)
            
            if repair_plan['recommended_action']:
                # Ejecutar acción recomendada
                execution_result = repair_engine.execute_repair_action(
                    repair_plan['recommended_action'],
                    anomaly['type']
                )
                
                repair_results.append({
                    'anomaly': anomaly,
                    'repair_plan': repair_plan,
                    'execution_result': execution_result
                })
        
        return jsonify({
            'status': 'success',
            'message': f'Ciclo de auto-reparación completado',
            'anomalies_detected': len(anomalies),
            'repairs_executed': len(repair_results),
            'results': repair_results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error en auto-reparación: {str(e)}'}), 500

