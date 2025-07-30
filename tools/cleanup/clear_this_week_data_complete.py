#!/usr/bin/env python3
"""
彻底清理本周数据脚本
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from app.models.database import Question, Answer, Score, ReviewStatus
    from app.utils.database import get_db_session
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)

def get_week_start():
    """获取本周开始时间（周一00:00:00）"""
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def clear_this_week_data():
    """彻底清理本周的所有数据"""
    week_start = get_week_start()
    print(f"彻底清理本周数据，本周开始时间: {week_start}")
    
    with get_db_session() as session:
        try:
            # 先查询本周问题的business_id列表
            week_questions = session.query(Question.business_id).filter(
                Question.created_at >= week_start
            ).all()
            week_business_ids = [q.business_id for q in week_questions]
            print(f"本周问题business_id数量: {len(week_business_ids)}")
            
            if week_business_ids:
                # 1. 删除与本周问题相关的所有评分数据（不管评分时间）
                scores_deleted = session.query(Score).join(Answer).filter(
                    Answer.question_business_id.in_(week_business_ids)
                ).delete(synchronize_session=False)
                print(f"删除与本周问题相关的评分数据: {scores_deleted} 条")
                
                # 2. 删除与本周问题相关的所有答案数据（不管答案创建时间）
                answers_deleted = session.query(Answer).filter(
                    Answer.question_business_id.in_(week_business_ids)
                ).delete(synchronize_session=False)
                print(f"删除与本周问题相关的答案数据: {answers_deleted} 条")
                
                # 3. 删除与本周问题相关的审核状态数据
                review_deleted = session.query(ReviewStatus).filter(
                    ReviewStatus.question_business_id.in_(week_business_ids)
                ).delete(synchronize_session=False)
                print(f"删除与本周问题相关的审核状态数据: {review_deleted} 条")
            
            # 4. 删除本周的问题数据
            questions_deleted = session.query(Question).filter(
                Question.created_at >= week_start
            ).delete()
            print(f"删除本周问题数据: {questions_deleted} 条")
            
            # 5. 额外清理：删除本周创建的所有评分和答案（防止遗漏）
            extra_scores_deleted = session.query(Score).filter(
                Score.rated_at >= week_start
            ).delete()
            print(f"额外删除本周创建的评分数据: {extra_scores_deleted} 条")
            
            extra_answers_deleted = session.query(Answer).filter(
                Answer.created_at >= week_start
            ).delete()
            print(f"额外删除本周创建的答案数据: {extra_answers_deleted} 条")
            
            session.commit()
            print("✅ 本周数据彻底清理完成")
            
            # 验证清理结果
            remaining_questions = session.query(Question).filter(
                Question.created_at >= week_start
            ).count()
            remaining_answers = session.query(Answer).filter(
                Answer.created_at >= week_start
            ).count()
            remaining_scores = session.query(Score).filter(
                Score.rated_at >= week_start
            ).count()
            
            # 检查是否还有与本周问题相关的数据
            if week_business_ids:
                remaining_related_answers = session.query(Answer).filter(
                    Answer.question_business_id.in_(week_business_ids)
                ).count()
                remaining_related_scores = session.query(Score).join(Answer).filter(
                    Answer.question_business_id.in_(week_business_ids)
                ).count()
            else:
                remaining_related_answers = 0
                remaining_related_scores = 0
            
            print(f"\n验证清理结果:")
            print(f"剩余本周问题: {remaining_questions}")
            print(f"剩余本周答案: {remaining_answers}")
            print(f"剩余本周评分: {remaining_scores}")
            print(f"剩余与本周问题相关的答案: {remaining_related_answers}")
            print(f"剩余与本周问题相关的评分: {remaining_related_scores}")
            
            if (remaining_questions == 0 and remaining_answers == 0 and 
                remaining_scores == 0 and remaining_related_answers == 0 and 
                remaining_related_scores == 0):
                print("🎉 所有本周数据已彻底清理完成！")
            else:
                print("⚠️  仍有部分数据未清理完成")
            
        except Exception as e:
            session.rollback()
            print(f"❌ 清理失败: {e}")
            raise

if __name__ == "__main__":
    clear_this_week_data()
