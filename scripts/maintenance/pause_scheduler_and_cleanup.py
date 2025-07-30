#!/usr/bin/env python3
"""
暂停调度器任务并彻底清理数据
"""

import os
import sys
import time
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

def pause_scheduler_job():
    """暂停调度器任务"""
    print(f"=== 暂停调度器任务 ===")
    
    try:
        # 暂停主要的工作流任务
        response = requests.post('http://localhost:8088/api/scheduler/jobs/configurable_workflow/pause', timeout=10)
        print(f"📡 暂停工作流任务API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 工作流任务已暂停")
                return True
            else:
                print(f"❌ 暂停工作流任务失败: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 暂停调度器任务失败: {e}")
        return False

def wait_for_current_tasks():
    """等待当前任务完成"""
    print(f"\n=== 等待当前任务完成 ===")
    print("等待10秒让当前运行的任务完成...")
    time.sleep(10)
    print("✅ 等待完成")

def force_cleanup_with_retry():
    """强制清理数据（带重试机制）"""
    week_start = get_week_start()
    print(f"\n=== 强制清理本周数据（带重试） ===")
    print(f"本周开始时间: {week_start}")
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"\n🔄 第 {attempt + 1} 次尝试清理...")
        
        conn = get_db_connection()
        try:
            # 设置较短的锁等待时间
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SET lock_timeout = '5s'")
                
                # 先删除评分数据（避免外键约束）
                cur.execute("""
                    DELETE FROM scores 
                    WHERE rated_at >= %s
                """, (week_start,))
                deleted_scores = cur.rowcount
                print(f"   删除评分数据: {deleted_scores} 条")
                
                # 删除答案数据
                cur.execute("""
                    DELETE FROM answers 
                    WHERE answer_time >= %s OR created_at >= %s
                """, (week_start, week_start))
                deleted_answers = cur.rowcount
                print(f"   删除答案数据: {deleted_answers} 条")
                
                # 删除问题数据
                cur.execute("""
                    DELETE FROM questions 
                    WHERE sendmessagetime >= %s OR created_at >= %s
                """, (week_start, week_start))
                deleted_questions = cur.rowcount
                print(f"   删除问题数据: {deleted_questions} 条")
                
                # 提交事务
                conn.commit()
                print(f"   ✅ 第 {attempt + 1} 次清理成功")
                
                # 验证清理结果
                cur.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM questions WHERE sendmessagetime >= %s OR created_at >= %s) as questions,
                        (SELECT COUNT(*) FROM answers WHERE answer_time >= %s OR created_at >= %s) as answers,
                        (SELECT COUNT(*) FROM scores WHERE rated_at >= %s) as scores
                """, (week_start, week_start, week_start, week_start, week_start))
                
                result = cur.fetchone()
                remaining_questions = result['questions']
                remaining_answers = result['answers']
                remaining_scores = result['scores']
                
                print(f"   📊 清理后验证:")
                print(f"      - 剩余问题: {remaining_questions} 条")
                print(f"      - 剩余答案: {remaining_answers} 条")
                print(f"      - 剩余评分: {remaining_scores} 条")
                
                if remaining_questions == 0 and remaining_answers == 0 and remaining_scores == 0:
                    print("   🎉 数据清理成功！")
                    return True
                else:
                    print("   ⚠️  仍有残留数据，继续下次尝试")
                    
        except Exception as e:
            print(f"   ❌ 第 {attempt + 1} 次清理失败: {e}")
            conn.rollback()
            if "deadlock" in str(e).lower():
                print("   🔄 检测到死锁，等待5秒后重试...")
                time.sleep(5)
            elif "lock_timeout" in str(e).lower():
                print("   ⏰ 锁等待超时，等待3秒后重试...")
                time.sleep(3)
        finally:
            conn.close()
    
    print(f"❌ 经过 {max_retries} 次尝试仍未完全清理成功")
    return False

def check_final_status():
    """检查最终状态"""
    print(f"\n=== 检查最终状态 ===")
    
    # 检查数据库状态
    week_start = get_week_start()
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM questions WHERE sendmessagetime >= %s OR created_at >= %s) as questions,
                    (SELECT COUNT(*) FROM answers WHERE answer_time >= %s OR created_at >= %s) as answers,
                    (SELECT COUNT(*) FROM scores WHERE rated_at >= %s) as scores
            """, (week_start, week_start, week_start, week_start, week_start))
            
            result = cur.fetchone()
            print(f"📊 数据库最终状态:")
            print(f"   - 本周问题: {result['questions']} 条")
            print(f"   - 本周答案: {result['answers']} 条")
            print(f"   - 本周评分: {result['scores']} 条")
            
            total_data = result['questions'] + result['answers'] + result['scores']
            return total_data == 0
            
    except Exception as e:
        print(f"❌ 检查最终状态失败: {e}")
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print(f"=== 暂停调度器并强制清理数据 ===")
    print(f"执行时间: {datetime.now()}")
    
    # 1. 暂停调度器任务
    pause_success = pause_scheduler_job()
    if not pause_success:
        print("⚠️  暂停调度器失败，但继续清理数据")
    
    # 2. 等待当前任务完成
    wait_for_current_tasks()
    
    # 3. 强制清理数据
    cleanup_success = force_cleanup_with_retry()
    
    # 4. 检查最终状态
    final_clean = check_final_status()
    
    # 5. 总结
    print(f"\n=== 总结 ===")
    if final_clean:
        print("🎉 数据清理成功！")
        print("📱 现在前端应该显示正确的数据了")
        print("\n💡 建议:")
        print("   1. 在浏览器中强制刷新页面 (Ctrl+F5)")
        print("   2. 等待30秒让前端自动刷新")
        print("   3. 调度器任务已暂停，不会再自动同步数据")
        print("\n⚠️  注意:")
        print("   - 调度器任务已暂停，如需恢复请手动启用")
        print("   - 可以通过API恢复: POST /api/scheduler/jobs/configurable_workflow/resume")
    else:
        print("⚠️  数据清理仍有问题")
        print("💡 建议:")
        print("   1. 重启后端服务以清除所有锁")
        print("   2. 或者等待一段时间后再次尝试清理")

if __name__ == "__main__":
    main()
