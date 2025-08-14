"""
分类处理服务
支持Mock API和外部API的灵活切换，提供完整的问题分类处理功能
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func

from app import db
from app.models.question import Question
from app.services.api_client import APIClientFactory
from app.config import Config

class ClassificationService:
    """分类处理服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_factory = APIClientFactory()
        self.classification_stats = {
            'total_processed': 0,
            'total_success': 0,
            'total_failed': 0,
            'api_mode': Config.API_MODE,
            'use_mock': Config.USE_MOCK_CLASSIFICATION,
            'last_process_time': None
        }
    
    def _get_classification_client(self):
        """获取分类API客户端"""
        return self.api_factory.get_classification_client()
    
    def _is_using_mock_api(self) -> bool:
        """检查是否使用Mock API"""
        return Config.USE_MOCK_CLASSIFICATION or Config.API_MODE == 'mock'
    
    def get_pending_questions(self, limit: Optional[int] = None) -> List[Question]:
        """获取待分类的问题"""
        try:
            query = db.session.query(Question).filter_by(processing_status='pending')
            
            if limit is not None:
                query = query.limit(limit)
            
            questions = query.all()
            self.logger.info(f"获取到 {len(questions)} 条待分类问题")
            return questions
            
        except Exception as e:
            self.logger.error(f"获取待分类问题失败: {str(e)}")
            return []
    
    def classify_single_question(self, question: Question) -> Dict:
        """
        对单个问题进行分类
        
        Args:
            question: Question对象
            
        Returns:
            分类结果字典
        """
        try:
            self.logger.info(f"开始分类问题: {question.id} - {question.query[:50]}...")
            
            # 更新状态为分类中
            question.processing_status = 'classifying'
            db.session.commit()
            
            # 获取分类客户端
            classification_client = self._get_classification_client()
            
            # 准备请求数据
            request_data = {
                'question': question.query,
                'answer': None  # 暂时没有答案，后续可以加入已有答案
            }
            
            # 如果问题已有初始分类，加入上下文
            if question.classification:
                request_data['context'] = {
                    'initial_classification': question.classification,
                    'intent': question.intent
                }
            
            # 调用分类API
            classification_data = classification_client.classify_question(
                question=question.query,
                context=request_data.get('context')
            )
            
            # 更新问题分类信息
            question.classification = classification_data.get('category')
            question.classification_confidence = classification_data.get('confidence', 0.0)
            question.classification_subcategory = classification_data.get('subcategory')
            question.classification_tags = ','.join(classification_data.get('tags', []))
            question.classification_reasoning = classification_data.get('reasoning', '')
            question.classification_api_used = 'mock' if self._is_using_mock_api() else 'external'
            question.classified_at = datetime.utcnow()
            
            # 检查置信度是否达到阈值
            confidence_threshold = Config.CLASSIFICATION_CONFIDENCE_THRESHOLD
            if question.classification_confidence >= confidence_threshold:
                question.processing_status = 'classified'
                status = 'success'
                message = f"分类成功，置信度: {question.classification_confidence:.2f}"
            else:
                question.processing_status = 'classification_uncertain'
                status = 'uncertain'
                message = f"分类完成但置信度较低: {question.classification_confidence:.2f}"
            
            question.updated_at = datetime.utcnow()
            db.session.commit()
            
            result = {
                'success': True,
                'status': status,
                'message': message,
                'question_id': question.id,
                'classification': question.classification,
                'confidence': question.classification_confidence,
                'api_mode': 'mock' if self._is_using_mock_api() else 'external'
            }
            
            self.classification_stats['total_success'] += 1
            self.logger.info(f"问题 {question.id} 分类成功: {question.classification}")
            
            self.classification_stats['total_processed'] += 1
            return result
            
        except Exception as e:
            # 异常处理（包括API异常）
            question.processing_status = 'classification_failed'
            question.error_message = f"分类处理失败: {str(e)}"
            question.updated_at = datetime.utcnow()
            db.session.rollback()
            
            result = {
                'success': False,
                'status': 'failed',
                'message': f"分类处理失败: {str(e)}",
                'question_id': question.id,
                'api_mode': 'mock' if self._is_using_mock_api() else 'external'
            }
            
            self.classification_stats['total_failed'] += 1
            self.logger.error(f"问题 {question.id} 分类失败: {str(e)}")
            return result
    
    def classify_batch_questions(self, batch_size: Optional[int] = None) -> Dict:
        """
        批量分类处理
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            批处理结果
        """
        if batch_size is None:
            batch_size = Config.CLASSIFICATION_BATCH_SIZE
        
        try:
            self.logger.info(f"开始批量分类处理，批大小: {batch_size}")
            
            # 获取待处理问题
            pending_questions = self.get_pending_questions(limit=batch_size)
            
            if not pending_questions:
                return {
                    'success': True,
                    'message': '没有待分类的问题',
                    'processed_count': 0,
                    'success_count': 0,
                    'failed_count': 0,
                    'results': []
                }
            
            # 批量处理
            results = []
            success_count = 0
            failed_count = 0
            
            for question in pending_questions:
                result = self.classify_single_question(question)
                results.append(result)
                
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
            
            # 更新统计
            self.classification_stats['last_process_time'] = datetime.utcnow().isoformat()
            
            batch_result = {
                'success': True,
                'message': f'批量分类完成，成功: {success_count}，失败: {failed_count}',
                'processed_count': len(results),
                'success_count': success_count,
                'failed_count': failed_count,
                'results': results,
                'api_mode': 'mock' if self._is_using_mock_api() else 'external',
                'batch_size': batch_size
            }
            
            self.logger.info(f"批量分类完成: {batch_result['message']}")
            return batch_result
            
        except Exception as e:
            error_msg = f"批量分类处理失败: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'processed_count': 0,
                'success_count': 0,
                'failed_count': 0,
                'results': []
            }
    
    def get_classification_statistics(self) -> Dict:
        """获取分类统计信息"""
        try:
            # 数据库统计
            total_questions = db.session.query(func.count(Question.id)).scalar()
            pending_count = db.session.query(func.count(Question.id)).filter_by(processing_status='pending').scalar()
            classified_count = db.session.query(func.count(Question.id)).filter_by(processing_status='classified').scalar()
            failed_count = db.session.query(func.count(Question.id)).filter(
                Question.processing_status.in_(['classification_failed', 'classification_error'])
            ).scalar()
            uncertain_count = db.session.query(func.count(Question.id)).filter_by(processing_status='classification_uncertain').scalar()
            
            # 分类分布统计
            classification_distribution = {}
            if classified_count > 0:
                distribution_query = db.session.query(
                    Question.classification,
                    func.count(Question.id).label('count')
                ).filter(
                    Question.classification.isnot(None)
                ).group_by(Question.classification).all()
                
                classification_distribution = {
                    category: count for category, count in distribution_query
                }
            
            # 计算处理率
            processed_count = classified_count + failed_count + uncertain_count
            processing_rate = (processed_count / total_questions * 100) if total_questions > 0 else 0
            success_rate = (classified_count / processed_count * 100) if processed_count > 0 else 0
            
            return {
                'overview': {
                    'total_questions': total_questions,
                    'pending_count': pending_count,
                    'classified_count': classified_count,
                    'failed_count': failed_count,
                    'uncertain_count': uncertain_count,
                    'processing_rate': f"{processing_rate:.1f}%",
                    'success_rate': f"{success_rate:.1f}%"
                },
                'distribution': classification_distribution,
                'api_info': {
                    'api_mode': self.classification_stats['api_mode'],
                    'use_mock': self.classification_stats['use_mock'],
                    'confidence_threshold': Config.CLASSIFICATION_CONFIDENCE_THRESHOLD
                },
                'service_stats': self.classification_stats,
                'config': {
                    'enabled': Config.CLASSIFICATION_ENABLED,
                    'batch_size': Config.CLASSIFICATION_BATCH_SIZE
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取分类统计失败: {str(e)}")
            return {'error': str(e)}
    
    def reset_failed_questions(self) -> Dict:
        """重置失败的问题状态，允许重新分类"""
        try:
            failed_questions = db.session.query(Question).filter(
                Question.processing_status.in_(['classification_failed', 'classification_error'])
            ).all()
            
            reset_count = 0
            for question in failed_questions:
                question.processing_status = 'pending'
                question.error_message = None
                question.updated_at = datetime.utcnow()
                reset_count += 1
            
            db.session.commit()
            
            message = f"已重置 {reset_count} 个失败问题的状态"
            self.logger.info(message)
            
            return {
                'success': True,
                'message': message,
                'reset_count': reset_count
            }
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"重置失败问题状态失败: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg,
                'reset_count': 0
            }
    
    def switch_api_mode(self, use_mock: bool) -> Dict:
        """
        切换API模式
        
        Args:
            use_mock: 是否使用Mock API
            
        Returns:
            切换结果
        """
        try:
            old_mode = 'mock' if self._is_using_mock_api() else 'external'
            
            # 注意：这里只是更新内存中的统计，真正的配置切换需要重启应用或环境变量
            self.classification_stats['use_mock'] = use_mock
            new_mode = 'mock' if use_mock else 'external'
            
            message = f"API模式已从 {old_mode} 切换到 {new_mode}"
            self.logger.info(message)
            
            return {
                'success': True,
                'message': message,
                'old_mode': old_mode,
                'new_mode': new_mode,
                'note': '生产环境下需要通过环境变量 USE_MOCK_CLASSIFICATION 进行配置'
            }
            
        except Exception as e:
            error_msg = f"切换API模式失败: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'message': error_msg
            }

    @classmethod
    def get_all_classifications(cls) -> List[Dict]:
        """获取所有分类列表"""
        try:
            # 从数据库获取所有已分类的问题的分类信息
            classifications_query = db.session.query(
                Question.classification.label('name'),
                func.count(Question.id).label('count')
            ).filter(
                Question.classification.isnot(None),
                Question.classification != ''
            ).group_by(Question.classification).all()

            classifications = []
            for classification, count in classifications_query:
                classifications.append({
                    'id': len(classifications) + 1,
                    'name': classification,
                    'count': count,
                    'description': f'{classification}相关问题',
                    'created_at': datetime.utcnow().isoformat()
                })

            # 如果没有分类数据，返回默认分类
            if not classifications:
                default_classifications = [
                    {'id': 1, 'name': '产品使用', 'count': 0, 'description': '产品使用相关问题'},
                    {'id': 2, 'name': '功能建议', 'count': 0, 'description': '功能建议相关问题'},
                    {'id': 3, 'name': '技术支持', 'count': 0, 'description': '技术支持相关问题'},
                    {'id': 4, 'name': '其他', 'count': 0, 'description': '其他类型问题'}
                ]
                return default_classifications

            return classifications

        except Exception as e:
            logging.getLogger(__name__).error(f"获取分类列表失败: {str(e)}")
            # 返回默认分类作为备选
            return [
                {'id': 1, 'name': '产品使用', 'count': 0, 'description': '产品使用相关问题'},
                {'id': 2, 'name': '功能建议', 'count': 0, 'description': '功能建议相关问题'},
                {'id': 3, 'name': '技术支持', 'count': 0, 'description': '技术支持相关问题'},
                {'id': 4, 'name': '其他', 'count': 0, 'description': '其他类型问题'}
            ]

    @classmethod
    def get_classifications_with_count(cls, time_range: str = 'all') -> List[Dict]:
        """获取带统计数量的分类列表"""
        try:
            # 构建时间过滤条件
            query = db.session.query(
                Question.classification.label('name'),
                func.count(Question.id).label('count')
            ).filter(
                Question.classification.isnot(None),
                Question.classification != ''
            )

            # 根据时间范围过滤
            if time_range == 'week':
                start_date = datetime.utcnow() - timedelta(days=7)
                query = query.filter(Question.created_at >= start_date)
            elif time_range == 'month':
                start_date = datetime.utcnow() - timedelta(days=30)
                query = query.filter(Question.created_at >= start_date)
            elif time_range == 'today':
                start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(Question.created_at >= start_date)

            classifications_query = query.group_by(Question.classification).order_by(func.count(Question.id).desc()).all()

            classifications = []
            total_count = sum(count for _, count in classifications_query)

            for idx, (classification, count) in enumerate(classifications_query):
                percentage = (count / total_count * 100) if total_count > 0 else 0
                classifications.append({
                    'id': idx + 1,
                    'name': classification,
                    'count': count,
                    'percentage': round(percentage, 2),
                    'description': f'{classification}相关问题',
                    'time_range': time_range
                })

            # 如果没有数据，返回空列表而不是默认数据
            return classifications

        except Exception as e:
            logging.getLogger(__name__).error(f"获取分类统计失败: {str(e)}")
            return []

    @classmethod
    def get_classifications_for_recent_period(cls, days: int = 7) -> List[Tuple[str, int]]:
        """获取最近指定天数内的分类统计"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            classifications_query = db.session.query(
                Question.classification.label('name'),
                func.count(Question.id).label('count')
            ).filter(
                Question.classification.isnot(None),
                Question.classification != '',
                Question.created_at >= start_date
            ).group_by(Question.classification).order_by(func.count(Question.id).desc()).all()

            # 返回元组列表 (分类名, 数量)
            return [(classification, count) for classification, count in classifications_query]

        except Exception as e:
            logging.getLogger(__name__).error(f"获取最近{days}天分类统计失败: {str(e)}")
            return []


# 创建全局分类服务实例
classification_service = ClassificationService()