"""
定时任务和工作流管理API
支持自动化和手动控制，为前端提供完整的接口
"""
from flask import jsonify, request
from app.api import Blueprint
from app.services.scheduler_service import scheduler_service, WorkflowPhase
from app.services.ai_processing_service import ai_processing_service

# 创建蓝图
scheduler_bp = Blueprint('scheduler', __name__)


# ============================================================================
# 定时任务管理API
# ============================================================================

@scheduler_bp.route('/status', methods=['GET'])
def get_scheduler_status():
    """获取调度器完整状态"""
    try:
        status = scheduler_service.get_scheduler_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取调度器状态失败: {str(e)}'
        }), 500


@scheduler_bp.route('/jobs', methods=['GET'])
def list_scheduled_jobs():
    """获取所有定时任务列表"""
    try:
        status = scheduler_service.get_scheduler_status()
        return jsonify({
            'success': True,
            'data': status['scheduled_jobs']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取任务列表失败: {str(e)}'
        }), 500


@scheduler_bp.route('/jobs/<job_id>/pause', methods=['POST'])
def pause_job(job_id):
    """暂停定时任务"""
    try:
        result = scheduler_service.pause_job(job_id)
        return jsonify({
            'success': result,
            'message': '任务暂停成功' if result else '任务暂停失败'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'暂停任务失败: {str(e)}'
        }), 500


@scheduler_bp.route('/jobs/<job_id>/resume', methods=['POST'])
def resume_job(job_id):
    """恢复定时任务"""
    try:
        result = scheduler_service.resume_job(job_id)
        return jsonify({
            'success': result,
            'message': '任务恢复成功' if result else '任务恢复失败'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'恢复任务失败: {str(e)}'
        }), 500


# ============================================================================
# 工作流管理API
# ============================================================================

@scheduler_bp.route('/workflow/status', methods=['GET'])
def get_workflow_status():
    """获取工作流状态"""
    try:
        status = scheduler_service.get_workflow_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取工作流状态失败: {str(e)}'
        }), 500


@scheduler_bp.route('/workflow/execute', methods=['POST'])
def execute_full_workflow():
    """手动执行完整工作流"""
    try:
        from flask import current_app
        result = scheduler_service.execute_full_workflow(current_app)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'data': {
                'workflow_id': result['workflow_id'],
                'results': result['results']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'执行工作流失败: {str(e)}'
        }), 500


@scheduler_bp.route('/workflow/phases/<phase_name>/execute', methods=['POST'])
def execute_workflow_phase(phase_name):
    """手动执行工作流的特定阶段"""
    try:
        # 验证阶段名称
        try:
            phase = WorkflowPhase(phase_name)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'无效的工作流阶段: {phase_name}'
            }), 400
        
        # 获取可选参数
        data = request.get_json() or {}
        workflow_id = data.get('workflow_id')
        
        from flask import current_app
        result = scheduler_service.execute_workflow_phase(current_app, phase, workflow_id)
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'执行工作流阶段失败: {str(e)}'
        }), 500


# ============================================================================
# 手动处理API（独立于工作流）
# ============================================================================

@scheduler_bp.route('/manual/sync', methods=['POST'])
def manual_data_sync():
    """手动触发数据同步"""
    try:
        data = request.get_json() or {}
        force_full_sync = data.get('force_full_sync', False)
        
        from app.services.sync_service import sync_service
        result = sync_service.perform_sync(force_full_sync=force_full_sync)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'手动同步失败: {str(e)}'
        }), 500


@scheduler_bp.route('/manual/classification', methods=['POST'])
def manual_classification():
    """手动触发分类处理"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)
        
        result = ai_processing_service.process_classification_batch(
            limit=limit, 
            days_back=days_back
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'手动分类处理失败: {str(e)}'
        }), 500


@scheduler_bp.route('/manual/answer-generation', methods=['POST'])
def manual_answer_generation():
    """手动触发答案生成"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)
        
        result = ai_processing_service.process_answer_generation_batch(
            limit=limit, 
            days_back=days_back
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'手动答案生成失败: {str(e)}'
        }), 500


@scheduler_bp.route('/manual/scoring', methods=['POST'])
def manual_scoring():
    """手动触发评分处理"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)
        
        result = ai_processing_service.process_scoring_batch(
            limit=limit, 
            days_back=days_back
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'手动评分处理失败: {str(e)}'
        }), 500


# ============================================================================
# 统计和监控API
# ============================================================================

@scheduler_bp.route('/statistics', methods=['GET'])
def get_processing_statistics():
    """获取处理统计信息"""
    try:
        days_back = request.args.get('days_back', 7, type=int)
        
        stats = ai_processing_service.get_processing_statistics(days_back=days_back)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500


@scheduler_bp.route('/api-stats', methods=['GET'])
def get_api_statistics():
    """获取API客户端统计信息"""
    try:
        from app.services.api_client import APIClientFactory
        stats = APIClientFactory.get_all_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取API统计失败: {str(e)}'
        }), 500


@scheduler_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        # 检查调度器状态
        scheduler_status = scheduler_service.get_scheduler_status()
        scheduler_running = scheduler_status['scheduler_running']
        
        # 检查工作流状态
        workflow_status = scheduler_service.get_workflow_status()
        
        # 检查最近的错误
        recent_errors = []
        for phase_data in workflow_status['phases'].values():
            if phase_data['status'] == 'failed':
                recent_errors.append({
                    'phase': phase_data['phase'],
                    'message': phase_data['message'],
                    'last_execution': phase_data['last_execution']
                })
        
        health_data = {
            'status': 'healthy' if scheduler_running and len(recent_errors) == 0 else 'warning',
            'scheduler_running': scheduler_running,
            'current_time': scheduler_status['current_time'],
            'recent_errors': recent_errors,
            'workflow_phases_status': {
                phase: data['status'] 
                for phase, data in workflow_status['phases'].items()
            }
        }
        
        return jsonify({
            'success': True,
            'data': health_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'健康检查失败: {str(e)}',
            'data': {
                'status': 'error',
                'scheduler_running': False,
                'current_time': None,
                'recent_errors': [{'message': str(e)}]
            }
        }), 500


# ============================================================================
# 配置管理API（为前端提供）
# ============================================================================

@scheduler_bp.route('/config', methods=['GET'])
def get_scheduler_config():
    """获取调度器配置信息"""
    try:
        from app.config import Config

        config_data = {
            'scheduler_enabled': getattr(Config, 'SCHEDULER_ENABLED', False),
            'auto_process_on_startup': getattr(Config, 'AUTO_PROCESS_ON_STARTUP', False),
            'workflow_interval_minutes': getattr(Config, 'WORKFLOW_INTERVAL_MINUTES', 3),
            'data_check_enabled': getattr(Config, 'DATA_CHECK_ENABLED', True),
            'auto_suspend_when_no_data': getattr(Config, 'AUTO_SUSPEND_WHEN_NO_DATA', True),
            'min_batch_size': getattr(Config, 'MIN_BATCH_SIZE', 1),
            'batch_size': getattr(Config, 'BATCH_SIZE', 100),
            'api_timeout': getattr(Config, 'API_TIMEOUT', 30),
            'api_retry_times': getattr(Config, 'API_RETRY_TIMES', 3),
            'workflow_phases': {
                phase.value: {
                    'name': scheduler_service.workflow_config[phase]['name'],
                    'description': scheduler_service.workflow_config[phase]['description'],
                    'auto_next': scheduler_service.workflow_config[phase]['auto_next'],
                    'depends_on': [dep.value for dep in scheduler_service.workflow_config[phase]['depends_on']]
                }
                for phase in WorkflowPhase
            }
        }
        
        return jsonify({
            'success': True,
            'data': config_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        }), 500


@scheduler_bp.route('/config', methods=['PUT'])
def update_scheduler_config():
    """更新调度器配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400

        from app.config import Config
        import os

        # 更新配置值（注意：这里只是演示，实际生产环境需要更安全的配置更新机制）
        config_mapping = {
            'scheduler_enabled': 'SCHEDULER_ENABLED',
            'auto_process_on_startup': 'AUTO_PROCESS_ON_STARTUP',
            'workflow_interval_minutes': 'WORKFLOW_INTERVAL_MINUTES',
            'data_check_enabled': 'DATA_CHECK_ENABLED',
            'auto_suspend_when_no_data': 'AUTO_SUSPEND_WHEN_NO_DATA',
            'min_batch_size': 'MIN_BATCH_SIZE',
            'batch_size': 'BATCH_SIZE'
        }

        updated_configs = []
        for key, value in data.items():
            if key in config_mapping:
                config_attr = config_mapping[key]
                # 更新Config类的属性
                setattr(Config, config_attr, value)
                updated_configs.append(f"{config_attr}={value}")

        return jsonify({
            'success': True,
            'message': f'配置更新成功: {", ".join(updated_configs)}',
            'data': {
                'updated_configs': updated_configs,
                'note': '配置已更新，部分配置可能需要重启应用才能生效'
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500


@scheduler_bp.route('/enable', methods=['POST'])
def enable_scheduler():
    """启用调度器"""
    try:
        from app.config import Config

        # 更新配置
        Config.SCHEDULER_ENABLED = True

        # 尝试启动调度器
        if hasattr(scheduler_service, 'start_scheduler'):
            scheduler_service.start_scheduler()

        return jsonify({
            'success': True,
            'message': '调度器已启用',
            'data': {
                'scheduler_enabled': True,
                'note': '调度器已启用，如果之前未运行，可能需要重启应用'
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启用调度器失败: {str(e)}'
        }), 500


@scheduler_bp.route('/disable', methods=['POST'])
def disable_scheduler():
    """禁用调度器"""
    try:
        from app.config import Config

        # 更新配置
        Config.SCHEDULER_ENABLED = False

        # 尝试停止调度器
        if hasattr(scheduler_service, 'stop_scheduler'):
            scheduler_service.stop_scheduler()

        return jsonify({
            'success': True,
            'message': '调度器已禁用',
            'data': {
                'scheduler_enabled': False,
                'note': '调度器已禁用，所有定时任务将停止执行'
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'禁用调度器失败: {str(e)}'
        }), 500


# ============================================================================
# 前端集成辅助API
# ============================================================================

@scheduler_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取前端仪表板所需的完整数据"""
    try:
        # 汇总所有需要的数据
        scheduler_status = scheduler_service.get_scheduler_status()
        workflow_status = scheduler_service.get_workflow_status()
        processing_stats = ai_processing_service.get_processing_statistics(days_back=7)
        
        dashboard_data = {
            'overview': {
                'scheduler_running': scheduler_status['scheduler_running'],
                'total_jobs': scheduler_status['scheduled_jobs']['count'],
                'workflow_phases_count': len(workflow_status['phases']),
                'last_workflow_execution': workflow_status['execution_history'][-1] if workflow_status['execution_history'] else None
            },
            'workflow': {
                'phases': workflow_status['phases'],
                'recent_executions': workflow_status['execution_history'][-5:]  # 最近5次执行
            },
            'processing_stats': processing_stats,
            'scheduled_jobs': scheduler_status['scheduled_jobs']['jobs']
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取仪表板数据失败: {str(e)}'
        }), 500 