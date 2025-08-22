"""
用户管理相关数据模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import db
from app.config import Config
from app.utils.datetime_helper import utc_to_beijing_str

class User(db.Model):
    """用户表模型"""
    __tablename__ = 'users'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='员工号码/登录账号')
    display_name = db.Column(db.String(100), nullable=False, comment='用户显示名称')
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user', name='user_role'), nullable=False, default='user')
    status = db.Column(db.Enum('active', 'inactive', name='user_status'), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'status': self.status,
            'created_at': utc_to_beijing_str(self.created_at),
            'last_login_at': utc_to_beijing_str(self.last_login_at),
            'login_count': self.login_count
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserApplication(db.Model):
    """用户注册申请表模型"""
    __tablename__ = 'user_applications'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, comment='申请的员工号码/登录账号')
    display_name = db.Column(db.String(100), nullable=False, comment='用户显示名称')
    password_hash = db.Column(db.String(255), nullable=False)
    apply_role = db.Column(db.Enum('admin', 'user', name='apply_role'), nullable=False, default='user')
    reason = db.Column(db.Text, comment='申请理由')
    status = db.Column(db.Enum('pending', 'approved', 'rejected', name='application_status'),
                      nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # 关系
    reviewer = db.relationship('User', backref='reviewed_applications')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'apply_role': self.apply_role,
            'reason': self.reason,
            'status': self.status,
            'created_at': utc_to_beijing_str(self.created_at),
            'reviewed_at': utc_to_beijing_str(self.reviewed_at),
            'reviewer': self.reviewer.username if self.reviewer else None
        }
    
    def __repr__(self):
        return f'<UserApplication {self.username}>'


class AccessLog(db.Model):
    """访问日志表模型"""
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username = db.Column(db.String(50))
    action = db.Column(db.Enum('login', 'logout', name='access_action'), nullable=False)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user = db.relationship('User', backref='access_logs')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'action': self.action,
            'ip_address': self.ip_address,
            'created_at': utc_to_beijing_str(self.created_at)
        }
    
    def __repr__(self):
        return f'<AccessLog {self.username} {self.action}>'
