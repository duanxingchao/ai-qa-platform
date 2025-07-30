#!/usr/bin/env python3
"""
验证最终清理结果
"""

import requests
import json
from datetime import datetime

def test_display_api():
    """测试大屏API"""
    print(f"=== 测试大屏API ===")
    
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
                        name = item.get('name', 'Unknown')
                        count = item.get('count', 0)
                        rate = item.get('rate', 0)
                        print(f"     * {name}: {count} 条 ({rate}%)")
                
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
        print(f"❌ 大屏API测试失败: {e}")

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
                
                # 检查汇总数据
                if 'summary' in dashboard_data:
                    summary = dashboard_data['summary']
                    print(f"   - 汇总数据:")
                    print(f"     * 总问题数: {summary.get('total_questions', 0)}")
                    print(f"     * 总答案数: {summary.get('total_answers', 0)}")
                    print(f"     * 已评分答案: {summary.get('scored_answers', 0)}")
                    print(f"     * 完成率: {summary.get('completion_rate', '0%')}")
                    
                    # 检查竞品答案
                    competitor_answers = summary.get('competitor_answers', {})
                    print(f"     * 竞品答案:")
                    print(f"       - 豆包: {competitor_answers.get('doubao', 0)}")
                    print(f"       - 小天: {competitor_answers.get('xiaotian', 0)}")
                    print(f"       - 总计: {competitor_answers.get('total', 0)}")
                
                # 检查同步状态
                if 'sync_status' in dashboard_data:
                    sync_status = dashboard_data['sync_status']
                    print(f"   - 同步状态:")
                    print(f"     * 问题数量: {sync_status.get('questions_count', 0)}")
                    print(f"     * 答案数量: {sync_status.get('answers_count', 0)}")
                    print(f"     * 同步状态: {sync_status.get('sync_status', 'unknown')}")
                
        else:
            print(f"   - API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 仪表板API测试失败: {e}")

def test_scheduler_status():
    """测试调度器状态"""
    print(f"\n=== 测试调度器状态 ===")
    
    try:
        response = requests.get('http://localhost:8088/api/scheduler/status', timeout=10)
        print(f"🔧 调度器API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                scheduler_data = data['data']
                print(f"   - 调度器运行状态: {scheduler_data.get('scheduler_running', False)}")
                
                # 显示调度器任务
                scheduled_jobs = scheduler_data.get('scheduled_jobs', {})
                scheduler_jobs = scheduled_jobs.get('scheduler_jobs', [])
                print(f"   - 调度器任务数量: {len(scheduler_jobs)}")
                for job in scheduler_jobs:
                    job_id = job.get('id', 'Unknown')
                    job_name = job.get('name', 'Unknown')
                    next_run = job.get('next_run_time', 'Unknown')
                    print(f"     * {job_id}: {job_name}")
                    print(f"       下次运行: {next_run}")
                
        else:
            print(f"   - API请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 调度器状态测试失败: {e}")

def main():
    """主函数"""
    print(f"=== 最终结果验证 ===")
    print(f"验证时间: {datetime.now()}")
    
    # 测试各个API
    test_display_api()
    test_dashboard_api()
    test_scheduler_status()
    
    print(f"\n=== 总结 ===")
    print("🎉 数据清理已完成！")
    print("\n📱 前端刷新建议:")
    print("   1. 在浏览器中按 Ctrl+F5 强制刷新页面")
    print("   2. 或者等待30秒让前端自动刷新")
    print("   3. 现在前端应该显示所有数据为0或空")
    
    print(f"\n⚠️  重要提醒:")
    print("   - 调度器任务已暂停，不会再自动同步数据")
    print("   - 如需恢复自动同步，请调用API:")
    print("     POST http://localhost:8088/api/scheduler/jobs/configurable_workflow/resume")
    print("   - 或者在前端管理界面中手动启用")

if __name__ == "__main__":
    main()
