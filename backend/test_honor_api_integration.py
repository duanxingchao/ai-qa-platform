#!/usr/bin/env python3
"""
荣耀API集成测试脚本
测试分类API和评分API的完整工作流程
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from app.services.api_client import APIClientFactory
from app.config import Config

def test_classification_api():
    """测试分类API"""
    print("🔍 测试分类API...")
    
    try:
        # 获取分类客户端
        client = APIClientFactory.get_classification_client()
        
        # 测试分类
        result = client.classify_question(
            question="如何优化数据库查询性能？",
            answer="可以通过添加索引、优化SQL语句等方式提升性能",
            user_id="00031559"
        )
        
        print(f"✅ 分类API测试成功")
        print(f"   问题: 如何优化数据库查询性能？")
        print(f"   分类结果: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 分类API测试失败: {str(e)}")
        return False

def test_scoring_api():
    """测试评分API"""
    print("\n📊 测试评分API...")
    
    try:
        # 获取评分客户端
        client = APIClientFactory.get_score_client()
        
        # 测试评分
        results = client.score_multiple_answers(
            question="如何优化数据库查询性能？",
            our_answer="可以通过添加索引、优化SQL语句等方式提升性能",
            doubao_answer="建议使用索引优化、查询缓存、分区表等技术手段",
            xiaotian_answer="从索引设计、SQL优化、硬件配置等多个维度进行优化",
            classification="技术问题"
        )
        
        print(f"✅ 评分API测试成功")
        print(f"   问题: 如何优化数据库查询性能？")
        print(f"   评分结果数量: {len(results)}")
        
        for i, result in enumerate(results):
            model_name = result.get('模型名称', f'模型{i+1}')
            print(f"   {model_name}: {json.dumps(result, ensure_ascii=False, indent=4)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 评分API测试失败: {str(e)}")
        return False

def test_direct_api_calls():
    """直接测试API调用"""
    print("\n🌐 直接测试API调用...")
    
    # 测试分类API
    print("测试分类API直接调用...")
    try:
        response = requests.post(
            Config.CLASSIFY_API_URL,
            json={
                "inputs": {
                    "QUERY": "如何优化数据库查询性能？",
                    "ANSWER": "可以通过添加索引、优化SQL语句等方式提升性能"
                },
                "response_mode": "blocking",
                "user": "00031559"
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 分类API直接调用成功: {data}")
        else:
            print(f"❌ 分类API直接调用失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 分类API直接调用异常: {str(e)}")
    
    # 测试评分API
    print("\n测试评分API直接调用...")
    try:
        response = requests.post(
            Config.SCORE_API_URL,
            json={
                "inputs": {
                    "QUERY": "如何优化数据库查询性能？",
                    "ANSWER": "可以通过添加索引、优化SQL语句等方式提升性能",
                    "ANSWER_DOUBAO": "建议使用索引优化、查询缓存、分区表等技术手段",
                    "ANSWER_XIAOTIAN": "从索引设计、SQL优化、硬件配置等多个维度进行优化",
                    "RESORT": "技术问题"
                },
                "response_mode": "blocking",
                "user": "user"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {Config.SCORE_API_KEY}"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 评分API直接调用成功")
            if 'data' in data and 'outputs' in data['data']:
                text_result = data['data']['outputs']['text']
                score_results = json.loads(text_result)
                print(f"   评分结果: {json.dumps(score_results, ensure_ascii=False, indent=2)}")
            else:
                print(f"   响应数据: {data}")
        else:
            print(f"❌ 评分API直接调用失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 评分API直接调用异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始荣耀API集成测试")
    print(f"分类API URL: {Config.CLASSIFY_API_URL}")
    print(f"评分API URL: {Config.SCORE_API_URL}")
    print(f"评分API Key: {Config.SCORE_API_KEY}")
    print("=" * 60)
    
    # 测试API客户端
    classification_success = test_classification_api()
    scoring_success = test_scoring_api()
    
    # 直接测试API调用
    test_direct_api_calls()
    
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    print(f"   分类API客户端: {'✅ 成功' if classification_success else '❌ 失败'}")
    print(f"   评分API客户端: {'✅ 成功' if scoring_success else '❌ 失败'}")
    
    if classification_success and scoring_success:
        print("\n🎉 所有测试通过！荣耀API集成配置正确。")
        print("💡 现在可以在生产环境中使用以下配置:")
        print("   export CLASSIFY_API_URL='http://aipipeline.ipd.hihonor.com/v1/workflows/run'")
        print("   export SCORE_API_URL='http://aipipeline.ipd.hihonor.com/v1/workflows/run'")
        print("   export SCORE_API_KEY='app-SXgaGHIf25NtJXEFmc9ecRSc'")
    else:
        print("\n⚠️  部分测试失败，请检查配置和API服务状态。")

if __name__ == "__main__":
    main()
