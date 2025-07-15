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
                        # 检查是否已经存在答案，避免重复生成
                        existing_doubao = db.session.query(Answer).filter_by(
                            question_business_id=question.business_id,
                            assistant_type='doubao'
                        ).first()
                        
                        existing_xiaotian = db.session.query(Answer).filter_by(
                            question_business_id=question.business_id,
                            assistant_type='xiaotian'
                        ).first()
                        
                        # 生成豆包AI答案
                        if not existing_doubao:
                            try:
                                doubao_result = doubao_client.generate_answer(
                                    question=question.query,
                                    context=f"分类: {question.classification}" if question.classification else None
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
                                self.logger.info(f"豆包答案生成成功: 问题 {question.id}")
                                
                            except Exception as e:
                                self.logger.error(f"豆包答案生成失败 {question.id}: {str(e)}")
                        else:
                            self.logger.debug(f"问题 {question.id} 已存在豆包答案，跳过")
                        
                        # 生成小天AI答案
                        if not existing_xiaotian:
                            try:
                                xiaotian_result = xiaotian_client.generate_answer(
                                    question=question.query,
                                    context=f"分类: {question.classification}" if question.classification else None
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
                                self.logger.info(f"小天答案生成成功: 问题 {question.id}")
                                
                            except Exception as e:
                                self.logger.error(f"小天答案生成失败 {question.id}: {str(e)}")
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
                    
                    # 构建评分API输入
                    our_answer = answers.get('our_ai', {}).get('answer_text', '') if 'our_ai' in answers else ''
                    doubao_answer = answers.get('doubao', {}).get('answer_text', '') if 'doubao' in answers else ''
                    xiaotian_answer = answers.get('xiaotian', {}).get('answer_text', '') if 'xiaotian' in answers else ''
                    classification = question.classification or ''
                    
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
                        '原始模型': 'our_ai',
                        '豆包模型': 'doubao', 
                        '小天模型': 'xiaotian'
                    }
                    
                    saved_scores = 0
                    for score_result in score_results:
                        model_name = score_result.get('模型名称', '')
                        assistant_type = model_name_mapping.get(model_name)
                        
                        if assistant_type and assistant_type in answers:
                            answer_obj = answers[assistant_type]
                            
                            # 创建评分记录
                            score = Score(
                                answer_id=answer_obj['id'],
                                score_1=score_result.get('准确性', 3),
                                score_2=score_result.get('完整性', 3),
                                score_3=score_result.get('清晰度', 3),
                                score_4=score_result.get('相关性', 3),
                                score_5=score_result.get('有用性', 3),
                                comment=score_result.get('理由', ''),
                                rated_at=datetime.utcnow()
                            )
                            
                            # 计算平均分
                            scores = [score.score_1, score.score_2, score.score_3, score.score_4, score.score_5]
                            valid_scores = [s for s in scores if s is not None]
                            if valid_scores:
                                score.average_score = sum(valid_scores) / len(valid_scores)
                            
                            db.session.add(score)
                            
                            # 更新答案状态
                            answer_record = db.session.query(Answer).filter_by(id=answer_obj['id']).first()
                            if answer_record:
                                answer_record.is_scored = True
                                answer_record.updated_at = datetime.utcnow()
                            
                            saved_scores += 1
                    
                    success_count += saved_scores
                    processed_questions += 1
                    
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
    
    def _get_questions_for_scoring(
        self, 
        limit: Optional[int] = None, 
        days_back: int = 1
    ) -> List[Dict[str, Any]]:
        """获取需要评分的问题组（按问题分组，包含多个AI模型答案）"""
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        # 查询有答案但未评分的问题
        questions_with_answers = db.session.query(Question).join(Answer).filter(
            and_(
                Question.created_at >= cutoff_time,
                Question.classification.isnot(None),
                Question.classification != '',
                Answer.is_scored == False,
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
                    'assistant_type': answer.assistant_type
                }
            
            # 只有包含多个AI模型答案的问题才进行评分
            if len(answers_by_type) >= 1:  # 至少有一个答案
                question_groups.append({
                    'question': question,
                    'answers': answers_by_type
                })
        
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