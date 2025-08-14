"""
大屏展示API - 实验室展示大屏数据接口
"""
from flask import jsonify, Blueprint, request
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.review import ReviewStatus
from app.models.user import AccessLog
from app.utils.database import db
from app.utils.response import api_response, error_response
from app.utils.datetime_helper import utc_to_beijing_str
from app.services.classification_service import ClassificationService
from app.services.system_config_service import SystemConfigService

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
        
        # 5. 热门问题分类（使用配置的时间范围）
        config_service = SystemConfigService()
        time_range = config_service.get_config('display.hot_categories_time_range', 'all')
        hot_categories = get_hot_categories(time_range)
        
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
    # 1. 累计数据量（从table1向questions表总更新问题数量）
    total_data_count = db.session.query(Question).count()

    # 2. 周新增数据量（本周新增同步更新的量）
    week_start = now - timedelta(days=now.weekday())  # 本周一
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    weekly_new_data_count = db.session.query(Question).filter(
        Question.created_at >= week_start
    ).count()

    # 3. 周抽样跑测量（统计已分类数据量）
    weekly_classified_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= week_start,
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).count()

    # 累计分类数据量
    total_classified_count = db.session.query(Question).filter(
        and_(
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).count()

    # 4. 平台访问量（统计总访问量/周访问量）- 使用访问统计真实数据
    week_start = now - timedelta(days=now.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    # 以登录作为“访问”口径，可按需扩展为页面访问PV/UV
    total_visits = db.session.query(AccessLog).filter(AccessLog.action == 'login').count()
    weekly_visits = db.session.query(AccessLog).filter(
        and_(
            AccessLog.action == 'login',
            AccessLog.created_at >= week_start
        )
    ).count()

    # 保留原有字段以兼容其他可能的调用
    daily_sync_count = db.session.query(Question).filter(
        Question.created_at >= today_start
    ).count()

    return {
        # 新的字段名 - 分离累计和本周数据
        'total_data_count': total_data_count,
        'weekly_new_data_count': weekly_new_data_count,
        'total_classified_count': total_classified_count,
        'weekly_classified_count': weekly_classified_count,
        'platform_visits': total_visits,
        'weekly_visits': weekly_visits,

        # 保留原有字段以兼容
        'total_sync_count': total_data_count,
        'weekly_sync_count': weekly_new_data_count,
        'weekly_scored_count': weekly_classified_count,
        'total_visits': total_visits,
        'daily_sync_count': daily_sync_count,
        'daily_visits': "暂无数据"
    }

def check_and_clean_duplicate_answers():
    """检查并清理重复答案"""
    try:
        # 查找重复答案
        duplicate_answers = db.session.query(
            Answer.question_business_id,
            Answer.assistant_type,
            func.count(Answer.id).label('count')
        ).group_by(
            Answer.question_business_id,
            Answer.assistant_type
        ).having(
            func.count(Answer.id) > 1
        ).all()

        if duplicate_answers:
            print(f"发现 {len(duplicate_answers)} 组重复答案")
            for business_id, assistant_type, count in duplicate_answers:
                print(f"问题 {business_id} 的 {assistant_type} 答案有 {count} 个重复")

                # 保留最新的答案，删除旧的
                answers = db.session.query(Answer).filter_by(
                    question_business_id=business_id,
                    assistant_type=assistant_type
                ).order_by(Answer.created_at.desc()).all()

                # 删除除第一个（最新）之外的所有答案
                for answer in answers[1:]:
                    db.session.delete(answer)
                    print(f"删除重复答案: {answer.id}")

            db.session.commit()
            print("重复答案清理完成")
            return len(duplicate_answers)
        else:
            print("未发现重复答案")
            return 0

    except Exception as e:
        db.session.rollback()
        print(f"清理重复答案失败: {str(e)}")
        return -1

def get_process_flow_stats():
    """获取数据处理流程统计（本周处理情况）"""
    # 获取本周开始时间（周一00:00:00）
    now = datetime.utcnow()
    days_since_monday = now.weekday()  # 0=周一, 6=周日
    week_start = now - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)  # 本周周一00:00:00

    # 本周数据同步：本周新增问题数
    synced_count = db.session.query(Question).filter(
        Question.created_at >= week_start
    ).count()

    # 本周智能分类：本周已分类问题数
    classified_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= week_start,
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).count()

    # 本周竞品答案生成：本周生成的竞品答案数（豆包+小天）
    # 以问题为单位，限制每个问题最多计入2个竞品答案，避免重复答案导致统计>100%
    per_question_counts_subq = db.session.query(
        Answer.question_business_id.label('qbid'),
        func.count(Answer.id).label('cnt')
    ).join(
        Question, Answer.question_business_id == Question.business_id
    ).filter(
        and_(
            Question.created_at >= week_start,
            Answer.created_at >= week_start,
            Answer.assistant_type.in_(['doubao', 'xiaotian']),
            Question.classification.isnot(None),
            Question.classification != ''
        )
    ).group_by(Answer.question_business_id).subquery()

    generated_count = db.session.query(
        func.coalesce(func.sum(func.least(per_question_counts_subq.c.cnt, 2)), 0)
    ).select_from(per_question_counts_subq).scalar()



    # 本周AI竞品横评：统计已完成横评的问题数
    # 核心逻辑：基于已分类问题，检查是否有完整的三个AI答案且已评分

    # 统计已完成横评的问题数（三个AI答案都已评分）
    # 使用GROUP BY和HAVING来确保每个问题都有三个AI模型的已评分答案
    scored_questions_count = db.session.query(
        func.count(func.distinct(Answer.question_business_id))
    ).select_from(Answer).join(
        Question, Answer.question_business_id == Question.business_id
    ).filter(
        and_(
            Question.created_at >= week_start,
            Question.classification.isnot(None),
            Question.classification != '',
            Answer.is_scored == True,
            Answer.assistant_type.in_(['yoyo', 'doubao', 'xiaotian'])
        )
    ).group_by(Answer.question_business_id).having(
        func.count(func.distinct(Answer.assistant_type)) == 3
    ).count()

    # 计算有竞品答案的问题数（评分的前提条件）
    questions_with_competitor_answers = db.session.query(
        func.count(func.distinct(Question.business_id))
    ).select_from(Question).join(
        Answer, Question.business_id == Answer.question_business_id
    ).filter(
        and_(
            Question.created_at >= week_start,
            Question.classification.isnot(None),
            Question.classification != '',
            Answer.assistant_type.in_(['doubao', 'xiaotian']),
            Answer.created_at >= week_start
        )
    ).scalar()

    # 本周Badcase分析及复核：统计本周的badcase数量和复核情况
    # 1. 本周badcase总数（已评分且被检测为badcase的问题）
    badcase_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= week_start,
            Question.processing_status == 'scored',
            Question.is_badcase == True
        )
    ).count()

    # 2. 本周已复核的问题数量（包括确认和误判两种情况）
    reviewed_badcase_count = db.session.query(Question).filter(
        and_(
            Question.created_at >= week_start,
            Question.processing_status == 'scored',
            Question.badcase_review_status == 'reviewed'
        )
    ).count()

    # 计算各阶段完成率（基于本周数据）
    sync_rate = 100.0  # 同步率始终为100%，表示本周新增问题都已同步
    classify_rate = (classified_count / synced_count * 100) if synced_count > 0 else 0

    # AI竞品跑测：基于已分类问题数×2计算（每个问题期望生成豆包+小天2个答案）
    expected_competitor_answers = classified_count * 2
    generate_rate = (generated_count / expected_competitor_answers * 100) if expected_competitor_answers > 0 else 0

    # AI竞品横评：基于已分类问题数计算横评完成率
    score_rate = (scored_questions_count / classified_count * 100) if classified_count > 0 else 0

    # Badcase分析及复核：计算复核完成率
    badcase_review_rate = (reviewed_badcase_count / badcase_count * 100) if badcase_count > 0 else 0

    # 获取各阶段状态
    sync_status = get_sync_status(now)
    classify_status = get_classify_status(synced_count, classified_count, now)
    generate_status = get_generate_status(classified_count, generated_count, now)
    score_status = get_score_status(classified_count, scored_questions_count, now)
    badcase_review_status = get_badcase_review_status(badcase_review_rate)

    return {
        'stages': [
            {'name': '同步&清洗', 'count': synced_count, 'rate': sync_rate, 'icon': '📊', 'status': sync_status},
            {'name': 'AI垂域分类', 'count': classified_count, 'rate': round(classify_rate, 1), 'icon': '🏷️', 'status': classify_status},
            {'name': '竞品跑测', 'count': generated_count, 'rate': round(generate_rate, 1), 'icon': '🤖', 'status': generate_status},
            {'name': 'AI竞品横评', 'count': scored_questions_count, 'rate': round(score_rate, 1), 'icon': '⭐', 'status': score_status},
            {'name': 'Badcase复核', 'count': reviewed_badcase_count, 'rate': round(badcase_review_rate, 1), 'icon': '🔍', 'status': badcase_review_status}
        ]
    }

def get_week_trends():
    """获取近一周趋势数据：同步&清洗数、分类数、评分数"""
    try:
        # 获取近一周的时间范围
        days_ago_7 = datetime.utcnow() - timedelta(days=7)

        # 1. 按天分组统计同步&清洗数量（基于数据库插入时间 created_at）
        daily_questions = db.session.query(
            func.date_trunc('day', Question.created_at).label('day'),
            func.count(Question.id).label('count')
        ).filter(
            Question.created_at >= days_ago_7
        ).group_by(
            func.date_trunc('day', Question.created_at)
        ).order_by('day').all()

        # 2. 按天分组统计分类数量（基于分类完成时间）
        daily_classifications = db.session.query(
            func.date_trunc('day', Question.updated_at).label('day'),
            func.count(Question.id).label('count')
        ).filter(
            Question.updated_at >= days_ago_7,
            Question.classification.isnot(None),
            Question.classification != '',
            Question.processing_status.in_(['classified', 'answers_generated', 'scored'])  # 已完成分类的状态
        ).group_by(
            func.date_trunc('day', Question.updated_at)
        ).order_by('day').all()

        # 3. 按天分组统计评分数量（统计被评分的竞品答案数）
        daily_scores = db.session.query(
            func.date_trunc('day', Answer.created_at).label('day'),
            func.count(Answer.id).label('count')
        ).join(
            Question, Answer.question_business_id == Question.business_id
        ).filter(
            Answer.created_at >= days_ago_7,
            Question.created_at >= days_ago_7,  # 确保问题也在时间范围内
            Answer.assistant_type.in_(['doubao', 'xiaotian']),  # 只统计竞品答案
            Answer.is_scored == True,  # 只统计已评分的答案
            Question.classification.isnot(None),  # 确保问题已分类
            Question.classification != ''
        ).group_by(
            func.date_trunc('day', Answer.created_at)
        ).order_by('day').all()

        # 转换查询结果为字典以便快速查找
        questions_dict = {item.day.date(): item.count for item in daily_questions if item.day}
        classifications_dict = {item.day.date(): item.count for item in daily_classifications if item.day}
        scores_dict = {item.day.date(): item.count for item in daily_scores if item.day}

        # 生成近一周完整日期序列
        trend_data = []
        for i in range(8):  # 包括今天共8天
            day_date = (datetime.utcnow() - timedelta(days=7-i)).date()
            day_label = day_date.strftime('%m-%d')
            # 查找对应日期的数据
            questions_count = questions_dict.get(day_date, 0)
            classifications_count = classifications_dict.get(day_date, 0)
            scores_count = scores_dict.get(day_date, 0)
            trend_data.append({
                'time': day_label,
                'questions': questions_count,
                'classifications': classifications_count,
                'scores': scores_count
            })

        return trend_data
    except Exception as e:
        print(f"获取近一周趋势数据失败: {e}")
        # 返回默认数据
        default_data = [
            {'time': (datetime.utcnow() - timedelta(days=7-i)).date().strftime('%m-%d'), 'questions': 0, 'classifications': 0, 'scores': 0}
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

def get_hot_categories(time_range='all'):
    """获取热门问题分类（用于饼图显示）- 支持时间范围选择"""

    # 获取所有分类
    all_classifications_data = ClassificationService.get_all_classifications()
    all_classifications = [cat['name'] for cat in all_classifications_data]

    if time_range == 'week':
        # 近一周模式：只显示近一周有数据的分类
        recent_stats = ClassificationService.get_classifications_for_recent_period(days=7)

        if not recent_stats:
            # 如果近一周没有数据，返回空结果
            return {
                'categories': [],
                'total_count': 0,
                'time_range': '近一周',
                'total_categories': 0,
                'data_source': '真实分类数据'
            }

        # 计算总数
        total_count = sum(count for _, count in recent_stats)

        # 构建分类数据
        categories = []
        for classification, count in recent_stats:
            percentage = (count / total_count * 100) if total_count > 0 else 0
            categories.append({
                'name': classification,
                'count': count,
                'percentage': round(percentage, 1),
                'value': count  # 饼图需要的value字段
            })

        # 按数量排序
        categories.sort(key=lambda x: x['count'], reverse=True)

        return {
            'categories': categories,
            'total_count': total_count,
            'time_range': '近一周',
            'total_categories': len(categories),
            'data_source': '真实分类数据'
        }

    else:
        # 全部时间模式：显示所有分类，按活跃度排序
        # 获取近一周的分类统计（用于排序）
        recent_stats = ClassificationService.get_classifications_for_recent_period(days=7)
        recent_dict = dict(recent_stats)

        # 获取全部时间的分类统计
        all_stats = ClassificationService.get_classifications_with_count()
        all_dict = {item['name']: item['count'] for item in all_stats}

        # 计算总数（使用全部数据）
        total_count = sum(item['count'] for item in all_stats)

        # 构建分类数据 - 包含所有分类
        categories = []
        for classification in all_classifications:
            # 全部时间的数量
            all_count = all_dict.get(classification, 0)
            # 近一周的数量（用于热度排序）
            recent_count = recent_dict.get(classification, 0)

            percentage = (all_count / total_count * 100) if total_count > 0 else 0
            categories.append({
                'name': classification,
                'count': all_count,  # 显示全部时间的数量
                'recent_count': recent_count,  # 近期数量用于排序
                'percentage': round(percentage, 1),
                'value': all_count  # 饼图需要的value字段
            })

        # 按近期活跃度排序，如果近期没有数据则按总数排序
        categories.sort(key=lambda x: (x['recent_count'], x['count']), reverse=True)

        return {
            'categories': categories,
            'total_count': total_count,
            'time_range': '全部时间（按近期活跃度排序）',
            'total_categories': len(categories),
            'data_source': '真实分类数据'
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
                beijing_time = utc_to_beijing_str(q.created_at)
                time_part = beijing_time.split(' ')[1] if beijing_time else '00:00:00'
                events.append({
                    'time': time_part,
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
                beijing_time = utc_to_beijing_str(a.created_at)
                time_part = beijing_time.split(' ')[1] if beijing_time else '00:00:00'
                events.append({
                    'time': time_part,
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
                beijing_time = utc_to_beijing_str(s.rated_at)
                time_part = beijing_time.split(' ')[1] if beijing_time else '00:00:00'
                events.append({
                    'time': time_part,
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
        {'name': '原始模型', 'status': 'online', 'type': 'yoyo'},
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
        'yoyo': '原始模型',
        'doubao': '豆包模型',
        'xiaotian': '小天模型'
    }
    return name_map.get(assistant_type, assistant_type)

@display_bp.route('/ai-category-scores', methods=['GET'])
def get_ai_category_scores():
    """获取所有分类下三个AI的评分数据（用于柱状图展示）- 动态获取所有分类"""
    try:
        # 动态获取所有分类
        all_categories_data = ClassificationService.get_all_classifications()
        all_categories = [cat['name'] for cat in all_categories_data]

        # 定义AI模型映射（修正为正确的数据库字段值）
        ai_models = {
            'yoyo': 'YOYO',    # yoyo模型在数据库中是 'yoyo'
            'doubao': '豆包',
            'xiaotian': '小天'
        }

        # 查询各分类下各AI模型的平均评分（所有时间数据）
        category_scores = {}

        for category in all_categories:
            category_scores[category] = {}

            for ai_type, ai_name in ai_models.items():
                # 查询该分类下该AI的平均评分（所有时间）
                avg_score = db.session.query(
                    func.avg(Score.average_score).label('avg_score'),
                    func.count(Score.id).label('score_count')
                ).join(Answer, Score.answer_id == Answer.id)\
                 .join(Question, Answer.question_business_id == Question.business_id)\
                 .filter(
                    and_(
                        Question.classification == category,
                        Answer.assistant_type == ai_type,
                        Score.average_score.isnot(None)
                    )
                ).first()

                if avg_score.avg_score is not None and avg_score.score_count > 0:
                    # 使用真实的平均评分
                    score_value = round(float(avg_score.avg_score), 2)
                    category_scores[category][ai_name] = score_value
                else:
                    # 没有评分数据时设为0，表示该分类下该AI模型暂无评分
                    category_scores[category][ai_name] = 0

        # 转换为前端需要的格式（显示所有16种分类）
        chart_data = []
        for category in all_categories:
            scores = category_scores[category]
            chart_data.append({
                'category': category,
                'YOYO': scores.get('YOYO', 0),
                '豆包': scores.get('豆包', 0),
                '小天': scores.get('小天', 0)
            })

        return api_response(
            data={
                'chart_data': chart_data,
                'categories': all_categories,
                'ai_models': ['YOYO', '豆包', '小天'],
                'total_categories': len(all_categories),
                'time_range': '所有时间',
                'data_source': '真实评分数据'
            },
            message=f"成功获取所有{len(all_categories)}种分类的AI评分数据"
        )

    except Exception as e:
        return error_response(f"获取AI分类评分数据失败: {str(e)}")

@display_bp.route('/hot-categories', methods=['GET'])
def get_hot_categories_api():
    """获取热门问题分类API接口"""
    try:
        # 获取时间范围参数，默认为 'all'
        time_range = request.args.get('time_range', 'all')
        hot_categories_data = get_hot_categories(time_range)
        return api_response(
            data=hot_categories_data,
            message="成功获取热门分类数据"
        )
    except Exception as e:
        return error_response(f"获取热门分类数据失败: {str(e)}")

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

@display_bp.route('/check-duplicates', methods=['POST'])
def check_duplicate_answers():
    """检查并清理重复答案"""
    try:
        duplicate_count = check_and_clean_duplicate_answers()

        if duplicate_count > 0:
            return api_response(
                data={'cleaned_duplicates': duplicate_count},
                message=f"成功清理 {duplicate_count} 组重复答案"
            )
        elif duplicate_count == 0:
            return api_response(
                data={'cleaned_duplicates': 0},
                message="未发现重复答案"
            )
        else:
            return error_response("清理重复答案时发生错误")

    except Exception as e:
        return error_response(f"检查重复答案失败: {str(e)}")


def get_sync_status(now):
    """获取同步&清洗阶段状态"""
    try:
        # 检查最近1小时和6小时的数据同步情况
        recent_1h = db.session.query(Question).filter(
            Question.created_at >= now - timedelta(hours=1)
        ).count()
        recent_6h = db.session.query(Question).filter(
            Question.created_at >= now - timedelta(hours=6)
        ).count()

        if recent_6h == 0:
            return "异常"  # 超过6小时无数据
        elif recent_1h > 0:
            return "进行中"  # 最近1小时有数据
        else:
            return "空闲"  # 1-6小时内有数据但最近1小时无数据
    except Exception as e:
        print(f"获取同步状态失败: {e}")
        return "异常"


def get_classify_status(synced_count, classified_count, now):
    """获取AI垂域分类阶段状态"""
    try:
        # 待分类数据数量
        pending_classify = synced_count - classified_count

        # 检查最近30分钟是否有分类活动
        recent_30min_classified = db.session.query(Question).filter(
            and_(
                Question.updated_at >= now - timedelta(minutes=30),
                Question.classification.isnot(None),
                Question.classification != ''
            )
        ).count()

        # 这里简化处理，实际应该检查垂域分类API调用状态
        # 如果有待分类数据或最近有分类活动，则为进行中
        if pending_classify > 0 or recent_30min_classified > 0:
            return "进行中"  # 有待处理数据或最近有分类活动
        else:
            return "空闲"  # 无待处理数据且最近无活动
    except Exception as e:
        print(f"获取分类状态失败: {e}")
        return "异常"  # 垂域分类API调用异常


def get_generate_status(classified_count, generated_count, now):
    """获取AI竞品跑测阶段状态"""
    try:
        # 简化逻辑：基于数据量判断
        # 实际项目中应该检查API调用状态

        # 检查最近30分钟是否有答案生成活动
        recent_30min_generated = db.session.query(Answer).join(
            Question, Answer.question_business_id == Question.business_id
        ).filter(
            Answer.created_at >= now - timedelta(minutes=30)
        ).count()

        # 这里简化处理，实际应该检查API调用状态
        if recent_30min_generated > 0:
            return "进行中"  # 最近有生成活动
        elif classified_count > generated_count:
            return "进行中"  # 有待跑测数据
        else:
            return "空闲"  # 无待处理数据
    except Exception as e:
        print(f"获取跑测状态失败: {e}")
        return "异常"  # API调用异常


def get_score_status(classified_count, scored_questions_count, now):
    """获取AI竞品横评阶段状态"""
    try:
        # 检查最近30分钟是否有评分活动
        recent_30min_scored = db.session.query(Answer).filter(
            and_(
                Answer.updated_at >= now - timedelta(minutes=30),
                Answer.is_scored == True
            )
        ).count()

        # 这里简化处理，实际应该检查评分API调用状态
        if recent_30min_scored > 0:
            return "进行中"  # 最近有评分活动
        elif classified_count > scored_questions_count:
            return "进行中"  # 有待横评的已分类问题
        else:
            return "空闲"  # 无待处理数据
    except Exception as e:
        print(f"获取横评状态失败: {e}")
        return "异常"  # API调用异常


def get_review_status(scored_questions_count, reviewed_count):
    """获取人工复核阶段状态（已废弃，保留兼容性）"""
    try:
        # 人工复核不显示异常状态
        if scored_questions_count > reviewed_count:
            return "进行中"  # 有待复核数据
        else:
            return "空闲"  # 无待复核数据
    except Exception as e:
        print(f"获取复核状态失败: {e}")
        return "空闲"  # 出错时默认显示空闲


def get_badcase_review_status(badcase_review_rate):
    """获取Badcase分析及复核阶段状态"""
    try:
        # 只有复核率达到100%时才显示空闲，否则都是进行中
        if badcase_review_rate >= 100.0:
            return "空闲"  # 所有badcase都已复核完成
        else:
            return "进行中"  # 还有badcase待复核
    except Exception as e:
        print(f"获取Badcase复核状态失败: {e}")
        return "进行中"  # 出错时默认显示进行中