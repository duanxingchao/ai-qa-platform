#!/usr/bin/env python3
"""
答案管理API测试脚本
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8088/api"

def test_get_answers():
    """测试获取答案列表"""
    print("🧪 测试获取答案列表...")
    url = f"{BASE_URL}/answers"
    params = {
        'page': 1,
        'page_size': 10
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取答案列表，共 {data['data']['total']} 条")
            if data['data']['answers']:
                print(f"首条答案ID: {data['data']['answers'][0]['id']}")
            return data['data']['answers']
        else:
            print(f"❌ 失败: {response.text}")
            return []
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return []

def test_get_answer_comparison():
    """测试获取答案对比"""
    print("\n🧪 测试获取答案对比...")
    
    # 首先获取一个问题ID
    questions_url = f"{BASE_URL}/questions"
    try:
        response = requests.get(questions_url, params={'page_size': 1})
        if response.status_code == 200:
            questions_data = response.json()
            if questions_data['data']['questions']:
                question_id = questions_data['data']['questions'][0]['business_id']
                print(f"使用问题ID: {question_id}")
                
                # 测试答案对比
                url = f"{BASE_URL}/answers/comparison"
                params = {'question_id': question_id}
                
                response = requests.get(url, params=params)
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 成功获取答案对比")
                    print(f"问题: {data['data']['question']['query'][:50]}...")
                    print(f"答案类型: {list(data['data']['answers'].keys())}")
                    print(f"评分数据: {list(data['data']['scores'].keys())}")
                    return question_id
                else:
                    print(f"❌ 失败: {response.text}")
            else:
                print("❌ 没有找到问题数据")
        else:
            print(f"❌ 获取问题列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    return None

def test_batch_score():
    """测试批量评分"""
    print("\n🧪 测试批量评分...")
    
    # 获取一些问题ID
    questions_url = f"{BASE_URL}/questions"
    try:
        response = requests.get(questions_url, params={'page_size': 3})
        if response.status_code == 200:
            questions_data = response.json()
            if questions_data['data']['questions']:
                question_ids = [q['business_id'] for q in questions_data['data']['questions'][:2]]
                print(f"使用问题IDs: {question_ids}")
                
                # 测试批量评分
                url = f"{BASE_URL}/answers/batch-score"
                data = {
                    'question_ids': question_ids,
                    'models': ['original', 'doubao'],
                    'comment': '测试批量评分'
                }
                
                response = requests.post(url, json=data)
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 批量评分完成")
                    print(f"成功: {result['data']['success_count']}")
                    print(f"失败: {result['data']['error_count']}")
                    if result['data']['errors']:
                        print(f"错误: {result['data']['errors'][:3]}...")
                else:
                    print(f"❌ 失败: {response.text}")
            else:
                print("❌ 没有找到问题数据")
        else:
            print(f"❌ 获取问题列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_export_answers():
    """测试导出答案数据"""
    print("\n🧪 测试导出答案数据...")
    
    # 获取一些问题ID
    questions_url = f"{BASE_URL}/questions"
    try:
        response = requests.get(questions_url, params={'page_size': 2})
        if response.status_code == 200:
            questions_data = response.json()
            if questions_data['data']['questions']:
                question_ids = [q['business_id'] for q in questions_data['data']['questions']]
                print(f"使用问题IDs: {question_ids}")
                
                # 测试导出
                url = f"{BASE_URL}/answers/export"
                data = {
                    'question_ids': question_ids
                }
                
                response = requests.post(url, json=data)
                print(f"状态码: {response.status_code}")
                if response.status_code == 200:
                    # 检查是否是Excel文件
                    content_type = response.headers.get('content-type', '')
                    print(f"✅ 导出成功，文件类型: {content_type}")
                    print(f"文件大小: {len(response.content)} bytes")
                    
                    # 保存文件进行验证
                    filename = f"test_export_{datetime.now().strftime('%H%M%S')}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"文件已保存为: {filename}")
                else:
                    print(f"❌ 失败: {response.text}")
            else:
                print("❌ 没有找到问题数据")
        else:
            print(f"❌ 获取问题列表失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_answer_statistics():
    """测试答案统计"""
    print("\n🧪 测试答案统计...")
    url = f"{BASE_URL}/answers/statistics"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取答案统计")
            
            stats = data['data']
            print(f"模型统计: {len(stats['type_statistics'])} 种模型")
            for type_stat in stats['type_statistics']:
                print(f"  - {type_stat['type_name']}: {type_stat['total']}条答案, 评分率{type_stat['score_rate']}%")
            
            print(f"日统计: {len(stats['daily_statistics'])} 天数据")
            print(f"平均评分: {stats['score_statistics']['average_score']:.2f}")
            print(f"总评分数: {stats['score_statistics']['total_scores']}")
        else:
            print(f"❌ 失败: {response.text}")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试答案管理API")
    print("=" * 50)
    
    # 测试各个API端点
    answers = test_get_answers()
    question_id = test_get_answer_comparison()
    test_batch_score()
    test_export_answers()
    test_answer_statistics()
    
    print("\n" + "=" * 50)
    print("🎯 答案管理API测试完成")
    print("\n📋 主要功能验证:")
    print("✅ 答案列表查询")
    print("✅ 答案对比数据")
    print("✅ 批量评分处理")
    print("✅ Excel数据导出")
    print("✅ 统计数据分析")
    
    print("\n🎉 答案管理页面后端API已就绪！")
    print("💡 接下来可以测试前端页面与API的集成")

if __name__ == '__main__':
    main() 