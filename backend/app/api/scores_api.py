"""
评分数据API
提供评分数据查询、统计和分析接口
"""
from flask import jsonify, request
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.api import Blueprint
from app.models.score import Score
from app.models.answer import Answer
from app.models.question import Question
from app.utils.database import db

# 创建评分API蓝图
scores_bp = Blueprint('scores', __name__)

@scores_bp.route('', methods=['GET'])
def get_scores_list():
    """获取评分数据列表（分页）"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        keyword = request.args.get('keyword', '').strip()
        assistant_type = request.args.get('assistant_type', '').strip()
        
        # 构建查询
        query = db.session.query(
            Score.id,
            Score.score_1,
            Score.score_2, 
            Score.score_3,
            Score.score_4,
            Score.score_5,
            Score.dimension_1_name,
            Score.dimension_2_name,
            Score.dimension_3_name,
            Score.dimension_4_name,
            Score.dimension_5_name,
            Score.average_score,
            Score.comment,
            Score.rated_at,
            Answer.assistant_type,
            Question.query.label('question_text')
        ).join(Answer, Score.answer_id == Answer.id)\
         .join(Question, Answer.question_business_id == Question.business_id)
        
        # 应用筛选条件
        if keyword:
            query = query.filter(Question.query.ilike(f'%{keyword}%'))
        
        if assistant_type:
            query = query.filter(Answer.assistant_type == assistant_type)
        
        # 排序
        query = query.order_by(desc(Score.rated_at))
        
        # 分页
        total = query.count()
        scores = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 格式化结果
        items = []
        for score in scores:
            items.append({
                'id': score.id,
                'question': score.question_text,
                'assistant_type': score.assistant_type,
                'score_1': score.score_1,
                'score_2': score.score_2,
                'score_3': score.score_3,
                'score_4': score.score_4,
                'score_5': score.score_5,
                'dimension_1_name': score.dimension_1_name,
                'dimension_2_name': score.dimension_2_name,
                'dimension_3_name': score.dimension_3_name,
                'dimension_4_name': score.dimension_4_name,
                'dimension_5_name': score.dimension_5_name,
                'average_score': float(score.average_score) if score.average_score else None,
                'comment': score.comment,
                'rated_at': score.rated_at.isoformat() if score.rated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            },
            'message': '获取评分数据成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取评分数据失败: {str(e)}'
        }), 500

@scores_bp.route('/statistics', methods=['GET'])
def get_score_statistics():
    """获取评分统计数据（用于图表展示）"""
    try:
        # 获取各AI模型的平均评分（雷达图数据）
        model_stats = db.session.query(
            Answer.assistant_type,
            func.avg(Score.score_1).label('avg_score_1'),
            func.avg(Score.score_2).label('avg_score_2'),
            func.avg(Score.score_3).label('avg_score_3'),
            func.avg(Score.score_4).label('avg_score_4'),
            func.avg(Score.score_5).label('avg_score_5'),
            func.count(Score.id).label('total_scores')
        ).join(Answer, Score.answer_id == Answer.id)\
         .group_by(Answer.assistant_type).all()
        
        # 获取常用的维度名称（用于图表标签）
        dimension_names = db.session.query(
            Score.dimension_1_name,
            Score.dimension_2_name,
            Score.dimension_3_name,
            Score.dimension_4_name,
            Score.dimension_5_name
        ).filter(
            and_(
                Score.dimension_1_name.isnot(None),
                Score.dimension_2_name.isnot(None),
                Score.dimension_3_name.isnot(None),
                Score.dimension_4_name.isnot(None),
                Score.dimension_5_name.isnot(None)
            )
        ).first()
        
        # 格式化雷达图数据
        radar_data = []
        for stat in model_stats:
            model_name_map = {
                'yoyo': '原始模型',
                'doubao': '豆包模型', 
                'xiaotian': '小天模型'
            }
            
            radar_data.append({
                'name': model_name_map.get(stat.assistant_type, stat.assistant_type),
                'values': [
                    round(float(stat.avg_score_1 or 0), 2),
                    round(float(stat.avg_score_2 or 0), 2),
                    round(float(stat.avg_score_3 or 0), 2),
                    round(float(stat.avg_score_4 or 0), 2),
                    round(float(stat.avg_score_5 or 0), 2)
                ],
                'total_scores': stat.total_scores
            })
        
        # 获取评分分布数据（柱状图）
        score_distribution = {}
        for i in range(1, 6):  # 1-5分
            for j in range(1, 6):  # 5个维度
                score_col = getattr(Score, f'score_{j}')
                count = db.session.query(func.count(Score.id)).filter(score_col == i).scalar()
                
                if f'score_{j}' not in score_distribution:
                    score_distribution[f'score_{j}'] = {}
                score_distribution[f'score_{j}'][str(i)] = count
        
        # 维度名称
        dimension_labels = []
        if dimension_names:
            dimension_labels = [
                dimension_names.dimension_1_name or '维度1',
                dimension_names.dimension_2_name or '维度2', 
                dimension_names.dimension_3_name or '维度3',
                dimension_names.dimension_4_name or '维度4',
                dimension_names.dimension_5_name or '维度5'
            ]
        else:
            dimension_labels = ['维度1', '维度2', '维度3', '维度4', '维度5']
        
        return jsonify({
            'success': True,
            'data': {
                'radar_chart': {
                    'data': radar_data,
                    'dimensions': dimension_labels
                },
                'distribution_chart': {
                    'categories': dimension_labels,
                    'data': score_distribution
                },
                'summary': {
                    'total_scores': sum(stat.total_scores for stat in model_stats),
                    'model_count': len(model_stats),
                    'dimension_names': dimension_labels
                }
            },
            'message': '获取评分统计成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取评分统计失败: {str(e)}'
        }), 500

@scores_bp.route('/model-comparison', methods=['GET'])
def get_model_comparison():
    """获取AI模型对比数据"""
    try:
        # 按分类和模型类型统计
        classification = request.args.get('classification', '').strip()
        
        query = db.session.query(
            Answer.assistant_type,
            Question.classification,
            func.avg(Score.average_score).label('avg_score'),
            func.count(Score.id).label('score_count')
        ).join(Answer, Score.answer_id == Answer.id)\
         .join(Question, Answer.question_business_id == Question.business_id)
        
        if classification:
            query = query.filter(Question.classification == classification)
            
        results = query.group_by(Answer.assistant_type, Question.classification).all()
        
        # 格式化结果
        comparison_data = {}
        for result in results:
            model_type = result.assistant_type
            classification_name = result.classification or '未分类'
            
            if model_type not in comparison_data:
                comparison_data[model_type] = {}
                
            comparison_data[model_type][classification_name] = {
                'average_score': round(float(result.avg_score or 0), 2),
                'score_count': result.score_count
            }
        
        return jsonify({
            'success': True,
            'data': comparison_data,
            'message': '获取模型对比数据成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型对比数据失败: {str(e)}'
        }), 500 