#!/usr/bin/env python3
"""
彻底清理本周数据
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

def thorough_cleanup():
    """彻底清理本周数据"""
    week_start = get_week_start()
    print(f"=== 彻底清理本周数据 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 先检查当前状态
            print(f"\n=== 清理前状态检查 ===")
            
            # 检查questions表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            questions_before = cur.fetchone()['count']
            print(f"questions表(sendmessagetime本周): {questions_before} 条")
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_created_before = cur.fetchone()['count']
            print(f"questions表(created_at本周): {questions_created_before} 条")
            
            # 检查answers表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE answer_time >= %s
            """, (week_start,))
            answers_before = cur.fetchone()['count']
            print(f"answers表(answer_time本周): {answers_before} 条")
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE created_at >= %s
            """, (week_start,))
            answers_created_before = cur.fetchone()['count']
            print(f"answers表(created_at本周): {answers_created_before} 条")
            
            # 检查scores表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM scores
                WHERE rated_at >= %s
            """, (week_start,))
            scores_before = cur.fetchone()['count']
            print(f"scores表(rated_at本周): {scores_before} 条")
            
            # 2. 开始清理
            print(f"\n=== 开始彻底清理 ===")
            
            # 获取本周问题的business_id列表
            cur.execute("""
                SELECT business_id 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            week_business_ids = [row['business_id'] for row in cur.fetchall()]
            print(f"本周问题business_id数量: {len(week_business_ids)}")
            
            if week_business_ids:
                # 删除与本周问题相关的评分数据
                cur.execute("""
                    DELETE FROM scores 
                    WHERE answer_id IN (
                        SELECT a.id FROM answers a 
                        WHERE a.question_business_id = ANY(%s)
                    )
                """, (week_business_ids,))
                deleted_scores_related = cur.rowcount
                print(f"删除与本周问题相关的评分数据: {deleted_scores_related} 条")
                
                # 删除与本周问题相关的答案数据
                cur.execute("""
                    DELETE FROM answers 
                    WHERE question_business_id = ANY(%s)
                """, (week_business_ids,))
                deleted_answers_related = cur.rowcount
                print(f"删除与本周问题相关的答案数据: {deleted_answers_related} 条")
            
            # 删除本周问题数据（基于sendmessagetime）
            cur.execute("""
                DELETE FROM questions 
                WHERE sendmessagetime >= %s
            """, (week_start,))
            deleted_questions_sendtime = cur.rowcount
            print(f"删除本周问题数据(sendmessagetime): {deleted_questions_sendtime} 条")
            
            # 删除本周问题数据（基于created_at）
            cur.execute("""
                DELETE FROM questions 
                WHERE created_at >= %s
            """, (week_start,))
            deleted_questions_created = cur.rowcount
            print(f"删除本周问题数据(created_at): {deleted_questions_created} 条")
            
            # 删除本周答案数据（基于answer_time）
            cur.execute("""
                DELETE FROM answers 
                WHERE answer_time >= %s
            """, (week_start,))
            deleted_answers_time = cur.rowcount
            print(f"删除本周答案数据(answer_time): {deleted_answers_time} 条")
            
            # 删除本周答案数据（基于created_at）
            cur.execute("""
                DELETE FROM answers 
                WHERE created_at >= %s
            """, (week_start,))
            deleted_answers_created = cur.rowcount
            print(f"删除本周答案数据(created_at): {deleted_answers_created} 条")
            
            # 删除本周评分数据（基于rated_at）
            cur.execute("""
                DELETE FROM scores 
                WHERE rated_at >= %s
            """, (week_start,))
            deleted_scores_time = cur.rowcount
            print(f"删除本周评分数据(rated_at): {deleted_scores_time} 条")
            
            # 提交事务
            conn.commit()
            print(f"✅ 所有删除操作已提交")
            
            # 3. 验证清理结果
            print(f"\n=== 清理后状态验证 ===")
            
            # 验证questions表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            questions_after_sendtime = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_after_created = cur.fetchone()['count']
            
            print(f"questions表(sendmessagetime本周): {questions_after_sendtime} 条")
            print(f"questions表(created_at本周): {questions_after_created} 条")
            
            # 验证answers表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE answer_time >= %s
            """, (week_start,))
            answers_after_time = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE created_at >= %s
            """, (week_start,))
            answers_after_created = cur.fetchone()['count']
            
            print(f"answers表(answer_time本周): {answers_after_time} 条")
            print(f"answers表(created_at本周): {answers_after_created} 条")
            
            # 验证scores表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM scores
                WHERE rated_at >= %s
            """, (week_start,))
            scores_after = cur.fetchone()['count']
            print(f"scores表(rated_at本周): {scores_after} 条")
            
            # 4. 最终结果
            print(f"\n=== 最终清理结果 ===")
            if (questions_after_sendtime == 0 and questions_after_created == 0 and
                answers_after_time == 0 and answers_after_created == 0 and
                scores_after == 0):
                print("🎉 彻底清理成功！所有本周数据已完全删除")
            else:
                print("⚠️  仍有残留数据:")
                if questions_after_sendtime > 0 or questions_after_created > 0:
                    print(f"   - questions表仍有数据")
                if answers_after_time > 0 or answers_after_created > 0:
                    print(f"   - answers表仍有数据")
                if scores_after > 0:
                    print(f"   - scores表仍有数据")
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    thorough_cleanup()
