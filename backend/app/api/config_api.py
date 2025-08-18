"""
系统配置API
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.system_config_service import SystemConfigService
from app.utils.time_utils import TimeRangeUtils
from app.utils.response import api_response, error_response
from datetime import datetime

# 创建蓝图
config_bp = Blueprint('config', __name__)


@config_bp.route('/', methods=['GET'])
def get_all_configs():
    """获取所有配置"""
    try:
        prefix = request.args.get('prefix')
        
        config_service = SystemConfigService()
        
        if prefix:
            configs = config_service.get_config_list(prefix)
        else:
            configs = config_service.get_config_list()
        
        return jsonify({
            'success': True,
            'data': configs
        })
        
    except Exception as e:
        current_app.logger.error(f"获取配置列表时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/<string:key>', methods=['GET'])
def get_config(key):
    """获取单个配置"""
    try:
        config_service = SystemConfigService()
        value = config_service.get_config(key)
        
        if value is None:
            return jsonify({
                'success': False,
                'message': '配置不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'key': key,
                'value': value
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/<string:key>', methods=['PUT'])
def update_config(key):
    """更新配置"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空，必须包含value字段'
            }), 400
        
        value = data['value']
        config_type = data.get('config_type')
        description = data.get('description')
        
        config_service = SystemConfigService()
        success = config_service.update_config(
            key=key,
            value=value,
            config_type=config_type,
            description=description
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': '更新配置失败'
            }), 500
        
        return jsonify({
            'success': True,
            'message': '配置更新成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"更新配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/<string:key>', methods=['DELETE'])
def delete_config(key):
    """删除配置"""
    try:
        config_service = SystemConfigService()
        success = config_service.delete_config(key)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '删除配置失败或配置不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '配置删除成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/monitor', methods=['GET'])
def get_monitor_configs():
    """获取监控相关配置"""
    try:
        config_service = SystemConfigService()
        configs = config_service.get_monitor_configs()
        
        return jsonify({
            'success': True,
            'data': configs
        })
        
    except Exception as e:
        current_app.logger.error(f"获取监控配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/monitor/<string:key>', methods=['PUT'])
def update_monitor_config(key):
    """更新监控配置"""
    try:
        data = request.get_json()
        
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空，必须包含value字段'
            }), 400
        
        value = data['value']
        
        config_service = SystemConfigService()
        success = config_service.update_monitor_config(key, value)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '更新监控配置失败'
            }), 500
        
        return jsonify({
            'success': True,
            'message': '监控配置更新成功'
        })

    except Exception as e:
        current_app.logger.error(f"更新监控配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/display', methods=['GET'])
def get_display_configs():
    """获取大屏展示配置"""
    try:
        config_service = SystemConfigService()

        # 获取大屏展示相关配置
        hot_categories_time_range = config_service.get_config('display.hot_categories_time_range', 'all')

        configs = {
            'hot_categories_time_range': hot_categories_time_range
        }

        return api_response(
            data=configs,
            message="获取大屏展示配置成功"
        )

    except Exception as e:
        current_app.logger.error(f"获取大屏展示配置时出错: {str(e)}")
        return error_response(f"获取大屏展示配置失败: {str(e)}")


@config_bp.route('/display', methods=['PUT'])
def update_display_configs():
    """更新大屏展示配置"""
    try:
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空")

        config_service = SystemConfigService()

        # 更新热门分类时间范围配置
        if 'hot_categories_time_range' in data:
            time_range = data['hot_categories_time_range']
            if time_range not in ['week', 'all']:
                return error_response("热门分类时间范围只能是 'week' 或 'all'")

            success = config_service.update_config(
                key='display.hot_categories_time_range',
                value=time_range,
                config_type='string',
                description='大屏展示热门分类时间范围配置'
            )

            if not success:
                return error_response("更新热门分类时间范围配置失败")

        return api_response(
            data=None,
            message="大屏展示配置更新成功"
        )

    except Exception as e:
        current_app.logger.error(f"更新大屏展示配置时出错: {str(e)}")
        return error_response(f"更新大屏展示配置失败: {str(e)}")


@config_bp.route('/reset/<string:key>', methods=['POST'])
def reset_config(key):
    """重置配置为默认值"""
    try:
        config_service = SystemConfigService()
        success = config_service.reset_config_to_default(key)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '重置配置失败或配置没有默认值'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '配置重置成功'
        })
        
    except Exception as e:
        current_app.logger.error(f"重置配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/batch', methods=['PUT'])
def batch_update_configs():
    """批量更新配置"""
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            return jsonify({
                'success': False,
                'message': '请求数据必须是配置键值对对象'
            }), 400
        
        config_service = SystemConfigService()
        success_count = 0
        error_count = 0
        errors = []
        
        for key, value in data.items():
            try:
                success = config_service.update_config(key, value)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"更新配置 {key} 失败")
            except Exception as e:
                error_count += 1
                errors.append(f"更新配置 {key} 时出错: {str(e)}")
        
        return jsonify({
            'success': error_count == 0,
            'message': f'批量更新完成，成功: {success_count}, 失败: {error_count}',
            'data': {
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"批量更新配置时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/schedule', methods=['POST'])
def schedule_config_change():
    """安排配置变更（延迟生效）"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400

        key = data.get('key')
        value = data.get('value')
        effective_time_str = data.get('effective_time')
        reason = data.get('reason', '')
        changed_by = data.get('changed_by', 'system')

        if not all([key, value is not None, effective_time_str]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数：key, value, effective_time'
            }), 400

        try:
            # 解析生效时间
            effective_time = datetime.fromisoformat(effective_time_str.replace('Z', ''))

            # 检查生效时间是否在未来
            if effective_time <= datetime.now():
                return jsonify({
                    'success': False,
                    'message': '生效时间必须在未来'
                }), 400

        except ValueError:
            return jsonify({
                'success': False,
                'message': '生效时间格式错误'
            }), 400

        config_service = SystemConfigService()
        success = config_service.schedule_config_change(key, value, effective_time, reason, changed_by)

        return jsonify({
            'success': success,
            'message': '配置变更已安排' if success else '安排配置变更失败'
        })

    except Exception as e:
        current_app.logger.error(f"安排配置变更时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/pending', methods=['GET'])
def get_pending_changes():
    """获取待生效的配置变更"""
    try:
        config_service = SystemConfigService()
        changes = config_service.get_pending_changes()

        return jsonify({
            'success': True,
            'data': changes
        })

    except Exception as e:
        current_app.logger.error(f"获取待生效变更时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/schedule/<string:key>', methods=['DELETE'])
def cancel_scheduled_change(key):
    """取消待生效的配置变更"""
    try:
        config_service = SystemConfigService()
        success = config_service.cancel_scheduled_change(key)

        return jsonify({
            'success': success,
            'message': '已取消配置变更' if success else '取消变更失败或变更不存在'
        })

    except Exception as e:
        current_app.logger.error(f"取消配置变更时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/next-week-start', methods=['GET'])
def get_next_week_start():
    """获取下周一的开始时间"""
    try:
        next_week_start = TimeRangeUtils.get_next_week_start()

        return jsonify({
            'success': True,
            'data': {
                'next_week_start': next_week_start.isoformat(),
                'formatted': next_week_start.strftime('%Y年%m月%d日 %H:%M')
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取下周开始时间时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@config_bp.route('/workflow', methods=['GET'])
def get_workflow_configs():
    """获取工作流配置"""
    try:
        config_service = SystemConfigService()

        # 获取工作流相关配置
        answer_generation_mode = config_service.get_config('workflow.answer_generation_mode', 'manual')

        configs = {
            'answer_generation_mode': answer_generation_mode
        }

        return api_response(
            data=configs,
            message="获取工作流配置成功"
        )

    except Exception as e:
        current_app.logger.error(f"获取工作流配置时出错: {str(e)}")
        return error_response(f"获取工作流配置失败: {str(e)}")


@config_bp.route('/workflow', methods=['PUT'])
def update_workflow_configs():
    """更新工作流配置"""
    try:
        data = request.get_json()

        if not data:
            return error_response("请求数据不能为空")

        config_service = SystemConfigService()

        # 更新答案生成模式配置
        if 'answer_generation_mode' in data:
            mode = data['answer_generation_mode']
            if mode not in ['manual', 'api']:
                return error_response("答案生成模式只能是 'manual' 或 'api'")

            success = config_service.update_config(
                key='workflow.answer_generation_mode',
                value=mode,
                config_type='string',
                description='工作流答案生成模式配置'
            )

            if not success:
                return error_response("更新答案生成模式配置失败")

        return api_response(
            data=None,
            message="工作流配置更新成功"
        )

    except Exception as e:
        current_app.logger.error(f"更新工作流配置时出错: {str(e)}")
        return error_response(f"更新工作流配置失败: {str(e)}")
