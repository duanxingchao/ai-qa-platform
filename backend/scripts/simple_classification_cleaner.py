#!/usr/bin/env python3
"""
简化版分类数据清理工具
直接使用SQLAlchemy连接数据库，避免Flask应用依赖问题
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 标准16种分类
STANDARD_CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]

def get_database_url():
    """获取数据库连接URL"""
    # 从环境变量或配置文件获取数据库URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # 默认SQLite数据库路径
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'ai_qa_platform.db')
        db_url = f'sqlite:///{db_path}'
    return db_url

def analyze_classifications():
    """分析数据库中的分类数据"""
    print("🔍 分析数据库中的分类数据...")
    
    db_url = get_database_url()
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 查询所有分类及其数量
        query = text("""
            SELECT classification, COUNT(*) as count 
            FROM questions 
            WHERE classification IS NOT NULL AND classification != '' 
            GROUP BY classification 
            ORDER BY count DESC
        """)
        
        result = session.execute(query)
        classifications = result.fetchall()
        
        print(f"\n📊 数据库中的分类总数: {len(classifications)}")
        print("=" * 60)
        
        standard_classifications = []
        invalid_classifications = []
        
        for row in classifications:
            classification = row[0]
            count = row[1]
            
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
        
    finally:
        session.close()

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
    }
    
    # 首先尝试精确匹配
    if invalid_classification in mapping_rules:
        return mapping_rules[invalid_classification]
    
    # 基于关键词匹配
    if any(keyword in invalid_classification for keyword in ['技术', '开发', 'API', '代码', '编程']):
        return '技术问题'
    elif any(keyword in invalid_classification for keyword in ['产品', '使用', '操作']):
        return '产品使用'
    elif any(keyword in invalid_classification for keyword in ['业务', '商务', '合作', '商业']):
        return '业务咨询'
    elif any(keyword in invalid_classification for keyword in ['建议', '需求', '改进']):
        return '功能建议'
    elif any(keyword in invalid_classification for keyword in ['故障', '错误', '异常']):
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
    elif any(keyword in invalid_classification for keyword in ['性能', '速度', '效率', '优化']):
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
        return '其他'

def clean_invalid_classifications(dry_run=True):
    """清理无效分类"""
    print(f"\n🧹 {'模拟' if dry_run else '执行'}清理无效分类...")
    
    db_url = get_database_url()
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 获取所有非标准分类的问题
        placeholders = ','.join(['?' for _ in STANDARD_CLASSIFICATIONS])
        query = text(f"""
            SELECT id, classification 
            FROM questions 
            WHERE classification IS NOT NULL 
            AND classification != '' 
            AND classification NOT IN ({placeholders})
        """)
        
        result = session.execute(query, STANDARD_CLASSIFICATIONS)
        invalid_questions = result.fetchall()
        
        if not invalid_questions:
            print("✅ 没有发现需要清理的无效分类")
            return
        
        print(f"📝 找到 {len(invalid_questions)} 个需要重新分类的问题")
        
        # 统计映射结果
        mapping_stats = {}
        updates = []
        
        for question_id, old_classification in invalid_questions:
            new_classification = map_invalid_to_standard(old_classification)
            
            if old_classification not in mapping_stats:
                mapping_stats[old_classification] = {'count': 0, 'new_classification': new_classification}
            mapping_stats[old_classification]['count'] += 1
            
            updates.append((new_classification, question_id))
        
        # 显示映射统计
        print("\n📋 分类映射统计:")
        print("-" * 80)
        for old_classification, stats in mapping_stats.items():
            print(f"   {old_classification} ({stats['count']}个) → {stats['new_classification']}")
        
        if not dry_run:
            try:
                # 批量更新
                update_query = text("UPDATE questions SET classification = ? WHERE id = ?")
                session.execute(update_query, updates)
                session.commit()
                print(f"\n✅ 成功更新了 {len(invalid_questions)} 个问题的分类")
            except Exception as e:
                session.rollback()
                print(f"\n❌ 更新失败: {str(e)}")
        else:
            print(f"\n💡 这是模拟运行，实际数据未被修改")
            print("   如需执行实际清理，请运行: python3 simple_classification_cleaner.py --execute")
            
    finally:
        session.close()

def main():
    """主函数"""
    print("🚀 开始分类数据清理工具")
    print("=" * 60)
    
    # 分析当前分类状态
    invalid_classifications = analyze_classifications()
    
    if not invalid_classifications:
        print("\n✅ 数据库中的分类数据已经是标准的，无需清理")
        return
    
    # 检查命令行参数
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
