"""
Badcase分析API
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.badcase_analysis_service import BadcaseAnalysisService
from app.services.badcase_detection_service import BadcaseDetectionService
from app.utils.time_utils import TimeRangeUtils
from app.models.question import Question
from app.utils.database import db
from app.utils.decorators import login_required
from datetime import datetime
import json

# 创建蓝图
badcase_bp = Blueprint('badcase', __name__, url_prefix='/api/badcase')


@badcase_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取badcase统计数据"""
    try:
        time_range = request.args.get('time_range', 'week')
        
        # 验证时间范围参数
        if not TimeRangeUtils.validate_range_type(time_range):
            valid_ranges = TimeRangeUtils.get_valid_range_types()
            return jsonify({
                'success': False,
                'message': f'无效的时间范围参数，支持的值: {valid_ranges}'
            }), 400
        
        badcase_service = BadcaseAnalysisService()
        statistics = badcase_service.get_statistics_by_range(time_range)
        
        if statistics is None:
            return jsonify({
                'success': False,
                'message': '获取统计数据失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        current_app.logger.error(f"获取badcase统计数据时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/list', methods=['GET'])
def get_badcase_list():
    """获取badcase列表"""
    try:
        time_range = request.args.get('time_range', 'week')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        # 支持多种参数名格式
        status_filter = request.args.get('status') or request.args.get('status_filter')
        category_filter = request.args.get('category')
        search_keyword = request.args.get('search')


        
        # 验证参数
        if not TimeRangeUtils.validate_range_type(time_range):
            valid_ranges = TimeRangeUtils.get_valid_range_types()
            return jsonify({
                'success': False,
                'message': f'无效的时间范围参数，支持的值: {valid_ranges}'
            }), 400
        
        if page < 1:
            return jsonify({
                'success': False,
                'message': '页码必须大于0'
            }), 400
        
        if page_size < 1 or page_size > 100:
            return jsonify({
                'success': False,
                'message': '每页大小必须在1-100之间'
            }), 400
        
        if status_filter and status_filter not in ['pending', 'reviewed']:
            return jsonify({
                'success': False,
                'message': '无效的状态筛选参数'
            }), 400
        
        badcase_service = BadcaseAnalysisService()
        result = badcase_service.get_badcase_list_by_range(
            time_range=time_range,
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            category_filter=category_filter,
            search_keyword=search_keyword
        )
        
        if result is None:
            return jsonify({
                'success': False,
                'message': '获取badcase列表失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'参数错误: {str(e)}'
        }), 400
    except Exception as e:
        current_app.logger.error(f"获取badcase列表时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/detail/<int:question_id>', methods=['GET'])
def get_badcase_detail(question_id):
    """获取badcase详情"""
    try:
        badcase_service = BadcaseAnalysisService()
        detail = badcase_service.get_badcase_detail(question_id)
        
        if detail is None:
            return jsonify({
                'success': False,
                'message': '问题不存在或不是badcase'
            }), 404
        
        return jsonify({
            'success': True,
            'data': detail
        })
        
    except Exception as e:
        current_app.logger.error(f"获取badcase详情时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500





@badcase_bp.route('/detect', methods=['POST'])
def manual_detect():
    """手动触发badcase检测"""
    try:
        data = request.get_json() or {}
        question_business_ids = data.get('question_business_ids')
        
        detection_service = BadcaseDetectionService()
        
        if question_business_ids:
            # 检测指定问题
            if not isinstance(question_business_ids, list):
                return jsonify({
                    'success': False,
                    'message': 'question_business_ids必须是数组'
                }), 400
            
            result = detection_service.batch_detect_badcases(question_business_ids)
        else:
            # 检测所有已评分问题
            result = detection_service.batch_detect_badcases()
        
        return jsonify({
            'success': True,
            'data': result,
            'message': f'检测完成，发现{result["badcase_count"]}个badcase'
        })
        
    except Exception as e:
        current_app.logger.error(f"手动检测badcase时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/threshold', methods=['GET'])
def get_threshold():
    """获取当前badcase阈值"""
    try:
        detection_service = BadcaseDetectionService()
        threshold = detection_service.get_badcase_threshold()

        return jsonify({
            'success': True,
            'data': {
                'threshold': threshold
            }
        })

    except Exception as e:
        current_app.logger.error(f"获取badcase阈值时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/review/<int:question_id>', methods=['PUT'])
@login_required
def submit_review(question_id):
    """提交badcase复核"""
    current_app.logger.info(f"收到复核请求: question_id={question_id}")
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400

        # 验证必需字段
        required_fields = ['scores', 'comment', 'review_result']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必需字段: {field}'
                }), 400

        # 验证scores数据格式
        scores = data['scores']
        if not isinstance(scores, list):
            return jsonify({
                'success': False,
                'message': 'scores必须是数组格式'
            }), 400

        for i, score_item in enumerate(scores):
            if not isinstance(score_item, dict):
                return jsonify({
                    'success': False,
                    'message': f'scores[{i}]必须是对象格式'
                }), 400

            if 'dimension_name' not in score_item or 'score' not in score_item:
                return jsonify({
                    'success': False,
                    'message': f'scores[{i}]缺少必需字段dimension_name或score'
                }), 400

        # 获取问题记录
        question = db.session.query(Question).filter_by(id=question_id).first()
        if not question:
            return jsonify({
                'success': False,
                'message': '问题不存在'
            }), 404

        if not question.is_badcase:
            return jsonify({
                'success': False,
                'message': '该问题不是badcase'
            }), 400

        # 更新复核状态
        review_result = data['review_result']
        if review_result == 'confirmed':
            question.badcase_review_status = 'reviewed'
            # is_badcase 保持 True
        elif review_result == 'rejected':
            # 误判时必须提供评分修改数据
            if not data.get('scores') or len(data['scores']) == 0:
                return jsonify({
                    'success': False,
                    'message': '选择误判时必须修改评分'
                }), 400

            question.badcase_review_status = 'reviewed'
            question.is_badcase = False  # 标记为非badcase
        else:
            return jsonify({
                'success': False,
                'message': '无效的复核结果'
            }), 400

        question.reviewed_at = datetime.utcnow()

        # 记录复核人员
        from flask import g
        if hasattr(g, 'current_user') and g.current_user:
            question.reviewed_by = g.current_user.id

        # 更新实际的评分数据
        from app.models.answer import Answer
        from app.models.score import Score

        # 获取yoyo答案
        yoyo_answer = db.session.query(Answer).filter_by(
            question_business_id=question.business_id,
            assistant_type='yoyo'
        ).first()

        if yoyo_answer:
            # 为了保留原始AI评分，不再覆盖scores表中的原始评分
            # 复核后的分数存入 badcase_dimensions.review_data 中供详情页展示
            current_app.logger.info(f"复核提交：保留原始AI评分，不覆盖scores记录 (answer_id={yoyo_answer.id})")

        # 计算新平均分，确保精度正确
        scores_list = data['scores']
        if scores_list:
            total_score = sum(float(score.get('score', 0)) for score in scores_list)
            new_average_score = round(total_score / len(scores_list), 2)
        else:
            new_average_score = 0

        # 保存复核评分到badcase_dimensions字段
        review_data = {
            'scores': data['scores'],
            'comment': data['comment'],
            'review_result': review_result,
            'average_score': new_average_score,
            'reviewed_at': datetime.utcnow().isoformat(),
            'reviewed_by': g.current_user.id if hasattr(g, 'current_user') and g.current_user else None,
            'reviewer_name': g.current_user.username if hasattr(g, 'current_user') and g.current_user else None
        }

        # 更新/初始化 badcase_dimensions 字段，写入复核数据
        if question.badcase_dimensions:
            try:
                dimensions_data = json.loads(question.badcase_dimensions)
                if not isinstance(dimensions_data, dict):
                    dimensions_data = {}
            except Exception:
                dimensions_data = {}
            dimensions_data['review_data'] = review_data
            question.badcase_dimensions = json.dumps(dimensions_data, ensure_ascii=False)
        else:
            # 如果之前没有维度数据，也创建一个仅包含复核数据的结构
            question.badcase_dimensions = json.dumps({'review_data': review_data}, ensure_ascii=False)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '复核提交成功'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"提交复核时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/dimension-analysis', methods=['GET'])
def get_dimension_analysis():
    """获取维度分析数据"""
    try:
        classification = request.args.get('classification')
        assistant_type = request.args.get('assistant_type')
        time_range = request.args.get('time_range', 'all')

        # 验证必需参数
        if not classification:
            return jsonify({
                'success': False,
                'message': '分类参数不能为空'
            }), 400

        # 验证时间范围参数
        if not TimeRangeUtils.validate_range_type(time_range):
            valid_ranges = TimeRangeUtils.get_valid_range_types()
            return jsonify({
                'success': False,
                'message': f'无效的时间范围参数，支持的值: {valid_ranges}'
            }), 400

        # 验证助手类型参数
        if assistant_type and assistant_type not in ['yoyo', 'doubao', 'xiaotian']:
            return jsonify({
                'success': False,
                'message': '无效的助手类型参数，支持的值: yoyo, doubao, xiaotian'
            }), 400

        badcase_service = BadcaseAnalysisService()
        result = badcase_service.get_dimension_analysis(
            classification=classification,
            assistant_type=assistant_type,
            time_range=time_range
        )

        if result is None:
            return jsonify({
                'success': False,
                'message': '获取维度分析数据失败'
            }), 500

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        current_app.logger.error(f"获取维度分析数据时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500


@badcase_bp.route('/top-categories-analysis', methods=['GET'])
def get_top_categories_analysis():
    """获取Top3分类分析数据（大屏专用）"""
    try:
        badcase_service = BadcaseAnalysisService()
        analysis_data = badcase_service.get_top_categories_with_lowest_dimensions()

        if analysis_data is None:
            return jsonify({
                'success': False,
                'message': '获取分类分析数据失败'
            }), 500

        return jsonify({
            'success': True,
            'data': analysis_data
        })

    except Exception as e:
        current_app.logger.error(f"获取Top3分类分析数据时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': '服务器内部错误'
        }), 500
