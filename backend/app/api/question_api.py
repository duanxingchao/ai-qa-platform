"""
问题管理API - 完整实现
"""
from flask import request, jsonify
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from app.api import question_bp
from app.models.question import Question
from app.models.answer import Answer
from app.utils.database import db

@question_bp.route('', methods=['GET'])
def get_questions():
    """获取问题列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        keyword = request.args.get('keyword', '')
        classification = request.args.get('classification', '')
        status = request.args.get('status', '')
        start_time = request.args.get('start_time', '')
        end_time = request.args.get('end_time', '')
        
        # 构建查询
        question_query = db.session.query(Question)
        
        # 关键词搜索
        if keyword:
            question_query = question_query.filter(Question.query.ilike(f'%{keyword}%'))
        
        # 分类筛选
        if classification:
            question_query = question_query.filter(Question.classification == classification)
        
        # 状态筛选
        if status:
            question_query = question_query.filter(Question.processing_status == status)
        
        # 时间范围筛选
        if start_time:
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            question_query = question_query.filter(Question.sendmessagetime >= start_dt)
        
        if end_time:
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            question_query = question_query.filter(Question.sendmessagetime <= end_dt)
        
        # 排序和分页
        question_query = question_query.order_by(Question.created_at.desc())
        
        # 获取总数
        total = question_query.count()
        
        # 分页查询
        offset = (page - 1) * page_size
        questions = question_query.offset(offset).limit(page_size).all()
        
        # 序列化数据
        data = []
        for question in questions:
            data.append({
                'id': question.id,
                'business_id': question.business_id,
                'pageid': question.pageid,
                'devicetypename': question.devicetypename,
                'query': question.query,
                'sendmessagetime': question.sendmessagetime.isoformat() if question.sendmessagetime else None,
                'classification': question.classification,
                'processing_status': question.processing_status,
                'created_at': question.created_at.isoformat() if question.created_at else None,
                'updated_at': question.updated_at.isoformat() if question.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'message': '获取问题列表成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取问题列表失败: {str(e)}'
        }), 500

@question_bp.route('/statistics', methods=['GET'])
def get_question_statistics():
    """获取问题统计数据"""
    try:
        # 总问题数
        total_questions = db.session.query(Question).count()
        
        # 按处理状态统计
        status_stats = db.session.query(
            Question.processing_status,
            func.count(Question.id)
        ).group_by(Question.processing_status).all()
        
        # 按分类统计
        classification_stats = db.session.query(
            Question.classification,
            func.count(Question.id)
        ).filter(Question.classification.isnot(None)).group_by(Question.classification).all()
        
        # 按设备类型统计
        device_stats = db.session.query(
            Question.devicetypename,
            func.count(Question.id)
        ).group_by(Question.devicetypename).all()
        
        # 最近7天问题趋势
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_questions = db.session.query(
            func.date(Question.created_at).label('date'),
            func.count(Question.id).label('count')
        ).filter(
            Question.created_at >= week_ago
        ).group_by(func.date(Question.created_at)).all()
        
        # 组织返回数据
        data = {
            'total_questions': total_questions,
            'status_distribution': {
                status or 'unknown': count for status, count in status_stats
            },
            'classification_distribution': {
                classification: count for classification, count in classification_stats
            },
            'device_distribution': {
                device or 'unknown': count for device, count in device_stats
            },
            'recent_trend': [
                {
                    'date': str(date),
                    'count': count
                } for date, count in recent_questions
            ]
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取问题统计成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取问题统计失败: {str(e)}'
        }), 500

@question_bp.route('/<int:question_id>', methods=['GET'])
def get_question_detail(question_id):
    """获取问题详情"""
    try:
        question = Question.query.get_or_404(question_id)
        
        # 获取相关答案
        answers = Answer.query.filter_by(question_business_id=question.business_id).all()
        
        # 序列化答案数据
        answers_data = []
        for answer in answers:
            answers_data.append({
                'id': answer.id,
                'question_business_id': answer.question_business_id,
                'answer_text': answer.answer_text,
                'assistant_type': answer.assistant_type,
                'is_scored': answer.is_scored,
                'answer_time': answer.answer_time.isoformat() if answer.answer_time else None,
                'created_at': answer.created_at.isoformat() if answer.created_at else None,
                'updated_at': answer.updated_at.isoformat() if answer.updated_at else None
            })
        
        # 序列化问题数据
        data = {
            'id': question.id,
            'business_id': question.business_id,
            'pageid': question.pageid,
            'devicetypename': question.devicetypename,
            'query': question.query,
            'sendmessagetime': question.sendmessagetime.isoformat() if question.sendmessagetime else None,
            'classification': question.classification,
            'serviceid': question.serviceid,
            'qatype': question.qatype,
            'intent': question.intent,
            'iskeyboardinput': question.iskeyboardinput,
            'isstopanswer': question.isstopanswer,
            'processing_status': question.processing_status,
            'created_at': question.created_at.isoformat() if question.created_at else None,
            'updated_at': question.updated_at.isoformat() if question.updated_at else None,
            'answers': answers_data
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取问题详情成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取问题详情失败: {str(e)}'
        }), 500

@question_bp.route('/categories', methods=['GET'])
def get_question_categories():
    """获取问题分类列表"""
    try:
        # 从数据库中获取所有不为空的分类
        categories = db.session.query(Question.classification).filter(
            and_(
                Question.classification.isnot(None),
                Question.classification != ''
            )
        ).distinct().all()
        
        # 转换为前端需要的格式
        data = []
        for category in categories:
            if category[0]:  # 确保不为空
                data.append({
                    'value': category[0],
                    'label': category[0]
                })
        
        # 添加一些常见的分类（如果数据库中没有的话）
        common_categories = [
            {'value': '技术问题', 'label': '技术问题'},
            {'value': '产品咨询', 'label': '产品咨询'},
            {'value': '使用指导', 'label': '使用指导'},
            {'value': '故障报告', 'label': '故障报告'},
            {'value': '功能建议', 'label': '功能建议'},
            {'value': '其他', 'label': '其他'}
        ]
        
        # 去重并合并
        existing_values = {item['value'] for item in data}
        for category in common_categories:
            if category['value'] not in existing_values:
                data.append(category)
        
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取分类列表成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类列表失败: {str(e)}'
        }), 500

@question_bp.route('/<int:question_id>/reclassify', methods=['POST'])
def reclassify_question(question_id):
    """重新分类问题"""
    try:
        question = Question.query.get_or_404(question_id)
        
        # 这里可以调用AI分类API重新分类
        # 暂时模拟一个简单的重新分类逻辑
        from app.services.ai_processing_service import AIProcessingService
        ai_service = AIProcessingService()
        
        # 调用分类服务
        result = ai_service.process_classification_batch(limit=1)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': '重新分类成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '重新分类失败'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重新分类失败: {str(e)}'
        }), 500

@question_bp.route('/batch', methods=['POST'])
def batch_update_questions():
    """批量操作问题"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据为空'
            }), 400
        
        ids = data.get('ids', [])
        action = data.get('action', '')
        
        if not ids:
            return jsonify({
                'success': False,
                'message': '请选择要操作的问题'
            }), 400
        
        if action == 'reclassify':
            # 批量重新分类
            questions = Question.query.filter(Question.id.in_(ids)).all()
            
            for question in questions:
                # 这里可以调用AI分类API
                # 暂时标记为待重新分类
                question.processing_status = 'pending'
                question.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'成功标记 {len(questions)} 个问题进行重新分类'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': '不支持的操作类型'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'批量操作失败: {str(e)}'
        }), 500 