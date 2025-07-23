"""
Mock服务管理API
提供Mock服务状态检查、启动脚本生成等功能
"""
from flask import Blueprint, jsonify, request
from app.services.mock_service_manager import mock_service_manager

# 创建蓝图
mock_bp = Blueprint('mock', __name__)

@mock_bp.route('/status', methods=['GET'])
def get_mock_services_status():
    """获取所有Mock服务状态"""
    try:
        status_report = mock_service_manager.check_all_services_status()
        
        return jsonify({
            'success': True,
            'data': status_report,
            'message': f'Mock服务状态检查完成，{status_report["running_count"]}/{status_report["total_count"]} 个服务运行中'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'检查Mock服务状态失败: {str(e)}'
        }), 500

@mock_bp.route('/status/<service_name>', methods=['GET'])
def get_single_service_status(service_name):
    """获取单个Mock服务状态"""
    try:
        status = mock_service_manager.check_service_status(service_name)
        
        return jsonify({
            'success': True,
            'data': status,
            'message': f'{service_name} 服务状态检查完成'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'检查{service_name}服务状态失败: {str(e)}'
        }), 500

@mock_bp.route('/startup-commands', methods=['GET'])
def get_startup_commands():
    """获取Mock服务启动命令列表"""
    try:
        commands = mock_service_manager.get_startup_commands()
        
        return jsonify({
            'success': True,
            'data': {
                'commands': commands,
                'total_services': len(commands),
                'instructions': [
                    '1. 打开终端并进入backend目录',
                    '2. 逐个执行下面的命令启动Mock服务',
                    '3. 启动完成后可通过 /api/mock/status 检查状态'
                ]
            },
            'message': 'Mock服务启动命令获取成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取启动命令失败: {str(e)}'
        }), 500

@mock_bp.route('/startup-script', methods=['GET'])
def get_startup_script():
    """获取Mock服务启动脚本"""
    try:
        script_content = mock_service_manager.get_startup_script()
        
        return jsonify({
            'success': True,
            'data': {
                'script_content': script_content,
                'filename': 'start_mock_services.sh',
                'instructions': [
                    '1. 将脚本内容保存为 start_mock_services.sh',
                    '2. 在backend目录下执行: chmod +x start_mock_services.sh',
                    '3. 运行: ./start_mock_services.sh',
                    '4. 检查状态: curl http://localhost:8001/health'
                ]
            },
            'message': 'Mock服务启动脚本生成成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成启动脚本失败: {str(e)}'
        }), 500

@mock_bp.route('/validation', methods=['GET'])
def validate_mock_configuration():
    """验证Mock服务配置"""
    try:
        validation_result = mock_service_manager.validate_configuration()
        
        return jsonify({
            'success': validation_result['valid'],
            'data': validation_result,
            'message': '配置验证完成' if validation_result['valid'] else '配置验证发现问题'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'配置验证失败: {str(e)}'
        }), 500

@mock_bp.route('/health-check', methods=['POST'])
def batch_health_check():
    """批量健康检查（可指定服务列表）"""
    try:
        data = request.get_json() or {}
        service_names = data.get('services', list(mock_service_manager.mock_services.keys()))
        
        results = {}
        healthy_count = 0
        
        for service_name in service_names:
            if service_name in mock_service_manager.mock_services:
                status = mock_service_manager.check_service_status(service_name)
                results[service_name] = status
                if status['status'] == 'running':
                    healthy_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'healthy_count': healthy_count,
                'total_count': len(service_names),
                'all_healthy': healthy_count == len(service_names)
            },
            'message': f'批量健康检查完成，{healthy_count}/{len(service_names)} 个服务正常'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量健康检查失败: {str(e)}'
        }), 500 