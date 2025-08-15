#!/usr/bin/env python3
"""
添加reason字段到user_applications表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import db
from sqlalchemy import text

def add_reason_field():
    """添加reason字段到user_applications表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            result = db.session.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_name = 'user_applications' 
                AND column_name = 'reason'
            """)).fetchone()
            
            if result.count == 0:
                # 添加reason字段
                db.session.execute(text("""
                    ALTER TABLE user_applications
                    ADD COLUMN reason TEXT
                """))
                db.session.commit()
                print("✅ 成功添加reason字段到user_applications表")
            else:
                print("ℹ️  reason字段已存在，跳过添加")
                
        except Exception as e:
            print(f"❌ 添加字段失败: {str(e)}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    print("开始添加reason字段...")
    success = add_reason_field()
    if success:
        print("✅ 数据库更新完成")
    else:
        print("❌ 数据库更新失败")
        sys.exit(1)
