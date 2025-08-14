"""
Badcase分析服务
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_

from app.utils.database import db
from app.utils.time_utils import TimeRangeUtils
from app.utils.datetime_helper import utc_to_beijing_str
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from sqlalchemy import func
from app.services.classification_service import ClassificationService


class BadcaseAnalysisService:
    """Badcase分析服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_statistics_by_range(self, time_range: str = 'week') -> Optional[Dict[str, Any]]:
        """
        根据时间范围获取badcase统计数据
        
        Args:
            time_range: 时间范围类型 ('today', 'week', 'month', 'year', 'all')
            
        Returns:
            dict: 统计数据
        """
        try:
            # 验证时间范围参数
            if not TimeRangeUtils.validate_range_type(time_range):
                self.logger.error(f"无效的时间范围参数: {time_range}")
                return None
            
            # 获取时间范围
            start_time, end_time = TimeRangeUtils.get_time_range(time_range)
            
            # 时间范围内问题总数（已评分的问题）
            total_questions = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored'
                )
            ).count()
            
            # 时间范围内badcase总数（只统计已评分的badcase）
            badcase_count = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored',
                    Question.is_badcase == True
                )
            ).count()
            
            # 待处理案例（pending状态，只统计已评分的badcase）
            pending_count = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored',
                    Question.is_badcase == True,
                    Question.badcase_review_status == 'pending'
                )
            ).count()

            # 已复核案例（reviewed状态，包括确认和误判两种情况）
            reviewed_count = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored',
                    Question.badcase_review_status == 'reviewed'
                )
            ).count()

            # 误判修正数（reviewed状态且is_badcase=False）
            misjudged_count = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored',
                    Question.badcase_review_status == 'reviewed',
                    Question.is_badcase == False
                )
            ).count()
            
            # 计算比率
            badcase_ratio = (badcase_count / total_questions * 100) if total_questions > 0 else 0
            # 复核率 = 已复核数 / (已复核数 + 待复核数) × 100%
            total_need_review = pending_count + reviewed_count
            review_rate = (reviewed_count / total_need_review * 100) if total_need_review > 0 else 0

            return {
                'total_questions': total_questions,
                'badcase_count': badcase_count,
                'badcase_ratio': round(badcase_ratio, 2),
                'pending_count': pending_count,
                'reviewed_count': reviewed_count,
                'misjudged_count': misjudged_count,
                'review_rate': round(review_rate, 2),
                'time_range': time_range,
                'time_range_text': TimeRangeUtils.get_range_display_text(time_range),
                'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"获取统计数据时出错: {str(e)}")
            return None
    
    def get_badcase_list_by_range(
        self,
        time_range: str = 'week',
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        search_keyword: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        根据时间范围获取badcase列表

        Args:
            time_range: 时间范围类型
            page: 页码
            page_size: 每页大小
            status_filter: 状态筛选
            category_filter: 分类筛选
            search_keyword: 搜索关键词

        Returns:
            dict: 分页的badcase列表数据
        """
        try:
            # 验证时间范围参数
            if not TimeRangeUtils.validate_range_type(time_range):
                self.logger.error(f"无效的时间范围参数: {time_range}")
                return None
            
            # 获取时间范围
            start_time, end_time = TimeRangeUtils.get_time_range(time_range)
            
            # 基础查询条件
            base_conditions = [
                Question.created_at >= start_time,
                Question.created_at <= end_time,
                Question.processing_status == 'scored'
            ]

            # 根据状态筛选决定查询范围
            if status_filter == 'reviewed':
                # 已复核状态：包括确认的badcase和误判的记录
                query = db.session.query(Question).filter(
                    and_(
                        *base_conditions,
                        Question.badcase_review_status == 'reviewed'
                    )
                )
            else:
                # 其他状态：只查询真正的badcase
                query = db.session.query(Question).filter(
                    and_(
                        *base_conditions,
                        Question.is_badcase == True
                    )
                )
                # 状态筛选
                if status_filter:
                    query = query.filter(Question.badcase_review_status == status_filter)

            # 分类筛选
            if category_filter:
                query = query.filter(Question.classification == category_filter)

            # 搜索筛选
            if search_keyword:
                query = query.filter(Question.query.ilike(f'%{search_keyword}%'))
            
            # 分页与排序
            total = query.count()
            # 已复核按复核时间倒序；其他按检测时间倒序
            if status_filter == 'reviewed':
                order_expr = Question.reviewed_at.desc()
            else:
                order_expr = Question.badcase_detected_at.desc()

            questions = query.order_by(order_expr).offset(
                (page - 1) * page_size
            ).limit(page_size).all()
            
            # 构建返回数据
            badcase_list = []
            for question in questions:
                # 获取yoyo答案
                yoyo_answer = db.session.query(Answer).filter_by(
                    question_business_id=question.business_id,
                    assistant_type='yoyo'
                ).first()

                # 获取yoyo评分信息
                yoyo_scores = None
                if yoyo_answer:
                    score_record = db.session.query(Score).filter_by(
                        answer_id=yoyo_answer.id
                    ).first()

                    if score_record:
                        dimensions = []
                        dimension_scores = [
                            (score_record.dimension_1_name, score_record.score_1),
                            (score_record.dimension_2_name, score_record.score_2),
                            (score_record.dimension_3_name, score_record.score_3),
                            (score_record.dimension_4_name, score_record.score_4),
                            (score_record.dimension_5_name, score_record.score_5)
                        ]

                        for dimension_name, score in dimension_scores:
                            if dimension_name and score is not None:
                                dimensions.append({
                                    'dimension_name': dimension_name,
                                    'score': float(score)
                                })

                        yoyo_scores = {
                            'dimensions': dimensions,
                            'average_score': float(score_record.average_score) if score_record.average_score else 0,
                            'comment': score_record.comment,
                            'rated_at': score_record.rated_at.strftime('%Y-%m-%d %H:%M:%S') if score_record.rated_at else ''
                        }

                # 解析低分维度信息和复核人员信息
                low_score_info = []
                reviewer_name = None
                if question.badcase_dimensions:
                    try:
                        dimensions_data = json.loads(question.badcase_dimensions)
                        low_score_info = dimensions_data.get('low_score_dimensions', [])
                        # 获取复核人员信息
                        review_data = dimensions_data.get('review_data', {})
                        reviewer_name = review_data.get('reviewer_name')
                    except json.JSONDecodeError:
                        self.logger.error(f"解析badcase维度信息失败: {question.business_id}")

                # 如果没有从dimensions中获取到复核人员，尝试从reviewed_by字段获取
                if not reviewer_name and question.reviewed_by:
                    from app.models.user import User
                    reviewer = db.session.query(User).filter_by(id=question.reviewed_by).first()
                    if reviewer:
                        reviewer_name = reviewer.username

                badcase_list.append({
                    'id': question.id,
                    'business_id': question.business_id,
                    'query': question.query,
                    'yoyo_answer': yoyo_answer.answer_text if yoyo_answer else '',
                    'classification': question.classification,
                    'yoyo_scores': yoyo_scores,
                    'low_score_dimensions': low_score_info,
                    'review_status': question.badcase_review_status,
                    'badcase_review_status': question.badcase_review_status,  # 添加一致的字段名
                    'is_badcase': question.is_badcase,  # 添加is_badcase字段用于区分真正的badcase和误判记录
                    'reviewer_name': reviewer_name,
                    'detected_at': utc_to_beijing_str(question.badcase_detected_at) if question.badcase_detected_at else '',
                    'reviewed_at': utc_to_beijing_str(question.reviewed_at) if question.reviewed_at else ''
                })
            
            return {
                'list': badcase_list,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'time_range': time_range,
                'time_range_text': TimeRangeUtils.get_range_display_text(time_range)
            }
            
        except Exception as e:
            self.logger.error(f"获取badcase列表时出错: {str(e)}")
            return None

    def get_badcase_detail(self, question_id: int) -> Optional[Dict[str, Any]]:
        """
        获取badcase详情

        Args:
            question_id: 问题ID

        Returns:
            dict: badcase详细信息
        """
        try:
            question = db.session.query(Question).filter_by(id=question_id).first()

            if not question:
                self.logger.error(f"问题不存在: {question_id}")
                return None

            # 获取三个AI模型的答案
            answers = db.session.query(Answer).filter_by(
                question_business_id=question.business_id
            ).all()

            answers_data = []
            original_ai_scoring = None

            for answer in answers:
                answer_data = {
                    'id': answer.id,
                    'assistant_type': answer.assistant_type,
                    'answer_text': answer.answer_text,
                    'is_scored': answer.is_scored,
                    'answer_time': answer.answer_time.strftime('%Y-%m-%d %H:%M:%S') if answer.answer_time else ''
                }

                # 如果是yoyo答案，获取原始AI评分详情
                if answer.assistant_type == 'yoyo':
                    # 获取最早的评分记录（原始AI评分）
                    score_record = db.session.query(Score).filter_by(
                        answer_id=answer.id
                    ).order_by(Score.rated_at.asc()).first()

                    if score_record:
                        dimensions = []
                        dimension_scores = [
                            (score_record.dimension_1_name, score_record.score_1),
                            (score_record.dimension_2_name, score_record.score_2),
                            (score_record.dimension_3_name, score_record.score_3),
                            (score_record.dimension_4_name, score_record.score_4),
                            (score_record.dimension_5_name, score_record.score_5)
                        ]

                        for dimension_name, score in dimension_scores:
                            if dimension_name and score is not None:
                                dimensions.append({
                                    'dimension_name': dimension_name,
                                    'score': float(score)
                                })

                        original_ai_scoring = {
                            'dimensions': dimensions,
                            'average_score': float(score_record.average_score) if score_record.average_score else 0,
                            'comment': score_record.comment,
                            'rated_at': score_record.rated_at.strftime('%Y-%m-%d %H:%M:%S') if score_record.rated_at else ''
                        }

                        # 将评分信息添加到答案数据中
                        answer_data['scores'] = original_ai_scoring

                answers_data.append(answer_data)

            # 解析低分维度信息和复核信息
            low_score_info = []
            detection_threshold = 2.5
            review_info = None

            if question.badcase_dimensions:
                try:
                    dimensions_data = json.loads(question.badcase_dimensions)
                    low_score_info = dimensions_data.get('low_score_dimensions', [])
                    detection_threshold = dimensions_data.get('detection_threshold', 2.5)
                    review_info = dimensions_data.get('review_data')
                except json.JSONDecodeError:
                    self.logger.error(f"解析badcase维度信息失败: {question.business_id}")

            # 构建复核信息
            review_data = None
            if question.badcase_review_status != 'pending':
                review_data = {
                    'status': question.badcase_review_status,
                    'reviewed_at': utc_to_beijing_str(question.reviewed_at) if question.reviewed_at else '',
                    'reviewer_id': None,  # 预留字段，后续添加登录功能时使用
                    'is_badcase_after_review': question.is_badcase,
                }

                # 如果有复核详细信息，添加到返回数据中
                if review_info:
                    # 计算新平均分，确保精度正确
                    new_average_score = review_info.get('average_score', 0)
                    if isinstance(new_average_score, (int, float)):
                        new_average_score = round(float(new_average_score), 2)

                    review_data.update({
                        'review_result': review_info.get('review_result'),
                        'review_comment': review_info.get('comment'),
                        'modified_scores': review_info.get('scores'),
                        'new_average_score': new_average_score
                    })

            return {
                'id': question.id,
                'business_id': question.business_id,
                'query': question.query,
                'classification': question.classification,
                'processing_status': question.processing_status,
                'is_badcase': question.is_badcase,
                'badcase_detected_at': utc_to_beijing_str(question.badcase_detected_at) if question.badcase_detected_at else '',
                'badcase_review_status': question.badcase_review_status,
                'reviewed_at': utc_to_beijing_str(question.reviewed_at) if question.reviewed_at else '',
                'created_at': utc_to_beijing_str(question.created_at) if question.created_at else '',
                'answers': answers_data,
                'original_ai_scoring': original_ai_scoring,  # 原始AI评分
                'review_info': review_data,  # 复核信息
                'low_score_dimensions': low_score_info,
                'detection_threshold': detection_threshold
            }

        except Exception as e:
            self.logger.error(f"获取badcase详情时出错: {str(e)}")
            return None

    def update_review_status(
        self,
        question_id: int,
        status: str,
        new_scores: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新复核状态

        Args:
            question_id: 问题ID
            status: 新状态 ('reviewed', 'optimized')
            new_scores: 新的评分数据（可选）

        Returns:
            bool: 更新是否成功
        """
        try:
            question = db.session.query(Question).filter_by(id=question_id).first()

            if not question:
                self.logger.error(f"问题不存在: {question_id}")
                return False

            if not question.is_badcase:
                self.logger.error(f"问题不是badcase: {question_id}")
                return False

            # 更新复核状态
            question.badcase_review_status = status
            question.reviewed_at = datetime.utcnow()
            question.updated_at = datetime.utcnow()

            # 如果提供了新的评分数据，更新yoyo答案的评分
            if new_scores:
                yoyo_answer = db.session.query(Answer).filter_by(
                    question_business_id=question.business_id,
                    assistant_type='yoyo'
                ).first()

                if yoyo_answer:
                    score_record = db.session.query(Score).filter_by(
                        answer_id=yoyo_answer.id
                    ).first()

                    if score_record:
                        # 更新评分
                        score_record.score_1 = new_scores.get('score_1', score_record.score_1)
                        score_record.score_2 = new_scores.get('score_2', score_record.score_2)
                        score_record.score_3 = new_scores.get('score_3', score_record.score_3)
                        score_record.score_4 = new_scores.get('score_4', score_record.score_4)
                        score_record.score_5 = new_scores.get('score_5', score_record.score_5)

                        # 计算平均分
                        scores = [
                            score_record.score_1, score_record.score_2, score_record.score_3,
                            score_record.score_4, score_record.score_5
                        ]
                        valid_scores = [s for s in scores if s is not None]
                        if valid_scores:
                            score_record.average_score = sum(valid_scores) / len(valid_scores)

                        # 更新评分理由
                        if 'comment' in new_scores:
                            score_record.comment = new_scores['comment']

                        score_record.rated_at = datetime.utcnow()

                        self.logger.info(f"更新了问题 {question_id} 的yoyo答案评分")

            db.session.commit()

            self.logger.info(f"更新badcase复核状态成功: {question_id} -> {status}")
            return True

        except Exception as e:
            self.logger.error(f"更新复核状态时出错: {str(e)}")
            db.session.rollback()
            return False

    def get_dimension_analysis(
        self,
        classification: str,
        assistant_type: Optional[str] = None,
        time_range: str = 'all'
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定分类的维度分析数据

        Args:
            classification: 问题分类
            assistant_type: 助手类型 (可选)
            time_range: 时间范围

        Returns:
            dict: 维度分析数据
        """
        try:
            # 验证时间范围参数
            if not TimeRangeUtils.validate_range_type(time_range):
                self.logger.error(f"无效的时间范围参数: {time_range}")
                return None

            # 获取时间范围
            start_time, end_time = TimeRangeUtils.get_time_range(time_range)

            # 基础查询条件 - 查询有评分的问题
            if assistant_type:
                # 指定助手类型时
                base_query = db.session.query(Question).join(
                    Answer, Question.business_id == Answer.question_business_id
                ).join(
                    Score, Answer.id == Score.answer_id
                ).filter(
                    and_(
                        Question.created_at >= start_time,
                        Question.created_at <= end_time,
                        Question.processing_status == 'scored',
                        Question.classification == classification,
                        Answer.assistant_type == assistant_type
                    )
                )
            else:
                # 不指定助手类型时，查询所有有评分的问题
                base_query = db.session.query(Question).join(
                    Answer, Question.business_id == Answer.question_business_id
                ).join(
                    Score, Answer.id == Score.answer_id
                ).filter(
                    and_(
                        Question.created_at >= start_time,
                        Question.created_at <= end_time,
                        Question.processing_status == 'scored',
                        Question.classification == classification
                    )
                )

            # 获取该分类下的总问题数
            total_questions = base_query.count()

            if total_questions == 0:
                return {
                    'classification': classification,
                    'assistant_type': assistant_type,
                    'time_range': time_range,
                    'total_questions': 0,
                    'total_badcases': 0,
                    'badcase_rate': 0,
                    'dimension_analysis': []
                }

            # 获取该分类下的badcase数量
            badcase_query = base_query.filter(Question.is_badcase == True)
            total_badcases = badcase_query.count()
            badcase_rate = (total_badcases / total_questions) * 100 if total_questions > 0 else 0

            # 分析各维度的badcase分布
            dimension_analysis = self._analyze_dimensions_for_classification(
                classification, assistant_type, start_time, end_time, total_questions
            )

            return {
                'classification': classification,
                'assistant_type': assistant_type,
                'time_range': time_range,
                'total_questions': total_questions,
                'total_badcases': total_badcases,
                'badcase_rate': round(badcase_rate, 2),
                'dimension_analysis': dimension_analysis
            }

        except Exception as e:
            self.logger.error(f"获取维度分析数据时出错: {str(e)}")
            return None

    def _get_dimension_mapping(self) -> Dict[str, str]:
        """
        获取维度名称标准化映射
        将不同的维度名称映射到标准的5个维度
        """
        return {
            # 准确性相关
            '准确性': '准确性',
            '信息准确性': '准确性',
            '操作准确性': '准确性',

            # 完整性相关
            '完整性': '完整性',
            '功能完整性': '完整性',
            '信息完整性': '完整性',

            # 清晰度相关
            '清晰度': '清晰度',
            '表达清晰度': '清晰度',
            '逻辑清晰度': '清晰度',

            # 实用性相关
            '实用性': '实用性',
            '针对性': '实用性',
            '有效性': '实用性',

            # 专业性相关
            '专业性': '专业性',
            '权威性': '专业性',
            '可信度': '专业性',

            # 用户体验相关
            '用户体验': '用户体验',
            '易用性': '用户体验',
            '友好性': '用户体验',

            # 创新性相关
            '创新性': '创新性',
            '新颖性': '创新性',
            '独特性': '创新性'
        }

    def _normalize_dimension_name(self, dim_name: str) -> str:
        """
        标准化维度名称

        Args:
            dim_name: 原始维度名称

        Returns:
            str: 标准化后的维度名称
        """
        if not dim_name:
            return None

        mapping = self._get_dimension_mapping()
        return mapping.get(dim_name, dim_name)

    def _analyze_dimensions_for_classification(
        self,
        classification: str,
        assistant_type: Optional[str],
        start_time: datetime,
        end_time: datetime,
        total_questions: int
    ) -> List[Dict[str, Any]]:
        """
        分析指定分类下各维度的badcase分布

        Args:
            classification: 问题分类
            assistant_type: 助手类型
            start_time: 开始时间
            end_time: 结束时间
            total_questions: 总问题数

        Returns:
            list: 维度分析结果
        """
        try:
            # 构建查询 - 按问题去重，避免重复统计
            query = db.session.query(Score, Question.business_id).join(
                Answer, Score.answer_id == Answer.id
            ).join(
                Question, Answer.question_business_id == Question.business_id
            ).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.processing_status == 'scored',
                    Question.classification == classification
                )
            )

            # 如果指定了助手类型
            if assistant_type:
                query = query.filter(Answer.assistant_type == assistant_type)

            # 获取所有评分记录
            score_records = query.all()

            # 按问题去重，每个问题只取最新的评分记录
            question_scores = {}
            for score, business_id in score_records:
                if business_id not in question_scores or score.rated_at > question_scores[business_id].rated_at:
                    question_scores[business_id] = score

            # 统计各维度的badcase数量
            dimension_stats = {}
            badcase_threshold = 2.5

            for score in question_scores.values():
                # 处理5个维度，进行标准化
                dimensions = [
                    (self._normalize_dimension_name(score.dimension_1_name), score.score_1),
                    (self._normalize_dimension_name(score.dimension_2_name), score.score_2),
                    (self._normalize_dimension_name(score.dimension_3_name), score.score_3),
                    (self._normalize_dimension_name(score.dimension_4_name), score.score_4),
                    (self._normalize_dimension_name(score.dimension_5_name), score.score_5)
                ]

                for dim_name, dim_score in dimensions:
                    if dim_name and dim_score is not None:
                        if dim_name not in dimension_stats:
                            dimension_stats[dim_name] = {
                                'total_count': 0,
                                'badcase_count': 0
                            }

                        dimension_stats[dim_name]['total_count'] += 1
                        if dim_score < badcase_threshold:
                            dimension_stats[dim_name]['badcase_count'] += 1

            # 计算百分比并构建结果
            result = []
            for dim_name, stats in dimension_stats.items():
                percentage = (stats['badcase_count'] / total_questions) * 100 if total_questions > 0 else 0
                result.append({
                    'dimension_name': dim_name,
                    'badcase_count': stats['badcase_count'],
                    'total_questions_with_dimension': stats['total_count'],
                    'percentage': round(percentage, 2)
                })

            # 按badcase数量降序排序，并限制为最多5个维度
            result.sort(key=lambda x: x['badcase_count'], reverse=True)
            return result[:5]  # 只返回前5个维度

        except Exception as e:
            self.logger.error(f"分析维度数据时出错: {str(e)}")
            return []

    def get_top_categories_with_lowest_dimensions(self) -> Optional[Dict[str, Any]]:
        """
        获取Top3分类及其最低平均分的两个维度数据（大屏专用）

        Returns:
            dict: 包含Top3分类分析数据
        """
        try:
            # 1. 获取所有分类的badcase统计，按数量排序取前3
            category_stats = db.session.query(
                Question.classification,
                func.count(Question.id).label('badcase_count')
            ).filter(
                Question.is_badcase == True
            ).group_by(
                Question.classification
            ).order_by(
                func.count(Question.id).desc()
            ).limit(3).all()

            if not category_stats:
                self.logger.warning("未找到badcase分类数据")
                return {
                    'total_categories': 0,
                    'analysis_date': datetime.now().isoformat(),
                    'top_categories': []
                }

            result_categories = []

            # 2. 对每个分类，计算5个维度的平均分并取最低的2个
            for rank, (classification, badcase_count) in enumerate(category_stats, 1):
                # 获取该分类下所有维度的平均分
                # 需要通过questions -> answers -> scores的关联路径
                dimension_averages = self._get_dimension_averages_for_classification(classification)

                if not dimension_averages:
                    self.logger.warning(f"分类 {classification} 未找到维度评分数据")
                    continue

                # 3. 排序并取最低的2个维度
                sorted_dimensions = sorted(
                    dimension_averages,
                    key=lambda x: x[1] if x[1] else 0
                )[:2]

                # 4. 构建维度数据
                lowest_dimensions = []
                for dim_name, avg_score, sample_count in sorted_dimensions:
                    lowest_dimensions.append({
                        'dimension_name': dim_name or '未知维度',
                        'dimension_code': self._get_dimension_code(dim_name),
                        'avg_score': round(float(avg_score), 1) if avg_score else 0.0,
                        'sample_count': sample_count
                    })

                # 5. 构建分类数据
                category_data = {
                    'category_id': rank,  # 使用排名作为ID
                    'category_name': classification or '未分类',
                    'total_badcase': badcase_count,
                    'percentage': 0,  # 稍后计算
                    'rank': rank,
                    'lowest_dimensions': lowest_dimensions
                }

                result_categories.append(category_data)

            # 6. 计算百分比
            total_badcase = sum(cat['total_badcase'] for cat in result_categories)
            for category in result_categories:
                if total_badcase > 0:
                    category['percentage'] = round(
                        (category['total_badcase'] / total_badcase) * 100, 1
                    )

            return {
                'total_categories': len(category_stats),
                'analysis_date': datetime.now().isoformat(),
                'top_categories': result_categories
            }

        except Exception as e:
            self.logger.error(f"获取Top3分类分析数据时出错: {str(e)}")
            return None

    def _get_dimension_code(self, dimension_name: str) -> str:
        """
        将维度名称转换为代码

        Args:
            dimension_name: 维度名称

        Returns:
            str: 维度代码
        """
        if not dimension_name:
            return 'unknown'

        mapping = {
            '准确性': 'accuracy',
            '完整性': 'completeness',
            '相关性': 'relevance',
            '时效性': 'timeliness',
            '有用性': 'usefulness',
            '满意度': 'satisfaction',
            '清晰度': 'clarity',
            '专业性': 'professionalism'
        }

        return mapping.get(dimension_name, dimension_name.lower().replace(' ', '_'))

    def _get_dimension_averages_for_classification(self, classification: str) -> List[tuple]:
        """
        获取指定分类下所有维度的平均分

        Args:
            classification: 问题分类

        Returns:
            List[tuple]: [(dimension_name, avg_score, sample_count), ...]
        """
        try:
            # 使用原生SQL查询，因为需要处理动态维度字段
            from sqlalchemy import text

            sql = text("""
                WITH dimension_scores AS (
                    -- 维度1的数据
                    SELECT
                        s.dimension_1_name as dimension_name,
                        s.score_1 as score
                    FROM questions q
                    JOIN answers a ON q.business_id = a.question_business_id
                    JOIN scores s ON a.id = s.answer_id
                    WHERE q.classification = :classification
                    AND q.is_badcase = true
                    AND s.dimension_1_name IS NOT NULL
                    AND s.score_1 IS NOT NULL

                    UNION ALL

                    -- 维度2的数据
                    SELECT
                        s.dimension_2_name as dimension_name,
                        s.score_2 as score
                    FROM questions q
                    JOIN answers a ON q.business_id = a.question_business_id
                    JOIN scores s ON a.id = s.answer_id
                    WHERE q.classification = :classification
                    AND q.is_badcase = true
                    AND s.dimension_2_name IS NOT NULL
                    AND s.score_2 IS NOT NULL

                    UNION ALL

                    -- 维度3的数据
                    SELECT
                        s.dimension_3_name as dimension_name,
                        s.score_3 as score
                    FROM questions q
                    JOIN answers a ON q.business_id = a.question_business_id
                    JOIN scores s ON a.id = s.answer_id
                    WHERE q.classification = :classification
                    AND q.is_badcase = true
                    AND s.dimension_3_name IS NOT NULL
                    AND s.score_3 IS NOT NULL

                    UNION ALL

                    -- 维度4的数据
                    SELECT
                        s.dimension_4_name as dimension_name,
                        s.score_4 as score
                    FROM questions q
                    JOIN answers a ON q.business_id = a.question_business_id
                    JOIN scores s ON a.id = s.answer_id
                    WHERE q.classification = :classification
                    AND q.is_badcase = true
                    AND s.dimension_4_name IS NOT NULL
                    AND s.score_4 IS NOT NULL

                    UNION ALL

                    -- 维度5的数据
                    SELECT
                        s.dimension_5_name as dimension_name,
                        s.score_5 as score
                    FROM questions q
                    JOIN answers a ON q.business_id = a.question_business_id
                    JOIN scores s ON a.id = s.answer_id
                    WHERE q.classification = :classification
                    AND q.is_badcase = true
                    AND s.dimension_5_name IS NOT NULL
                    AND s.score_5 IS NOT NULL
                )
                SELECT
                    dimension_name,
                    AVG(score) as avg_score,
                    COUNT(*) as sample_count
                FROM dimension_scores
                GROUP BY dimension_name
                ORDER BY avg_score ASC
            """)

            result = db.session.execute(sql, {'classification': classification})
            return [(row[0], float(row[1]), row[2]) for row in result]

        except Exception as e:
            self.logger.error(f"获取分类 {classification} 维度平均分时出错: {str(e)}")
            return []
