#!/usr/bin/env python3
"""
检查数据库中的实际数据状态
"""

import os
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

def get_week_start():
    """获取本周开始时间（周一00:00:00）"""
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def get_db_connection():
    """获取数据库连接"""
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
    
    if database_url.startswith('postgresql://'):
        url_parts = database_url.replace('postgresql://', '').split('@')
        user_pass = url_parts[0].split(':')
        host_port_db = url_parts[1].split('/')
        host_port = host_port_db[0].split(':')
        
        return psycopg2.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=host_port_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )

def check_actual_data():
    """检查数据库中的实际数据状态"""
    week_start = get_week_start()
    print(f"=== 检查数据库实际状态 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 检查questions表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_created_this_week = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            questions_sendtime_this_week = cur.fetchone()['count']
            
            print(f"1. questions表:")
            print(f"   - created_at本周: {questions_created_this_week} 条")
            print(f"   - sendmessagetime本周: {questions_sendtime_this_week} 条")
            
            # 2. 检查answers表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE created_at >= %s
            """, (week_start,))
            answers_created_this_week = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE answer_time >= %s
            """, (week_start,))
            answers_time_this_week = cur.fetchone()['count']
            
            print(f"2. answers表:")
            print(f"   - created_at本周: {answers_created_this_week} 条")
            print(f"   - answer_time本周: {answers_time_this_week} 条")
            
            # 3. 检查scores表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM scores
                WHERE created_at >= %s
            """, (week_start,))
            scores_this_week = cur.fetchone()['count']
            
            print(f"3. scores表:")
            print(f"   - created_at本周: {scores_this_week} 条")
            
            # 4. 检查各个状态的问题数量
            cur.execute("""
                SELECT 
                    processing_status,
                    COUNT(*) as count
                FROM questions
                WHERE sendmessagetime >= %s
                GROUP BY processing_status
                ORDER BY processing_status
            """, (week_start,))
            
            status_counts = cur.fetchall()
            print(f"4. 问题处理状态分布:")
            for status in status_counts:
                print(f"   - {status['processing_status']}: {status['count']} 条")
            
            # 5. 检查分类状态
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
                AND (classification IS NULL OR classification = '')
            """, (week_start,))
            unclassified_count = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
                AND classification IS NOT NULL 
                AND classification != ''
            """, (week_start,))
            classified_count = cur.fetchone()['count']
            
            print(f"5. 分类状态:")
            print(f"   - 未分类: {unclassified_count} 条")
            print(f"   - 已分类: {classified_count} 条")
            
            # 6. 检查竞品答案
            cur.execute("""
                SELECT 
                    assistant_type,
                    COUNT(*) as count
                FROM answers a
                JOIN questions q ON a.question_business_id = q.business_id
                WHERE q.sendmessagetime >= %s
                AND a.assistant_type IN ('doubao', 'xiaotian')
                GROUP BY assistant_type
            """, (week_start,))
            
            competitor_answers = cur.fetchall()
            print(f"6. 竞品答案:")
            total_competitor = 0
            for answer in competitor_answers:
                print(f"   - {answer['assistant_type']}: {answer['count']} 条")
                total_competitor += answer['count']
            print(f"   - 总计: {total_competitor} 条")
            
            # 7. 检查评分状态
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers a
                JOIN questions q ON a.question_business_id = q.business_id
                WHERE q.sendmessagetime >= %s
                AND a.is_scored = true
            """, (week_start,))
            scored_answers = cur.fetchone()['count']
            
            print(f"7. 评分状态:")
            print(f"   - 已评分答案: {scored_answers} 条")
            
            # 8. 总结
            print(f"\n=== 总结 ===")
            if (questions_sendtime_this_week == 0 and answers_time_this_week == 0 and 
                scores_this_week == 0):
                print("✅ 数据库中确实没有本周数据")
                print("❓ 前端显示的数据可能是缓存问题")
            else:
                print("⚠️  数据库中仍有本周数据:")
                print(f"   - 问题: {questions_sendtime_this_week} 条")
                print(f"   - 答案: {answers_time_this_week} 条") 
                print(f"   - 评分: {scores_this_week} 条")
                print("需要进一步清理")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    check_actual_data()
