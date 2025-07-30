#!/usr/bin/env python3
"""
添加示例评分数据脚本
为现有的答案添加有效的评分数据，用于大屏展示测试
"""

import sys
import os
import random
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.answer import Answer
from app.models.score import Score
from app.utils.database import db

def add_sample_scores():
    """为现有答案添加示例评分数据"""
    app = create_app()
    
    with app.app_context():
        # 获取没有评分的答案
        unscored_answers = db.session.query(Answer).filter(
            Answer.is_scored == False
        ).limit(100).all()
        
        print(f"找到 {len(unscored_answers)} 个未评分的答案")
        
        if not unscored_answers:
            print("没有找到未评分的答案，退出")
            return
        
        # 为每个答案添加评分
        added_count = 0
        for answer in unscored_answers:
            try:
                # 根据模型类型生成不同的评分范围
                if answer.assistant_type == 'doubao':
                    base_score = random.uniform(3.5, 4.5)  # 豆包模型 3.5-4.5分
                elif answer.assistant_type == 'xiaotian':
                    base_score = random.uniform(3.0, 4.0)  # 小天模型 3.0-4.0分
                elif answer.assistant_type == 'original':
                    base_score = random.uniform(4.0, 5.0)  # 原始模型 4.0-5.0分
                else:
                    base_score = random.uniform(3.0, 4.5)  # 其他模型 3.0-4.5分
                
                # 生成5个维度的评分（在基础分附近波动）
                scores = []
                for i in range(5):
                    score = base_score + random.uniform(-0.5, 0.5)
                    score = max(1, min(5, score))  # 确保在1-5范围内
                    scores.append(int(round(score)))
                
                # 计算平均分
                avg_score = sum(scores) / len(scores)
                
                # 创建评分记录
                score_record = Score(
                    answer_id=answer.id,
                    score_1=scores[0],
                    score_2=scores[1],
                    score_3=scores[2],
                    score_4=scores[3],
                    score_5=scores[4],
                    dimension_1_name="相关性",
                    dimension_2_name="准确性",
                    dimension_3_name="完整性",
                    dimension_4_name="清晰度",
                    dimension_5_name="有用性",
                    average_score=round(avg_score, 2),
                    comment=f"系统自动评分 - {answer.assistant_type}模型",
                    rated_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))  # 随机时间
                )
                
                db.session.add(score_record)
                
                # 更新答案的评分状态
                answer.is_scored = True
                
                added_count += 1
                
                if added_count % 20 == 0:
                    print(f"已添加 {added_count} 条评分...")
                    
            except Exception as e:
                print(f"为答案 {answer.id} 添加评分失败: {str(e)}")
                continue
        
        # 提交所有更改
        try:
            db.session.commit()
            print(f"✅ 成功添加 {added_count} 条评分数据")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 提交评分数据失败: {str(e)}")

if __name__ == '__main__':
    add_sample_scores()
