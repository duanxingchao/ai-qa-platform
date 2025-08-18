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
    try:
        from app.services.ai_processing_service import ai_processing_service

        # 获取请求参数
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)

        # 调用AI处理服务进行分类
        result = ai_processing_service.process_classification_batch(
            limit=limit,
            days_back=days_back
        )

        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'data': {
                'processed_count': result.get('processed_count', 0),
                'success_count': result.get('success_count', 0),
                'error_count': result.get('error_count', 0)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分类处理失败: {str(e)}'
        }), 500

@process_bp.route('/generate', methods=['POST'])
def generate_answers():
    """触发答案生成"""
    try:
        from app.services.ai_processing_service import ai_processing_service

        # 获取请求参数
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)

        # 调用AI处理服务进行答案生成
        result = ai_processing_service.process_answer_generation_batch(
            limit=limit,
            days_back=days_back
        )

        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'data': {
                'processed_count': result.get('processed_count', 0),
                'doubao_count': result.get('doubao_count', 0),
                'xiaotian_count': result.get('xiaotian_count', 0),
                'error_count': result.get('error_count', 0)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'答案生成失败: {str(e)}'
        }), 500

@process_bp.route('/score', methods=['POST'])
def score_answers():
    """触发评分"""
    try:
        from app.services.ai_processing_service import ai_processing_service

        # 获取请求参数
        data = request.get_json() or {}
        limit = data.get('limit')
        days_back = data.get('days_back', 1)

        # 调用AI处理服务进行评分
        result = ai_processing_service.process_scoring_batch(
            limit=limit,
            days_back=days_back
        )

        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'data': {
                'processed_count': result.get('processed_count', 0),
                'success_count': result.get('success_count', 0),
                'error_count': result.get('error_count', 0)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'评分处理失败: {str(e)}'
        }), 500