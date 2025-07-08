#!/usr/bin/env python3
"""
快速数据同步测试
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

def test_table1_data():
    """测试table1中的数据"""
    from app.utils.database import db, execute_sql
    from app import create_app
    
    app = create_app()
    with app.app_context():
        print("🔍 检查table1数据...")
        result = execute_sql("SELECT COUNT(*) FROM table1")
        count = result.scalar()
        print(f"  table1总记录数: {count}")
        
        if count > 0:
            result = execute_sql("SELECT pageid, query, sendmessagetime FROM table1 LIMIT 3")
            print("  前3条记录:")
            for row in result:
               print(f"    页面ID:{row[0]}, 问题:{row[1][:50]}..., 时间:{row[2]}")

def test_questions_data():
    """测试questions表中的数据"""
    from app.utils.database import db, execute_sql
    from app import create_app
    
    app = create_app()
    with app.app_context():
        print("🔍 检查questions表数据...")
        result = execute_sql("SELECT COUNT(*) FROM questions")
        count = result.scalar()
        print(f"  questions总记录数: {count}")

def test_sync_operation():
    """测试同步操作"""
    from app import create_app
    from app.services.sync_service import sync_service
    
    app = create_app()
    with app.app_context():
        print("🔄 执行数据同步...")
        result = sync_service.perform_sync()
        print(f"  同步结果: {result}")

if __name__ == "__main__":
    print("🚀 开始快速同步测试...\n")
    
    try:
        # 步骤1: 检查源数据
        test_table1_data()
        print()
        
        # 步骤2: 检查目标表
        test_questions_data()
        print()
        
        # 步骤3: 执行同步
        test_sync_operation()
        print()
        
        # 步骤4: 再次检查目标表
        test_questions_data()
        
        print("\n✅ 快速同步测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc() 