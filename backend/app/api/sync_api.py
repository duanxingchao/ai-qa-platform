"""
数据同步API（支持questions和answers表分离同步）
"""
from flask import jsonify, request
from app.api import sync_bp
from app.services.sync_service import sync_service

@sync_bp.route('/status', methods=['GET'])
def get_sync_status():
    """获取同步状态"""
    try:
        status = sync_service.get_sync_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步状态失败: {str(e)}'
        }), 500

@sync_bp.route('/statistics', methods=['GET'])
def get_sync_statistics():
    """获取详细的同步统计信息"""
    try:
        stats = sync_service.get_sync_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步统计失败: {str(e)}'
        }), 500

@sync_bp.route('/trigger', methods=['POST'])
def trigger_sync():
    """手动触发数据同步"""
    try:
        # 获取请求参数
        data = request.get_json() or {}
        force_full_sync = data.get('force_full_sync', False)
        
        # 执行同步
        result = sync_service.perform_sync(force_full_sync=force_full_sync)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'触发同步失败: {str(e)}'
        }), 500

@sync_bp.route('/data', methods=['GET'])
def get_synced_data():
    """查看已同步的数据"""
    try:
        from app.models.question import Question
        from app.models.answer import Answer
        from app.utils.database import db
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        data_type = request.args.get('type', 'questions')  # questions, answers, both
        
        # 限制页面大小
        page_size = min(page_size, 100)
        offset = (page - 1) * page_size
        
        # 创建基础返回结构
        result = {
            'success': True
        }
        
        if data_type in ['questions', 'both']:
            # 查询questions数据
            questions_query = db.session.query(Question).order_by(Question.sendmessagetime.desc())
            questions_total = questions_query.count()
            questions = questions_query.offset(offset).limit(page_size).all()
            
            # 添加questions数据到结果
            questions_data = {
                'total': questions_total,
                'page': page,
                'page_size': page_size,
                'data': [
                    {
                        'id': q.id,
                        'business_id': q.business_id,
                        'pageid': q.pageid,
                        'devicetypename': q.devicetypename,
                        'query': q.query,
                        'sendmessagetime': q.sendmessagetime.isoformat() if q.sendmessagetime else None,
                        'classification': q.classification,
                        'serviceid': q.serviceid,
                        'qatype': q.qatype,
                        'intent': q.intent,
                        'iskeyboardinput': q.iskeyboardinput,
                        'isstopanswer': q.isstopanswer,
                        'processing_status': q.processing_status,
                        'created_at': q.created_at.isoformat() if q.created_at else None,
                        'updated_at': q.updated_at.isoformat() if q.updated_at else None
                    } for q in questions
                ]
            }
            result['questions'] = questions_data
        
        if data_type in ['answers', 'both']:
            # 查询answers数据
            answers_query = db.session.query(Answer).order_by(Answer.answer_time.desc())
            answers_total = answers_query.count()
            answers = answers_query.offset(offset).limit(page_size).all()
            
            # 添加answers数据到结果
            answers_data = {
                'total': answers_total,
                'page': page,
                'page_size': page_size,
                'data': [
                    {
                        'id': a.id,
                        'question_business_id': a.question_business_id,
                        'answer_text': a.answer_text,
                        'assistant_type': a.assistant_type,
                        'answer_time': a.answer_time.isoformat() if a.answer_time else None,
                        'is_scored': a.is_scored,
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                        'updated_at': a.updated_at.isoformat() if a.updated_at else None
                    } for a in answers
                ]
            }
            result['answers'] = answers_data
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取同步数据失败: {str(e)}'
        }), 500

@sync_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'service': 'sync_api',
        'timestamp': 'now'
    }) 