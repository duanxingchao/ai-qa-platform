#!/usr/bin/env python3
"""
分析同步逻辑中的问题
"""

import os
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

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

def generate_business_id(pageid, sendmessagetime, query):
    """生成business_id"""
    raw_str = f"{pageid}{sendmessagetime.isoformat() if sendmessagetime else ''}{query}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def analyze_sync_issue():
    """分析同步问题"""
    week_start = get_week_start()
    print(f"=== 分析同步逻辑问题 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 获取最后同步时间
            cur.execute("""
                SELECT sendmessagetime 
                FROM questions 
                WHERE sendmessagetime <= NOW()
                ORDER BY sendmessagetime DESC 
                LIMIT 1
            """)
            last_sync_result = cur.fetchone()
            last_sync_time = last_sync_result['sendmessagetime'] if last_sync_result else None
            actual_since_time = last_sync_time if last_sync_time and last_sync_time >= week_start else week_start
            
            print(f"1. 最后同步时间: {last_sync_time}")
            print(f"2. 实际since_time: {actual_since_time}")
            
            # 2. 获取新逻辑会同步的数据
            cur.execute("""
                SELECT 
                    pageid,
                    sendmessagetime,
                    query
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime > %s
                AND sendmessagetime >= %s
                ORDER BY sendmessagetime ASC
            """, (actual_since_time, week_start))
            
            table1_data = cur.fetchall()
            print(f"3. 新逻辑会同步的table1数据: {len(table1_data)} 条")
            
            # 3. 生成business_id并检查是否已存在
            existing_count = 0
            new_count = 0
            duplicate_examples = []
            
            for row in table1_data:
                business_id = generate_business_id(row['pageid'], row['sendmessagetime'], row['query'])
                
                # 检查是否已存在
                cur.execute("""
                    SELECT COUNT(*) as count 
                    FROM questions 
                    WHERE business_id = %s
                """, (business_id,))
                
                exists = cur.fetchone()['count'] > 0
                if exists:
                    existing_count += 1
                    if len(duplicate_examples) < 5:  # 只记录前5个例子
                        duplicate_examples.append({
                            'business_id': business_id,
                            'pageid': row['pageid'],
                            'sendmessagetime': row['sendmessagetime'],
                            'query': row['query'][:50] + '...' if len(row['query']) > 50 else row['query']
                        })
                else:
                    new_count += 1
            
            print(f"4. 其中已存在的数据: {existing_count} 条")
            print(f"5. 其中真正新的数据: {new_count} 条")
            
            # 4. 显示重复数据示例
            if duplicate_examples:
                print(f"\n=== 重复数据示例 ===")
                for i, example in enumerate(duplicate_examples, 1):
                    print(f"{i}. business_id: {example['business_id']}")
                    print(f"   pageid: {example['pageid']}")
                    print(f"   sendmessagetime: {example['sendmessagetime']}")
                    print(f"   query: {example['query']}")
                    print()
            
            # 5. 分析时间范围
            print(f"=== 时间范围分析 ===")
            if table1_data:
                earliest = min(row['sendmessagetime'] for row in table1_data)
                latest = max(row['sendmessagetime'] for row in table1_data)
                print(f"6. 待同步数据时间范围: {earliest} 到 {latest}")
                
                # 检查是否有本周之前的数据
                before_week_count = sum(1 for row in table1_data if row['sendmessagetime'] < week_start)
                print(f"7. 其中本周之前的数据: {before_week_count} 条")
            
            # 6. 检查questions表中的数据
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_this_week = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            questions_sendtime_this_week = cur.fetchone()['count']
            
            print(f"8. questions表中created_at本周的数据: {questions_this_week} 条")
            print(f"9. questions表中sendmessagetime本周的数据: {questions_sendtime_this_week} 条")
            
            # 7. 问题分析
            print(f"\n=== 问题分析 ===")
            if existing_count > 0:
                print(f"⚠️  发现问题：有 {existing_count} 条数据已经存在但仍会被同步")
                print("   这可能是因为：")
                print("   1. 同步逻辑基于sendmessagetime，但去重基于business_id")
                print("   2. 可能存在sendmessagetime更新但business_id相同的情况")
                print("   3. 或者同步条件与去重条件不一致")
            
            if new_count != (len(table1_data) - existing_count):
                print(f"❌ 计算错误：new_count({new_count}) + existing_count({existing_count}) != total({len(table1_data)})")
            
            # 8. 建议的修复方案
            print(f"\n=== 建议的修复方案 ===")
            print("1. 在同步逻辑中添加去重检查，避免同步已存在的数据")
            print("2. 或者修改同步条件，确保只同步真正新的数据")
            print("3. 考虑使用business_id来判断是否需要同步，而不仅仅是时间")
            
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_sync_issue()
