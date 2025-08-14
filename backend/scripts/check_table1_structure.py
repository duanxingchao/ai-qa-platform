#!/usr/bin/env python3
"""
检查table1表的实际结构
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
    """检查table1表结构"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 检查table1表结构...")
        print("=" * 60)
        
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
            return
        
        print("✅ table1表存在")
        
        # 获取表结构
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'table1'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print(f"\n📋 table1表字段结构 (共{len(columns)}个字段):")
        print("-" * 80)
        print(f"{'字段名':<20} {'数据类型':<15} {'可空':<8} {'默认值':<15} {'长度':<10}")
        print("-" * 80)
        
        for col in columns:
            column_name = col['column_name']
            data_type = col['data_type']
            is_nullable = 'YES' if col['is_nullable'] == 'YES' else 'NO'
            default_value = str(col['column_default']) if col['column_default'] else ''
            max_length = str(col['character_maximum_length']) if col['character_maximum_length'] else ''
            
            print(f"{column_name:<20} {data_type:<15} {is_nullable:<8} {default_value:<15} {max_length:<10}")
        
        # 检查是否有classification字段
        classification_exists = any(col['column_name'] == 'classification' for col in columns)
        
        print(f"\n🔍 classification字段检查:")
        if classification_exists:
            print("✅ table1表包含classification字段")
        else:
            print("❌ table1表不包含classification字段")
        
        # 获取表中的数据样本
        cursor.execute("SELECT COUNT(*) FROM table1")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 table1表数据统计:")
        print(f"   总记录数: {total_count}")
        
        if total_count > 0:
            # 获取前5条记录作为样本
            cursor.execute("SELECT * FROM table1 LIMIT 5")
            sample_data = cursor.fetchall()
            
            print(f"\n📝 数据样本 (前5条记录):")
            print("-" * 100)
            
            if sample_data:
                # 显示字段名
                field_names = list(sample_data[0].keys())
                print(" | ".join(f"{name:<15}" for name in field_names))
                print("-" * 100)
                
                # 显示数据
                for i, row in enumerate(sample_data, 1):
                    values = []
                    for field in field_names:
                        value = str(row[field]) if row[field] is not None else 'NULL'
                        # 截断长文本
                        if len(value) > 15:
                            value = value[:12] + "..."
                        values.append(f"{value:<15}")
                    print(" | ".join(values))
        
        # 如果有classification字段，检查其值
        if classification_exists:
            cursor.execute("""
                SELECT classification, COUNT(*) as count 
                FROM table1 
                WHERE classification IS NOT NULL AND classification != ''
                GROUP BY classification 
                ORDER BY count DESC
            """)
            
            classifications = cursor.fetchall()
            
            print(f"\n🏷️ classification字段值分布:")
            print("-" * 50)
            if classifications:
                for row in classifications:
                    print(f"   {row['classification']}: {row['count']}条记录")
            else:
                print("   没有分类数据")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("🚀 开始检查table1表结构")
    check_table1_structure()

if __name__ == '__main__':
    main()
