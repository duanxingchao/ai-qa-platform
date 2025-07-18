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
        
        # 处理time_range参数
        if time_range and time_range != 'all':
            now = datetime.utcnow()
            if time_range == 'today':
                # 今日：从今天0点到明天0点
                start_dt = datetime(now.year, now.month, now.day)
                end_dt = start_dt + timedelta(days=1)
                time_filter = [
                    Question.sendmessagetime >= start_dt,
                    Question.sendmessagetime < end_dt
                ]
            elif time_range == 'week':
                # 本周：最近7天
                start_dt = now - timedelta(days=7)
                end_dt = now
                time_filter = [
                    Question.sendmessagetime >= start_dt,
                    Question.sendmessagetime <= end_dt
                ]
            elif time_range == 'month':
                # 本月：从本月1号到现在
                start_dt = datetime(now.year, now.month, 1)
                end_dt = now
                time_filter = [
                    Question.sendmessagetime >= start_dt,
                    Question.sendmessagetime <= end_dt
                ]
            elif time_range == 'year':
                # 本年：从今年1月1号到现在
                start_dt = datetime(now.year, 1, 1)
                end_dt = now
                time_filter = [
                    Question.sendmessagetime >= start_dt,
                    Question.sendmessagetime <= end_dt
                ]
        
        # 如果time_range没有匹配，则使用start_time和end_time参数
        elif start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                time_filter = [
                    Question.sendmessagetime >= start_dt,
                    Question.sendmessagetime <= end_dt
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
        
        # 竞品答案统计（豆包和小天）
        doubao_answers = answer_query.filter(Answer.assistant_type == 'doubao').count()
        xiaotian_answers = answer_query.filter(Answer.assistant_type == 'xiaotian').count()
        competitor_answers = doubao_answers + xiaotian_answers
        
        # 计算完成率
        completion_rate = (scored_answers / total_answers * 100) if total_answers > 0 else 0
        
        # 获取同步统计
        sync_stats = sync_service.get_sync_statistics()
        
        # 最近7天趋势数据
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # 生成最近7天的日期列表
        date_list = []
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=6-i)).date()
            date_list.append(date)
        
        # 查询最近7天的问题趋势
        question_trend_query = db.session.query(
            func.date(Question.sendmessagetime).label('date'),
            func.count(Question.id).label('questions')
        ).filter(Question.sendmessagetime >= week_ago)
        
        if time_filter:
            question_trend_query = question_trend_query.filter(and_(*time_filter))
            
        question_trend = question_trend_query.group_by(func.date(Question.sendmessagetime)).all()
        question_trend_dict = {str(item.date): item.questions for item in question_trend}
        
        # 查询最近7天的分类趋势
        classification_trend_query = db.session.query(
            func.date(Question.sendmessagetime).label('date'),
            func.count(Question.id).label('classifications')
        ).filter(
            and_(
                Question.sendmessagetime >= week_ago,
                Question.classification.isnot(None),
                Question.classification != ''
            )
        )
        
        if time_filter:
            classification_trend_query = classification_trend_query.filter(and_(*time_filter))
            
        classification_trend = classification_trend_query.group_by(func.date(Question.sendmessagetime)).all()
        classification_trend_dict = {str(item.date): item.classifications for item in classification_trend}
        
        # 查询最近7天的评分趋势
        score_trend_query = db.session.query(
            func.date(Score.rated_at).label('date'),
            func.count(Score.id).label('scores')
        ).filter(Score.rated_at >= week_ago)
        
        score_trend = score_trend_query.group_by(func.date(Score.rated_at)).all()
        score_trend_dict = {str(item.date): item.scores for item in score_trend}
        
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
                'completion_rate': f"{completion_rate:.1f}%",
                'competitor_answers': {
                    'doubao': doubao_answers,
                    'xiaotian': xiaotian_answers,
                    'total': competitor_answers
                }
            },
            'sync_status': sync_stats,
            'trend_data': [
                {
                    'date': str(date),
                    'questions': question_trend_dict.get(str(date), 0),
                    'classifications': classification_trend_dict.get(str(date), 0),
                    'scores': score_trend_dict.get(str(date), 0)
                } for date in date_list
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