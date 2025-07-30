#!/usr/bin/env python3
"""
调试大屏API返回的具体数据
"""

import requests
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os

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

def check_database_data():
    """检查数据库中的实际数据"""
    week_start = get_week_start()
    print(f"=== 检查数据库实际数据 ===")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 检查本周数据
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM questions WHERE sendmessagetime >= %s) as questions_sendtime,
                    (SELECT COUNT(*) FROM questions WHERE created_at >= %s) as questions_created,
                    (SELECT COUNT(*) FROM answers WHERE answer_time >= %s) as answers_time,
                    (SELECT COUNT(*) FROM answers WHERE created_at >= %s) as answers_created,
                    (SELECT COUNT(*) FROM scores WHERE rated_at >= %s) as scores_rated
            """, (week_start, week_start, week_start, week_start, week_start))
            
            result = cur.fetchone()
            print(f"📊 本周数据统计:")
            print(f"   - questions(sendmessagetime): {result['questions_sendtime']} 条")
            print(f"   - questions(created_at): {result['questions_created']} 条")
            print(f"   - answers(answer_time): {result['answers_time']} 条")
            print(f"   - answers(created_at): {result['answers_created']} 条")
            print(f"   - scores(rated_at): {result['scores_rated']} 条")
            
            # 检查总数据
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM questions) as total_questions,
                    (SELECT COUNT(*) FROM answers) as total_answers,
                    (SELECT COUNT(*) FROM scores) as total_scores
            """)
            
            total_result = cur.fetchone()
            print(f"📈 总数据统计:")
            print(f"   - 总问题数: {total_result['total_questions']} 条")
            print(f"   - 总答案数: {total_result['total_answers']} 条")
            print(f"   - 总评分数: {total_result['total_scores']} 条")
            
            return result
            
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return None
    finally:
        conn.close()

def test_display_api_detailed():
    """详细测试大屏API"""
    print(f"\n=== 详细测试大屏API ===")
    
    try:
        response = requests.get('http://localhost:8088/api/display/dashboard', timeout=10)
        print(f"📡 API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API响应成功: {data.get('success', False)}")
            
            if data.get('success') and data.get('data'):
                api_data = data['data']
                print(f"\n📋 API返回的完整数据:")
                print(json.dumps(api_data, indent=2, ensure_ascii=False))
                
                # 特别检查处理流程数据
                if 'process_flow' in api_data:
                    print(f"\n🔍 处理流程数据详情:")
                    flow_data = api_data['process_flow']
                    for i, item in enumerate(flow_data):
                        print(f"   [{i}] {json.dumps(item, ensure_ascii=False)}")
                
            else:
                print("❌ API返回数据格式异常")
                print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def check_backend_logic():
    """检查后端逻辑"""
    print(f"\n=== 检查后端处理逻辑 ===")
    
    # 检查大屏API的具体实现
    try:
        # 先检查API是否使用了正确的时间范围
        week_start = get_week_start()
        print(f"当前本周开始时间: {week_start}")
        
        # 检查API可能使用的时间范围参数
        test_params = [
            {},  # 默认参数
            {'time_range': 'week'},  # 本周
            {'time_range': 'all'},   # 全部
        ]
        
        for i, params in enumerate(test_params):
            print(f"\n🧪 测试参数组合 {i+1}: {params}")
            try:
                response = requests.get('http://localhost:8088/api/display/dashboard', 
                                      params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        process_flow = data['data'].get('process_flow', [])
                        if process_flow:
                            first_item = process_flow[0] if process_flow else {}
                            print(f"   第一个流程项: {json.dumps(first_item, ensure_ascii=False)}")
                        else:
                            print("   无处理流程数据")
                    else:
                        print("   API返回失败")
                else:
                    print(f"   API请求失败: {response.status_code}")
            except Exception as e:
                print(f"   测试失败: {e}")
                
    except Exception as e:
        print(f"❌ 后端逻辑检查失败: {e}")

def main():
    """主函数"""
    print(f"=== 调试大屏API数据问题 ===")
    print(f"调试时间: {datetime.now()}")
    
    # 1. 检查数据库实际数据
    db_result = check_database_data()
    
    # 2. 详细测试大屏API
    test_display_api_detailed()
    
    # 3. 检查后端逻辑
    check_backend_logic()
    
    # 4. 分析问题
    print(f"\n=== 问题分析 ===")
    if db_result:
        total_week_data = (db_result['questions_sendtime'] + db_result['questions_created'] + 
                          db_result['answers_time'] + db_result['answers_created'] + 
                          db_result['scores_rated'])
        
        if total_week_data == 0:
            print("✅ 数据库中本周数据确实已清空")
            print("❓ 问题可能在于:")
            print("   1. 大屏API没有正确过滤本周数据")
            print("   2. 前端缓存了旧数据")
            print("   3. API使用了错误的时间范围")
            print("   4. 后端代码逻辑有问题")
        else:
            print("⚠️  数据库中仍有本周数据残留")
            print("   需要重新清理数据")
    
    print(f"\n💡 建议解决方案:")
    print("   1. 检查大屏API的后端实现代码")
    print("   2. 确认API是否正确使用本周时间范围")
    print("   3. 清除浏览器缓存并强制刷新")
    print("   4. 重启后端服务")

if __name__ == "__main__":
    main()
