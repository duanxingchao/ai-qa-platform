#!/usr/bin/env python3
"""
执行SQL清理脚本
通过psycopg2直接连接PostgreSQL数据库执行清理
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """获取数据库连接"""
    # 从环境变量获取数据库连接信息
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
    
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_cleanup():
    """执行分类清理"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🧹 开始执行分类清理...")
        
        # 定义更新操作
        updates = [
            ("账户管理类", "账户管理"),
            ("技术问题类", "技术问题"),
            ("功能使用类", "产品使用"),
            ("系统配置类", "系统优化"),
            ("数据处理类", "数据分析")
        ]
        
        total_updated = 0
        
        for old_classification, new_classification in updates:
            # 先查询有多少条记录需要更新
            cursor.execute(
                "SELECT COUNT(*) as count FROM questions WHERE classification = %s",
                (old_classification,)
            )
            count_result = cursor.fetchone()
            count = count_result['count'] if count_result else 0
            
            if count > 0:
                # 执行更新
                cursor.execute(
                    "UPDATE questions SET classification = %s WHERE classification = %s",
                    (new_classification, old_classification)
                )
                updated_rows = cursor.rowcount
                total_updated += updated_rows
                print(f"   {old_classification} → {new_classification}: {updated_rows} 条记录")
            else:
                print(f"   {old_classification}: 没有找到需要更新的记录")
        
        # 提交事务
        conn.commit()
        print(f"\n✅ 清理完成，共更新了 {total_updated} 条记录")
        
        # 验证结果
        print("\n🔄 验证清理结果...")
        cursor.execute("""
            SELECT classification, COUNT(*) as count 
            FROM questions 
            WHERE classification IS NOT NULL AND classification != ''
            GROUP BY classification 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        print(f"📊 清理后的分类总数: {len(results)}")
        
        # 标准分类列表
        standard_classifications = [
            '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
            '其他', '工程问题', '科学问题', '教育问题', '经济问题',
            '账户管理', '系统优化', '安全设置', '数据分析',
            '用户体验', '性能优化'
        ]
        
        standard_found = []
        non_standard_found = []
        
        for row in results:
            classification = row['classification']
            count = row['count']
            if classification in standard_classifications:
                standard_found.append((classification, count))
            else:
                non_standard_found.append((classification, count))
        
        print(f"\n✅ 标准分类 ({len(standard_found)}个):")
        for classification, count in standard_found:
            print(f"   {classification}: {count}个问题")
        
        if non_standard_found:
            print(f"\n❌ 仍存在非标准分类 ({len(non_standard_found)}个):")
            for classification, count in non_standard_found:
                print(f"   {classification}: {count}个问题")
        else:
            print(f"\n🎉 所有分类都已标准化！")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 执行清理失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("🚀 开始执行SQL分类清理")
    print("=" * 60)
    
    # 检查是否为执行模式
    if '--execute' not in sys.argv:
        print("⚠️  这是模拟运行模式")
        print("   如需执行实际清理，请添加 --execute 参数")
        return
    
    success = execute_cleanup()
    
    if success:
        print("\n🎉 分类清理完成！")
        print("   现在可以刷新前端页面查看效果")
    else:
        print("\n❌ 分类清理失败")

if __name__ == '__main__':
    main()
