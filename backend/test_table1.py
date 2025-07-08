"""
测试table1表结构脚本
"""
import psycopg2
import json

# 数据库连接配置
conn = psycopg2.connect(
    host="test-huiliu-postgresql.ns-q8rah3y5.svc",
    port=5432,
    user="postgres",
    password="l69jjd9n",
    database="ai_qa_platform"
)

cursor = conn.cursor()

try:
    # 检查table1是否存在
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'table1'
        );
    """)
    exists = cursor.fetchone()[0]
    
    if exists:
        print("✅ table1表存在")
        
        # 获取表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'table1'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n表结构：")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
        # 获取数据样本
        cursor.execute("SELECT COUNT(*) FROM table1")
        count = cursor.fetchone()[0]
        print(f"\n数据总数: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM table1 LIMIT 5")
            rows = cursor.fetchall()
            print("\n数据样本:")
            for i, row in enumerate(rows):
                print(f"\n记录 {i+1}:")
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = 'table1'
                    ORDER BY ordinal_position;
                """)
                col_names = [col[0] for col in cursor.fetchall()]
                for j, col_name in enumerate(col_names):
                    print(f"  {col_name}: {row[j]}")
    else:
        print("❌ table1表不存在")
        print("需要创建table1表用于测试")
        
except Exception as e:
    print(f"错误: {str(e)}")
finally:
    cursor.close()
    conn.close() 