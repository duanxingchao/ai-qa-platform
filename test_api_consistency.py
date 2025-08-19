#!/usr/bin/env python3
"""
测试问题管理页面和大屏展示页面的竞品横评统计一致性
"""

import requests
import json

def test_api_consistency():
    """测试两个API的竞品横评统计是否一致"""
    
    # 问题管理页面API
    dashboard_url = "http://localhost:8088/api/dashboard"
    
    # 大屏展示页面API
    display_url = "http://localhost:8088/api/display/dashboard"
    
    try:
        # 获取问题管理页面数据
        print("🔍 获取问题管理页面数据...")
        dashboard_response = requests.get(dashboard_url)
        dashboard_data = dashboard_response.json()
        
        if not dashboard_data.get('success'):
            print(f"❌ 问题管理页面API调用失败: {dashboard_data.get('message')}")
            return
            
        # 获取大屏展示页面数据
        print("🔍 获取大屏展示页面数据...")
        display_response = requests.get(display_url)
        display_data = display_response.json()
        
        if not display_data.get('success'):
            print(f"❌ 大屏展示页面API调用失败: {display_data.get('message')}")
            return
        
        # 提取竞品横评相关数据
        dashboard_scored = dashboard_data['data']['summary']['scored_answers']
        
        # 从大屏展示的系统流程中找到竞品横评数据
        process_flow = display_data['data']['process_flow']['stages']
        display_scored = None
        
        for stage in process_flow:
            if stage['name'] == 'AI竞品横评':
                display_scored = stage['count']
                break
        
        print("\n📊 竞品横评统计对比:")
        print(f"问题管理页面: {dashboard_scored}")
        print(f"大屏展示页面: {display_scored}")
        
        if dashboard_scored == display_scored:
            print("✅ 统计数据一致！修改成功！")
        else:
            print("❌ 统计数据不一致，需要进一步检查")
            
        # 显示详细数据用于调试
        print("\n🔍 详细数据:")
        print("问题管理页面 summary:")
        print(json.dumps(dashboard_data['data']['summary'], indent=2, ensure_ascii=False))
        
        print("\n大屏展示页面 process_flow:")
        print(json.dumps(display_data['data']['process_flow'], indent=2, ensure_ascii=False))
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_api_consistency()
