"""
为questions表添加reviewed_by字段的迁移脚本
"""
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import db

def add_reviewed_by_field():
    """为questions表添加reviewed_by字段"""
    app = create_app()
    
    with app.app_context():
        try:
            print("正在为questions表添加reviewed_by字段...")
            
            # 执行SQL添加字段
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE questions
                    ADD COLUMN IF NOT EXISTS reviewed_by INTEGER;
                """))
                conn.commit()

            # 添加外键约束（如果不存在）
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        ALTER TABLE questions
                        ADD CONSTRAINT fk_questions_reviewed_by
                        FOREIGN KEY (reviewed_by) REFERENCES users(id);
                    """))
                    conn.commit()
                print("外键约束添加成功")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("外键约束已存在，跳过")
                else:
                    print(f"添加外键约束时出现警告: {e}")
            
            print("✅ questions表reviewed_by字段添加完成！")
            
        except Exception as e:
            print(f"❌ 添加字段失败: {e}")
            return False
    
    return True

if __name__ == '__main__':
    add_reviewed_by_field()
