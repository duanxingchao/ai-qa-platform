#!/usr/bin/env python3
"""
删除本周的所有问题数据和相关数据
包括：questions、answers、scores、review_status 表中的相关记录
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append('/home/devbox/project/backend')

from app.utils.database import get_db_session
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.review import ReviewStatus
from app.config import Config

def get_week_start():
    """获取本周开始时间（周一00:00:00）"""
    now = datetime.now()
    # 计算本周一的日期
    days_since_monday = now.weekday()  # 0=Monday, 6=Sunday
    week_start = now - timedelta(days=days_since_monday)
    # 设置为当天的00:00:00
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return week_start

def delete_this_week_data():
    """删除本周的所有数据"""
    week_start = get_week_start()
    print(f"=== 删除本周数据 ===")
    print(f"本周开始时间: {week_start}")
    print(f"当前时间: {datetime.now()}")
    
    # 确认操作
    confirm = input("\n⚠️  警告：此操作将删除本周的所有数据，包括问题、答案、评分和审核状态！\n是否继续？(输入 'YES' 确认): ")
    if confirm != 'YES':
        print("操作已取消")
        return
    
    db = get_db_session(Config.DATABASE_URL)
    try:
        # 1. 查询本周的问题数量
        this_week_questions = db.query(Question).filter(
            Question.created_at >= week_start
        ).all()
        
        question_ids = [q.id for q in this_week_questions]
        question_business_ids = [q.business_id for q in this_week_questions]
        
        print(f"\n📊 数据统计:")
        print(f"本周问题数量: {len(this_week_questions)}")
        
        if not this_week_questions:
            print("没有找到本周的问题数据，无需删除")
            return
        
        # 2. 查询相关的答案数量
        this_week_answers = db.query(Answer).filter(
            Answer.question_business_id.in_(question_business_ids)
        ).all()
        print(f"相关答案数量: {len(this_week_answers)}")
        
        # 3. 查询相关的评分数量
        answer_ids = [a.id for a in this_week_answers]
        this_week_scores = []
        if answer_ids:
            this_week_scores = db.query(Score).filter(
                Score.answer_id.in_(answer_ids)
            ).all()
        print(f"相关评分数量: {len(this_week_scores)}")
        
        # 4. 查询相关的审核状态数量
        this_week_reviews = db.query(ReviewStatus).filter(
            ReviewStatus.question_business_id.in_(question_business_ids)
        ).all()
        print(f"相关审核状态数量: {len(this_week_reviews)}")
        
        # 最后确认
        total_records = len(this_week_questions) + len(this_week_answers) + len(this_week_scores) + len(this_week_reviews)
        print(f"\n总计将删除 {total_records} 条记录")
        
        final_confirm = input(f"\n最后确认：是否删除这 {total_records} 条记录？(输入 'DELETE' 确认): ")
        if final_confirm != 'DELETE':
            print("操作已取消")
            return
        
        print("\n🗑️  开始删除数据...")
        
        # 按照外键依赖顺序删除
        deleted_counts = {}
        
        # 1. 删除评分记录
        if this_week_scores:
            for score in this_week_scores:
                db.delete(score)
            deleted_counts['scores'] = len(this_week_scores)
            print(f"✅ 删除评分记录: {len(this_week_scores)} 条")
        
        # 2. 删除审核状态记录
        if this_week_reviews:
            for review in this_week_reviews:
                db.delete(review)
            deleted_counts['reviews'] = len(this_week_reviews)
            print(f"✅ 删除审核状态记录: {len(this_week_reviews)} 条")
        
        # 3. 删除答案记录
        if this_week_answers:
            for answer in this_week_answers:
                db.delete(answer)
            deleted_counts['answers'] = len(this_week_answers)
            print(f"✅ 删除答案记录: {len(this_week_answers)} 条")
        
        # 4. 删除问题记录
        for question in this_week_questions:
            db.delete(question)
        deleted_counts['questions'] = len(this_week_questions)
        print(f"✅ 删除问题记录: {len(this_week_questions)} 条")
        
        # 提交事务
        db.commit()
        
        print(f"\n🎉 删除完成！")
        print(f"删除统计:")
        for table, count in deleted_counts.items():
            print(f"  - {table}: {count} 条")
        
        print(f"\n总计删除: {sum(deleted_counts.values())} 条记录")
        
    except Exception as e:
        print(f"\n❌ 删除过程中出现错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_deletion():
    """验证删除结果"""
    week_start = get_week_start()
    print(f"\n🔍 验证删除结果...")
    
    db = get_db_session(Config.DATABASE_URL)
    try:
        # 检查各表中本周的数据
        remaining_questions = db.query(Question).filter(
            Question.created_at >= week_start
        ).count()
        
        print(f"剩余本周问题数量: {remaining_questions}")
        
        if remaining_questions == 0:
            print("✅ 验证通过：本周数据已全部删除")
        else:
            print("⚠️  警告：仍有本周数据残留")
            
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        delete_this_week_data()
        verify_deletion()
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n❌ 脚本执行失败: {e}")
        sys.exit(1)
