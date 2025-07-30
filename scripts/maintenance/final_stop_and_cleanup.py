#!/usr/bin/env python3
"""
最终停止所有自动化进程并彻底清理数据
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

def check_and_stop_all_jobs():
    """检查并停止所有调度器任务"""
    print(f"=== 检查并停止所有调度器任务 ===")
    
    try:
        # 获取调度器状态
        response = requests.get('http://localhost:8088/api/scheduler/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                scheduler_data = data['data']
                print(f"调度器运行状态: {scheduler_data.get('scheduler_running', False)}")
                
                # 获取所有任务
                scheduled_jobs = scheduler_data.get('scheduled_jobs', {})
                scheduler_jobs = scheduled_jobs.get('scheduler_jobs', [])
                
                print(f"发现 {len(scheduler_jobs)} 个调度器任务:")
                for job in scheduler_jobs:
                    job_id = job.get('id', 'Unknown')
                    job_name = job.get('name', 'Unknown')
                    next_run = job.get('next_run_time', 'Unknown')
                    print(f"  - {job_id}: {job_name}")
                    print(f"    下次运行: {next_run}")
                    
                    # 尝试暂停任务
                    try:
                        pause_response = requests.post(
                            f'http://localhost:8088/api/scheduler/jobs/{job_id}/pause',
                            timeout=10
                        )
                        if pause_response.status_code == 200:
                            pause_data = pause_response.json()
                            if pause_data.get('success'):
                                print(f"    ✅ 任务 {job_id} 已暂停")
                            else:
                                print(f"    ❌ 暂停任务 {job_id} 失败: {pause_data.get('message')}")
                        else:
                            print(f"    ❌ 暂停任务 {job_id} API失败: {pause_response.status_code}")
                    except Exception as e:
                        print(f"    ❌ 暂停任务 {job_id} 异常: {e}")
                
                # 获取工作流任务状态
                jobs = scheduled_jobs.get('jobs', {})
                print(f"\n发现 {len(jobs)} 个工作流任务:")
                for job_id, job_info in jobs.items():
                    job_name = job_info.get('name', 'Unknown')
                    job_status = job_info.get('status', 'Unknown')
                    print(f"  - {job_id}: {job_name} ({job_status})")
                
        else:
            print(f"获取调度器状态失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查调度器状态失败: {e}")

def disable_auto_startup():
    """尝试禁用自动启动配置"""
    print(f"\n=== 尝试禁用自动启动配置 ===")
    
    # 这里我们无法直接修改配置，但可以尝试通过API停止
    try:
        # 尝试停止所有可能的自动化进程
        apis_to_try = [
            '/api/scheduler/stop',
            '/api/scheduler/shutdown',
            '/api/sync/stop',
        ]
        
        for api in apis_to_try:
            try:
                response = requests.post(f'http://localhost:8088{api}', timeout=5)
                print(f"尝试调用 {api}: {response.status_code}")
            except:
                pass
                
    except Exception as e:
        print(f"❌ 禁用自动启动失败: {e}")

def force_cleanup_all_week_data():
    """强制清理所有本周数据"""
    week_start = get_week_start()
    print(f"\n=== 强制清理所有本周数据 ===")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 设置较长的锁等待时间
            cur.execute("SET lock_timeout = '30s'")
            
            print("🔄 开始清理...")
            
            # 1. 先删除所有评分数据（避免外键约束）
            cur.execute("DELETE FROM scores WHERE rated_at >= %s", (week_start,))
            deleted_scores = cur.rowcount
            print(f"   删除评分数据: {deleted_scores} 条")
            
            # 2. 删除所有本周答案数据
            cur.execute("""
                DELETE FROM answers 
                WHERE answer_time >= %s OR created_at >= %s
            """, (week_start, week_start))
            deleted_answers = cur.rowcount
            print(f"   删除答案数据: {deleted_answers} 条")
            
            # 3. 删除所有本周问题数据
            cur.execute("""
                DELETE FROM questions 
                WHERE sendmessagetime >= %s OR created_at >= %s
            """, (week_start, week_start))
            deleted_questions = cur.rowcount
            print(f"   删除问题数据: {deleted_questions} 条")
            
            # 4. 额外清理：删除今天的所有数据
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            cur.execute("DELETE FROM scores WHERE rated_at >= %s", (today_start,))
            deleted_scores_today = cur.rowcount
            print(f"   删除今天评分数据: {deleted_scores_today} 条")
            
            cur.execute("""
                DELETE FROM answers 
                WHERE answer_time >= %s OR created_at >= %s
            """, (today_start, today_start))
            deleted_answers_today = cur.rowcount
            print(f"   删除今天答案数据: {deleted_answers_today} 条")
            
            cur.execute("""
                DELETE FROM questions 
                WHERE sendmessagetime >= %s OR created_at >= %s
            """, (today_start, today_start))
            deleted_questions_today = cur.rowcount
            print(f"   删除今天问题数据: {deleted_questions_today} 条")
            
            # 提交事务
            conn.commit()
            print(f"✅ 所有删除操作已提交")
            
            # 验证清理结果
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM questions WHERE sendmessagetime >= %s OR created_at >= %s) as questions,
                    (SELECT COUNT(*) FROM answers WHERE answer_time >= %s OR created_at >= %s) as answers,
                    (SELECT COUNT(*) FROM scores WHERE rated_at >= %s) as scores
            """, (week_start, week_start, week_start, week_start, week_start))
            
            result = cur.fetchone()
            print(f"\n📊 清理后验证:")
            print(f"   - 剩余本周问题: {result['questions']} 条")
            print(f"   - 剩余本周答案: {result['answers']} 条")
            print(f"   - 剩余本周评分: {result['scores']} 条")
            
            return result['questions'] == 0 and result['answers'] == 0 and result['scores'] == 0
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def monitor_for_new_data():
    """监控是否有新数据产生"""
    print(f"\n=== 监控新数据产生 ===")
    
    week_start = get_week_start()
    
    for i in range(3):  # 监控3次，每次间隔10秒
        print(f"🔍 第 {i+1} 次检查...")
        
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
                total_data = result['questions'] + result['answers'] + result['scores']
                
                if total_data > 0:
                    print(f"   ⚠️  检测到新数据: 问题{result['questions']}, 答案{result['answers']}, 评分{result['scores']}")
                    return False
                else:
                    print(f"   ✅ 无新数据")
                    
        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
        finally:
            conn.close()
        
        if i < 2:  # 不是最后一次检查
            print("   等待10秒...")
            time.sleep(10)
    
    return True

def main():
    """主函数"""
    print(f"=== 最终停止所有自动化进程并彻底清理 ===")
    print(f"执行时间: {datetime.now()}")
    
    # 1. 检查并停止所有调度器任务
    check_and_stop_all_jobs()
    
    # 2. 尝试禁用自动启动
    disable_auto_startup()
    
    # 3. 等待一下让任务停止
    print(f"\n⏰ 等待15秒让所有任务停止...")
    time.sleep(15)
    
    # 4. 强制清理所有本周数据
    cleanup_success = force_cleanup_all_week_data()
    
    # 5. 监控是否有新数据产生
    if cleanup_success:
        no_new_data = monitor_for_new_data()
        
        if no_new_data:
            print(f"\n🎉 成功！数据已清理且无新数据产生")
        else:
            print(f"\n⚠️  警告：清理后仍有新数据产生，可能需要重启后端服务")
    
    # 6. 最终建议
    print(f"\n=== 最终建议 ===")
    if cleanup_success and no_new_data:
        print("✅ 数据清理成功且系统稳定")
        print("📱 现在可以刷新前端页面查看效果")
        print("💡 建议:")
        print("   1. 在浏览器中按 Ctrl+F5 强制刷新")
        print("   2. 清除浏览器缓存")
        print("   3. 前端应该显示所有本周数据为0")
    else:
        print("⚠️  数据清理不完整或系统仍在产生新数据")
        print("💡 建议:")
        print("   1. 重启后端服务以完全停止所有自动化进程")
        print("   2. 重启后再次运行清理脚本")
        print("   3. 检查是否有其他进程在同步数据")

if __name__ == "__main__":
    main()
