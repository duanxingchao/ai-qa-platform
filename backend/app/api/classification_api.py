"""
分类管理API
提供分类相关的查询接口，完全基于数据库动态获取分类数据
"""
from flask import Blueprint, jsonify, request
from app.services.classification_service import ClassificationService
from app.utils.time_utils import TimeRangeUtils
from datetime import datetime, timedelta

# 创建蓝图
classification_bp = Blueprint('classification', __name__, url_prefix='/api/classifications')


@classification_bp.route('', methods=['GET'])
def get_all_classifications():
    """获取所有分类列表"""
    try:
        classifications = ClassificationService.get_all_classifications()
        
        return jsonify({
            'success': True,
            'data': classifications,
            'total': len(classifications),
            'message': f'成功获取{len(classifications)}个分类'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类列表失败: {str(e)}'
        }), 500


@classification_bp.route('/with-count', methods=['GET'])
def get_classifications_with_count():
    """获取分类及其问题数量"""
    try:
        classifications = ClassificationService.get_classifications_with_count()
        
        data = []
        for classification, count in classifications:
            data.append({
                'name': classification,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data),
            'message': f'成功获取{len(data)}个分类的统计数据'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类统计失败: {str(e)}'
        }), 500


@classification_bp.route('/active', methods=['GET'])
def get_active_classifications():
    """获取活跃分类（有足够数据的分类）"""
    try:
        min_count = request.args.get('min_count', 1, type=int)
        classifications = ClassificationService.get_active_classifications(min_count)
        
        return jsonify({
            'success': True,
            'data': classifications,
            'total': len(classifications),
            'min_count': min_count,
            'message': f'成功获取{len(classifications)}个活跃分类（最少{min_count}个问题）'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取活跃分类失败: {str(e)}'
        }), 500


@classification_bp.route('/by-time-range', methods=['GET'])
def get_classifications_by_time_range():
    """获取指定时间范围内的分类统计"""
    try:
        # 获取时间范围参数
        time_range = request.args.get('time_range', 'week')
        
        # 解析时间范围
        if time_range == 'today':
            days = 1
        elif time_range == 'week':
            days = 7
        elif time_range == 'month':
            days = 30
        elif time_range == 'quarter':
            days = 90
        else:
            days = int(request.args.get('days', 7))
        
        classifications = ClassificationService.get_classifications_for_recent_period(days)
        
        data = []
        for classification, count in classifications:
            data.append({
                'name': classification,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'total': len(data),
            'time_range': f'最近{days}天',
            'message': f'成功获取最近{days}天的{len(data)}个分类统计'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取时间范围分类统计失败: {str(e)}'
        }), 500


@classification_bp.route('/summary', methods=['GET'])
def get_classification_summary():
    """获取分类数据摘要"""
    try:
        summary = ClassificationService.get_classification_summary()
        
        return jsonify({
            'success': True,
            'data': summary,
            'message': '成功获取分类数据摘要'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类摘要失败: {str(e)}'
        }), 500


@classification_bp.route('/validate', methods=['POST'])
def validate_classification():
    """验证分类是否存在"""
    try:
        data = request.get_json()
        if not data or 'classification' not in data:
            return jsonify({
                'success': False,
                'message': '请提供要验证的分类名称'
            }), 400
        
        classification = data['classification']
        is_valid = ClassificationService.validate_classification(classification)
        
        return jsonify({
            'success': True,
            'data': {
                'classification': classification,
                'is_valid': is_valid
            },
            'message': f'分类"{classification}"{"存在" if is_valid else "不存在"}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证分类失败: {str(e)}'
        }), 500


@classification_bp.route('/health', methods=['GET'])
def health_check():
    """分类服务健康检查"""
    try:
        # 尝试获取分类数据
        classifications = ClassificationService.get_all_classifications()
        summary = ClassificationService.get_classification_summary()
        
        return jsonify({
            'success': True,
            'data': {
                'service': 'classification_service',
                'status': 'healthy',
                'total_classifications': len(classifications),
                'total_questions': summary.get('total_questions', 0),
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': '分类服务运行正常'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {
                'service': 'classification_service',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            },
            'message': f'分类服务异常: {str(e)}'
        }), 500
