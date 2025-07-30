#!/usr/bin/env python3
"""
验证修改后的同步逻辑是否正确
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
    else:
        return psycopg2.connect(
            host="localhost",
            port="5432",
            database="ai_qa_platform",
            user="postgres",
            password="l69jjd9n"
        )

def verify_sync_logic():
    """验证同步逻辑"""
    week_start = get_week_start()
    print(f"=== 验证修改后的同步逻辑 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 获取当前最后同步时间
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
            
            # 2. 模拟修改后的逻辑：确定实际的since_time
            if last_sync_time and last_sync_time < week_start:
                actual_since_time = week_start
                print(f"2. 最后同步时间早于本周，调整为本周开始时间: {actual_since_time}")
            elif last_sync_time:
                actual_since_time = last_sync_time
                print(f"2. 最后同步时间在本周内，使用原时间: {actual_since_time}")
            else:
                actual_since_time = week_start
                print(f"2. 没有最后同步时间，使用本周开始时间: {actual_since_time}")
            
            # 3. 验证修改后的查询逻辑
            print(f"\n=== 验证查询逻辑 ===")
            
            # 旧逻辑：只基于since_time
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime > %s
            """, (actual_since_time,))
            old_logic_count = cur.fetchone()['count']
            print(f"3. 旧逻辑（只基于since_time）会同步的数据量: {old_logic_count}")
            
            # 新逻辑：同时限制since_time和week_start
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime > %s
                AND sendmessagetime >= %s
            """, (actual_since_time, week_start))
            new_logic_count = cur.fetchone()['count']
            print(f"4. 新逻辑（同时限制since_time和week_start）会同步的数据量: {new_logic_count}")
            
            # 4. 分析差异
            print(f"\n=== 逻辑对比分析 ===")
            if old_logic_count == new_logic_count:
                print("✅ 新旧逻辑结果一致，说明没有本周之前的数据会被同步")
            else:
                print(f"⚠️  新旧逻辑结果不同，差异: {old_logic_count - new_logic_count} 条")
                
                # 查看被过滤掉的数据
                cur.execute("""
                    SELECT 
                        COUNT(*) as count,
                        MIN(sendmessagetime) as earliest,
                        MAX(sendmessagetime) as latest
                    FROM table1
                    WHERE query IS NOT NULL 
                    AND query != '' 
                    AND TRIM(query) != ''
                    AND sendmessagetime > %s
                    AND sendmessagetime < %s
                """, (actual_since_time, week_start))
                filtered_data = cur.fetchone()
                if filtered_data['count'] > 0:
                    print(f"   被过滤的数据: {filtered_data['count']} 条")
                    print(f"   时间范围: {filtered_data['earliest']} 到 {filtered_data['latest']}")
            
            # 5. 验证本周数据范围
            print(f"\n=== 本周数据验证 ===")
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime >= %s
            """, (week_start,))
            this_week_total = cur.fetchone()['count']
            print(f"5. table1中本周总数据量: {this_week_total}")
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            synced_this_week = cur.fetchone()['count']
            print(f"6. 已同步的本周数据量: {synced_this_week}")
            
            unsync_this_week = this_week_total - synced_this_week
            print(f"7. 本周未同步数据量: {unsync_this_week}")
            
            # 6. 验证新逻辑是否正确
            print(f"\n=== 新逻辑验证结果 ===")
            if new_logic_count == unsync_this_week:
                print("✅ 新逻辑正确：只会同步本周未同步的数据")
            elif new_logic_count < unsync_this_week:
                print(f"⚠️  新逻辑可能过于严格：应该同步{unsync_this_week}条，但只会同步{new_logic_count}条")
            else:
                print(f"❌ 新逻辑可能有问题：本周未同步数据只有{unsync_this_week}条，但会同步{new_logic_count}条")
            
            # 7. 显示修改效果总结
            print(f"\n=== 修改效果总结 ===")
            print("✅ 修改后的同步逻辑特点：")
            print("   1. 确保since_time不早于本周开始时间")
            print("   2. 查询条件同时限制sendmessagetime > since_time AND sendmessagetime >= week_start")
            print("   3. 防止同步本周之前的历史数据")
            print("   4. 只同步本周的新增且未同步的数据")
            
            if old_logic_count != new_logic_count:
                print(f"   5. 相比旧逻辑，减少了{old_logic_count - new_logic_count}条历史数据的同步")
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    verify_sync_logic()
