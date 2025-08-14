#!/usr/bin/env python3
"""
修复table1表结构 - 移除classification字段
根据正确的系统设计，table1表不应该包含classification字段
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """获取数据库连接"""
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
    
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def check_table1_structure():
    """检查table1表当前结构"""
    conn = get_db_connection()
    if not conn:
        return False, []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'table1'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ table1表不存在")
            return False, []
        
        # 获取表结构
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'table1'
            ORDER BY ordinal_position;
        """)
        
        columns = [row['column_name'] for row in cursor.fetchall()]
        
        print(f"📋 table1表当前字段: {', '.join(columns)}")
        
        has_classification = 'classification' in columns
        print(f"🏷️ 包含classification字段: {'是' if has_classification else '否'}")
        
        return True, columns
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        return False, []
    finally:
        cursor.close()
        conn.close()

def fix_table1_structure(dry_run=True):
    """修复table1表结构"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 检查classification字段是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'table1'
                AND column_name = 'classification'
            );
        """)
        
        has_classification = cursor.fetchone()[0]
        
        if not has_classification:
            print("✅ table1表已经没有classification字段，无需修复")
            return True
        
        print("🔧 发现table1表包含classification字段，需要移除")
        
        if dry_run:
            print("💡 这是模拟运行，实际表结构未被修改")
            print("   如需执行实际修复，请添加 --execute 参数")
            return True
        
        # 获取classification字段中的数据统计（用于记录）
        cursor.execute("""
            SELECT classification, COUNT(*) as count 
            FROM table1 
            WHERE classification IS NOT NULL AND classification != ''
            GROUP BY classification 
            ORDER BY count DESC
        """)
        
        classification_data = cursor.fetchall()
        
        if classification_data:
            print("📊 即将删除的classification字段数据分布:")
            for row in classification_data:
                print(f"   {row['classification']}: {row['count']}条记录")
        
        # 删除classification字段
        print("🗑️ 正在删除classification字段...")
        cursor.execute("ALTER TABLE table1 DROP COLUMN IF EXISTS classification;")
        
        conn.commit()
        print("✅ 成功删除table1表的classification字段")
        
        # 验证修复结果
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'table1'
            ORDER BY ordinal_position;
        """)
        
        new_columns = [row['column_name'] for row in cursor.fetchall()]
        print(f"📋 修复后的table1表字段: {', '.join(new_columns)}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 修复表结构失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def recreate_table1_with_correct_structure():
    """重新创建table1表（正确的结构）"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔄 重新创建table1表（正确结构）...")
        
        # 备份现有数据（如果表存在且有数据）
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'table1'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM table1")
            record_count = cursor.fetchone()[0]
            
            if record_count > 0:
                print(f"⚠️ table1表包含 {record_count} 条记录")
                print("   为了保持数据安全，建议先备份数据")
                print("   当前操作将删除现有表并重新创建")
                
                response = input("是否继续？(y/N): ")
                if response.lower() != 'y':
                    print("操作已取消")
                    return False
            
            # 删除现有表
            cursor.execute("DROP TABLE IF EXISTS table1;")
            print("🗑️ 已删除现有table1表")
        
        # 创建正确结构的table1表
        cursor.execute("""
            CREATE TABLE table1 (
                id SERIAL PRIMARY KEY,
                pageid VARCHAR(100),
                devicetypename VARCHAR(50),
                sendmessagetime TIMESTAMP,
                query TEXT,
                answer TEXT,
                serviceid VARCHAR(50),
                qatype VARCHAR(50),
                intent VARCHAR(100),
                iskeyboardinput BOOLEAN,
                isstopanswer BOOLEAN
            );
        """)
        
        conn.commit()
        print("✅ 成功创建正确结构的table1表")
        
        # 验证新表结构
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'table1'
            ORDER BY ordinal_position;
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 新table1表字段: {', '.join(columns)}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 重新创建表失败: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("🚀 开始修复table1表结构")
    print("=" * 60)
    print("📝 正确的系统设计:")
    print("   - table1表：存储原始数据，不包含classification字段")
    print("   - questions表：包含classification字段，由AI处理服务填充")
    print("=" * 60)
    
    # 检查当前表结构
    table_exists, columns = check_table1_structure()
    
    if not table_exists:
        print("❌ table1表不存在，无法进行修复")
        return
    
    has_classification = 'classification' in columns
    
    if not has_classification:
        print("✅ table1表结构已经正确，无需修复")
        return
    
    # 检查命令行参数
    if '--recreate' in sys.argv:
        print("\n🔄 选择重新创建表的方式...")
        success = recreate_table1_with_correct_structure()
    else:
        dry_run = '--execute' not in sys.argv
        
        if dry_run:
            print(f"\n⚠️ 这是模拟运行模式")
            print("   如需执行实际修复，请添加 --execute 参数")
            print("   如需重新创建表，请添加 --recreate 参数")
        
        success = fix_table1_structure(dry_run=dry_run)
    
    if success:
        print("\n🎉 table1表结构修复完成！")
        print("💡 现在table1表符合正确的系统设计：")
        print("   - 只存储原始数据，不包含classification字段")
        print("   - classification字段只存在于questions表中")
        print("   - 分类将由AI处理服务通过外部API获取并填充")
    else:
        print("\n❌ table1表结构修复失败")

if __name__ == '__main__':
    main()
