"""
AI处理服务
负责批量处理问题分类、答案生成和评分任务
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import text, func, and_
from sqlalchemy.exc import SQLAlchemyError
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

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
                        # 获取相关答案信息（如果存在）
                        existing_answer = None
                        answer_records = db.session.query(Answer).filter_by(
                            question_business_id=question.business_id
                        ).all()
                        
                        # 如果有多个答案，选择最新的一个作为参考
                        if answer_records:
                            existing_answer = max(answer_records, key=lambda x: x.created_at).answer_text
                        
                        # 调用分类API - 使用用户的格式
                        classification_result = classification_client.classify_question(
                            question=question.query,
                            answer=existing_answer,  # 传入答案信息
                            user_id="00031559"       # 使用用户指定的用户ID
                        )
                        
                        # 更新问题分类结果 - 现在直接是字符串
                        question.classification = classification_result
                        question.processing_status = 'classified'
                        question.updated_at = datetime.utcnow()
                        
                        success_count += 1
                        self.logger.info(f"问题 {question.id} 分类成功: {classification_result}")
                        
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
                        # 在事务中重新检查是否已经存在答案，避免并发重复生成
                        # 使用 count() 而不是 first() 来检查数量
                        existing_doubao_count = db.session.query(Answer).filter_by(
                            question_business_id=question.business_id,
                            assistant_type='doubao'
                        ).count()

                        existing_xiaotian_count = db.session.query(Answer).filter_by(
                            question_business_id=question.business_id,
                            assistant_type='xiaotian'
                        ).count()

                        # 生成豆包AI答案
                        if existing_doubao_count == 0:
                            try:
                                doubao_result = doubao_client.generate_answer(
                                    question=question.query,
                                    context=f"分类: {question.classification}" if question.classification else None
                                )

                                # 再次检查是否在生成过程中被其他进程创建了答案
                                # 再次检查是否在生成过程中被其他进程创建了答案
                                final_doubao_count = db.session.query(Answer).filter_by(
                                    question_business_id=question.business_id,
                                    assistant_type='doubao'
                                ).count()

                                if final_doubao_count == 0:
                                    # 保存豆包答案
                                    doubao_answer = Answer(
                                        question_business_id=question.business_id,
                                        answer_text=doubao_result.get('answer', ''),
                                        assistant_type='doubao',
                                        answer_time=datetime.utcnow()
                                    )
                                    db.session.merge(doubao_answer)
                                    doubao_count += 1
                                    self.logger.info(f"豆包答案生成成功: 问题 {question.id}")
                                else:
                                    self.logger.warning(f"问题 {question.id} 在生成过程中已被其他进程创建豆包答案，跳过保存")

                            except Exception as e:
                                self.logger.error(f"豆包答案生成失败 {question.id}: {str(e)}")
                        elif existing_doubao_count > 1:
                            self.logger.warning(f"问题 {question.id} 存在 {existing_doubao_count} 个豆包答案，存在重复数据")
                        else:
                            self.logger.debug(f"问题 {question.id} 已存在豆包答案，跳过")

                        # 生成小天AI答案
                        if existing_xiaotian_count == 0:
                            try:
                                xiaotian_result = xiaotian_client.generate_answer(
                                    question=question.query,
                                    context=f"分类: {question.classification}" if question.classification else None
                                )

                                # 再次检查是否在生成过程中被其他进程创建了答案
                                # 再次检查是否在生成过程中被其他进程创建了答案
                                final_xiaotian_count = db.session.query(Answer).filter_by(
                                    question_business_id=question.business_id,
                                    assistant_type='xiaotian'
                                ).count()

                                if final_xiaotian_count == 0:
                                    # 保存小天答案
                                    # 使用merge确保幂等，避免并发下重复插入
                                    xiaotian_answer = Answer(
                                        question_business_id=question.business_id,
                                        answer_text=xiaotian_result.get('answer', ''),
                                        assistant_type='xiaotian',
                                        answer_time=datetime.utcnow()
                                    )
                                    db.session.merge(xiaotian_answer)
                                    xiaotian_count += 1
                                    self.logger.info(f"小天答案生成成功: 问题 {question.id}")
                                else:
                                    self.logger.warning(f"问题 {question.id} 在生成过程中已被其他进程创建小天答案，跳过保存")

                            except Exception as e:
                                self.logger.error(f"小天答案生成失败 {question.id}: {str(e)}")
                        elif existing_xiaotian_count > 1:
                            self.logger.warning(f"问题 {question.id} 存在 {existing_xiaotian_count} 个小天答案，存在重复数据")
                        else:
                            self.logger.debug(f"问题 {question.id} 已存在小天答案，跳过")
                        
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
    
    def process_answer_generation_bulk(
        self, 
        batch_size: int = 1000,
        days_back: int = 1
    ) -> Dict[str, Any]:
        """
        按用户需求实现的批量答案生成
        
        流程：
        1. 一次性从数据库获取大批量数据（如1000条）
        2. 存储在列表中
        3. 用for循环逐条调用API
        4. 将结果收集到列表中
        5. 最终整体写回数据库，确保答案对应到正确位置
        
        Args:
            batch_size: 一次处理的数据量（默认1000）
            days_back: 处理最近几天的数据
            
        Returns:
            处理结果统计
        """
        try:
            self.logger.info(f"开始批量答案生成（新逻辑）- 批次大小: {batch_size}")
            
            # 1. 一次性批量获取数据
            questions = self._get_questions_for_answer_generation(limit=batch_size, days_back=days_back)
            
            if not questions:
                return {
                    'success': True,
                    'message': '没有需要生成答案的问题',
                    'processed_count': 0,
                    'doubao_count': 0,
                    'xiaotian_count': 0,
                    'error_count': 0
                }
            
            self.logger.info(f"一次性获取 {len(questions)} 个问题，开始处理")
            
            # 2. 获取AI客户端
            doubao_client = APIClientFactory.get_doubao_client()
            xiaotian_client = APIClientFactory.get_xiaotian_client()
            
            # 3. 初始化结果收集列表（保持与问题列表相同的索引顺序）
            doubao_answers = []  # 豆包答案列表
            xiaotian_answers = [] # 小天答案列表
            processing_errors = []  # 错误记录列表
            
            # 4. 用for循环逐条调用API
            for i, question in enumerate(questions):
                self.logger.info(f"处理问题 {i+1}/{len(questions)}: {question.query[:50]}...")
                
                # 检查是否已存在答案（避免重复生成）
                existing_doubao = db.session.query(Answer).filter_by(
                    question_business_id=question.business_id,
                    assistant_type='doubao'
                ).first()
                
                existing_xiaotian = db.session.query(Answer).filter_by(
                    question_business_id=question.business_id,
                    assistant_type='xiaotian'
                ).first()
                
                # 处理豆包AI答案
                doubao_result = None
                if not existing_doubao:
                    try:
                        doubao_result = doubao_client.generate_answer(
                            question=question.query,
                            context=f"分类: {question.classification}" if question.classification else None
                        )
                        self.logger.debug(f"豆包API调用成功 - 问题{i+1}")
                    except Exception as e:
                        error_info = {
                            'question_index': i,
                            'question_id': question.id,
                            'api_type': 'doubao',
                            'error': str(e)
                        }
                        processing_errors.append(error_info)
                        self.logger.error(f"豆包API调用失败 - 问题{i+1}: {str(e)}")
                
                # 处理小天AI答案  
                xiaotian_result = None
                if not existing_xiaotian:
                    try:
                        xiaotian_result = xiaotian_client.generate_answer(
                            question=question.query,
                            context=f"分类: {question.classification}" if question.classification else None
                        )
                        self.logger.debug(f"小天API调用成功 - 问题{i+1}")
                    except Exception as e:
                        error_info = {
                            'question_index': i,
                            'question_id': question.id,
                            'api_type': 'xiaotian', 
                            'error': str(e)
                        }
                        processing_errors.append(error_info)
                        self.logger.error(f"小天API调用失败 - 问题{i+1}: {str(e)}")
                
                # 将结果添加到对应位置的列表中（保持索引对应关系）
                doubao_answers.append({
                    'question_index': i,
                    'question_business_id': question.business_id,
                    'result': doubao_result,
                    'existing': existing_doubao is not None
                })
                
                xiaotian_answers.append({
                    'question_index': i,
                    'question_business_id': question.business_id,
                    'result': xiaotian_result,
                    'existing': existing_xiaotian is not None
                })
            
            self.logger.info("API调用阶段完成，开始批量写入数据库")
            
            # 5. 最终整体写回数据库
            doubao_inserted = 0
            xiaotian_inserted = 0
            
            # 处理豆包答案写入
            for answer_data in doubao_answers:
                if not answer_data['existing'] and answer_data['result']:
                    try:
                        doubao_answer = Answer(
                            question_business_id=answer_data['question_business_id'],
                            answer_text=answer_data['result'].get('answer', ''),
                            assistant_type='doubao',
                            answer_time=datetime.utcnow()
                        )
                        db.session.add(doubao_answer)
                        doubao_inserted += 1
                    except Exception as e:
                        self.logger.error(f"豆包答案写入失败 - 索引{answer_data['question_index']}: {str(e)}")
            
            # 处理小天答案写入
            for answer_data in xiaotian_answers:
                if not answer_data['existing'] and answer_data['result']:
                    try:
                        xiaotian_answer = Answer(
                            question_business_id=answer_data['question_business_id'],
                            answer_text=answer_data['result'].get('answer', ''),
                            assistant_type='xiaotian',
                            answer_time=datetime.utcnow()
                        )
                        db.session.add(xiaotian_answer)
                        xiaotian_inserted += 1
                    except Exception as e:
                        self.logger.error(f"小天答案写入失败 - 索引{answer_data['question_index']}: {str(e)}")
            
            # 更新问题状态
            for question in questions:
                question.processing_status = 'answers_generated'
                question.updated_at = datetime.utcnow()
            
            # 一次性提交所有更改
            try:
                db.session.commit()
                self.logger.info("数据库批量提交成功")
            except Exception as e:
                db.session.rollback()
                self.logger.error(f"数据库批量提交失败: {str(e)}")
                raise
            
            # 6. 返回处理结果
            result = {
                'success': True,
                'message': f'批量答案生成完成（新逻辑）- 豆包: {doubao_inserted}, 小天: {xiaotian_inserted}',
                'processed_count': len(questions),
                'doubao_count': doubao_inserted,
                'xiaotian_count': xiaotian_inserted,
                'error_count': len(processing_errors),
                'processing_errors': processing_errors[:10] if processing_errors else [],  # 只返回前10个错误
                'batch_size_used': batch_size,
                'position_mapping_maintained': True  # 标识保持了位置对应关系
            }
            
            self.logger.info(f"批量答案生成完成（新逻辑）: {result}")
            return result
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"批量答案生成异常（新逻辑）: {str(e)}"
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
        """批量评分处理 - 按问题分组，支持多模型评分"""
        try:
            self.logger.info("开始批量评分处理")
            
            # 获取需要评分的问题组（包含多个AI模型答案）
            question_groups = self._get_questions_for_scoring(limit, days_back)
            
            if not question_groups:
                return {
                    'success': True,
                    'message': '没有需要评分的问题',
                    'processed_count': 0,
                    'success_count': 0,
                    'error_count': 0
                }
            
            self.logger.info(f"找到 {len(question_groups)} 个待评分问题组")
            
            # 获取评分API客户端
            score_client = APIClientFactory.get_score_client()
            
            success_count = 0
            error_count = 0
            processed_questions = 0
            
            # 按问题组逐个处理
            for question_data in question_groups:
                try:
                    question = question_data['question']
                    answers = question_data['answers']  # {assistant_type: answer_obj}
                    
                    self.logger.info(f"处理问题评分: {question.query[:50]}... (包含{len(answers)}个AI答案)")
                    
                    # 构建评分API输入（确保三个答案都存在）
                    our_answer = answers.get('yoyo', {}).get('answer_text', '')
                    doubao_answer = answers.get('doubao', {}).get('answer_text', '')
                    xiaotian_answer = answers.get('xiaotian', {}).get('answer_text', '')
                    classification = question.classification or ''

                    # 验证三个答案都不为空（双重保险）
                    if not all([our_answer, doubao_answer, xiaotian_answer, classification]):
                        self.logger.warning(f"问题 {question.business_id} 答案或分类为空，跳过评分")
                        continue
                        
                        # 调用评分API
                    score_results = score_client.score_multiple_answers(
                            question=question.query,
                        our_answer=our_answer,
                        doubao_answer=doubao_answer,
                        xiaotian_answer=xiaotian_answer,
                        classification=classification
                    )
                    
                    # 处理评分结果，按模型匹配
                    model_name_mapping = {
                        'yoyo': 'yoyo',
                        '豆包': 'doubao',
                        '小天': 'xiaotian',
                        '原始模型': 'yoyo',
                        '豆包模型': 'doubao', 
                        '小天模型': 'xiaotian'
                    }
                    
                    saved_scores = 0
                    for score_result in score_results:
                        model_name = score_result.get('模型名称', '')
                        assistant_type = model_name_mapping.get(model_name)

                        if assistant_type and assistant_type in answers:
                            answer_obj = answers[assistant_type]

                            # 使用新的创建方法，支持动态维度名称
                            score = Score.create_from_api_response(
                                answer_obj['id'],
                                score_result
                            )

                            db.session.add(score)

                            # 更新答案状态
                            answer_record = db.session.query(Answer).filter_by(id=answer_obj['id']).first()
                            if answer_record:
                                answer_record.is_scored = True
                                answer_record.updated_at = datetime.utcnow()

                            saved_scores += 1

                    success_count += saved_scores
                    processed_questions += 1

                    # 检查并更新问题状态为scored
                    if saved_scores > 0:  # 如果有评分被保存
                        if self._check_question_scoring_complete(question.business_id):
                            # 更新问题状态为scored
                            question.processing_status = 'scored'
                            question.updated_at = datetime.utcnow()
                            self.logger.info(f"问题 {question.business_id} 所有答案评分完成，状态更新为scored")

                            # 检测badcase（新增）
                            try:
                                from app.services.badcase_detection_service import BadcaseDetectionService
                                badcase_service = BadcaseDetectionService()
                                is_badcase = badcase_service.detect_badcase(question.business_id)
                                if is_badcase:
                                    self.logger.info(f"问题 {question.business_id} 被标记为badcase")
                            except Exception as e:
                                self.logger.error(f"检测badcase时出错 {question.business_id}: {str(e)}")

                    # 提交当前问题的评分
                    try:
                        db.session.commit()
                        self.logger.info(f"问题 {question.business_id} 评分保存成功，共{saved_scores}个模型")
                    except Exception as e:
                        db.session.rollback()
                        self.logger.error(f"问题 {question.business_id} 评分保存失败: {str(e)}")
                        error_count += saved_scores
                        
                except Exception as e:
                    self.logger.error(f"评分问题失败 {question.business_id}: {str(e)}")
                    error_count += 1
                    db.session.rollback()
                    continue
            
            result = {
                'success': True,
                'message': f'评分处理完成，处理问题: {processed_questions}, 成功评分: {success_count}, 失败: {error_count}',
                'processed_count': processed_questions,
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
        """获取未分类的问题 - 查找所有状态为pending或classification_failed的问题"""
        self.logger.info(f"查找所有待分类问题（不限制时间范围）")

        query = db.session.query(Question).filter(
            and_(
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
                # ① 不再要求必须已经有分类
                # Question.classification.isnot(None),
                # Question.classification != '',
                # ② 处理状态允许 pending
                Question.processing_status.in_(
                    ['pending', 'classified', 'answer_generation_failed']
                )
            )
        ).order_by(Question.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()
    
    def _get_questions_for_scoring(
        self, 
        limit: Optional[int] = None, 
        days_back: int = 1
    ) -> List[Dict[str, Any]]:
        """获取需要评分的问题组（按问题分组，包含多个AI模型答案）"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        # 查询有答案的问题（优化：只查询已生成答案但未评分的问题）
        questions_with_answers = db.session.query(Question).join(Answer).filter(
            and_(
                Question.created_at >= cutoff_time,
                Question.classification.isnot(None),
                Question.classification != '',
                Question.processing_status.in_(['answers_generated', 'scoring']),
                Answer.answer_text.isnot(None),
                Answer.answer_text != ''
            )
        ).distinct().order_by(Question.created_at.desc())
        
        if limit:
            questions_with_answers = questions_with_answers.limit(limit)
        
        question_groups = []
        
        for question in questions_with_answers:
            # 获取该问题的所有AI模型答案
            answers = db.session.query(Answer).filter(
                and_(
                    Answer.question_business_id == question.business_id,
                    Answer.is_scored == False,
                    Answer.answer_text.isnot(None),
                    Answer.answer_text != ''
                )
            ).all()
            
            if not answers:
                continue
            
            # 按assistant_type分组
            answers_by_type = {}
            for answer in answers:
                answers_by_type[answer.assistant_type] = {
                    'id': answer.id,
                    'answer_text': answer.answer_text,
                    'assistant_type': answer.assistant_type,
                    'is_scored': answer.is_scored
                }
            
            # 只有包含完整三个AI模型答案且未评分的问题才进行评分（符合设计要求）
            # 注意：数据库中实际存储的是 yoyo, doubao, xiaotian
            required_types = {'yoyo', 'doubao', 'xiaotian'}
            available_types = set(answers_by_type.keys())

            if required_types.issubset(available_types):  # 必须有完整的三个答案
                # 检查三个答案是否都未评分
                all_unscored = all(
                    not answers_by_type[ai_type]['is_scored']
                    for ai_type in required_types
                )

                if all_unscored:
                    question_groups.append({
                        'question': question,
                        'answers': answers_by_type
                    })
                    self.logger.info(f"添加问题到评分队列: {question.business_id} (包含{len(required_types)}个AI答案)")
                else:
                    self.logger.debug(f"跳过问题 {question.business_id}：已有答案被评分")
            else:
                missing_types = required_types - available_types
                self.logger.info(f"跳过问题 {question.business_id}：缺少答案类型 {missing_types}, 现有类型 {available_types}")
        
        return question_groups
    
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

    def _check_question_scoring_complete(self, question_business_id: str) -> bool:
        """检查问题的所有答案是否都已完成评分"""
        try:
            # 查询该问题的所有答案
            answers = db.session.query(Answer).filter_by(
                question_business_id=question_business_id
            ).all()

            if not answers:
                self.logger.warning(f"问题 {question_business_id} 没有找到任何答案")
                return False

            # 检查是否有完整的三个AI模型答案
            required_types = {'yoyo', 'doubao', 'xiaotian'}
            answers_by_type = {}

            for answer in answers:
                if answer.assistant_type in required_types:
                    answers_by_type[answer.assistant_type] = answer

            # 必须有完整的三个AI模型答案
            if not required_types.issubset(set(answers_by_type.keys())):
                missing_types = required_types - set(answers_by_type.keys())
                self.logger.debug(f"问题 {question_business_id} 缺少答案类型: {missing_types}")
                return False

            # 检查所有必需的答案是否都已评分
            for assistant_type in required_types:
                answer = answers_by_type[assistant_type]
                if not answer.is_scored:
                    self.logger.debug(f"问题 {question_business_id} 的 {assistant_type} 答案尚未评分")
                    return False

            self.logger.debug(f"问题 {question_business_id} 所有答案都已完成评分")
            return True

        except Exception as e:
            self.logger.error(f"检查问题 {question_business_id} 评分完成状态时出错: {str(e)}")
            return False

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