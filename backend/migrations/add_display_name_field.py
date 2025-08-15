#!/usr/bin/env python3
"""
数据库迁移脚本：添加用户显示名称字段
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.utils.database import db
from app.models.user import User, UserApplication
from sqlalchemy import text

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始数据库迁移...")
            
            # 检查users表是否已有display_name字段
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'display_name'
            """)).fetchone()
            
            if not result:
                print("为users表添加display_name字段...")
                db.session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN display_name VARCHAR(100)
                """))
                
                # 为现有用户设置默认的display_name（使用username）
                print("为现有用户设置默认display_name...")
                db.session.execute(text("""
                    UPDATE users 
                    SET display_name = username 
                    WHERE display_name IS NULL
                """))
                
                # 设置字段为NOT NULL
                print("设置display_name字段为NOT NULL...")
                db.session.execute(text("""
                    ALTER TABLE users 
                    ALTER COLUMN display_name SET NOT NULL
                """))
                
                print("users表迁移完成")
            else:
                print("users表已有display_name字段，跳过")
            
            # 检查user_applications表是否已有display_name字段
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_applications' AND column_name = 'display_name'
            """)).fetchone()
            
            if not result:
                print("为user_applications表添加display_name字段...")
                db.session.execute(text("""
                    ALTER TABLE user_applications 
                    ADD COLUMN display_name VARCHAR(100)
                """))
                
                # 为现有申请设置默认的display_name（使用username）
                print("为现有申请设置默认display_name...")
                db.session.execute(text("""
                    UPDATE user_applications 
                    SET display_name = username 
                    WHERE display_name IS NULL
                """))
                
                # 设置字段为NOT NULL
                print("设置display_name字段为NOT NULL...")
                db.session.execute(text("""
                    ALTER TABLE user_applications 
                    ALTER COLUMN display_name SET NOT NULL
                """))
                
                print("user_applications表迁移完成")
            else:
                print("user_applications表已有display_name字段，跳过")
            
            # 提交事务
            db.session.commit()
            print("数据库迁移完成！")
            
        except Exception as e:
            print(f"数据库迁移失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_database()
