"""
答案管理API接口
"""
from flask import Blueprint, request, jsonify, send_file
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.utils.database import db
from app.utils.response import api_response, error_response
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
# 临时注释掉pandas相关的导入，让后端先启动
# import pandas as pd
from io import BytesIO
# from openpyxl import Workbook
import logging

logger = logging.getLogger(__name__)

answer_bp = Blueprint('answers', __name__)

@answer_bp.route('', methods=['GET'])
def get_answers():
    """获取答案列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        question_id = request.args.get('question_id', '').strip()
        score_status = request.args.get('score_status', '').strip()
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        # 构建查询
        query = db.session.query(Answer).join(Question)
        
        # 添加筛选条件
        if question_id:
            query = query.filter(Answer.question_business_id.like(f'%{question_id}%'))
            
        if score_status == 'scored':
            query = query.filter(Answer.is_scored == True)
        elif score_status == 'unscored':
            query = query.filter(Answer.is_scored == False)
            
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                query = query.filter(Answer.created_at >= start_dt)
            except ValueError:
                pass
                
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                query = query.filter(Answer.created_at <= end_dt)
            except ValueError:
                pass
        
        # 分页
        total = query.count()
        answers = query.order_by(desc(Answer.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为字典格式
        result = []
        for answer in answers:
            answer_dict = answer.to_dict(include_score=True)
            # 添加问题信息
            question = db.session.query(Question).filter_by(business_id=answer.question_business_id).first()
            if question:
                answer_dict['question'] = {
                    'business_id': question.business_id,
                    'query': question.query,
                    'classification': question.classification,
                    'created_at': question.created_at.isoformat() if question.created_at else None
                }
            result.append(answer_dict)
        
        return api_response({
            'answers': result,
            'total': total,
            'page': page,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"获取答案列表失败: {str(e)}")
        return error_response(f"获取答案列表失败: {str(e)}")

@answer_bp.route('/<int:answer_id>', methods=['GET'])
def get_answer_detail(answer_id):
    """获取答案详情"""
    try:
        answer = db.session.query(Answer).filter_by(id=answer_id).first()
        if not answer:
            return error_response("答案不存在", 404)
        
        result = answer.to_dict(include_score=True)
        
        # 添加问题信息
        question = db.session.query(Question).filter_by(business_id=answer.question_business_id).first()
        if question:
            result['question'] = question.to_dict()
        
        # 添加评分历史
        scores = db.session.query(Score).filter_by(answer_id=answer.id).order_by(desc(Score.rated_at)).all()
        result['score_history'] = [score.to_dict() for score in scores]
        
        return api_response(result)
        
    except Exception as e:
        logger.error(f"获取答案详情失败: {str(e)}")
        return error_response(f"获取答案详情失败: {str(e)}")

@answer_bp.route('/comparison', methods=['GET'])
def get_answer_comparison():
    """获取问题的所有答案对比"""
    try:
        question_id = request.args.get('question_id', '').strip()
        if not question_id:
            return error_response("问题ID不能为空")
        
        # 获取问题信息
        question = db.session.query(Question).filter_by(business_id=question_id).first()
        if not question:
            return error_response("问题不存在", 404)
        
        # 获取所有答案
        answers = db.session.query(Answer).filter_by(question_business_id=question_id).all()
        
        # 按助手类型分组
        answers_by_type = {}
        scores_by_type = {}
        
        for answer in answers:
            assistant_type = answer.assistant_type
            # 映射助手类型
            if assistant_type == 'our_ai':
                assistant_type = 'original'
            
            answers_by_type[assistant_type] = answer.to_dict()
            
            # 获取最新评分
            latest_score = db.session.query(Score).filter_by(answer_id=answer.id).order_by(desc(Score.rated_at)).first()
            if latest_score:
                scores_by_type[assistant_type] = latest_score.to_dict()
        
        return api_response({
            'question': question.to_dict(),
            'answers': answers_by_type,
            'scores': scores_by_type
        })
        
    except Exception as e:
        logger.error(f"获取答案对比失败: {str(e)}")
        return error_response(f"获取答案对比失败: {str(e)}")

@answer_bp.route('/batch-score', methods=['POST'])
def batch_score_answers():
    """批量评分答案"""
    try:
        data = request.get_json()
        question_ids = data.get('question_ids', [])
        models = data.get('models', [])
        comment = data.get('comment', '')
        
        if not question_ids:
            return error_response("问题ID列表不能为空")
        
        if not models:
            return error_response("模型列表不能为空")
        
        # 映射模型名称
        model_mapping = {
            'original': 'our_ai',
            'doubao': 'doubao',
            'xiaotian': 'xiaotian'
        }
        
        success_count = 0
        error_count = 0
        errors = []
        
        for question_id in question_ids:
            try:
                for model in models:
                    db_model = model_mapping.get(model, model)
                    
                    # 查找对应答案
                    answer = db.session.query(Answer).filter_by(
                        question_business_id=question_id,
                        assistant_type=db_model
                    ).first()
                    
                    if answer:
                        # 检查是否已有评分
                        existing_score = db.session.query(Score).filter_by(answer_id=answer.id).first()
                        if not existing_score:
                            # 调用评分服务（这里暂时创建一个默认评分）
                            score = Score(
                                answer_id=answer.id,
                                score_1=4,  # 默认评分
                                score_2=4,
                                score_3=4,
                                score_4=4,
                                score_5=4,
                                dimension_1_name="准确性",
                                dimension_2_name="完整性",
                                dimension_3_name="清晰度",
                                dimension_4_name="实用性",
                                dimension_5_name="创新性",
                                average_score=4.0,
                                comment=comment,
                                rated_at=datetime.utcnow()
                            )
                            db.session.add(score)
                            
                            # 更新答案评分状态
                            answer.is_scored = True
                            success_count += 1
                        else:
                            success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"问题 {question_id} 的 {model} 答案不存在")
                        
            except Exception as e:
                error_count += 1
                errors.append(f"问题 {question_id} 评分失败: {str(e)}")
        
        # 提交事务
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return error_response(f"批量评分保存失败: {str(e)}")
        
        return api_response({
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"批量评分失败: {str(e)}")
        db.session.rollback()
        return error_response(f"批量评分失败: {str(e)}")

@answer_bp.route('/export', methods=['POST'])
def export_answers():
    """导出答案数据"""
    try:
        # 临时返回提示信息，等pandas问题解决后再启用
        return error_response("Excel导出功能暂时不可用，正在修复pandas兼容性问题")
        
        # 原来的导出代码先注释
        # data = request.get_json() or {}
        # question_ids = data.get('question_ids', [])
        
        # if not question_ids:
        #     return error_response("问题ID列表不能为空")
        
        # # 查询数据
        # query = """
        # SELECT 
        #     q.business_id as question_id,
        #     q.query as question_content,
        #     q.classification,
        #     q.created_at as question_created_at,
        #     a.assistant_type,
        #     a.answer_text,
        #     a.is_scored,
        #     a.created_at as answer_created_at,
        #     s.score_1,
        #     s.score_2, 
        #     s.score_3,
        #     s.score_4,
        #     s.score_5,
        #     s.average_score,
        #     s.comment as score_comment,
        #     s.rated_at
        # FROM questions q
        # LEFT JOIN answers a ON q.business_id = a.question_business_id
        # LEFT JOIN scores s ON a.id = s.answer_id
        # WHERE q.business_id IN :question_ids
        # ORDER BY q.created_at DESC, a.assistant_type
        # """
        
        # result = db.session.execute(query, {'question_ids': tuple(question_ids)})
        # rows = result.fetchall()
        
        # # 转换为DataFrame
        # df = pd.DataFrame(rows, columns=[
        #     '问题ID', '问题内容', '问题分类', '问题创建时间',
        #     '助手类型', '答案内容', '是否已评分', '答案创建时间',
        #     '评分1', '评分2', '评分3', '评分4', '评分5',
        #     '平均分', '评分备注', '评分时间'
        # ])
        
        # # 处理助手类型显示
        # type_mapping = {
        #     'our_ai': '原始AI',
        #     'doubao': '豆包',
        #     'xiaotian': '小天'
        # }
        # df['助手类型'] = df['助手类型'].map(type_mapping).fillna(df['助手类型'])
        
        # # 处理布尔值
        # df['是否已评分'] = df['是否已评分'].map({True: '是', False: '否'})
        
        # # 创建Excel文件
        # output = BytesIO()
        # with pd.ExcelWriter(output, engine='openpyxl') as writer:
        #     df.to_excel(writer, sheet_name='答案对比数据', index=False)
        # output.seek(0)
        
        # # 生成文件名
        # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # filename = f'answers_export_{timestamp}.xlsx'
        
        # return send_file(
        #     output,
        #     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        #     as_attachment=True,
        #     download_name=filename
        # )
        
    except Exception as e:
        logger.error(f"导出答案数据失败: {str(e)}")
        return error_response(f"导出失败: {str(e)}")

@answer_bp.route('/statistics', methods=['GET'])
def get_answer_statistics():
    """获取答案统计数据"""
    try:
        # 获取时间范围参数
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按助手类型统计答案数量
        type_stats = db.session.query(
            Answer.assistant_type,
            func.count(Answer.id).label('count'),
            func.sum(func.case([(Answer.is_scored == True, 1)], else_=0)).label('scored_count')
        ).filter(Answer.created_at >= start_date).group_by(Answer.assistant_type).all()
        
        # 按日期统计答案数量
        daily_stats = db.session.query(
            func.date(Answer.created_at).label('date'),
            func.count(Answer.id).label('count')
        ).filter(Answer.created_at >= start_date).group_by(func.date(Answer.created_at)).all()
        
        # 评分统计
        score_stats = db.session.query(
            func.avg(Score.average_score).label('avg_score'),
            func.count(Score.id).label('total_scores')
        ).join(Answer).filter(Answer.created_at >= start_date).first()
        
        # 转换数据格式
        type_data = []
        for stat in type_stats:
            assistant_type = stat.assistant_type
            if assistant_type == 'our_ai':
                assistant_type = 'original'
            type_data.append({
                'type': assistant_type,
                'type_name': Answer.get_assistant_type_display(stat.assistant_type),
                'total': stat.count,
                'scored': stat.scored_count,
                'score_rate': round(stat.scored_count / stat.count * 100, 1) if stat.count > 0 else 0
            })
        
        daily_data = [
            {
                'date': stat.date.strftime('%Y-%m-%d'),
                'count': stat.count
            } for stat in daily_stats
        ]
        
        return api_response({
            'type_statistics': type_data,
            'daily_statistics': daily_data,
            'score_statistics': {
                'average_score': float(score_stats.avg_score) if score_stats.avg_score else 0,
                'total_scores': score_stats.total_scores or 0
            }
        })
        
    except Exception as e:
        logger.error(f"获取答案统计数据失败: {str(e)}")
        return error_response(f"获取答案统计数据失败: {str(e)}")

@answer_bp.route('/<int:answer_id>/status', methods=['PUT'])
def update_answer_status(answer_id):
    """更新答案状态"""
    try:
        data = request.get_json()
        is_scored = data.get('is_scored')
        
        answer = db.session.query(Answer).filter_by(id=answer_id).first()
        if not answer:
            return error_response("答案不存在", 404)
        
        if is_scored is not None:
            answer.is_scored = bool(is_scored)
            answer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return api_response({
            'message': '答案状态更新成功',
            'answer': answer.to_dict()
        })
        
    except Exception as e:
        logger.error(f"更新答案状态失败: {str(e)}")
        db.session.rollback()
        return error_response(f"更新答案状态失败: {str(e)}") 