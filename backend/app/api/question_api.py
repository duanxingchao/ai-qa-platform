"""
问题查询API
"""
from flask import jsonify, request
from app.api import question_bp

@question_bp.route('', methods=['GET'])
def get_questions():
    """获取问题列表"""
    # TODO: 实现查询逻辑
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    return jsonify({
        'status': 'success',
        'data': {
            'items': [],
            'total': 0,
            'page': page,
            'page_size': page_size
        }
    })

@question_bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """获取问题详情"""
    # TODO: 实现详情查询逻辑
    return jsonify({
        'status': 'success',
        'data': None
    }) 