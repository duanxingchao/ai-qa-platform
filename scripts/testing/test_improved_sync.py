#!/usr/bin/env python3
"""
测试改进后的同步逻辑
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

def test_improved_sync():
    """测试改进后的同步逻辑"""
    week_start = get_week_start()
    print(f"=== 测试改进后的同步逻辑 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 测试旧逻辑（基于时间）
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime >= %s
            """, (week_start,))
            old_logic_count = cur.fetchone()['count']
            print(f"1. 旧逻辑（基于时间）会同步的数据量: {old_logic_count}")
            
            # 2. 测试新逻辑（基于时间+去重）
            cur.execute("""
                SELECT COUNT(*) FROM table1 t1
                WHERE t1.query IS NOT NULL 
                AND t1.query != '' 
                AND TRIM(t1.query) != ''
                AND t1.sendmessagetime >= %s
                AND NOT EXISTS (
                    SELECT 1 FROM questions q 
                    WHERE q.business_id = MD5(CONCAT(t1.pageid, COALESCE(t1.sendmessagetime::text, ''), t1.query))
                )
            """, (week_start,))
            new_logic_count = cur.fetchone()['count']
            print(f"2. 新逻辑（基于时间+去重）会同步的数据量: {new_logic_count}")
            
            # 3. 计算差异
            duplicate_count = old_logic_count - new_logic_count
            print(f"3. 被去重的数据量: {duplicate_count}")
            
            # 4. 验证questions表状态
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_this_week = cur.fetchone()['count']
            print(f"4. questions表中本周数据量: {questions_this_week}")
            
            # 5. 验证逻辑正确性
            print(f"\n=== 逻辑验证 ===")
            if new_logic_count == 0:
                print("✅ 新逻辑正确：没有需要同步的新数据")
            elif new_logic_count > 0:
                print(f"📝 新逻辑检测到 {new_logic_count} 条真正需要同步的新数据")
                
                # 显示一些新数据示例
                cur.execute("""
                    SELECT 
                        t1.pageid,
                        t1.sendmessagetime,
                        LEFT(t1.query, 50) as query_preview
                    FROM table1 t1
                    WHERE t1.query IS NOT NULL 
                    AND t1.query != '' 
                    AND TRIM(t1.query) != ''
                    AND t1.sendmessagetime >= %s
                    AND NOT EXISTS (
                        SELECT 1 FROM questions q 
                        WHERE q.business_id = MD5(CONCAT(t1.pageid, COALESCE(t1.sendmessagetime::text, ''), t1.query))
                    )
                    ORDER BY t1.sendmessagetime ASC
                    LIMIT 5
                """, (week_start,))
                
                new_data_samples = cur.fetchall()
                print("   新数据示例:")
                for i, sample in enumerate(new_data_samples, 1):
                    print(f"   {i}. pageid: {sample['pageid']}, time: {sample['sendmessagetime']}")
                    print(f"      query: {sample['query_preview']}...")
            
            # 6. 性能分析
            print(f"\n=== 性能分析 ===")
            print(f"去重效果: 减少了 {duplicate_count} 条重复数据的同步")
            if old_logic_count > 0:
                efficiency = (duplicate_count / old_logic_count) * 100
                print(f"去重率: {efficiency:.1f}%")
            
            # 7. 总结
            print(f"\n=== 改进效果总结 ===")
            print("✅ 改进后的同步逻辑优势：")
            print("   1. 只同步本周的数据")
            print("   2. 避免重复同步已存在的数据")
            print("   3. 基于business_id进行精确去重")
            print("   4. 提高同步效率，减少不必要的数据库操作")
            print(f"   5. 在这次测试中，避免了 {duplicate_count} 条重复数据的同步")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_improved_sync()
