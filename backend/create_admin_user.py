#!/usr/bin/env python3
"""
创建默认管理员用户脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from app.utils.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """创建默认管理员用户"""
    app = create_app('development')
    
    with app.app_context():
        try:
            # 检查是否已存在管理员用户
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                logger.info("管理员用户 'admin' 已存在")
                logger.info(f"用户信息: {existing_admin.to_dict()}")
                return True
            
            # 创建管理员用户
            admin_user = User(
                username='admin',
                role='admin',
                status='active'
            )
            admin_user.set_password('admin123')  # 默认密码
            
            db.session.add(admin_user)
            db.session.commit()
            
            logger.info("✅ 默认管理员用户创建成功！")
            logger.info("用户名: admin")
            logger.info("密码: admin123")
            logger.info("角色: admin")
            logger.info("⚠️  请登录后立即修改默认密码！")
            
            return True
            
        except Exception as e:
            logger.error(f"创建管理员用户失败: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = create_admin_user()
    exit(0 if success else 1)
