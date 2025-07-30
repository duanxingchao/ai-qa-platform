#!/usr/bin/env python3
"""
调度器配置管理API测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8088/api/scheduler"

def test_api(method, endpoint, data=None, description=""):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n🔍 {description}")
    print(f"📡 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        else:
            print(f"❌ 不支持的HTTP方法: {method}")
            return False
            
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功: {result.get('message', '操作成功')}")
            if 'data' in result:
                print(f"📄 数据: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False

def main():
    """主测试流程"""
    print("🚀 开始调度器配置管理API测试")
    print("=" * 60)
    
    # 测试1: 获取调度器状态
    test_api("GET", "/status", description="获取调度器状态")
    
    # 测试2: 获取配置信息
    test_api("GET", "/config", description="获取调度器配置")
    
    # 测试3: 更新配置
    config_data = {
        "scheduler_enabled": True,
        "workflow_interval_minutes": 5,
        "batch_size": 50,
        "auto_process_on_startup": True,
        "auto_suspend_when_no_data": True,
        "data_check_enabled": True,
        "min_batch_size": 2
    }
    test_api("PUT", "/config", config_data, "更新调度器配置")
    
    # 测试4: 验证配置更新
    time.sleep(1)
    test_api("GET", "/config", description="验证配置更新结果")
    
    # 测试5: 获取定时任务
    test_api("GET", "/jobs", description="获取定时任务列表")
    
    # 测试6: 获取工作流状态
    test_api("GET", "/workflow/status", description="获取工作流状态")
    
    # 测试7: 手动执行工作流阶段
    phases = ["data_sync", "classification", "answer_generation", "scoring"]
    for phase in phases:
        test_api("POST", f"/workflow/phases/{phase}/execute", description=f"手动执行{phase}阶段")
        time.sleep(0.5)  # 避免请求过快
    
    # 测试8: 启用/禁用调度器
    test_api("POST", "/enable", description="启用调度器")
    time.sleep(1)
    test_api("POST", "/disable", description="禁用调度器")
    
    print("\n" + "=" * 60)
    print("🎉 调度器配置管理API测试完成！")

if __name__ == "__main__":
    main()
