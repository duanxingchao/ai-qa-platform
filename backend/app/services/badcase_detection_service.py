"""
Badcase检测服务
"""

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.utils.database import db
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.system_config import SystemConfig


class BadcaseDetectionService:
    """Badcase检测服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_badcase_threshold(self) -> float:
        """获取badcase评分阈值"""
        try:
            threshold = SystemConfig.get_config('badcase_score_threshold', 2.5)
            return float(threshold)
        except (ValueError, TypeError):
            self.logger.warning("获取badcase阈值失败，使用默认值2.5")
            return 2.5
    
    def detect_badcase(self, question_business_id: str) -> bool:
        """
        检测问题是否为badcase
        
        Args:
            question_business_id: 问题业务ID
            
        Returns:
            bool: True表示是badcase，False表示不是
        """
        try:
            # 获取配置的阈值
            threshold = self.get_badcase_threshold()
            
            # 获取yoyo模型的答案
            yoyo_answer = db.session.query(Answer).filter_by(
                question_business_id=question_business_id,
                assistant_type='yoyo'
            ).first()
            
            if not yoyo_answer:
                self.logger.debug(f"问题 {question_business_id} 没有找到yoyo答案")
                return False
            
            # 获取评分记录
            score_record = db.session.query(Score).filter_by(
                answer_id=yoyo_answer.id
            ).first()
            
            if not score_record:
                self.logger.debug(f"问题 {question_business_id} 的yoyo答案没有评分记录")
                return False
            
            # 检查五个维度的评分
            low_score_dimensions = []
            dimension_scores = [
                (score_record.dimension_1_name, score_record.score_1),
                (score_record.dimension_2_name, score_record.score_2),
                (score_record.dimension_3_name, score_record.score_3),
                (score_record.dimension_4_name, score_record.score_4),
                (score_record.dimension_5_name, score_record.score_5)
            ]
            
            for dimension_name, score in dimension_scores:
                if dimension_name and score is not None and score < threshold:
                    low_score_dimensions.append({
                        "dimension_name": dimension_name,
                        "score": float(score),
                        "threshold": threshold
                    })
            
            # 更新问题的badcase状态
            question = db.session.query(Question).filter_by(
                business_id=question_business_id
            ).first()
            
            if not question:
                self.logger.error(f"问题 {question_business_id} 不存在")
                return False
            
            is_badcase = len(low_score_dimensions) > 0
            question.is_badcase = is_badcase
            
            if is_badcase:
                question.badcase_detected_at = datetime.utcnow()
                question.badcase_dimensions = json.dumps({
                    "low_score_dimensions": low_score_dimensions,
                    "detection_threshold": threshold,
                    "detected_at": datetime.utcnow().isoformat()
                }, ensure_ascii=False)
                
                # 如果之前不是badcase，重置复核状态
                if question.badcase_review_status != 'pending':
                    question.badcase_review_status = 'pending'
                    question.reviewed_at = None
                
                self.logger.info(
                    f"检测到badcase: {question_business_id}, "
                    f"低分维度: {[d['dimension_name'] for d in low_score_dimensions]}, "
                    f"阈值: {threshold}"
                )
            else:
                # 如果之前是badcase但现在不是，清除相关信息
                if question.is_badcase:
                    question.badcase_detected_at = None
                    question.badcase_dimensions = None
                    question.badcase_review_status = 'pending'
                    question.reviewed_at = None
                
                self.logger.debug(f"问题 {question_business_id} 不是badcase")
            
            question.updated_at = datetime.utcnow()
            db.session.commit()
            
            return is_badcase
            
        except Exception as e:
            self.logger.error(f"检测badcase时出错 {question_business_id}: {str(e)}")
            db.session.rollback()
            return False
    
    def batch_detect_badcases(self, question_business_ids: List[str] = None) -> Dict[str, Any]:
        """
        批量检测badcase
        
        Args:
            question_business_ids: 问题业务ID列表，如果为None则检测所有已评分的问题
            
        Returns:
            dict: 检测结果统计
        """
        try:
            if question_business_ids is None:
                # 获取所有已评分的问题
                questions = db.session.query(Question).filter_by(
                    processing_status='scored'
                ).all()
                question_business_ids = [q.business_id for q in questions]
            
            total_count = len(question_business_ids)
            badcase_count = 0
            success_count = 0
            error_count = 0
            
            self.logger.info(f"开始批量检测badcase，共 {total_count} 个问题")
            
            for business_id in question_business_ids:
                try:
                    is_badcase = self.detect_badcase(business_id)
                    if is_badcase:
                        badcase_count += 1
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"检测问题 {business_id} 时出错: {str(e)}")
                    error_count += 1
            
            result = {
                'total_count': total_count,
                'success_count': success_count,
                'error_count': error_count,
                'badcase_count': badcase_count,
                'badcase_rate': (badcase_count / success_count * 100) if success_count > 0 else 0
            }
            
            self.logger.info(
                f"批量检测完成: 总数={total_count}, 成功={success_count}, "
                f"错误={error_count}, badcase={badcase_count}, "
                f"badcase率={result['badcase_rate']:.2f}%"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"批量检测badcase时出错: {str(e)}")
            return {
                'total_count': 0,
                'success_count': 0,
                'error_count': 1,
                'badcase_count': 0,
                'badcase_rate': 0,
                'error': str(e)
            }
    
    def get_badcase_details(self, question_business_id: str) -> Optional[Dict[str, Any]]:
        """
        获取badcase详细信息
        
        Args:
            question_business_id: 问题业务ID
            
        Returns:
            dict: badcase详细信息，如果不是badcase则返回None
        """
        try:
            question = db.session.query(Question).filter_by(
                business_id=question_business_id
            ).first()
            
            if not question or not question.is_badcase:
                return None
            
            # 解析低分维度信息
            low_score_info = []
            if question.badcase_dimensions:
                try:
                    dimensions_data = json.loads(question.badcase_dimensions)
                    low_score_info = dimensions_data.get('low_score_dimensions', [])
                except json.JSONDecodeError:
                    self.logger.error(f"解析badcase维度信息失败: {question_business_id}")
            
            return {
                'business_id': question.business_id,
                'is_badcase': question.is_badcase,
                'detected_at': question.badcase_detected_at.isoformat() if question.badcase_detected_at else None,
                'review_status': question.badcase_review_status,
                'reviewed_at': question.reviewed_at.isoformat() if question.reviewed_at else None,
                'low_score_dimensions': low_score_info,
                'threshold': self.get_badcase_threshold()
            }
            
        except Exception as e:
            self.logger.error(f"获取badcase详情时出错 {question_business_id}: {str(e)}")
            return None
