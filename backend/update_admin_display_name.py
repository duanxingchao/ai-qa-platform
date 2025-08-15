#!/usr/bin/env python3
"""
更新管理员用户的display_name
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import db
from app.models.user import User

def update_admin_display_name():
    """更新管理员用户的display_name"""
    app = create_app()
    
    with app.app_context():
        try:
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                admin_user.display_name = '系统管理员'
                db.session.commit()
                print(f'管理员用户display_name已更新为: {admin_user.display_name}')
            else:
                print('未找到管理员用户')
        except Exception as e:
            print(f'更新失败: {str(e)}')
            db.session.rollback()

if __name__ == '__main__':
    update_admin_display_name()
