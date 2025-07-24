"""
大屏展示API - 实验室展示大屏数据接口
"""
from flask import jsonify, Blueprint
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.review import ReviewStatus
from app.utils.database import db
from app.utils.response import api_response, error_response

# 创建蓝图
display_bp = Blueprint('display', __name__)

@display_bp.route('/dashboard', methods=['GET'])
def get_display_dashboard():
    """获取大屏展示仪表板数据"""
    try:
        # 获取当前时间
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        
        # 1. 核心指标统计
        core_metrics = get_core_metrics(today_start, now)
        
        # 2. 数据处理流程统计
        process_flow = get_process_flow_stats()
        
        # 3. 近一周趋势数据（原24小时）
        trends_24h = get_week_trends()
        
        # 4. AI模型性能对比
        ai_performance = get_ai_performance_comparison()
        
        # 5. 热门问题分类
        hot_categories = get_hot_categories()
        
        # 6. 实时数据流（最近20条记录）
        realtime_events = get_realtime_events()
        
        # 7. 系统状态（基于现有数据推断）
        system_status = get_system_status()
        
        dashboard_data = {
            'core_metrics': core_metrics,
            'process_flow': process_flow,
            'trends_24h': trends_24h,
            'ai_performance': ai_performance,
            'hot_categories': hot_categories,
            'realtime_events': realtime_events,
            'system_status': system_status,
            'last_update': now.isoformat()
        }
        
        return api_response(data=dashboard_data, message="获取大屏数据成功")
        
    except Exception as e:
        return error_response(f"获取大屏数据失败: {str(e)}")

def get_core_metrics(today_start, now):
    """获取核心指标"""
    # 1. 累计总数据（从table1向questions表总更新问题数量）
    total_sync_count = db.session.query(Question).count()
    
    # 2. 月新增数据（从table1向questions表月更新问题数量）
    month_start = datetime(now.year, now.month, 1)
    monthly_sync_count = db.session.query(Question).filter(
        Question.created_at >= month_start
    ).count()
    
    # 3. 日新增数据（从table1向questions表本日更新问题数量）
    daily_sync_count = db.session.query(Question).filter(
        Question.created_at >= today_start
    ).count()
    
    # 4. 日总完成度计算
    # 获取今日的已分类数和已评分数
    today_classified_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= today_start,
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).count()
    
    today_scored_count = db.session.query(Answer).join(
        Question, Answer.question_business_id == Question.business_id
    ).filter(
        and_(
            Question.created_at >= today_start,
            Answer.is_scored == True
        )
    ).count()
    
    # 计算日完成度：（已分类数+已评分数）/日更新总问题数×2×100%
    if daily_sync_count > 0:
        daily_completion_rate = (today_classified_count + today_scored_count) / (daily_sync_count * 2) * 100
        daily_completion_rate = min(daily_completion_rate, 100)  # 限制最大值为100%
    else:
        daily_completion_rate = 0
    
    # 5. 平台日访问量（暂时返回暂无数据）
    daily_visits = "暂无数据"
    
    return {
        'total_sync_count': total_sync_count,
        'monthly_sync_count': monthly_sync_count,
        'daily_sync_count': daily_sync_count,
        'daily_completion_rate': round(daily_completion_rate, 1),
        'daily_visits': daily_visits
    }

def get_process_flow_stats():
    """获取数据处理流程统计（当日处理情况）"""
    # 获取当日时间范围
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    
    # 当日数据同步：当日新增问题数
    synced_count = db.session.query(Question).filter(
        Question.created_at >= today_start
    ).count()
    
    # 当日智能分类：当日已分类问题数
    classified_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= today_start,
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).count()
    
    # 当日答案生成：当日生成的答案数
    generated_count = db.session.query(Answer).join(
        Question, Answer.question_business_id == Question.business_id
    ).filter(
        Question.created_at >= today_start
    ).count()
    
    # 当日质量评分：当日已评分答案数
    scored_count = db.session.query(Answer).join(
        Question, Answer.question_business_id == Question.business_id
    ).filter(
        and_(
            Question.created_at >= today_start,
            Answer.is_scored == True
        )
    ).count()
    
    # 当日人工审核：当日已审核数（如果有数据）
    reviewed_count = db.session.query(ReviewStatus).join(
        Question, ReviewStatus.question_business_id == Question.business_id
    ).filter(
        and_(
            Question.created_at >= today_start,
            ReviewStatus.is_reviewed == True
        )
    ).count()
    
    # 计算各阶段完成率（基于当日数据）
    sync_rate = 100.0  # 同步率始终为100%，表示当日新增问题都已同步
    classify_rate = (classified_count / synced_count * 100) if synced_count > 0 else 0
    generate_rate = (generated_count / classified_count * 100) if classified_count > 0 else 0
    score_rate = (scored_count / generated_count * 100) if generated_count > 0 else 0
    review_rate = (reviewed_count / scored_count * 100) if scored_count > 0 else 0
    
    return {
        'stages': [
            {'name': '同步&清洗', 'count': synced_count, 'rate': sync_rate, 'icon': '📊'},
            {'name': 'AI垂域分类', 'count': classified_count, 'rate': round(classify_rate, 1), 'icon': '🏷️'},
            {'name': 'AI竞品跑测', 'count': generated_count, 'rate': round(generate_rate, 1), 'icon': '🤖'},
            {'name': 'AI答案评测', 'count': scored_count, 'rate': round(score_rate, 1), 'icon': '⭐'},
            {'name': '人工复核', 'count': reviewed_count, 'rate': round(review_rate, 1), 'icon': '✅'}
        ]
    }

def get_week_trends():
    """获取近一周趋势数据"""
    try:
        # 获取近一周的时间范围
        days_ago_7 = datetime.utcnow() - timedelta(days=7)
        
        # 按天分组统计问题数量
        daily_questions = db.session.query(
            func.date_trunc('day', Question.sendmessagetime).label('day'),
            func.count(Question.id).label('count')
        ).filter(
            Question.sendmessagetime >= days_ago_7
        ).group_by(
            func.date_trunc('day', Question.sendmessagetime)
        ).order_by('day').all()
        
        # 按天分组统计答案数量
        daily_answers = db.session.query(
            func.date_trunc('day', Answer.created_at).label('day'),
            func.count(Answer.id).label('count')
        ).filter(
            Answer.created_at >= days_ago_7
        ).group_by(
            func.date_trunc('day', Answer.created_at)
        ).order_by('day').all()
        
        # 按天分组统计评分数量
        daily_scores = db.session.query(
            func.date_trunc('day', Score.rated_at).label('day'),
            func.count(Score.id).label('count')
        ).filter(
            Score.rated_at >= days_ago_7
        ).group_by(
            func.date_trunc('day', Score.rated_at)
        ).order_by('day').all()
        
        # 转换查询结果为字典以便快速查找
        questions_dict = {item.day.date(): item.count for item in daily_questions if item.day}
        answers_dict = {item.day.date(): item.count for item in daily_answers if item.day}
        scores_dict = {item.day.date(): item.count for item in daily_scores if item.day}
        
        # 生成近一周完整日期序列
        trend_data = []
        for i in range(8):  # 包括今天共8天
            day_date = (datetime.utcnow() - timedelta(days=7-i)).date()
            day_label = day_date.strftime('%m-%d')
            # 查找对应日期的数据
            questions_count = questions_dict.get(day_date, 0)
            answers_count = answers_dict.get(day_date, 0)
            scores_count = scores_dict.get(day_date, 0)
            trend_data.append({
                'time': day_label,
                'questions': questions_count,
                'answers': answers_count,
                'scores': scores_count
            })
        
        return trend_data
    except Exception as e:
        print(f"获取近一周趋势数据失败: {e}")
        # 返回默认数据
        default_data = [
            {'time': (datetime.utcnow() - timedelta(days=7-i)).date().strftime('%m-%d'), 'questions': 0, 'answers': 0, 'scores': 0}
            for i in range(8)
        ]
        return default_data

# 保留原函数但不再使用
def get_24h_trends():
    """获取24小时趋势数据"""
    try:
        hours_ago_24 = datetime.utcnow() - timedelta(hours=24)
        
        # 按小时分组统计问题数量
        hourly_questions = db.session.query(
            func.date_trunc('hour', Question.sendmessagetime).label('hour'),
            func.count(Question.id).label('count')
        ).filter(
            Question.sendmessagetime >= hours_ago_24
        ).group_by(
            func.date_trunc('hour', Question.sendmessagetime)
        ).order_by('hour').all()
        
        # 按小时分组统计答案数量
        hourly_answers = db.session.query(
            func.date_trunc('hour', Answer.created_at).label('hour'),
            func.count(Answer.id).label('count')
        ).filter(
            Answer.created_at >= hours_ago_24
        ).group_by(
            func.date_trunc('hour', Answer.created_at)
        ).order_by('hour').all()
        
        # 按小时分组统计评分数量
        hourly_scores = db.session.query(
            func.date_trunc('hour', Score.rated_at).label('hour'),
            func.count(Score.id).label('count')
        ).filter(
            Score.rated_at >= hours_ago_24
        ).group_by(
            func.date_trunc('hour', Score.rated_at)
        ).order_by('hour').all()
        
        # 转换查询结果为字典以便快速查找
        questions_dict = {item.hour: item.count for item in hourly_questions if item.hour}
        answers_dict = {item.hour: item.count for item in hourly_answers if item.hour}
        scores_dict = {item.hour: item.count for item in hourly_scores if item.hour}
        
        # 生成24小时完整时间序列
        trend_data = []
        for i in range(24):
            hour_time = datetime.utcnow() - timedelta(hours=23-i)
            hour_time = hour_time.replace(minute=0, second=0, microsecond=0)
            
            # 查找对应时间的数据
            questions_count = questions_dict.get(hour_time, 0)
            answers_count = answers_dict.get(hour_time, 0)
            scores_count = scores_dict.get(hour_time, 0)
            
            # 计算成功率
            success_rate = (scores_count / answers_count * 100) if answers_count > 0 else 0
            
            trend_data.append({
                'time': hour_time.strftime('%H:%M'),
                'questions': questions_count,
                'answers': answers_count,
                'scores': scores_count,
                'success_rate': round(success_rate, 1)
            })
        
        return trend_data
    except Exception as e:
        print(f"获取24小时趋势数据失败: {e}")
        # 返回默认数据
        default_data = []
        for i in range(24):
            hour_time = datetime.utcnow() - timedelta(hours=23-i)
            hour_time = hour_time.replace(minute=0, second=0, microsecond=0)
            default_data.append({
                'time': hour_time.strftime('%H:%M'),
                'questions': 0,
                'answers': 0,
                'scores': 0,
                'success_rate': 0
            })
        return default_data

def get_ai_performance_comparison():
    """获取AI模型性能对比"""
    # 查询各AI模型的评分数据
    model_performance = db.session.query(
        Answer.assistant_type,
        func.avg(Score.score_1).label('avg_score_1'),
        func.avg(Score.score_2).label('avg_score_2'),
        func.avg(Score.score_3).label('avg_score_3'),
        func.avg(Score.score_4).label('avg_score_4'),
        func.avg(Score.score_5).label('avg_score_5'),
        func.avg(Score.average_score).label('avg_total'),
        func.count(Score.id).label('score_count')
    ).join(Score, Answer.id == Score.answer_id).group_by(
        Answer.assistant_type
    ).all()
    
    # 处理结果
    radar_data = []
    for item in model_performance:
        model_name = get_model_display_name(item.assistant_type)
        radar_data.append({
            'name': model_name,
            'data': [
                round(float(item.avg_score_1 or 0), 1),
                round(float(item.avg_score_2 or 0), 1),
                round(float(item.avg_score_3 or 0), 1),
                round(float(item.avg_score_4 or 0), 1),
                round(float(item.avg_score_5 or 0), 1)
            ],
            'total_score': round(float(item.avg_total or 0), 1),
            'score_count': item.score_count
        })
    
    return {
        'dimensions': ['相关性', '准确性', '完整性', '清晰度', '有用性'],
        'models': radar_data
    }

def get_hot_categories():
    """获取热门问题分类（近一周，用于饼图显示）"""
    # 近一周时间范围
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # 定义16个问题分类
    all_categories = [
        '技术问题', '功能建议', '产品使用', '业务咨询', '故障排查',
        '其他', '科学问题', '工程问题', '教育问题', '经济问题',
        '医学问题', '法律问题', '历史问题', '文化问题', '体育问题', '娱乐问题'
    ]
    
    # 查询近一周的问题分类统计
    category_stats = db.session.query(
        Question.classification,
        func.count(Question.id).label('count')
    ).filter(
        and_(
            Question.classification.isnot(None),
            Question.classification != '',
            Question.sendmessagetime >= week_ago
        )
    ).group_by(Question.classification).all()
    
    # 转换为字典便于查找
    stats_dict = {item.classification: item.count for item in category_stats}
    
    # 计算总数
    total_count = sum(stats_dict.values())
    
    # 构建16个分类的完整数据
    categories = []
    for category_name in all_categories:
        count = stats_dict.get(category_name, 0)
        percentage = (count / total_count * 100) if total_count > 0 else 0
        categories.append({
            'name': category_name,
            'count': count,
            'percentage': round(percentage, 1),
            'value': count  # 饼图需要的value字段
        })
    
    # 按数量排序（饼图展示时大的扇形在前）
    categories.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        'categories': categories,
        'total_count': total_count,
        'time_range': '近一周'
    }

def get_realtime_events():
    """获取实时事件流（模拟）"""
    try:
        events = []
        
        # 最近问题
        recent_questions = db.session.query(Question).order_by(
            desc(Question.created_at)
        ).limit(5).all()
        
        for q in recent_questions:
            if q.created_at:  # 检查时间不为空
                events.append({
                    'time': q.created_at.strftime('%H:%M:%S'),
                    'type': 'question',
                    'message': f'新增问题: {(q.query or "")[:30]}...',
                    'icon': '❓'
                })
        
        # 最近答案
        recent_answers = db.session.query(Answer).order_by(
            desc(Answer.created_at)
        ).limit(5).all()
        
        for a in recent_answers:
            if a.created_at:  # 检查时间不为空
                model_name = get_model_display_name(a.assistant_type)
                events.append({
                    'time': a.created_at.strftime('%H:%M:%S'),
                    'type': 'answer',
                    'message': f'{model_name}完成回答',
                    'icon': '🤖'
                })
        
        # 最近评分
        recent_scores = db.session.query(Score).order_by(
            desc(Score.rated_at)
        ).limit(5).all()
        
        for s in recent_scores:
            if s.rated_at:  # 检查时间不为空
                events.append({
                    'time': s.rated_at.strftime('%H:%M:%S'),
                    'type': 'score',
                    'message': f'评分完成: {s.average_score or 0}分',
                    'icon': '⭐'
                })
        
        # 按时间排序
        events.sort(key=lambda x: x['time'], reverse=True)
        
        return events[:20]
    except Exception as e:
        print(f"获取实时事件失败: {e}")
        # 返回默认事件
        return [
            {
                'time': datetime.utcnow().strftime('%H:%M:%S'),
                'type': 'system',
                'message': '系统正常运行中...',
                'icon': '🔄'
            }
        ]

def get_system_status():
    """获取系统状态（基于数据推断）"""
    # 检查最近数据更新情况来推断系统状态
    now = datetime.utcnow()
    minutes_ago_5 = now - timedelta(minutes=5)
    
    # 检查最近5分钟是否有新数据
    recent_questions = db.session.query(Question).filter(
        Question.created_at >= minutes_ago_5
    ).count()
    
    recent_answers = db.session.query(Answer).filter(
        Answer.created_at >= minutes_ago_5
    ).count()
    
    recent_scores = db.session.query(Score).filter(
        Score.rated_at >= minutes_ago_5
    ).count()
    
    # 计算系统健康度
    health_score = 85  # 基础分数
    if recent_questions > 0:
        health_score += 5
    if recent_answers > 0:
        health_score += 5
    if recent_scores > 0:
        health_score += 5
    
    # AI模型状态
    ai_models = [
        {'name': '原始模型', 'status': 'online', 'type': 'our_ai'},
        {'name': '豆包模型', 'status': 'online', 'type': 'doubao'},
        {'name': '小天模型', 'status': 'online', 'type': 'xiaotian'}
    ]
    
    # 根据最近答案活动判断模型状态
    for model in ai_models:
        recent_model_answers = db.session.query(Answer).filter(
            and_(
                Answer.assistant_type == model['type'],
                Answer.created_at >= minutes_ago_5
            )
        ).count()
        
        if recent_model_answers == 0:
            model['status'] = 'idle'
    
    return {
        'health_score': min(health_score, 100),
        'ai_models': ai_models,
        'services': [
            {'name': '数据同步', 'status': 'online'},
            {'name': '智能分类', 'status': 'online'},
            {'name': '答案生成', 'status': 'online'},
            {'name': '质量评分', 'status': 'online'}
        ]
    }

def get_model_display_name(assistant_type):
    """获取AI模型显示名称"""
    name_map = {
        'our_ai': '原始模型',
        'doubao': '豆包模型',
        'xiaotian': '小天模型'
    }
    return name_map.get(assistant_type, assistant_type)

@display_bp.route('/realtime', methods=['GET'])
def get_realtime_update():
    """获取实时更新数据（轻量级）"""
    try:
        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        
        # 只返回核心指标和最新事件
        core_metrics = get_core_metrics(today_start, now)
        realtime_events = get_realtime_events()[:5]  # 只要最新5条
        
        data = {
            'core_metrics': core_metrics,
            'realtime_events': realtime_events,
            'last_update': now.isoformat()
        }
        
        return api_response(data=data, message="获取实时数据成功")
        
    except Exception as e:
        return error_response(f"获取实时数据失败: {str(e)}") 