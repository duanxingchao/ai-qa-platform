"""
API测试脚本
用于测试基础API是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_apis():
    """测试所有API端点"""
    print("开始测试API...")
    
    # 测试同步API
    print("\n1. 测试同步API")
    try:
        # 获取同步状态
        response = requests.get(f"{BASE_URL}/sync/status")
        print(f"GET /sync/status: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 触发同步
        response = requests.post(f"{BASE_URL}/sync/trigger")
        print(f"\nPOST /sync/trigger: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"同步API测试失败: {str(e)}")
    
    # 测试问题API
    print("\n2. 测试问题API")
    try:
        # 获取问题列表
        response = requests.get(f"{BASE_URL}/questions?page=1&page_size=10")
        print(f"GET /questions: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 获取问题详情
        response = requests.get(f"{BASE_URL}/questions/1")
        print(f"\nGET /questions/1: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"问题API测试失败: {str(e)}")
    
    # 测试处理API
    print("\n3. 测试处理API")
    try:
        # 清洗数据
        response = requests.post(f"{BASE_URL}/process/clean")
        print(f"POST /process/clean: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 分类
        response = requests.post(f"{BASE_URL}/process/classify")
        print(f"\nPOST /process/classify: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 生成答案
        response = requests.post(f"{BASE_URL}/process/generate")
        print(f"\nPOST /process/generate: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 评分
        response = requests.post(f"{BASE_URL}/process/score")
        print(f"\nPOST /process/score: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"处理API测试失败: {str(e)}")
    
    print("\nAPI测试完成！")

if __name__ == '__main__':
    test_apis() 