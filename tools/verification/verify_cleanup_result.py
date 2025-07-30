#!/usr/bin/env python3
"""
验证清理结果并测试API响应
"""

import os
import sys
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json

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

def verify_database_cleanup():
    """验证数据库清理结果"""
    week_start = get_week_start()
    print(f"=== 验证数据库清理结果 ===")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 检查questions表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s
            """, (week_start,))
            questions_sendtime = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE created_at >= %s
            """, (week_start,))
            questions_created = cur.fetchone()['count']
            
            # 检查answers表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE answer_time >= %s
            """, (week_start,))
            answers_time = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE created_at >= %s
            """, (week_start,))
            answers_created = cur.fetchone()['count']
            
            # 检查scores表
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM scores
                WHERE rated_at >= %s
            """, (week_start,))
            scores_rated = cur.fetchone()['count']
            
            print(f"📊 数据库状态:")
            print(f"   - questions表(sendmessagetime本周): {questions_sendtime} 条")
            print(f"   - questions表(created_at本周): {questions_created} 条")
            print(f"   - answers表(answer_time本周): {answers_time} 条")
            print(f"   - answers表(created_at本周): {answers_created} 条")
            print(f"   - scores表(rated_at本周): {scores_rated} 条")
            
            # 验证结果
            total_week_data = (questions_sendtime + questions_created + 
                             answers_time + answers_created + scores_rated)
            
            if total_week_data == 0:
                print("✅ 数据库清理成功！本周数据已完全删除")
                return True
            else:
                print("❌ 数据库清理不完整，仍有本周数据残留")
                return False
                
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")
        return False
    finally:
        conn.close()

def test_api_response():
    """测试API响应"""
    print(f"\n=== 测试API响应 ===")
    
    # 测试大屏API
    try:
        response = requests.get('http://localhost:8088/api/display/dashboard', timeout=10)
        print(f"📡 大屏API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - 响应成功: {data.get('success', False)}")
            
            if data.get('success') and data.get('data'):
                api_data = data['data']
                
                # 检查处理流程数据
                if 'process_flow' in api_data:
                    flow_data = api_data['process_flow']
                    print(f"   - 处理流程数据:")
                    for item in flow_data:
                        print(f"     * {item.get('name', 'Unknown')}: {item.get('count', 0)} 条")
                
                # 检查核心指标
                if 'core_metrics' in api_data:
                    metrics = api_data['core_metrics']
                    print(f"   - 核心指标:")
                    for key, value in metrics.items():
                        print(f"     * {key}: {value}")
                        
            else:
                print("   - API返回数据格式异常")
        else:
            print(f"   - API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def test_dashboard_api():
    """测试仪表板API"""
    print(f"\n=== 测试仪表板API ===")
    
    try:
        response = requests.get('http://localhost:8088/api/dashboard', timeout=10)
        print(f"📊 仪表板API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   - 响应成功: {data.get('success', False)}")
            
            if data.get('success') and data.get('data'):
                dashboard_data = data['data']
                print(f"   - 仪表板数据:")
                for key, value in dashboard_data.items():
                    if isinstance(value, dict):
                        print(f"     * {key}: {json.dumps(value, ensure_ascii=False)}")
                    else:
                        print(f"     * {key}: {value}")
        else:
            print(f"   - API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 仪表板API测试失败: {e}")

def main():
    """主函数"""
    print(f"=== 清理结果验证报告 ===")
    print(f"验证时间: {datetime.now()}")
    
    # 1. 验证数据库清理结果
    db_clean = verify_database_cleanup()
    
    # 2. 测试API响应
    test_api_response()
    test_dashboard_api()
    
    # 3. 总结
    print(f"\n=== 总结 ===")
    if db_clean:
        print("🎉 数据库清理成功！")
        print("📱 前端显示的数据可能是以下原因:")
        print("   1. 浏览器缓存 - 建议强制刷新页面 (Ctrl+F5)")
        print("   2. 前端定时器 - 等待30秒自动刷新")
        print("   3. API缓存 - 重启后端服务")
        print("\n💡 建议操作:")
        print("   1. 在浏览器中按 Ctrl+F5 强制刷新页面")
        print("   2. 或者等待30秒让前端自动刷新")
        print("   3. 如果仍有问题，重启前端和后端服务")
    else:
        print("⚠️  数据库清理不完整，需要进一步处理")

if __name__ == "__main__":
    main()
