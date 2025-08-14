#!/usr/bin/env python3
"""
通过API清理分类数据的脚本
直接调用后端API来执行数据库操作
"""

import requests
import json
import sys

# 标准16种分类
STANDARD_CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]

# API基础URL
API_BASE_URL = "http://localhost:8088/api"

def get_current_classifications():
    """获取当前数据库中的所有分类"""
    try:
        response = requests.get(f"{API_BASE_URL}/display/ai-category-scores")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                categories = [item['category'] for item in data['data']['chart_data']]
                return categories
        return None
    except Exception as e:
        print(f"获取分类数据失败: {e}")
        return None

def map_invalid_to_standard(invalid_classification):
    """将无效分类映射到标准分类"""
    # 定义映射规则
    mapping_rules = {
        # 直接映射
        '技术问题类': '技术问题',
        '功能使用类': '产品使用',
        '数据处理类': '数据分析',
        '系统配置类': '系统优化',
        '账户管理类': '账户管理',
        
        # 其他可能的映射
        '产品咨询': '产品使用',
        '使用指南': '产品使用',
        '操作问题': '产品使用',
        '功能咨询': '功能建议',
        '新功能': '功能建议',
        '功能需求': '功能建议',
        '故障问题': '故障排查',
        '错误排查': '故障排查',
        '问题排查': '故障排查',
        '商务咨询': '业务咨询',
        '合作咨询': '业务咨询',
        '账号问题': '账户管理',
        '登录问题': '账户管理',
        '权限问题': '账户管理',
        '系统问题': '系统优化',
        '性能问题': '性能优化',
        '安全问题': '安全设置',
        '数据问题': '数据分析',
        '界面问题': '用户体验',
        'UI问题': '用户体验',
    }
    
    # 首先尝试精确匹配
    if invalid_classification in mapping_rules:
        return mapping_rules[invalid_classification]
    
    # 基于关键词匹配
    if any(keyword in invalid_classification for keyword in ['技术', '开发', 'API', '代码']):
        return '技术问题'
    elif any(keyword in invalid_classification for keyword in ['产品', '使用', '操作', '功能']):
        return '产品使用'
    elif any(keyword in invalid_classification for keyword in ['业务', '商务', '合作']):
        return '业务咨询'
    elif any(keyword in invalid_classification for keyword in ['建议', '需求', '改进']):
        return '功能建议'
    elif any(keyword in invalid_classification for keyword in ['故障', '错误', '异常']):
        return '故障排查'
    elif any(keyword in invalid_classification for keyword in ['账户', '账号', '登录']):
        return '账户管理'
    elif any(keyword in invalid_classification for keyword in ['系统', '配置']):
        return '系统优化'
    elif any(keyword in invalid_classification for keyword in ['安全', '防护']):
        return '安全设置'
    elif any(keyword in invalid_classification for keyword in ['数据', '统计', '分析']):
        return '数据分析'
    elif any(keyword in invalid_classification for keyword in ['体验', '界面', 'UI']):
        return '用户体验'
    elif any(keyword in invalid_classification for keyword in ['性能', '速度', '优化']):
        return '性能优化'
    elif any(keyword in invalid_classification for keyword in ['教育', '学习']):
        return '教育问题'
    elif any(keyword in invalid_classification for keyword in ['工程', '项目']):
        return '工程问题'
    elif any(keyword in invalid_classification for keyword in ['科学', '研究']):
        return '科学问题'
    elif any(keyword in invalid_classification for keyword in ['经济', '费用', '价格']):
        return '经济问题'
    else:
        return '其他'

def create_classification_cleanup_api():
    """创建一个临时的API端点来执行分类清理"""
    cleanup_code = '''
import sys
sys.path.append('/home/devbox/project/backend')

from app import create_app
from app.models.question import Question
from app.utils.database import db

# 标准分类
STANDARD_CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]

# 映射规则
MAPPING_RULES = {
    '技术问题类': '技术问题',
    '功能使用类': '产品使用',
    '数据处理类': '数据分析',
    '系统配置类': '系统优化',
    '账户管理类': '账户管理'
}

app = create_app()
with app.app_context():
    try:
        # 查找需要更新的问题
        questions_to_update = []
        for old_classification, new_classification in MAPPING_RULES.items():
            questions = Question.query.filter_by(classification=old_classification).all()
            for question in questions:
                questions_to_update.append((question.id, old_classification, new_classification))
                question.classification = new_classification
        
        if questions_to_update:
            db.session.commit()
            print(f"成功更新了 {len(questions_to_update)} 个问题的分类:")
            for question_id, old_class, new_class in questions_to_update:
                print(f"  问题ID {question_id}: {old_class} → {new_class}")
        else:
            print("没有找到需要更新的问题")
            
    except Exception as e:
        db.session.rollback()
        print(f"更新失败: {e}")
'''
    
    # 将清理代码写入临时文件
    with open('/tmp/cleanup_classifications.py', 'w', encoding='utf-8') as f:
        f.write(cleanup_code)
    
    return '/tmp/cleanup_classifications.py'

def main():
    """主函数"""
    print("🚀 开始分类数据清理工具")
    print("=" * 60)
    
    # 获取当前分类
    current_classifications = get_current_classifications()
    if not current_classifications:
        print("❌ 无法获取当前分类数据")
        return
    
    print(f"📊 当前数据库中的分类总数: {len(current_classifications)}")
    
    # 分析标准和非标准分类
    standard_classifications = [c for c in current_classifications if c in STANDARD_CLASSIFICATIONS]
    invalid_classifications = [c for c in current_classifications if c not in STANDARD_CLASSIFICATIONS]
    
    print(f"✅ 标准分类 ({len(standard_classifications)}个):")
    for classification in standard_classifications:
        print(f"   {classification}")
    
    print(f"\n❌ 非标准分类 ({len(invalid_classifications)}个):")
    mapping_plan = {}
    for classification in invalid_classifications:
        mapped = map_invalid_to_standard(classification)
        mapping_plan[classification] = mapped
        print(f"   {classification} → {mapped}")
    
    if not invalid_classifications:
        print("\n✅ 所有分类都是标准的，无需清理")
        return
    
    # 检查是否执行清理
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print(f"\n⚠️  这是模拟运行模式")
        print("   如需执行实际清理，请添加 --execute 参数")
        return
    
    print(f"\n🧹 执行分类清理...")
    
    # 创建并执行清理脚本
    cleanup_script = create_classification_cleanup_api()
    
    import subprocess
    try:
        result = subprocess.run(['python3', cleanup_script], 
                              capture_output=True, text=True, cwd='/home/devbox/project/backend')
        
        if result.returncode == 0:
            print("✅ 清理执行成功:")
            print(result.stdout)
        else:
            print("❌ 清理执行失败:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 执行清理脚本失败: {e}")
    
    # 验证清理结果
    print("\n🔄 验证清理结果...")
    updated_classifications = get_current_classifications()
    if updated_classifications:
        print(f"📊 清理后的分类总数: {len(updated_classifications)}")
        if len(updated_classifications) == 16:
            print("✅ 分类数量已恢复到标准的16种")
        else:
            print(f"⚠️  分类数量仍为 {len(updated_classifications)} 种，可能需要进一步清理")

if __name__ == '__main__':
    main()
