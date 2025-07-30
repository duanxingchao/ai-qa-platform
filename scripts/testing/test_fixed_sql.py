#!/usr/bin/env python3
"""
测试修复后的SQL查询
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
    """生成business_id（与Python代码一致）"""
    raw_str = f"{pageid}{sendmessagetime.isoformat() if sendmessagetime else ''}{query}"
    return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

def test_fixed_sql():
    """测试修复后的SQL查询"""
    week_start = get_week_start()
    print(f"=== 测试修复后的SQL查询 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. 获取一些table1数据样本来测试business_id生成
            cur.execute("""
                SELECT 
                    pageid,
                    sendmessagetime,
                    query
                FROM table1
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
                AND sendmessagetime >= %s
                ORDER BY sendmessagetime ASC
                LIMIT 5
            """, (week_start,))
            
            samples = cur.fetchall()
            print(f"1. 获取 {len(samples)} 条样本数据进行测试")
            
            # 2. 测试Python和SQL的business_id生成是否一致
            print(f"\n=== business_id生成一致性测试 ===")
            consistent_count = 0
            
            for i, sample in enumerate(samples, 1):
                # Python生成
                python_business_id = generate_business_id(
                    sample['pageid'], 
                    sample['sendmessagetime'], 
                    sample['query']
                )
                
                # SQL生成
                cur.execute("""
                    SELECT MD5(CONCAT(
                        %s, 
                        COALESCE(to_char(%s, 'YYYY-MM-DD"T"HH24:MI:SS.US'), ''), 
                        %s
                    )) as sql_business_id
                """, (sample['pageid'], sample['sendmessagetime'], sample['query']))
                
                sql_result = cur.fetchone()
                sql_business_id = sql_result['sql_business_id']
                
                is_consistent = python_business_id == sql_business_id
                if is_consistent:
                    consistent_count += 1
                
                print(f"样本 {i}:")
                print(f"  pageid: {sample['pageid']}")
                print(f"  sendmessagetime: {sample['sendmessagetime']}")
                print(f"  query: {sample['query'][:30]}...")
                print(f"  Python business_id: {python_business_id}")
                print(f"  SQL business_id:    {sql_business_id}")
                print(f"  一致性: {'✅' if is_consistent else '❌'}")
                print()
            
            print(f"一致性测试结果: {consistent_count}/{len(samples)} 一致")
            
            if consistent_count == len(samples):
                print("✅ business_id生成完全一致！")
                
                # 3. 测试修复后的完整查询
                print(f"\n=== 测试修复后的完整查询 ===")
                
                # 修复后的SQL查询
                cur.execute("""
                    SELECT COUNT(*) as count FROM table1 t1
                    WHERE t1.query IS NOT NULL 
                    AND t1.query != '' 
                    AND TRIM(t1.query) != ''
                    AND t1.sendmessagetime >= %s
                    AND NOT EXISTS (
                        SELECT 1 FROM questions q 
                        WHERE q.business_id = MD5(CONCAT(
                            t1.pageid, 
                            COALESCE(to_char(t1.sendmessagetime, 'YYYY-MM-DD"T"HH24:MI:SS.US'), ''), 
                            t1.query
                        ))
                    )
                """, (week_start,))
                
                fixed_sql_count = cur.fetchone()['count']
                print(f"3. 修复后的SQL查询结果: {fixed_sql_count} 条新数据")
                
                # 4. Python验证
                cur.execute("""
                    SELECT 
                        pageid,
                        sendmessagetime,
                        query
                    FROM table1
                    WHERE query IS NOT NULL 
                    AND query != '' 
                    AND TRIM(query) != ''
                    AND sendmessagetime >= %s
                    ORDER BY sendmessagetime ASC
                """, (week_start,))
                
                all_data = cur.fetchall()
                python_new_count = 0
                
                for row in all_data:
                    business_id = generate_business_id(row['pageid'], row['sendmessagetime'], row['query'])
                    
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM questions 
                        WHERE business_id = %s
                    """, (business_id,))
                    
                    exists = cur.fetchone()['count'] > 0
                    if not exists:
                        python_new_count += 1
                
                print(f"4. Python验证结果: {python_new_count} 条新数据")
                
                # 5. 对比结果
                print(f"\n=== 结果对比 ===")
                if fixed_sql_count == python_new_count:
                    print("✅ 修复成功！SQL查询与Python验证结果完全一致")
                    print(f"   都检测到 {fixed_sql_count} 条真正需要同步的新数据")
                else:
                    print(f"❌ 仍有差异：SQL={fixed_sql_count}, Python={python_new_count}")
                
            else:
                print("❌ business_id生成不一致，需要进一步调试")
                
                # 显示时间格式差异
                sample = samples[0]
                python_time_str = sample['sendmessagetime'].isoformat() if sample['sendmessagetime'] else ''
                
                cur.execute("""
                    SELECT to_char(%s, 'YYYY-MM-DD"T"HH24:MI:SS.US') as sql_time_str
                """, (sample['sendmessagetime'],))
                sql_time_str = cur.fetchone()['sql_time_str']
                
                print(f"时间格式对比:")
                print(f"  Python isoformat(): {python_time_str}")
                print(f"  SQL to_char():      {sql_time_str}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_fixed_sql()
