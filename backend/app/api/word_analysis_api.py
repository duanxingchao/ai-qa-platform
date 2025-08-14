"""
热词分析API
提供问题文本的热词统计和词云数据
"""
import logging
from flask import jsonify, request
from app.api import analysis_bp
from app.services.word_analysis_service import word_analysis_service

logger = logging.getLogger(__name__)


@analysis_bp.route('/word-cloud', methods=['GET'])
def get_word_cloud_data():
    """
    获取词云数据
    
    Query Parameters:
        time_range (str): 时间范围，可选值: 'week', 'month', 'all'，默认 'week'
        limit (int): 返回热词数量限制，默认 20
    
    Returns:
        JSON: 词云数据
        {
            "success": true,
            "data": {
                "word_cloud": [
                    {"name": "登录问题", "value": 156},
                    {"name": "密码重置", "value": 134}
                ],
                "total_questions": 1234,
                "unique_words": 456,
                "analysis_period": "2024-01-01 至 2024-01-07",
                "time_range": "week"
            }
        }
    """
    try:
        # 获取查询参数
        time_range = request.args.get('time_range', 'week')
        limit = int(request.args.get('limit', 20))
        
        # 参数验证
        if time_range not in ['week', 'month', 'all']:
            return jsonify({
                'success': False,
                'message': '无效的时间范围参数，支持: week, month, all'
            }), 400
        
        if limit <= 0 or limit > 100:
            return jsonify({
                'success': False,
                'message': '热词数量限制必须在1-100之间'
            }), 400
        
        logger.info(f"获取词云数据请求: time_range={time_range}, limit={limit}")
        
        # 调用服务获取数据
        result = word_analysis_service.get_word_cloud_data(
            time_range=time_range,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': result,
            'message': '获取词云数据成功'
        })
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'参数错误: {str(e)}'
        }), 400
        
    except Exception as e:
        logger.error(f"获取词云数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取词云数据失败: {str(e)}'
        }), 500


@analysis_bp.route('/hot-words', methods=['GET'])
def get_hot_words():
    """
    获取热词列表（简化版本，仅返回词汇和频次）
    
    Query Parameters:
        time_range (str): 时间范围，默认 'week'
        limit (int): 返回热词数量限制，默认 20
    
    Returns:
        JSON: 热词列表
    """
    try:
        time_range = request.args.get('time_range', 'week')
        limit = int(request.args.get('limit', 20))
        
        logger.info(f"获取热词列表请求: time_range={time_range}, limit={limit}")
        
        # 获取词云数据
        result = word_analysis_service.get_word_cloud_data(
            time_range=time_range,
            limit=limit
        )
        
        # 提取热词列表
        hot_words = [
            {
                'word': item['name'],
                'count': item['value'],
                'percentage': round((item['value'] / result['total_questions']) * 100, 2) if result['total_questions'] > 0 else 0
            }
            for item in result['word_cloud']
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'hot_words': hot_words,
                'total_questions': result['total_questions'],
                'analysis_period': result['analysis_period']
            },
            'message': '获取热词列表成功'
        })
        
    except Exception as e:
        logger.error(f"获取热词列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取热词列表失败: {str(e)}'
        }), 500
