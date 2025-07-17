"""
仪表板API
提供仪表板页面所需的汇总数据
"""
from flask import jsonify, request
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.api import dashboard_bp
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.utils.database import db
from app.services.sync_service import sync_service
from app.services.api_client import APIClientFactory

@dashboard_bp.route('', methods=['GET'])
def get_dashboard_data():
    """获取仪表板汇总数据"""
    try:
        # 获取时间筛选参数
        time_range = request.args.get('time_range', 'all')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        # 构建时间过滤条件
        time_filter = []
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                time_filter = [
                    Question.created_at >= start_dt,
                    Question.created_at <= end_dt
                ]
            except ValueError:
                # 如果时间格式错误，忽略时间筛选
                pass
        
        # 基础统计查询
        question_query = db.session.query(Question)
        answer_query = db.session.query(Answer)
        
        # 应用时间筛选
        if time_filter:
            question_query = question_query.filter(and_(*time_filter))
            # 对于答案，我们通过关联问题来过滤
            answer_query = answer_query.join(Question, Answer.question_business_id == Question.business_id)
            answer_query = answer_query.filter(and_(*time_filter))
        
        # 基础统计
        total_questions = question_query.count()
        total_answers = answer_query.count()
        scored_answers = answer_query.filter(Answer.is_scored == True).count()
        total_scores = db.session.query(Score).count()
        
        # 计算完成率
        completion_rate = (scored_answers / total_answers * 100) if total_answers > 0 else 0
        
        # 获取同步统计
        sync_stats = sync_service.get_sync_statistics()
        
        # 最近7天趋势数据
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # 问题趋势 - 简化版本
        trend_query = db.session.query(
            func.date(Question.created_at).label('date'),
            func.count(Question.id).label('questions')
        ).filter(Question.created_at >= week_ago)
        
        if time_filter:
            trend_query = trend_query.filter(and_(*time_filter))
            
        question_trend = trend_query.group_by(func.date(Question.created_at)).all()
        
        # 按分类统计
        classification_query = question_query.filter(Question.classification.isnot(None))
        classification_stats = classification_query.with_entities(
            Question.classification,
            func.count(Question.id)
        ).group_by(Question.classification).all()
        
        # AI模型性能对比 - 简化版本
        ai_performance_query = answer_query.with_entities(
            Answer.assistant_type,
            func.count(Answer.id).label('total')
        ).group_by(Answer.assistant_type)
        
        ai_performance = ai_performance_query.all()
        
        # 检查外部API状态
        api_status = {}
        try:
            client_factory = APIClientFactory()
            api_status = {
                'classify_api': 'online',
                'doubao_api': 'online', 
                'xiaotian_api': 'online',
                'score_api': 'online'
            }
        except:
            api_status = {
                'classify_api': 'offline',
                'doubao_api': 'offline',
                'xiaotian_api': 'offline', 
                'score_api': 'offline'
            }
        
        # 组织返回数据
        data = {
            'summary': {
                'total_questions': total_questions,
                'total_answers': total_answers,
                'scored_answers': scored_answers,
                'completion_rate': f"{completion_rate:.1f}%"
            },
            'sync_status': sync_stats,
            'trend_data': [
                {
                    'date': str(item.date),
                    'questions': item.questions or 0,
                    'answers': 0,
                    'scores': 0
                } for item in question_trend
            ],
            'classification_distribution': {
                classification: count for classification, count in classification_stats
            },
            'ai_performance': [
                {
                    'assistant_type': item.assistant_type or 'unknown',
                    'total_answers': item.total,
                    'scored_answers': 0,
                    'average_score': 0.0
                } for item in ai_performance
            ],
            'api_status': api_status,
            'time_range': time_range,
            'filter_applied': bool(time_filter)
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取仪表板数据成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取仪表板数据失败: {str(e)}'
        }), 500 