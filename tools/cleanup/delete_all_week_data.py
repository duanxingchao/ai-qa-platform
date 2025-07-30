#!/usr/bin/env python3
"""
删除本周内所有表中的数据
"""

import sys
import os
sys.path.append('backend')

from datetime import datetime, timedelta
from app import create_app
from app.utils.database import db
from app.models import Question, Answer, Score, ReviewStatus

def get_week_start():
    """获取本周开始时间（周一00:00:00）"""
    now = datetime.utcnow()
    days_since_monday = now.weekday()  # 0=周一, 6=周日
    week_start = now - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return week_start

def delete_week_data():
    """删除本周的所有数据"""
    app = create_app()
    
    with app.app_context():
        week_start = get_week_start()
        print(f"🗑️  开始删除本周数据（从 {week_start} 开始）...")
        
        try:
            # 1. 删除本周的评分数据
            week_scores = db.session.query(Score).filter(
                Score.rated_at >= week_start
            )
            score_count = week_scores.count()
            week_scores.delete(synchronize_session=False)
            print(f"✅ 删除评分数据: {score_count} 条")
            
            # 2. 删除本周的答案数据
            week_answers = db.session.query(Answer).filter(
                Answer.created_at >= week_start
            )
            answer_count = week_answers.count()
            week_answers.delete(synchronize_session=False)
            print(f"✅ 删除答案数据: {answer_count} 条")
            
            # 3. 删除本周的审核状态数据（先获取要删除的business_id列表）
            week_question_business_ids = db.session.query(Question.business_id).filter(
                Question.created_at >= week_start
            ).subquery()

            week_reviews = db.session.query(ReviewStatus).filter(
                ReviewStatus.question_business_id.in_(
                    db.session.query(week_question_business_ids.c.business_id)
                )
            )
            review_count = week_reviews.count()
            week_reviews.delete(synchronize_session=False)
            print(f"✅ 删除审核状态数据: {review_count} 条")
            
            # 4. 删除本周的问题数据
            week_questions = db.session.query(Question).filter(
                Question.created_at >= week_start
            )
            question_count = week_questions.count()
            week_questions.delete(synchronize_session=False)
            print(f"✅ 删除问题数据: {question_count} 条")
            
            # 提交所有删除操作
            db.session.commit()
            
            print(f"\n🎉 本周数据删除完成！")
            print(f"📊 删除统计:")
            print(f"   - 问题: {question_count} 条")
            print(f"   - 答案: {answer_count} 条")
            print(f"   - 评分: {score_count} 条")
            print(f"   - 审核: {review_count} 条")
            print(f"   - 总计: {question_count + answer_count + score_count + review_count} 条")
            
            # 验证删除结果
            print(f"\n🔍 验证删除结果:")
            remaining_questions = db.session.query(Question).filter(Question.created_at >= week_start).count()
            remaining_answers = db.session.query(Answer).filter(Answer.created_at >= week_start).count()
            remaining_scores = db.session.query(Score).filter(Score.rated_at >= week_start).count()
            
            print(f"   - 剩余问题: {remaining_questions} 条")
            print(f"   - 剩余答案: {remaining_answers} 条")
            print(f"   - 剩余评分: {remaining_scores} 条")
            
            if remaining_questions == 0 and remaining_answers == 0 and remaining_scores == 0:
                print("✅ 本周数据已完全清空！")
            else:
                print("⚠️  仍有部分数据未删除")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ 删除失败: {str(e)}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("🗑️  本周数据清理工具")
    print("=" * 50)
    
    # 确认操作
    week_start = get_week_start()
    print(f"⚠️  即将删除从 {week_start} 开始的本周所有数据")
    print("📋 包括以下表的数据:")
    print("   - questions (问题表)")
    print("   - answers (答案表)")
    print("   - scores (评分表)")
    print("   - review_status (审核状态表)")
    
    confirm = input("\n❓ 确认删除？(输入 'YES' 确认): ")
    
    if confirm == "YES":
        delete_week_data()
    else:
        print("❌ 操作已取消")
