#!/usr/bin/env python3
"""
调试竞品跑测统计的脚本
"""
import sys
import os
sys.path.append('/home/devbox/project/backend')

from datetime import datetime, timedelta
from app.utils.database import db
from app.models.question import Question
from app.models.answer import Answer
from app import create_app

def debug_competitor_stats():
    """调试竞品跑测统计"""
    app = create_app()
    
    with app.app_context():
        # 计算本周开始时间
        now = datetime.now()
        days_since_monday = now.weekday()
        week_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        
        print(f"=== 竞品跑测统计调试 ===")
        print(f"当前时间: {now}")
        print(f"本周开始时间: {week_start}")
        print()
        
        # 1. 本周问题总数
        total_questions = db.session.query(Question).filter(
            Question.created_at >= week_start
        ).count()
        print(f"1. 本周问题总数: {total_questions}")
        
        # 2. 本周已分类问题数
        classified_questions = db.session.query(Question).filter(
            Question.created_at >= week_start,
            Question.classification.isnot(None),
            Question.classification != ''
        ).count()
        print(f"2. 本周已分类问题数: {classified_questions}")
        
        # 3. 本周竞品答案数（旧逻辑：只限制问题时间）
        old_logic_answers = db.session.query(Answer).join(
            Question, Answer.question_business_id == Question.business_id
        ).filter(
            Question.created_at >= week_start,
            Answer.assistant_type.in_(['doubao', 'xiaotian'])
        ).count()
        print(f"3. 竞品答案数（旧逻辑-只限制问题时间）: {old_logic_answers}")
        
        # 4. 本周竞品答案数（新逻辑：同时限制问题和答案时间）
        new_logic_answers = db.session.query(Answer).join(
            Question, Answer.question_business_id == Question.business_id
        ).filter(
            Question.created_at >= week_start,
            Answer.created_at >= week_start,
            Answer.assistant_type.in_(['doubao', 'xiaotian'])
        ).count()
        print(f"4. 竞品答案数（新逻辑-同时限制问题和答案时间）: {new_logic_answers}")
        
        # 5. 计算百分比
        expected_answers = classified_questions * 2
        old_percentage = (old_logic_answers / expected_answers * 100) if expected_answers > 0 else 0
        new_percentage = (new_logic_answers / expected_answers * 100) if expected_answers > 0 else 0
        
        print()
        print(f"=== 百分比计算 ===")
        print(f"期望竞品答案数 (已分类问题数×2): {expected_answers}")
        print(f"旧逻辑百分比: {old_percentage:.1f}%")
        print(f"新逻辑百分比: {new_percentage:.1f}%")
        
        # 6. 分析历史数据
        print()
        print(f"=== 历史数据分析 ===")
        
        # 查看所有竞品答案的创建时间分布
        all_competitor_answers = db.session.query(Answer).filter(
            Answer.assistant_type.in_(['doubao', 'xiaotian'])
        ).all()
        
        before_week = 0
        during_week = 0
        
        for answer in all_competitor_answers:
            if answer.created_at < week_start:
                before_week += 1
            else:
                during_week += 1
        
        print(f"本周之前创建的竞品答案: {before_week}")
        print(f"本周创建的竞品答案: {during_week}")
        print(f"总竞品答案数: {before_week + during_week}")

if __name__ == "__main__":
    debug_competitor_stats()
