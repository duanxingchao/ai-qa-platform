#!/usr/bin/env python3
"""
验证清理后API返回的数据
"""

import requests
import json
from datetime import datetime

def test_display_api_after_cleanup():
    """测试清理后的大屏API"""
    print(f"=== 测试清理后的大屏API ===")
    
    try:
        response = requests.get('http://localhost:8088/api/display/dashboard', timeout=10)
        print(f"📡 API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API响应成功: {data.get('success', False)}")
            
            if data.get('success') and data.get('data'):
                api_data = data['data']
                
                # 检查处理流程数据
                if 'process_flow' in api_data:
                    process_flow = api_data['process_flow']
                    if 'stages' in process_flow:
                        stages = process_flow['stages']
                        print(f"\n🔍 处理流程数据:")
                        for stage in stages:
                            name = stage.get('name', 'Unknown')
                            count = stage.get('count', 0)
                            rate = stage.get('rate', 0)
                            status = stage.get('status', 'Unknown')
                            print(f"   - {name}: {count} 条 ({rate}%) - {status}")
                
                # 检查核心指标
                if 'core_metrics' in api_data:
                    metrics = api_data['core_metrics']
                    print(f"\n📊 核心指标:")
                    for key, value in metrics.items():
                        print(f"   - {key}: {value}")
                
                # 检查热门分类
                if 'hot_categories' in api_data:
                    categories = api_data['hot_categories']
                    total_count = categories.get('total_count', 0)
                    time_range = categories.get('time_range', 'Unknown')
                    print(f"\n🏷️  热门分类 ({time_range}): 总计 {total_count} 条")
                    
                    categories_list = categories.get('categories', [])
                    for cat in categories_list[:5]:  # 只显示前5个
                        name = cat.get('name', 'Unknown')
                        count = cat.get('count', 0)
                        percentage = cat.get('percentage', 0)
                        print(f"   - {name}: {count} 条 ({percentage}%)")
                
                # 检查24小时趋势
                if 'trends_24h' in api_data:
                    trends = api_data['trends_24h']
                    print(f"\n📈 24小时趋势:")
                    for trend in trends[-3:]:  # 只显示最后3天
                        time_str = trend.get('time', 'Unknown')
                        questions = trend.get('questions', 0)
                        answers = trend.get('answers', 0)
                        scores = trend.get('scores', 0)
                        print(f"   - {time_str}: 问题{questions}, 答案{answers}, 评分{scores}")
                
            else:
                print("❌ API返回数据格式异常")
        else:
            print(f"❌ API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")

def main():
    """主函数"""
    print(f"=== 验证清理后API数据 ===")
    print(f"验证时间: {datetime.now()}")
    
    test_display_api_after_cleanup()
    
    print(f"\n=== 前端刷新指南 ===")
    print("🎯 现在请在浏览器中刷新前端页面:")
    print("   1. 按 Ctrl+F5 (Windows/Linux) 或 Cmd+Shift+R (Mac) 强制刷新")
    print("   2. 或者清除浏览器缓存后刷新")
    print("   3. 访问大屏页面: http://localhost:5173/display")
    print("   4. 系统流程中的数据应该显示为0或很小的数值")
    
    print(f"\n✅ 预期结果:")
    print("   - 同步&清洗: 应该显示0或历史数据")
    print("   - AI垂域分类: 应该显示0或很小数值")
    print("   - AI竞品跑测: 应该显示0或很小数值") 
    print("   - AI答案评测: 应该显示0或很小数值")
    print("   - 人工复核: 应该显示0")
    
    print(f"\n⚠️  注意:")
    print("   - 如果前端仍显示大数值，请清除浏览器缓存")
    print("   - 调度器已停止，数据不会再自动增长")
    print("   - 只清理了本周数据，历史数据仍保留")

if __name__ == "__main__":
    main()
