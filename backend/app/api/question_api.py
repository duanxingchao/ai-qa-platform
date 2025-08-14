"""
问题管理API - 完整实现
"""
from flask import request, jsonify
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from app.api import question_bp
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.review import ReviewStatus
from app.utils.database import db
from app.models.reclassification import QuestionReclassification
from app.services.classification_service import ClassificationService

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
    """获取问题详情 - 增强版，返回所有相关信息"""
    try:
        question = db.session.query(Question).filter_by(id=question_id).first()
        if not question:
            return jsonify({
                'success': False,
                'message': '问题不存在'
            }), 404

        # 获取相关答案
        answers = Answer.query.filter_by(question_business_id=question.business_id).all()

        # 序列化答案数据，包含评分信息
        answers_data = []
        for answer in answers:
            answer_dict = answer.to_dict(include_score=True)

            # 获取该答案的所有评分历史
            scores = Score.query.filter_by(answer_id=answer.id).order_by(Score.rated_at.desc()).all()
            answer_dict['score_history'] = [score.to_dict() for score in scores]

            answers_data.append(answer_dict)
        
        # 获取审核状态信息
        review_status = ReviewStatus.query.filter_by(question_business_id=question.business_id).first()
        review_data = None
        if review_status:
            review_data = {
                'id': review_status.id,
                'is_reviewed': review_status.is_reviewed,
                'reviewer_id': review_status.reviewer_id,
                'review_comment': review_status.review_comment,
                'reviewed_at': review_status.reviewed_at.isoformat() if review_status.reviewed_at else None
            }

        # 统计信息
        stats = {
            'total_answers': len(answers_data),
            'scored_answers': sum(1 for answer in answers_data if answer['is_scored']),
            'assistant_types': list(set(answer['assistant_type'] for answer in answers_data)),
            'avg_scores': {}
        }

        # 计算各AI类型的平均分
        for assistant_type in stats['assistant_types']:
            type_scores = []
            for answer in answers_data:
                if answer['assistant_type'] == assistant_type and answer.get('score'):
                    avg_score = answer['score'].get('average_score')
                    if avg_score:
                        type_scores.append(float(avg_score))

            if type_scores:
                stats['avg_scores'][assistant_type] = round(sum(type_scores) / len(type_scores), 2)

        # 序列化问题数据 - 完整版
        data = question.to_dict()
        data.update({
            'answers': answers_data,
            'review_status': review_data,
            'statistics': stats
        })
        
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
    """获取问题分类列表 - 动态从数据库获取"""
    try:
        # 从数据库动态获取分类及数量
        classifications_with_count = ClassificationService.get_classifications_with_count()

        # 转换为前端需要的格式
        data = []
        for classification_dict in classifications_with_count:
            data.append({
                'value': classification_dict['name'],
                'label': f"{classification_dict['name']} ({classification_dict['count']})",
                'count': classification_dict['count']
            })

        return jsonify({
            'success': True,
            'data': data,
            'total_categories': len(data),
            'message': f'成功获取{len(data)}个分类'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类列表失败: {str(e)}'
        }), 500

@question_bp.route('/<int:question_id>/reclassify', methods=['POST'])
def reclassify_question(question_id):
    """重新分类问题（支持指定新分类并记录历史）"""
    try:
        data = request.get_json() or {}
        new_classification = data.get('new_classification')
        reason = data.get('reason')
        changed_by = data.get('changed_by')

        question = db.session.get(Question, question_id)
        if not question:
            return jsonify({'success': False, 'message': '问题不存在'}), 404

        if not new_classification:
            return jsonify({'success': False, 'message': '新分类不能为空'}), 400

        # 确保历史表存在（首次部署免迁移保护）
        try:
            QuestionReclassification.__table__.create(bind=db.engine, checkfirst=True)
        except Exception:
            pass

        old_classification = question.classification

        # 先更新问题分类并提交，确保核心业务成功
        # 注意：重新分类只更改分类字段，不影响处理状态
        question.classification = new_classification
        question.updated_at = datetime.utcnow()
        db.session.commit()

        # 历史记录尽力写入，不影响主流程
        try:
            history = QuestionReclassification(
                question_business_id=question.business_id,
                old_classification=old_classification,
                new_classification=new_classification,
                reason=reason,
                changed_by=changed_by
            )
            db.session.add(history)
            db.session.commit()
            history_data = history.to_dict()
        except Exception as he:
            db.session.rollback()
            history_data = None

        return jsonify({'success': True, 'message': '重新分类成功', 'data': history_data})

    except Exception as e:
        db.session.rollback()
        # 返回更详细的错误信息，便于前端提示（开发阶段）
        return jsonify({'success': False, 'message': f'重新分类失败: {type(e).__name__}: {str(e)}'}), 500

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
            # 批量重新分类到指定新分类
            new_classification = data.get('new_classification')
            reason = data.get('reason')
            changed_by = data.get('changed_by')

            if not new_classification:
                return jsonify({'success': False, 'message': '新分类不能为空'}), 400

            # 确保历史表存在（首次部署免迁移保护）
            try:
                QuestionReclassification.__table__.create(bind=db.engine, checkfirst=True)
            except Exception:
                pass

            questions = db.session.query(Question).filter(Question.id.in_(ids)).all()

            # 保存旧分类值用于历史记录
            old_classifications = {}
            for question in questions:
                old_classifications[question.business_id] = question.classification
                # 注意：重新分类只更改分类字段，不影响处理状态
                question.classification = new_classification
                question.updated_at = datetime.utcnow()

            # 先提交主表更新
            db.session.commit()

            # 历史记录尽力写入
            try:
                for question in questions:
                    history = QuestionReclassification(
                        question_business_id=question.business_id,
                        old_classification=old_classifications.get(question.business_id),
                        new_classification=new_classification,
                        reason=reason,
                        changed_by=changed_by
                    )
                    db.session.add(history)
                db.session.commit()
            except Exception:
                db.session.rollback()

            return jsonify({'success': True, 'message': f'成功重新分类 {len(questions)} 个问题'})
        
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