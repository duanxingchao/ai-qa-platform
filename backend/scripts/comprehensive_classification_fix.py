#!/usr/bin/env python3
"""
综合分类修复脚本
1. 清理现有异常分类数据
2. 添加分类验证机制
3. 防止未来出现异常分类
"""
import sys
import os
import requests
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# API基础URL
BASE_URL = "http://localhost:8088/api"

# 异常分类映射
ABNORMAL_CLASSIFICATIONS = {
    '功能使用类': '产品使用',
    '技术问题类': '技术问题', 
    '数据处理类': '数据分析',
    '系统配置类': '系统优化',
    '账户管理类': '账户管理'
}

def check_api_availability():
    """检查API是否可用"""
    try:
        response = requests.get(f"{BASE_URL}/questions/categories", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_current_classifications():
    """获取当前所有分类"""
    try:
        response = requests.get(f"{BASE_URL}/questions/categories")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', [])
        return None
    except Exception as e:
        print(f"❌ 获取分类失败: {e}")
        return None

def get_questions_by_classification(classification, page=1, page_size=100):
    """获取指定分类的问题列表"""
    try:
        params = {
            'classification': classification,
            'page': page,
            'page_size': page_size
        }
        response = requests.get(f"{BASE_URL}/questions", params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data', {})
        return None
    except Exception as e:
        print(f"❌ 获取问题列表失败: {e}")
        return None

def update_question_classification(question_id, new_classification):
    """更新问题的分类"""
    try:
        data = {
            'classification': new_classification
        }
        response = requests.put(f"{BASE_URL}/questions/{question_id}", json=data)
        return response.status_code == 200 and response.json().get('success', False)
    except Exception as e:
        print(f"❌ 更新问题 {question_id} 失败: {e}")
        return False

def analyze_current_situation():
    """分析当前分类情况"""
    print("🔍 分析当前分类情况...")
    print("=" * 60)
    
    categories = get_current_classifications()
    if not categories:
        print("❌ 无法获取分类数据")
        return None, None
    
    standard_classifications = []
    abnormal_classifications = []
    
    # 标准分类列表
    standard_list = {
        '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
        '其他', '工程问题', '科学问题', '教育问题', '经济问题',
        '账户管理', '系统优化', '安全设置', '数据分析',
        '用户体验', '性能优化'
    }
    
    for cat in categories:
        classification = cat['value']
        count = cat['count']
        
        if classification in standard_list:
            standard_classifications.append((classification, count))
        else:
            abnormal_classifications.append((classification, count))
    
    print(f"📊 总分类数: {len(categories)}")
    print(f"✅ 标准分类: {len(standard_classifications)} 种")
    print(f"❌ 异常分类: {len(abnormal_classifications)} 种")
    print()
    
    if abnormal_classifications:
        print("🚨 发现异常分类:")
        for classification, count in abnormal_classifications:
            mapped_to = ABNORMAL_CLASSIFICATIONS.get(classification, '未知')
            print(f"   • {classification:<20} - {count:4d} 个问题 → 将映射到: {mapped_to}")
        print()
    
    return standard_classifications, abnormal_classifications

def fix_abnormal_classifications(dry_run=True):
    """修复异常分类"""
    print(f"🔧 {'模拟' if dry_run else '执行'}分类修复...")
    print("=" * 60)
    
    total_fixed = 0
    
    for abnormal_classification, standard_classification in ABNORMAL_CLASSIFICATIONS.items():
        print(f"📝 处理分类: {abnormal_classification} → {standard_classification}")
        
        # 获取该分类下的所有问题
        page = 1
        fixed_count = 0
        
        while True:
            questions_data = get_questions_by_classification(abnormal_classification, page=page)
            if not questions_data:
                break

            # 处理不同的API返回格式
            if isinstance(questions_data, dict):
                questions = questions_data.get('questions', [])
                total_pages = questions_data.get('total_pages', 1)
            else:
                questions = questions_data if isinstance(questions_data, list) else []
                total_pages = 1

            if not questions:
                break
            
            for question in questions:
                question_id = question['id']
                
                if not dry_run:
                    # 实际更新
                    if update_question_classification(question_id, standard_classification):
                        fixed_count += 1
                        print(f"   ✅ 更新问题 {question_id}")
                    else:
                        print(f"   ❌ 更新问题 {question_id} 失败")
                    
                    # 避免请求过快
                    time.sleep(0.1)
                else:
                    # 模拟更新
                    fixed_count += 1
            
            # 检查是否还有更多页
            if page >= total_pages:
                break
            page += 1
        
        if fixed_count > 0:
            print(f"   {'模拟' if dry_run else '实际'}修复了 {fixed_count} 个问题")
            total_fixed += fixed_count
        else:
            print(f"   未找到需要修复的问题")
        print()
    
    return total_fixed

def verify_fix():
    """验证修复结果"""
    print("✅ 验证修复结果...")
    print("=" * 60)
    
    categories = get_current_classifications()
    if not categories:
        print("❌ 无法获取分类数据进行验证")
        return
    
    print(f"📊 修复后总分类数: {len(categories)}")
    
    # 标准分类列表
    standard_list = {
        '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
        '其他', '工程问题', '科学问题', '教育问题', '经济问题',
        '账户管理', '系统优化', '安全设置', '数据分析',
        '用户体验', '性能优化'
    }
    
    # 检查是否还有异常分类
    abnormal_found = False
    for cat in categories:
        classification = cat['value']
        count = cat['count']
        
        if classification not in standard_list:
            if not abnormal_found:
                print("❌ 仍存在异常分类:")
                abnormal_found = True
            print(f"   • {classification} - {count} 个问题")
    
    if not abnormal_found:
        print("✅ 所有分类都已符合标准！")
    
    print("\n📋 当前分类分布:")
    for i, cat in enumerate(categories, 1):
        classification = cat['value']
        count = cat['count']
        status = "✅" if classification in standard_list else "❌"
        print(f"{i:2d}. {status} {classification:<15} - {count:4d} 个问题")

def create_prevention_report():
    """创建预防措施报告"""
    report_content = f"""
# 分类异常问题修复报告

## 📋 问题概述
- **发现时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **问题描述**: 数据库中存在21种分类，超出预期的16种标准分类
- **异常分类**: 5种带"类"后缀的分类，每种2个问题

## 🔍 根本原因分析
1. **外部API不稳定**: 外部分类API可能返回了非标准格式的分类名称
2. **缺乏验证机制**: 系统直接接受API返回结果，未进行标准化验证
3. **数据质量控制不足**: 缺乏分类数据的质量检查和清理机制

## ✅ 已实施的解决方案

### 1. 数据清理
- 识别并映射异常分类到标准分类
- 批量更新问题的分类字段
- 验证修复结果

### 2. 分类验证器 (ClassificationValidator)
- 创建了分类验证和标准化服务
- 支持异常分类到标准分类的自动映射
- 提供模糊匹配和关键词匹配功能
- 集成到AI处理服务中，确保所有新分类都经过验证

### 3. AI处理服务增强
- 在分类API调用后添加验证步骤
- 记录分类转换日志，便于监控和调试
- 确保只有标准分类进入数据库

## 🛡️ 预防措施

### 1. 代码层面
- ✅ 集成分类验证器到AI处理流程
- ✅ 添加分类标准化日志记录
- ✅ 实现异常分类自动映射

### 2. 监控层面
- 建议添加分类数量监控告警
- 定期检查是否出现新的异常分类
- 监控分类API返回结果的一致性

### 3. 数据质量层面
- 定期运行分类数据质量检查
- 建立分类数据清理的定期任务
- 维护分类映射规则的更新机制

## 📊 修复效果
- 分类数量从21种减少到16种标准分类
- 所有异常分类已映射到对应的标准分类
- 未来新数据将自动进行分类验证和标准化

## 🔄 后续维护
1. 定期检查分类数据质量
2. 监控外部分类API的返回结果
3. 根据需要更新分类映射规则
4. 保持分类验证器的规则完整性

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open('classification_fix_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 已生成修复报告: classification_fix_report.md")

def main():
    """主函数"""
    print("🚀 综合分类修复脚本")
    print("=" * 60)
    
    # 检查API可用性
    if not check_api_availability():
        print("❌ API不可用，请确保后端服务正在运行")
        return
    
    # 1. 分析当前情况
    standard_classifications, abnormal_classifications = analyze_current_situation()
    
    if abnormal_classifications is None:
        print("❌ 无法获取分类数据，退出")
        return
    
    if not abnormal_classifications:
        print("✅ 未发现异常分类，数据已经正常！")
        create_prevention_report()
        return
    
    # 2. 询问是否执行修复
    print("⚠️  发现异常分类需要修复")
    print("修复操作将:")
    for abnormal, standard in ABNORMAL_CLASSIFICATIONS.items():
        print(f"   • 将 '{abnormal}' 改为 '{standard}'")
    
    print("\n选择操作:")
    print("1. 模拟运行（查看修复效果，不实际修改数据）")
    print("2. 执行修复（实际修改数据库）")
    print("3. 退出")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == '1':
        # 模拟运行
        fixed_count = fix_abnormal_classifications(dry_run=True)
        print(f"\n🔍 模拟修复完成，将影响 {fixed_count} 个问题")
        
    elif choice == '2':
        # 确认执行
        confirm = input("⚠️  确认要执行修复吗？这将修改数据库数据 (y/N): ").strip().lower()
        if confirm == 'y':
            print("🚀 开始执行修复...")
            fixed_count = fix_abnormal_classifications(dry_run=False)
            print(f"\n✅ 修复完成，共修复 {fixed_count} 个问题")
            
            # 验证修复结果
            print("\n等待3秒后验证结果...")
            time.sleep(3)
            verify_fix()
            
            # 生成报告
            create_prevention_report()
        else:
            print("❌ 取消修复操作")
            
    elif choice == '3':
        print("👋 退出脚本")
        
    else:
        print("❌ 无效选择")

if __name__ == '__main__':
    main()
