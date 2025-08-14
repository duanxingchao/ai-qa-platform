#!/usr/bin/env python3
"""
清理数据库中的无效分类数据
将非标准分类的问题重新分类为标准的16种分类之一
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.question import Question
from app.utils.database import db
import random

# Mock分类API定义的标准16种分类
STANDARD_CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]

def analyze_classifications():
    """分析数据库中的分类数据"""
    print("🔍 分析数据库中的分类数据...")
    
    # 获取所有不同的分类及其数量
    classifications = db.session.query(
        Question.classification,
        db.func.count(Question.id).label('count')
    ).filter(
        Question.classification.isnot(None),
        Question.classification != ''
    ).group_by(Question.classification).order_by(db.func.count(Question.id).desc()).all()
    
    print(f"\n📊 数据库中的分类总数: {len(classifications)}")
    print("=" * 60)
    
    standard_classifications = []
    invalid_classifications = []
    
    for classification, count in classifications:
        if classification in STANDARD_CLASSIFICATIONS:
            standard_classifications.append((classification, count))
        else:
            invalid_classifications.append((classification, count))
    
    print(f"✅ 标准分类 ({len(standard_classifications)}个):")
    for classification, count in standard_classifications:
        print(f"   {classification}: {count}个问题")
    
    print(f"\n❌ 非标准分类 ({len(invalid_classifications)}个):")
    total_invalid_questions = 0
    for classification, count in invalid_classifications:
        print(f"   {classification}: {count}个问题")
        total_invalid_questions += count
    
    print(f"\n📈 统计摘要:")
    print(f"   - 标准分类数量: {len(standard_classifications)}")
    print(f"   - 非标准分类数量: {len(invalid_classifications)}")
    print(f"   - 需要重新分类的问题数: {total_invalid_questions}")
    
    return invalid_classifications

def map_invalid_to_standard(invalid_classification):
    """将无效分类映射到标准分类"""
    # 定义映射规则
    mapping_rules = {
        # 技术相关
        '技术问题类': '技术问题',
        '技术支持': '技术问题',
        '开发问题': '技术问题',
        '编程问题': '技术问题',
        'API问题': '技术问题',
        '集成问题': '技术问题',
        
        # 产品使用相关
        '产品咨询': '产品使用',
        '使用指南': '产品使用',
        '操作问题': '产品使用',
        '使用方法': '产品使用',
        
        # 功能相关
        '功能咨询': '功能建议',
        '新功能': '功能建议',
        '功能需求': '功能建议',
        '改进建议': '功能建议',
        
        # 故障相关
        '故障问题': '故障排查',
        '错误排查': '故障排查',
        '问题排查': '故障排查',
        '异常处理': '故障排查',
        
        # 业务相关
        '商务咨询': '业务咨询',
        '合作咨询': '业务咨询',
        '商业问题': '业务咨询',
        
        # 账户相关
        '账号问题': '账户管理',
        '登录问题': '账户管理',
        '权限问题': '账户管理',
        
        # 系统相关
        '系统问题': '系统优化',
        '性能问题': '性能优化',
        '优化建议': '性能优化',
        
        # 安全相关
        '安全问题': '安全设置',
        '权限设置': '安全设置',
        
        # 数据相关
        '数据问题': '数据分析',
        '统计问题': '数据分析',
        '报表问题': '数据分析',
        
        # 用户体验相关
        '界面问题': '用户体验',
        'UI问题': '用户体验',
        '交互问题': '用户体验',
        
        # 教育相关
        '学习问题': '教育问题',
        '培训问题': '教育问题',
        
        # 工程相关
        '工程咨询': '工程问题',
        '项目问题': '工程问题',
        
        # 科学相关
        '研究问题': '科学问题',
        '学术问题': '科学问题',
        
        # 经济相关
        '费用问题': '经济问题',
        '价格咨询': '经济问题',
        '成本问题': '经济问题'
    }
    
    # 首先尝试精确匹配
    if invalid_classification in mapping_rules:
        return mapping_rules[invalid_classification]
    
    # 然后尝试模糊匹配
    invalid_lower = invalid_classification.lower()
    for key, value in mapping_rules.items():
        if key.lower() in invalid_lower or invalid_lower in key.lower():
            return value
    
    # 基于关键词匹配
    if any(keyword in invalid_classification for keyword in ['技术', '开发', 'API', '代码', '编程']):
        return '技术问题'
    elif any(keyword in invalid_classification for keyword in ['产品', '使用', '操作', '功能']):
        return '产品使用'
    elif any(keyword in invalid_classification for keyword in ['业务', '商务', '合作', '商业']):
        return '业务咨询'
    elif any(keyword in invalid_classification for keyword in ['建议', '需求', '改进', '优化']):
        return '功能建议'
    elif any(keyword in invalid_classification for keyword in ['故障', '错误', '异常', '问题']):
        return '故障排查'
    elif any(keyword in invalid_classification for keyword in ['账户', '账号', '登录', '权限']):
        return '账户管理'
    elif any(keyword in invalid_classification for keyword in ['系统', '配置']):
        return '系统优化'
    elif any(keyword in invalid_classification for keyword in ['安全', '防护']):
        return '安全设置'
    elif any(keyword in invalid_classification for keyword in ['数据', '统计', '分析', '报表']):
        return '数据分析'
    elif any(keyword in invalid_classification for keyword in ['体验', '界面', 'UI', '交互']):
        return '用户体验'
    elif any(keyword in invalid_classification for keyword in ['性能', '速度', '效率']):
        return '性能优化'
    elif any(keyword in invalid_classification for keyword in ['教育', '学习', '培训']):
        return '教育问题'
    elif any(keyword in invalid_classification for keyword in ['工程', '项目']):
        return '工程问题'
    elif any(keyword in invalid_classification for keyword in ['科学', '研究', '学术']):
        return '科学问题'
    elif any(keyword in invalid_classification for keyword in ['经济', '费用', '价格', '成本']):
        return '经济问题'
    else:
        # 如果都不匹配，随机分配到一个合适的分类
        return '其他'

def clean_invalid_classifications(dry_run=True):
    """清理无效分类"""
    print(f"\n🧹 {'模拟' if dry_run else '执行'}清理无效分类...")
    
    # 获取所有非标准分类的问题
    invalid_questions = db.session.query(Question).filter(
        Question.classification.isnot(None),
        Question.classification != '',
        ~Question.classification.in_(STANDARD_CLASSIFICATIONS)
    ).all()
    
    if not invalid_questions:
        print("✅ 没有发现需要清理的无效分类")
        return
    
    print(f"📝 找到 {len(invalid_questions)} 个需要重新分类的问题")
    
    # 统计映射结果
    mapping_stats = {}
    
    for question in invalid_questions:
        old_classification = question.classification
        new_classification = map_invalid_to_standard(old_classification)
        
        if old_classification not in mapping_stats:
            mapping_stats[old_classification] = {'count': 0, 'new_classification': new_classification}
        mapping_stats[old_classification]['count'] += 1
        
        if not dry_run:
            question.classification = new_classification
    
    # 显示映射统计
    print("\n📋 分类映射统计:")
    print("-" * 80)
    for old_classification, stats in mapping_stats.items():
        print(f"   {old_classification} ({stats['count']}个) → {stats['new_classification']}")
    
    if not dry_run:
        try:
            db.session.commit()
            print(f"\n✅ 成功更新了 {len(invalid_questions)} 个问题的分类")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ 更新失败: {str(e)}")
    else:
        print(f"\n💡 这是模拟运行，实际数据未被修改")
        print("   如需执行实际清理，请运行: python clean_invalid_classifications.py --execute")

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始分类数据清理工具")
        print("=" * 60)
        
        # 分析当前分类状态
        invalid_classifications = analyze_classifications()
        
        if not invalid_classifications:
            print("\n✅ 数据库中的分类数据已经是标准的，无需清理")
            return
        
        # 检查命令行参数
        import sys
        dry_run = '--execute' not in sys.argv
        
        if dry_run:
            print(f"\n⚠️  这是模拟运行模式")
            print("   如需执行实际清理，请添加 --execute 参数")
        
        # 执行清理
        clean_invalid_classifications(dry_run=dry_run)
        
        if not dry_run:
            print("\n🔄 重新分析清理后的分类数据...")
            analyze_classifications()

if __name__ == '__main__':
    main()
