#!/usr/bin/env python3
"""
分类数据清理脚本
将非标准分类映射到标准分类，确保数据库中只有Mock API定义的16个标准分类
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.database import db
from app.models.question import Question
from app.services.classification_service import ClassificationService
from sqlalchemy import func


def analyze_classifications():
    """分析当前分类数据"""
    print("=== 当前分类数据分析 ===")
    
    classifications = db.session.query(
        Question.classification,
        func.count(Question.id).label('count')
    ).filter(
        Question.classification.isnot(None),
        Question.classification != ''
    ).group_by(Question.classification).order_by(
        func.count(Question.id).desc()
    ).all()
    
    print(f"总共发现 {len(classifications)} 个分类:")
    total_questions = 0
    
    for i, (classification, count) in enumerate(classifications, 1):
        print(f"  {i:2d}. {classification}: {count}个问题")
        total_questions += count
    
    print(f"\n总问题数: {total_questions}")
    return classifications


def get_standard_classifications():
    """获取Mock API定义的标准16分类"""
    return [
        '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
        '其他', '工程问题', '科学问题', '教育问题', '经济问题',
        '账户管理', '系统优化', '安全设置', '数据分析',
        '用户体验', '性能优化'
    ]


def identify_non_standard_classifications():
    """识别非标准分类"""
    print("\n=== 识别非标准分类 ===")
    
    standard_classifications = set(get_standard_classifications())
    current_classifications = ClassificationService.get_all_classifications()
    
    non_standard = []
    for classification in current_classifications:
        if classification not in standard_classifications:
            count = db.session.query(Question).filter(
                Question.classification == classification
            ).count()
            non_standard.append((classification, count))
    
    if non_standard:
        print(f"发现 {len(non_standard)} 个非标准分类:")
        for classification, count in non_standard:
            print(f"  - {classification}: {count}个问题")
    else:
        print("所有分类都是标准分类")
    
    return non_standard


def get_classification_mapping():
    """定义非标准分类到标准分类的映射关系"""
    return {
        '支付问题': '账户管理',
        '概念问题': '其他',
        '产品咨询': '产品使用',
        '使用指导': '产品使用',
        '故障报告': '故障排查',
        # 可以根据需要添加更多映射关系
    }


def clean_non_standard_classifications(dry_run=True):
    """清理非标准分类"""
    print(f"\n=== {'模拟' if dry_run else '执行'}数据清理 ===")
    
    mapping = get_classification_mapping()
    total_updated = 0
    
    for old_classification, new_classification in mapping.items():
        count = db.session.query(Question).filter(
            Question.classification == old_classification
        ).count()
        
        if count > 0:
            print(f"{'将要' if dry_run else '正在'}将 {count} 个'{old_classification}'问题重新分类为'{new_classification}'")
            
            if not dry_run:
                updated = db.session.query(Question).filter(
                    Question.classification == old_classification
                ).update({'classification': new_classification})
                
                total_updated += updated
                print(f"  实际更新了 {updated} 个问题")
        else:
            print(f"未找到'{old_classification}'分类的问题")
    
    if not dry_run and total_updated > 0:
        db.session.commit()
        print(f"\n数据清理完成，总共更新了 {total_updated} 个问题")
    elif dry_run:
        print(f"\n模拟清理完成，预计将更新 {sum(db.session.query(Question).filter(Question.classification == old).count() for old in mapping.keys())} 个问题")
    else:
        print("\n没有需要清理的数据")


def validate_after_cleanup():
    """清理后验证数据"""
    print("\n=== 清理后数据验证 ===")
    
    standard_classifications = set(get_standard_classifications())
    current_classifications = ClassificationService.get_all_classifications()
    
    non_standard = [c for c in current_classifications if c not in standard_classifications]
    
    if non_standard:
        print(f"警告：仍然存在 {len(non_standard)} 个非标准分类:")
        for classification in non_standard:
            count = db.session.query(Question).filter(
                Question.classification == classification
            ).count()
            print(f"  - {classification}: {count}个问题")
        return False
    else:
        print("✓ 所有分类都是标准分类")
        return True


def backup_data():
    """备份数据（可选）"""
    print("\n=== 数据备份建议 ===")
    print("建议在执行清理前备份数据库:")
    print("  pg_dump -h localhost -U your_user -d your_database > backup_before_cleanup.sql")
    print("或者创建问题表的备份:")
    print("  CREATE TABLE questions_backup AS SELECT * FROM questions;")


def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print("分类数据清理工具")
        print("=" * 50)
        
        # 1. 分析当前数据
        current_classifications = analyze_classifications()
        
        # 2. 识别非标准分类
        non_standard = identify_non_standard_classifications()
        
        if not non_standard:
            print("\n✓ 数据库中所有分类都是标准分类，无需清理")
            return
        
        # 3. 显示标准分类
        print(f"\n=== Mock API标准16分类 ===")
        standard = get_standard_classifications()
        for i, classification in enumerate(standard, 1):
            print(f"  {i:2d}. {classification}")
        
        # 4. 显示映射关系
        print(f"\n=== 分类映射关系 ===")
        mapping = get_classification_mapping()
        for old, new in mapping.items():
            print(f"  {old} → {new}")
        
        # 5. 备份建议
        backup_data()
        
        # 6. 模拟清理
        clean_non_standard_classifications(dry_run=True)
        
        # 7. 询问是否执行实际清理
        print("\n" + "=" * 50)
        response = input("是否执行实际的数据清理？(y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n执行实际数据清理...")
            clean_non_standard_classifications(dry_run=False)
            
            # 8. 验证清理结果
            validate_after_cleanup()
            
            # 9. 显示最终结果
            print("\n=== 清理后数据分析 ===")
            analyze_classifications()
        else:
            print("\n取消数据清理操作")


if __name__ == '__main__':
    main()
