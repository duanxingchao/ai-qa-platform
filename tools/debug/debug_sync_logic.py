#!/usr/bin/env python3
"""
调试同步逻辑脚本
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
    
    # 解析数据库URL
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
    else:
        return psycopg2.connect(
            host="localhost",
            port="5432",
            database="ai_qa_platform",
            user="postgres",
            password="l69jjd9n"
        )

def debug_sync_logic():
    """调试同步逻辑"""
    week_start = get_week_start()
    print(f"=== 同步逻辑调试 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 检查questions表中最后同步时间
            cur.execute("""
                SELECT sendmessagetime 
                FROM questions 
                WHERE sendmessagetime <= NOW()
                ORDER BY sendmessagetime DESC 
                LIMIT 1
            """)
            last_sync_result = cur.fetchone()
            last_sync_time = last_sync_result['sendmessagetime'] if last_sync_result else None
            print(f"1. 当前最后同步时间: {last_sync_time}")
            
            # 2. 检查table1中本周数据量
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime >= %s
            """, (week_start,))
            this_week_table1_count = cur.fetchone()['count']
            print(f"2. table1中本周数据量: {this_week_table1_count}")
            
            # 3. 检查table1中从last_sync_time到现在的数据量
            if last_sync_time:
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM table1
                    WHERE query IS NOT NULL 
                    AND query != '' 
                    AND TRIM(query) != ''
                    AND sendmessagetime > %s
                """, (last_sync_time,))
                new_data_count = cur.fetchone()['count']
                print(f"3. table1中从最后同步时间到现在的数据量: {new_data_count}")
                
                # 4. 检查这些新数据中有多少是本周的
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM table1
                    WHERE query IS NOT NULL 
                    AND query != '' 
                    AND TRIM(query) != ''
                    AND sendmessagetime > %s
                    AND sendmessagetime >= %s
                """, (last_sync_time, week_start))
                new_this_week_count = cur.fetchone()['count']
                print(f"4. 其中本周的数据量: {new_this_week_count}")
                
                # 5. 检查这些新数据中有多少是本周之前的
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM table1
                    WHERE query IS NOT NULL 
                    AND query != '' 
                    AND TRIM(query) != ''
                    AND sendmessagetime > %s
                    AND sendmessagetime < %s
                """, (last_sync_time, week_start))
                new_before_this_week_count = cur.fetchone()['count']
                print(f"5. 其中本周之前的数据量: {new_before_this_week_count}")
                
                # 6. 显示时间范围分析
                if new_before_this_week_count > 0:
                    cur.execute("""
                        SELECT 
                            MIN(sendmessagetime) as earliest,
                            MAX(sendmessagetime) as latest
                        FROM table1
                        WHERE query IS NOT NULL 
                        AND query != '' 
                        AND TRIM(query) != ''
                        AND sendmessagetime > %s
                        AND sendmessagetime < %s
                    """, (last_sync_time, week_start))
                    time_range = cur.fetchone()
                    print(f"6. 本周之前数据的时间范围: {time_range['earliest']} 到 {time_range['latest']}")
            else:
                print("3. 没有最后同步时间，将进行全量同步")
            
            # 7. 检查questions表中本周数据量
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            this_week_questions_count = cur.fetchone()['count']
            print(f"7. questions表中本周数据量: {this_week_questions_count}")
            
            # 8. 分析问题
            print(f"\n=== 问题分析 ===")
            if last_sync_time and last_sync_time < week_start:
                print(f"⚠️  问题：最后同步时间({last_sync_time})早于本周开始时间({week_start})")
                print(f"   这意味着系统会同步从{last_sync_time}到现在的所有数据，包括非本周数据")
                if new_before_this_week_count > 0:
                    print(f"   实际上有{new_before_this_week_count}条非本周数据会被同步")
            else:
                print("✅ 同步时间范围正常")
                
    except Exception as e:
        print(f"❌ 调试失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_sync_logic()
