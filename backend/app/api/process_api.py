"""
数据处理API
"""
from flask import jsonify, request
from app.api import process_bp

@process_bp.route('/classify', methods=['POST'])
def classify_data():
    """触发分类"""
    # TODO: 实现分类逻辑
    return jsonify({
        'status': 'success',
        'message': '分类处理已开始'
    })

@process_bp.route('/generate', methods=['POST'])
def generate_answers():
    """触发答案生成"""
    # TODO: 实现答案生成逻辑
    return jsonify({
        'status': 'success',
        'message': '答案生成已开始'
    })

@process_bp.route('/score', methods=['POST'])
def score_answers():
    """触发评分"""
    # TODO: 实现评分逻辑
    return jsonify({
        'status': 'success',
        'message': '评分处理已开始'
    }) 