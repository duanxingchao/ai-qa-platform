"""
AI处理服务
负责批量处理问题分类、答案生成和评分任务
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import text, func, and_
from sqlalchemy.exc import SQLAlchemyError

from app.utils.database import db
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.services.api_client import APIClientFactory
from app.utils.helpers import batch_process
from app.config import Config


class AIProcessingService:
    """AI处理服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.batch_size = Config.BATCH_SIZE or 50
        
    def process_classification_batch(
        self, 
        limit: Optional[int] = None,
        days_back: int = 1
    ) -> Dict[str, Any]:
        """批量处理问题分类"""
        try:
            self.logger.info("开始批量分类处理")
            
            # 获取需要分类的问题
            questions = self._get_unclassified_questions(limit, days_back)
            
            if not questions:
                return {
                    'success': True,
                    'message': '没有需要分类的问题',
                    'processed_count': 0,
                    'success_count': 0,
                    'error_count': 0
                }
            
            self.logger.info(f"找到 {len(questions)} 个待分类问题")
            
            # 获取分类API客户端
            classification_client = APIClientFactory.get_classification_client()
            
            success_count = 0
            error_count = 0
            
            # 批量处理
            for i in range(0, len(questions), self.batch_size):
                batch = questions[i:i + self.batch_size]
                self.logger.info(f"处理批次 {i//self.batch_size + 1}, 包含 {len(batch)} 个问题")
                
                for question in batch:
                    try:
                        # 调用分类API
                        result = classification_client.classify_question(
                            question=question.query,
                            context=f"页面: {question.pageid}, 设备: {question.devicetypename}"
                        )
                        
                        # 更新问题分类结果
                        question.classification = result.get('category', 'unknown')
                        question.processing_status = 'classified'
                        question.updated_at = datetime.utcnow()
                        
                        success_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"分类问题失败 {question.id}: {str(e)}")
                        question.processing_status = 'classification_failed'
                        error_count += 1
                        continue
                
                # 提交批次
                try:
                    db.session.commit()
                    self.logger.info(f"批次 {i//self.batch_size + 1} 提交成功")
                except Exception as e:
                    db.session.rollback()
                    self.logger.error(f"批次 {i//self.batch_size + 1} 提交失败: {str(e)}")
                    error_count += len(batch) - success_count
            
            result = {
                'success': True,
                'message': f'分类处理完成，成功: {success_count}, 失败: {error_count}',
                'processed_count': len(questions),
                'success_count': success_count,
                'error_count': error_count
            }
            
            self.logger.info(f"批量分类处理完成: {result}")
            return result
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"批量分类处理异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'processed_count': 0,
                'success_count': 0,
                'error_count': 0
            }
    
    def process_answer_generation_batch(
        self, 
        limit: Optional[int] = None,
        days_back: int = 1
    ) -> Dict[str, Any]:
        """批量生成AI答案"""
        try:
            self.logger.info("开始批量答案生成")
            
            # 获取需要生成答案的问题
            questions = self._get_questions_for_answer_generation(limit, days_back)
            
            if not questions:
                return {
                    'success': True,
                    'message': '没有需要生成答案的问题',
                    'processed_count': 0,
                    'doubao_count': 0,
                    'xiaotian_count': 0,
                    'error_count': 0
                }
            
            self.logger.info(f"找到 {len(questions)} 个待生成答案的问题")
            
            # 获取AI客户端
            doubao_client = APIClientFactory.get_doubao_client()
            xiaotian_client = APIClientFactory.get_xiaotian_client()
            
            doubao_count = 0
            xiaotian_count = 0
            error_count = 0
            
            # 批量处理
            for i in range(0, len(questions), self.batch_size):
                batch = questions[i:i + self.batch_size]
                self.logger.info(f"处理答案生成批次 {i//self.batch_size + 1}, 包含 {len(batch)} 个问题")
                
                for question in batch:
                    try:
                        # 生成豆包AI答案
                        try:
                            doubao_result = doubao_client.generate_answer(
                                question=question.query,
                                context=f"分类: {question.classification}"
                            )
                            
                            # 保存豆包答案
                            doubao_answer = Answer(
                                question_business_id=question.business_id,
                                answer_text=doubao_result.get('answer', ''),
                                assistant_type='doubao',
                                answer_time=datetime.utcnow()
                            )
                            db.session.add(doubao_answer)
                            doubao_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"豆包答案生成失败 {question.id}: {str(e)}")
                        
                        # 生成小天AI答案
                        try:
                            xiaotian_result = xiaotian_client.generate_answer(
                                question=question.query,
                                context=f"分类: {question.classification}"
                            )
                            
                            # 保存小天答案
                            xiaotian_answer = Answer(
                                question_business_id=question.business_id,
                                answer_text=xiaotian_result.get('answer', ''),
                                assistant_type='xiaotian',
                                answer_time=datetime.utcnow()
                            )
                            db.session.add(xiaotian_answer)
                            xiaotian_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"小天答案生成失败 {question.id}: {str(e)}")
                        
                        # 更新问题状态
                        question.processing_status = 'answers_generated'
                        question.updated_at = datetime.utcnow()
                        
                    except Exception as e:
                        self.logger.error(f"问题 {question.id} 答案生成异常: {str(e)}")
                        question.processing_status = 'answer_generation_failed'
                        error_count += 1
                        continue
                
                # 提交批次
                try:
                    db.session.commit()
                    self.logger.info(f"答案生成批次 {i//self.batch_size + 1} 提交成功")
                except Exception as e:
                    db.session.rollback()
                    self.logger.error(f"答案生成批次 {i//self.batch_size + 1} 提交失败: {str(e)}")
            
            result = {
                'success': True,
                'message': f'答案生成完成，豆包: {doubao_count}, 小天: {xiaotian_count}, 错误: {error_count}',
                'processed_count': len(questions),
                'doubao_count': doubao_count,
                'xiaotian_count': xiaotian_count,
                'error_count': error_count
            }
            
            self.logger.info(f"批量答案生成完成: {result}")
            return result
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"批量答案生成异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'processed_count': 0,
                'doubao_count': 0,
                'xiaotian_count': 0,
                'error_count': 0
            }
    
    def process_scoring_batch(
        self, 
        limit: Optional[int] = None,
        days_back: int = 1
    ) -> Dict[str, Any]:
        """批量评分处理"""
        try:
            self.logger.info("开始批量评分处理")
            
            # 获取需要评分的答案
            answers = self._get_unscored_answers(limit, days_back)
            
            if not answers:
                return {
                    'success': True,
                    'message': '没有需要评分的答案',
                    'processed_count': 0,
                    'success_count': 0,
                    'error_count': 0
                }
            
            self.logger.info(f"找到 {len(answers)} 个待评分答案")
            
            # 获取评分API客户端
            score_client = APIClientFactory.get_score_client()
            
            success_count = 0
            error_count = 0
            
            # 批量处理
            for i in range(0, len(answers), self.batch_size):
                batch = answers[i:i + self.batch_size]
                self.logger.info(f"处理评分批次 {i//self.batch_size + 1}, 包含 {len(batch)} 个答案")
                
                for answer in batch:
                    try:
                        # 获取问题信息
                        question = db.session.query(Question).filter_by(
                            business_id=answer.question_business_id
                        ).first()
                        
                        if not question:
                            self.logger.warning(f"答案 {answer.id} 对应的问题未找到")
                            continue
                        
                        # 调用评分API
                        score_result = score_client.score_answer(
                            question=question.query,
                            answer=answer.answer_text,
                            reference_answer=None,
                            criteria=['accuracy', 'completeness', 'clarity', 'relevance', 'helpfulness']
                        )
                        
                        # 保存评分结果
                        score = Score(
                            answer_id=answer.id,
                            score_1=self._convert_score(score_result.get('dimension_scores', {}).get('accuracy', 0)),
                            score_2=self._convert_score(score_result.get('dimension_scores', {}).get('completeness', 0)),
                            score_3=self._convert_score(score_result.get('dimension_scores', {}).get('clarity', 0)),
                            score_4=self._convert_score(score_result.get('dimension_scores', {}).get('relevance', 0)),
                            score_5=self._convert_score(score_result.get('dimension_scores', {}).get('helpfulness', 0)),
                            comment=score_result.get('feedback', ''),
                            rated_at=datetime.utcnow()
                        )
                        
                        # 计算平均分
                        scores = [score.score_1, score.score_2, score.score_3, score.score_4, score.score_5]
                        valid_scores = [s for s in scores if s is not None]
                        if valid_scores:
                            score.average_score = sum(valid_scores) / len(valid_scores)
                        
                        db.session.add(score)
                        
                        # 更新答案状态
                        answer.is_scored = True
                        answer.updated_at = datetime.utcnow()
                        
                        success_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"评分答案失败 {answer.id}: {str(e)}")
                        error_count += 1
                        continue
                
                # 提交批次
                try:
                    db.session.commit()
                    self.logger.info(f"评分批次 {i//self.batch_size + 1} 提交成功")
                except Exception as e:
                    db.session.rollback()
                    self.logger.error(f"评分批次 {i//self.batch_size + 1} 提交失败: {str(e)}")
            
            result = {
                'success': True,
                'message': f'评分处理完成，成功: {success_count}, 失败: {error_count}',
                'processed_count': len(answers),
                'success_count': success_count,
                'error_count': error_count
            }
            
            self.logger.info(f"批量评分处理完成: {result}")
            return result
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"批量评分处理异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'processed_count': 0,
                'success_count': 0,
                'error_count': 0
            }
    
    def _get_unclassified_questions(
        self, 
        limit: Optional[int] = None, 
        days_back: int = 1
    ) -> List[Question]:
        """获取未分类的问题"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        query = db.session.query(Question).filter(
            and_(
                Question.created_at >= cutoff_time,
                Question.classification.is_(None) | (Question.classification == ''),
                Question.processing_status.in_(['pending', 'classification_failed'])
            )
        ).order_by(Question.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def _get_questions_for_answer_generation(
        self, 
        limit: Optional[int] = None, 
        days_back: int = 1
    ) -> List[Question]:
        """获取需要生成答案的问题"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        query = db.session.query(Question).filter(
            and_(
                Question.created_at >= cutoff_time,
                Question.classification.isnot(None),
                Question.classification != '',
                Question.processing_status.in_(['classified', 'answer_generation_failed'])
            )
        ).order_by(Question.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def _get_unscored_answers(
        self, 
        limit: Optional[int] = None, 
        days_back: int = 1
    ) -> List[Answer]:
        """获取未评分的答案"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        query = db.session.query(Answer).filter(
            and_(
                Answer.created_at >= cutoff_time,
                Answer.is_scored == False,
                Answer.answer_text.isnot(None),
                Answer.answer_text != ''
            )
        ).order_by(Answer.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def _convert_score(self, api_score: float) -> Optional[int]:
        """将API返回的评分（0-100）转换为1-5分"""
        if api_score is None or api_score < 0:
            return None
        
        # 0-100分转换为1-5分
        if api_score <= 20:
            return 1
        elif api_score <= 40:
            return 2
        elif api_score <= 60:
            return 3
        elif api_score <= 80:
            return 4
        else:
            return 5
    
    def get_processing_statistics(self, days_back: int = 7) -> Dict[str, Any]:
        """获取处理统计信息"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_back)
            
            # 问题统计
            total_questions = db.session.query(func.count(Question.id)).filter(
                Question.created_at >= cutoff_time
            ).scalar()
            
            classified_questions = db.session.query(func.count(Question.id)).filter(
                and_(
                    Question.created_at >= cutoff_time,
                    Question.classification.isnot(None),
                    Question.classification != ''
                )
            ).scalar()
            
            # 答案统计
            total_answers = db.session.query(func.count(Answer.id)).filter(
                Answer.created_at >= cutoff_time
            ).scalar()
            
            scored_answers = db.session.query(func.count(Answer.id)).filter(
                and_(
                    Answer.created_at >= cutoff_time,
                    Answer.is_scored == True
                )
            ).scalar()
            
            # 按AI类型统计答案
            doubao_answers = db.session.query(func.count(Answer.id)).filter(
                and_(
                    Answer.created_at >= cutoff_time,
                    Answer.assistant_type == 'doubao'
                )
            ).scalar()
            
            xiaotian_answers = db.session.query(func.count(Answer.id)).filter(
                and_(
                    Answer.created_at >= cutoff_time,
                    Answer.assistant_type == 'xiaotian'
                )
            ).scalar()
            
            return {
                'time_range': f'最近{days_back}天',
                'questions': {
                    'total': total_questions,
                    'classified': classified_questions,
                    'classification_rate': f"{(classified_questions/total_questions*100):.1f}%" if total_questions > 0 else "0%"
                },
                'answers': {
                    'total': total_answers,
                    'scored': scored_answers,
                    'scoring_rate': f"{(scored_answers/total_answers*100):.1f}%" if total_answers > 0 else "0%",
                    'by_type': {
                        'doubao': doubao_answers,
                        'xiaotian': xiaotian_answers
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取处理统计失败: {str(e)}")
            return {'error': str(e)}


# 创建全局AI处理服务实例
ai_processing_service = AIProcessingService() 