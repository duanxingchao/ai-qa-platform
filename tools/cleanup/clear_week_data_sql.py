#!/usr/bin/env python3
"""
使用SQL直接清理本周数据
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
    # 从环境变量或配置中获取数据库连接信息
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')

    # 解析数据库URL
    if database_url.startswith('postgresql://'):
        # 简单解析URL
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
    else:
        # 默认连接参数
        return psycopg2.connect(
            host="localhost",
            port="5432",
            database="ai_qa_platform",
            user="postgres",
            password="l69jjd9n"
        )

def clear_this_week_data():
    """彻底清理本周的所有数据"""
    week_start = get_week_start()
    print(f"彻底清理本周数据，本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 先查询本周问题的business_id列表
            cur.execute("""
                SELECT business_id FROM questions 
                WHERE created_at >= %s
            """, (week_start,))
            week_business_ids = [row['business_id'] for row in cur.fetchall()]
            print(f"本周问题business_id数量: {len(week_business_ids)}")
            
            if week_business_ids:
                # 1. 删除与本周问题相关的所有评分数据
                cur.execute("""
                    DELETE FROM scores 
                    WHERE answer_id IN (
                        SELECT id FROM answers 
                        WHERE question_business_id = ANY(%s)
                    )
                """, (week_business_ids,))
                scores_deleted = cur.rowcount
                print(f"删除与本周问题相关的评分数据: {scores_deleted} 条")
                
                # 2. 删除与本周问题相关的所有答案数据
                cur.execute("""
                    DELETE FROM answers 
                    WHERE question_business_id = ANY(%s)
                """, (week_business_ids,))
                answers_deleted = cur.rowcount
                print(f"删除与本周问题相关的答案数据: {answers_deleted} 条")
                
                # 3. 删除与本周问题相关的审核状态数据
                cur.execute("""
                    DELETE FROM review_status 
                    WHERE question_business_id = ANY(%s)
                """, (week_business_ids,))
                review_deleted = cur.rowcount
                print(f"删除与本周问题相关的审核状态数据: {review_deleted} 条")
            
            # 4. 删除本周的问题数据
            cur.execute("""
                DELETE FROM questions 
                WHERE created_at >= %s
            """, (week_start,))
            questions_deleted = cur.rowcount
            print(f"删除本周问题数据: {questions_deleted} 条")
            
            # 5. 额外清理：删除本周创建的所有评分和答案（防止遗漏）
            cur.execute("""
                DELETE FROM scores 
                WHERE rated_at >= %s
            """, (week_start,))
            extra_scores_deleted = cur.rowcount
            print(f"额外删除本周创建的评分数据: {extra_scores_deleted} 条")
            
            cur.execute("""
                DELETE FROM answers 
                WHERE created_at >= %s
            """, (week_start,))
            extra_answers_deleted = cur.rowcount
            print(f"额外删除本周创建的答案数据: {extra_answers_deleted} 条")
            
            conn.commit()
            print("✅ 本周数据彻底清理完成")
            
            # 验证清理结果
            cur.execute("""
                SELECT COUNT(*) as count FROM questions 
                WHERE created_at >= %s
            """, (week_start,))
            remaining_questions = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count FROM answers 
                WHERE created_at >= %s
            """, (week_start,))
            remaining_answers = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count FROM scores 
                WHERE rated_at >= %s
            """, (week_start,))
            remaining_scores = cur.fetchone()['count']
            
            # 检查是否还有与本周问题相关的数据
            if week_business_ids:
                cur.execute("""
                    SELECT COUNT(*) as count FROM answers 
                    WHERE question_business_id = ANY(%s)
                """, (week_business_ids,))
                remaining_related_answers = cur.fetchone()['count']
                
                cur.execute("""
                    SELECT COUNT(*) as count FROM scores s
                    JOIN answers a ON s.answer_id = a.id
                    WHERE a.question_business_id = ANY(%s)
                """, (week_business_ids,))
                remaining_related_scores = cur.fetchone()['count']
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
        conn.rollback()
        print(f"❌ 清理失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    clear_this_week_data()
