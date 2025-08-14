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

@sync_bp.route('/table1-structure', methods=['GET'])
def get_table1_structure():
    """获取table1表结构信息"""
    try:
        from sqlalchemy import text
        from app.utils.database import db

        # 检查表是否存在
        table_exists_query = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'table1'
            );
        """)

        table_exists = db.session.execute(table_exists_query).scalar()

        if not table_exists:
            return jsonify({
                'success': True,
                'data': {'exists': False, 'message': 'table1表不存在'},
                'message': "table1表不存在"
            })

        # 获取表结构
        columns_query = text("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'table1'
            ORDER BY ordinal_position;
        """)

        columns_result = db.session.execute(columns_query)
        columns = []

        for row in columns_result:
            columns.append({
                'column_name': row[0],
                'data_type': row[1],
                'is_nullable': row[2],
                'column_default': row[3],
                'character_maximum_length': row[4]
            })

        # 获取记录数
        count_query = text("SELECT COUNT(*) FROM table1")
        total_count = db.session.execute(count_query).scalar()

        # 检查是否有classification字段
        has_classification = any(col['column_name'] == 'classification' for col in columns)

        # 如果有classification字段，获取其值分布
        classification_distribution = []
        if has_classification:
            classification_query = text("""
                SELECT classification, COUNT(*) as count
                FROM table1
                WHERE classification IS NOT NULL AND classification != ''
                GROUP BY classification
                ORDER BY count DESC
            """)

            classification_result = db.session.execute(classification_query)
            for row in classification_result:
                classification_distribution.append({
                    'classification': row[0],
                    'count': row[1]
                })

        return jsonify({
            'success': True,
            'data': {
                'exists': True,
                'columns': columns,
                'total_count': total_count,
                'has_classification': has_classification,
                'classification_distribution': classification_distribution
            },
            'message': f"成功获取table1表结构，共{len(columns)}个字段，{total_count}条记录"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取table1表结构失败: {str(e)}'
        }), 500