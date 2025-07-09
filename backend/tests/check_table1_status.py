#!/usr/bin/env python3
"""
检查table1表的当前状态和数据情况
"""
import sys
import os
import psycopg2
from datetime import datetime

# 添加父目录到路径，以便导入app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 数据库连接配置
DB_CONFIG = {
    'host': "test-huiliu-postgresql.ns-q8rah3y5.svc",
    'port': 5432,
    'user': "postgres",
    'password': "l69jjd9n",
    'database': "ai_qa_platform"
}

def check_table1_structure():
    """检查table1表结构"""
    print("🔍 检查table1表结构")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'table1' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("表字段信息:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (可空: {col[2]}, 默认值: {col[3]})")
        
        # 检查是否有answer字段
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'table1' AND column_name = 'answer'
        """)
        
        has_answer = cursor.fetchone()
        print(f"\n答案字段存在: {'✅ 是' if has_answer else '❌ 否'}")
        
        cursor.close()
        conn.close()
        
        return has_answer is not None
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {str(e)}")
        return False

def check_table1_data():
    """检查table1数据情况"""
    print("\n📊 检查table1数据情况")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 总数据量
        cursor.execute("SELECT COUNT(*) FROM table1")
        total_count = cursor.fetchone()[0]
        print(f"总数据量: {total_count}")
        
        # 有query的数据量
        cursor.execute("SELECT COUNT(*) FROM table1 WHERE query IS NOT NULL AND query != ''")
        query_count = cursor.fetchone()[0]
        print(f"有query的数据: {query_count}")
        
        # 检查answer字段情况
        try:
            cursor.execute("SELECT COUNT(*) FROM table1 WHERE answer IS NOT NULL AND answer != ''")
            answer_count = cursor.fetchone()[0]
            print(f"有answer的数据: {answer_count}")
            
            cursor.execute("SELECT COUNT(*) FROM table1 WHERE answer IS NULL OR answer = ''")
            no_answer_count = cursor.fetchone()[0]
            print(f"缺少answer的数据: {no_answer_count}")
            
        except Exception:
            print("answer字段不存在或无法访问")
        
        # 查看前3条数据样例
        print("\n📝 数据样例（前3条）:")
        cursor.execute("SELECT * FROM table1 LIMIT 3")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'table1' 
            ORDER BY ordinal_position
        """)
        column_names = [row[0] for row in cursor.fetchall()]
        
        for i, row in enumerate(rows, 1):
            print(f"\n  记录 {i}:")
            for j, value in enumerate(row):
                if j < len(column_names):
                    print(f"    {column_names[j]}: {value}")
        
        cursor.close()
        conn.close()
        
        return total_count, query_count
        
    except Exception as e:
        print(f"❌ 检查数据失败: {str(e)}")
        return 0, 0

def main():
    """主函数"""
    print("🔍 Table1状态检查")
    print("=" * 60)
    
    # 检查表结构
    has_answer = check_table1_structure()
    
    # 检查数据情况
    total_count, query_count = check_table1_data()
    
    print("\n" + "=" * 60)
    print("📋 检查结果总结:")
    print(f"  表结构完整性: {'✅' if has_answer else '❌ 缺少answer字段'}")
    print(f"  数据总量: {total_count}")
    print(f"  有效数据量: {query_count}")
    
    if not has_answer:
        print("\n⚠️  需要添加answer字段到table1表")
    elif query_count > 0:
        print(f"\n✅ 可以开始为现有 {query_count} 条数据补齐answer字段")
    
    return has_answer and total_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 