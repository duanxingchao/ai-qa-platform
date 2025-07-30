#!/usr/bin/env python3
"""
停止调度器并彻底清理数据
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

def check_scheduler_status():
    """检查调度器状态"""
    print(f"=== 检查调度器状态 ===")
    
    try:
        response = requests.get('http://localhost:8088/api/scheduler/status', timeout=10)
        print(f"📡 调度器API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                scheduler_data = data['data']
                print(f"   - 调度器运行状态: {scheduler_data.get('scheduler_running', False)}")
                
                # 显示定时任务
                scheduled_jobs = scheduler_data.get('scheduled_jobs', {})
                jobs = scheduled_jobs.get('jobs', {})
                print(f"   - 定时任务数量: {len(jobs)}")
                
                for job_id, job_info in jobs.items():
                    print(f"     * {job_id}: {job_info.get('name', 'Unknown')} - {job_info.get('status', 'Unknown')}")
                
                # 显示调度器任务
                scheduler_jobs = scheduled_jobs.get('scheduler_jobs', [])
                print(f"   - 调度器任务数量: {len(scheduler_jobs)}")
                for job in scheduler_jobs:
                    print(f"     * {job.get('id', 'Unknown')}: {job.get('name', 'Unknown')} - 下次运行: {job.get('next_run_time', 'Unknown')}")
                
                return scheduler_data.get('scheduler_running', False)
        else:
            print(f"   - API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 调度器状态检查失败: {e}")
        return False

def stop_scheduler():
    """停止调度器"""
    print(f"\n=== 停止调度器 ===")
    
    try:
        response = requests.post('http://localhost:8088/api/scheduler/stop', timeout=10)
        print(f"📡 停止调度器API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 调度器已成功停止")
                return True
            else:
                print(f"❌ 停止调度器失败: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API请求失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 停止调度器失败: {e}")
        return False

def disable_all_jobs():
    """禁用所有定时任务"""
    print(f"\n=== 禁用所有定时任务 ===")
    
    # 获取所有任务列表
    try:
        response = requests.get('http://localhost:8088/api/scheduler/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                scheduled_jobs = data['data'].get('scheduled_jobs', {})
                jobs = scheduled_jobs.get('jobs', {})
                
                for job_id in jobs.keys():
                    try:
                        disable_response = requests.post(
                            f'http://localhost:8088/api/scheduler/jobs/{job_id}/disable',
                            timeout=10
                        )
                        if disable_response.status_code == 200:
                            print(f"✅ 已禁用任务: {job_id}")
                        else:
                            print(f"❌ 禁用任务失败: {job_id}")
                    except Exception as e:
                        print(f"❌ 禁用任务 {job_id} 失败: {e}")
                        
    except Exception as e:
        print(f"❌ 获取任务列表失败: {e}")

def thorough_cleanup_again():
    """再次彻底清理本周数据"""
    week_start = get_week_start()
    print(f"\n=== 再次彻底清理本周数据 ===")
    print(f"本周开始时间: {week_start}")
    
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 获取本周问题的business_id列表
            cur.execute("""
                SELECT business_id 
                FROM questions
                WHERE sendmessagetime >= %s OR created_at >= %s
            """, (week_start, week_start))
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
            
            # 验证清理结果
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM questions
                WHERE sendmessagetime >= %s OR created_at >= %s
            """, (week_start, week_start))
            remaining_questions = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM answers
                WHERE answer_time >= %s OR created_at >= %s
            """, (week_start, week_start))
            remaining_answers = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count 
                FROM scores
                WHERE rated_at >= %s
            """, (week_start,))
            remaining_scores = cur.fetchone()['count']
            
            print(f"\n📊 清理后验证:")
            print(f"   - 剩余问题: {remaining_questions} 条")
            print(f"   - 剩余答案: {remaining_answers} 条")
            print(f"   - 剩余评分: {remaining_scores} 条")
            
            if remaining_questions == 0 and remaining_answers == 0 and remaining_scores == 0:
                print("🎉 数据清理成功！")
                return True
            else:
                print("⚠️  仍有残留数据")
                return False
            
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print(f"=== 停止调度器并彻底清理数据 ===")
    print(f"执行时间: {datetime.now()}")
    
    # 1. 检查调度器状态
    scheduler_running = check_scheduler_status()
    
    # 2. 如果调度器在运行，停止它
    if scheduler_running:
        print("\n🛑 检测到调度器正在运行，需要先停止")
        stop_success = stop_scheduler()
        if stop_success:
            print("✅ 调度器已停止")
        else:
            print("❌ 调度器停止失败，但继续清理数据")
    else:
        print("\n✅ 调度器未运行")
    
    # 3. 禁用所有定时任务
    disable_all_jobs()
    
    # 4. 再次彻底清理数据
    cleanup_success = thorough_cleanup_again()
    
    # 5. 总结
    print(f"\n=== 总结 ===")
    if cleanup_success:
        print("🎉 数据清理成功！")
        print("📱 现在前端应该显示正确的数据了")
        print("\n💡 建议:")
        print("   1. 在浏览器中刷新页面 (F5 或 Ctrl+F5)")
        print("   2. 等待30秒让前端自动刷新")
        print("   3. 调度器已停止，不会再自动同步数据")
    else:
        print("⚠️  数据清理仍有问题，需要进一步检查")

if __name__ == "__main__":
    main()
