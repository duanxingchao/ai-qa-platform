"""
访问统计API接口
"""
from flask import Blueprint, current_app
from app.services.access_service import AccessService
from app.utils.decorators import login_required, admin_required
from app.utils.response import success_response, error_response

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/access', methods=['GET'])
@login_required
@admin_required
def get_access_stats():
    """获取访问统计数据"""
    try:
        stats = AccessService.get_access_stats()
        return success_response("获取成功", stats)
        
    except Exception as e:
        current_app.logger.error(f"获取访问统计失败: {e}")
        return error_response("获取访问统计失败")

@stats_bp.route('/access-logs', methods=['GET'])
@login_required
@admin_required
def get_access_logs():
    """获取访问日志"""
    try:
        from flask import request

        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        action = request.args.get('action', '')

        logs = AccessService.get_access_logs_with_duration(
            page=page,
            page_size=page_size,
            action=action
        )

        return success_response("获取成功", logs)

    except Exception as e:
        current_app.logger.error(f"获取访问日志失败: {e}")
        return error_response("获取访问日志失败")
