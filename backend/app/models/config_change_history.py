"""
配置变更历史模型
"""

from datetime import datetime
from app.utils.database import db
from sqlalchemy import Column, Integer, String, Text, DateTime


class ConfigChangeHistory(db.Model):
    """配置变更历史模型"""
    
    __tablename__ = 'config_change_history'
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), nullable=False, comment='配置键名')
    old_value = Column(Text, comment='旧配置值')
    new_value = Column(Text, comment='新配置值')
    config_type = Column(String(20), comment='配置类型')
    change_reason = Column(Text, comment='变更原因')
    operator = Column(String(100), comment='操作人')
    operation_type = Column(String(20), default='update', comment='操作类型：create-创建，update-更新，delete-删除')
    created_at = Column(DateTime, default=datetime.utcnow, comment='变更时间')
    
    def __repr__(self):
        return f'<ConfigChangeHistory {self.config_key}: {self.old_value} -> {self.new_value}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'config_type': self.config_type,
            'change_reason': self.change_reason,
            'operator': self.operator,
            'operation_type': self.operation_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    @classmethod
    def record_change(cls, config_key: str, old_value: str = None, new_value: str = None, 
                     config_type: str = 'string', change_reason: str = None, 
                     operator: str = 'system', operation_type: str = 'update') -> 'ConfigChangeHistory':
        """记录配置变更"""
        history = cls(
            config_key=config_key,
            old_value=old_value,
            new_value=new_value,
            config_type=config_type,
            change_reason=change_reason,
            operator=operator,
            operation_type=operation_type
        )
        db.session.add(history)
        db.session.commit()
        return history
    
    @classmethod
    def get_history_by_key(cls, config_key: str, limit: int = 50):
        """获取指定配置的变更历史"""
        return cls.query.filter_by(config_key=config_key)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent_changes(cls, limit: int = 100):
        """获取最近的配置变更"""
        return cls.query.order_by(cls.created_at.desc())\
                       .limit(limit).all()
