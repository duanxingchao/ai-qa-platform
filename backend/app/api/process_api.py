"""
数据处理API
"""
from flask import jsonify, request
from sqlalchemy import func
from app.api import process_bp
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.utils.database import db

@process_bp.route('/statistics', methods=['GET'])
def get_process_statistics():
    """获取处理统计数据"""
    try:
        # 总问题数和答案数
        total_questions = db.session.query(Question).count()
        total_answers = db.session.query(Answer).count()
        
        # 评分统计
        total_scores = db.session.query(Score).count()
        scored_answers = db.session.query(Answer).filter(Answer.is_scored == True).count()
        
        # 按助手类型统计答案
        answer_by_type = db.session.query(
            Answer.assistant_type,
            func.count(Answer.id)
        ).group_by(Answer.assistant_type).all()
        
        # 按处理状态统计问题
        status_stats = db.session.query(
            Question.processing_status,
            func.count(Question.id)
        ).group_by(Question.processing_status).all()
        
        # 计算完成率
        completion_rate = (scored_answers / total_answers * 100) if total_answers > 0 else 0
        
        data = {
            'total_questions': total_questions,
            'total_answers': total_answers,
            'total_scores': total_scores,
            'scored_answers': scored_answers,
            'completion_rate': f"{completion_rate:.1f}%",
            'answer_distribution': {
                assistant_type or 'unknown': count for assistant_type, count in answer_by_type
            },
            'status_distribution': {
                status or 'unknown': count for status, count in status_stats
            }
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取处理统计成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取处理统计失败: {str(e)}'
        }), 500

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