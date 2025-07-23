"""
Mock服务管理器
提供Mock服务状态检查和管理功能
注意：根据用户要求，不实现自动启动功能，需要手动启动Mock服务
"""
import logging
import requests
import subprocess
import time
from typing import Dict, List, Optional
from app.config import Config

class MockServiceManager:
    """Mock服务管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mock_services = {
            'classification': {
                'name': '分类API服务',
                'url': Config.CLASSIFY_API_URL,
                'port': 8001,
                'script': 'mock_classification_api.py',
                'health_endpoint': '/health'
            },
            'doubao': {
                'name': '豆包AI服务',
                'url': Config.DOUBAO_API_URL,
                'port': 8002,
                'script': 'mock_ai_api.py',
                'args': ['--service', 'doubao'],
                'health_endpoint': '/health'
            },
            'xiaotian': {
                'name': '小天AI服务',
                'url': Config.XIAOTIAN_API_URL,
                'port': 8003,
                'script': 'mock_ai_api.py',
                'args': ['--service', 'xiaotian'],
                'health_endpoint': '/health'
            },
            'score': {
                'name': '评分API服务',
                'url': Config.SCORE_API_URL,
                'port': 8004,
                'script': 'mock_score_api.py',
                'health_endpoint': '/health'
            }
        }
    
    def check_service_status(self, service_name: str) -> Dict:
        """检查单个服务状态"""
        if service_name not in self.mock_services:
            return {
                'status': 'unknown',
                'message': f'未知的服务: {service_name}'
            }
        
        service = self.mock_services[service_name]
        
        try:
            # 尝试访问健康检查端点
            health_url = f"{service['url']}{service.get('health_endpoint', '/health')}"
            response = requests.get(health_url, timeout=3)
            
            if response.status_code == 200:
                return {
                    'status': 'running',
                    'message': f"{service['name']} 运行正常",
                    'url': service['url'],
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': 'error',
                    'message': f"{service['name']} 返回错误状态码: {response.status_code}",
                    'url': service['url']
                }
        
        except requests.exceptions.ConnectionError:
            return {
                'status': 'offline',
                'message': f"{service['name']} 无法连接，可能未启动",
                'url': service['url']
            }
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'message': f"{service['name']} 响应超时",
                'url': service['url']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"{service['name']} 检查失败: {str(e)}",
                'url': service['url']
            }
    
    def check_all_services_status(self) -> Dict:
        """检查所有服务状态"""
        status_report = {
            'overall_status': 'unknown',
            'services': {},
            'running_count': 0,
            'total_count': len(self.mock_services),
            'offline_services': [],
            'error_services': []
        }
        
        for service_name in self.mock_services:
            service_status = self.check_service_status(service_name)
            status_report['services'][service_name] = service_status
            
            if service_status['status'] == 'running':
                status_report['running_count'] += 1
            elif service_status['status'] == 'offline':
                status_report['offline_services'].append(service_name)
            elif service_status['status'] in ['error', 'timeout']:
                status_report['error_services'].append(service_name)
        
        # 判断总体状态
        if status_report['running_count'] == status_report['total_count']:
            status_report['overall_status'] = 'all_running'
        elif status_report['running_count'] > 0:
            status_report['overall_status'] = 'partial_running'
        else:
            status_report['overall_status'] = 'all_offline'
        
        return status_report
    
    def get_startup_commands(self) -> List[str]:
        """获取启动Mock服务的命令列表（供用户手动执行）"""
        commands = []
        
        for service_name, service in self.mock_services.items():
            script = service['script']
            port = service['port']
            
            if 'args' in service:
                args = ' '.join(service['args'])
                cmd = f"python tests/{script} {args} --port {port} &"
            else:
                cmd = f"python tests/{script} --port {port} &"
            
            commands.append({
                'service': service_name,
                'name': service['name'],
                'command': cmd,
                'description': f"启动{service['name']} (端口:{port})"
            })
        
        return commands
    
    def get_startup_script(self) -> str:
        """生成完整的启动脚本"""
        script_lines = [
            "#!/bin/bash",
            "# Mock服务启动脚本",
            "# 请在backend目录下执行此脚本",
            "",
            "echo '🚀 启动Mock服务...'",
            "cd tests",
            ""
        ]
        
        for service_name, service in self.mock_services.items():
            script = service['script']
            port = service['port']
            
            if 'args' in service:
                args = ' '.join(service['args'])
                cmd = f"python {script} {args} --port {port} &"
            else:
                cmd = f"python {script} --port {port} &"
            
            script_lines.extend([
                f"echo '启动{service['name']} (端口:{port})'",
                cmd,
                "sleep 1",
                ""
            ])
        
        script_lines.extend([
            "cd ..",
            "echo '✅ 所有Mock服务启动完成'",
            "echo '使用以下命令检查服务状态:'",
            "echo 'curl http://localhost:8001/health'",
            "echo 'curl http://localhost:8002/health'",
            "echo 'curl http://localhost:8003/health'",
            "echo 'curl http://localhost:8004/health'"
        ])
        
        return '\n'.join(script_lines)
    
    def validate_configuration(self) -> Dict:
        """验证Mock服务配置"""
        validation_result = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        for service_name, service in self.mock_services.items():
            # 检查URL配置
            if not service.get('url'):
                validation_result['valid'] = False
                validation_result['issues'].append(f"{service_name}: 缺少URL配置")
            
            # 检查端口配置
            if not service.get('port'):
                validation_result['valid'] = False
                validation_result['issues'].append(f"{service_name}: 缺少端口配置")
            
            # 检查脚本文件
            script_path = f"tests/{service['script']}"
            import os
            if not os.path.exists(script_path):
                validation_result['warnings'].append(f"{service_name}: 脚本文件不存在 {script_path}")
        
        return validation_result

# 创建全局实例
mock_service_manager = MockServiceManager() 