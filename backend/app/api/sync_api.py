"""
数据同步API
"""
from flask import Blueprint, jsonify, request
from app.services.sync_service import sync_service

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/status', methods=['GET'])
def get_sync_status():
    """获取同步状态"""
    try:
        status = sync_service.get_sync_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步状态失败: {str(e)}'
        }), 500

@sync_bp.route('/trigger', methods=['POST'])
def trigger_sync():
    """手动触发数据同步"""
    try:
        # 获取请求参数
        data = request.get_json() or {}
        force_full_sync = data.get('force_full_sync', False)
        
        # 执行同步
        result = sync_service.perform_sync(force_full_sync=force_full_sync)
        
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'触发同步失败: {str(e)}'
        }), 500

@sync_bp.route('/statistics', methods=['GET'])
def get_sync_statistics():
    """获取同步统计信息"""
    try:
        stats = sync_service.get_sync_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步统计失败: {str(e)}'
        }), 500

@sync_bp.route('/history', methods=['GET'])
def get_sync_history():
    """获取同步历史记录"""
    try:
        # TODO: 实现同步历史记录查询
        return jsonify({
            'success': True,
            'data': {
                'message': '同步历史记录功能开发中'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步历史失败: {str(e)}'
        }), 500 