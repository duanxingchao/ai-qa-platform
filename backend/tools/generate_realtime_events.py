#!/usr/bin/env python3
"""
生成更多实时事件数据的脚本
用于测试大屏展示的双排数据流效果
"""

import sys
import os
import random
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.utils.database import db

def generate_realtime_events():
    """生成更多实时事件数据"""
    app = create_app()
    
    with app.app_context():
        # 获取最近的一些数据
        recent_questions = db.session.query(Question).order_by(Question.created_at.desc()).limit(20).all()
        recent_answers = db.session.query(Answer).order_by(Answer.created_at.desc()).limit(20).all()
        recent_scores = db.session.query(Score).order_by(Score.rated_at.desc()).limit(20).all()
        
        events = []
        
        # 生成问题事件
        for i, question in enumerate(recent_questions):
            time_offset = timedelta(minutes=random.randint(1, 60))
            event_time = (datetime.now() - time_offset).strftime("%H:%M:%S")
            
            events.append({
                "time": event_time,
                "type": "question",
                "icon": "❓",
                "message": f"新问题: {question.query[:30]}..." if len(question.query) > 30 else f"新问题: {question.query}"
            })
        
        # 生成答案事件
        for i, answer in enumerate(recent_answers):
            time_offset = timedelta(minutes=random.randint(1, 60))
            event_time = (datetime.now() - time_offset).strftime("%H:%M:%S")
            
            model_name = {
                'doubao': '豆包',
                'xiaotian': '小天',
                'original': '原始'
            }.get(answer.assistant_type, answer.assistant_type)
            
            events.append({
                "time": event_time,
                "type": "answer",
                "icon": "💬",
                "message": f"{model_name}模型生成答案完成"
            })
        
        # 生成评分事件
        for i, score in enumerate(recent_scores):
            time_offset = timedelta(minutes=random.randint(1, 60))
            event_time = (datetime.now() - time_offset).strftime("%H:%M:%S")
            
            score_value = score.average_score if score.average_score is not None else 0.0
            events.append({
                "time": event_time,
                "type": "score",
                "icon": "⭐",
                "message": f"答案评分完成: {score_value:.1f}分"
            })
        
        # 添加一些系统事件
        system_events = [
            {"icon": "🔄", "message": "数据同步完成"},
            {"icon": "🤖", "message": "AI模型性能分析完成"},
            {"icon": "📊", "message": "统计数据更新完成"},
            {"icon": "🔍", "message": "问题分类处理完成"},
            {"icon": "✅", "message": "质量检查通过"},
            {"icon": "📈", "message": "趋势分析更新"},
            {"icon": "🎯", "message": "热门分类统计完成"},
            {"icon": "🔔", "message": "实时监控正常"},
            {"icon": "💾", "message": "数据备份完成"},
            {"icon": "🚀", "message": "性能优化完成"}
        ]
        
        for i in range(15):
            time_offset = timedelta(minutes=random.randint(1, 60))
            event_time = (datetime.now() - time_offset).strftime("%H:%M:%S")
            system_event = random.choice(system_events)
            
            events.append({
                "time": event_time,
                "type": "system",
                "icon": system_event["icon"],
                "message": system_event["message"]
            })
        
        # 按时间排序
        events.sort(key=lambda x: x["time"], reverse=True)
        
        print(f"生成了 {len(events)} 个实时事件")
        
        # 输出前10个事件作为示例
        print("\n前10个事件示例:")
        for i, event in enumerate(events[:10]):
            print(f"  {i+1}. [{event['time']}] {event['icon']} {event['message']}")
        
        return events

if __name__ == '__main__':
    generate_realtime_events()
