"""
系统配置模型
"""

from datetime import datetime
from app.utils.database import db
from app.config import Config
from sqlalchemy import Column, Integer, String, Text, DateTime
from typing import Optional, Any
import json


class SystemConfig(db.Model):
    """系统配置模型"""

    __tablename__ = 'system_config'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False, comment='配置键名')
    config_value = Column(Text, nullable=False, comment='配置值')
    config_type = Column(String(20), default='string', comment='配置类型')
    description = Column(Text, comment='配置描述')
    effective_time = Column(DateTime, comment='生效时间，NULL表示立即生效')
    previous_value = Column(Text, comment='上一个配置值，用于延迟生效期间的回退')
    status = Column(String(20), default='active', comment='配置状态：active-生效中，pending-待生效')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}={self.config_value}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.get_effective_value(),
            'config_type': self.config_type,
            'description': self.description,
            'effective_time': self.effective_time.strftime('%Y-%m-%d %H:%M:%S') if self.effective_time else None,
            'status': self.status,
            'has_pending_change': self.is_pending_change(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def is_pending_change(self) -> bool:
        """检查是否有待生效的变更"""
        return (self.effective_time and
                self.effective_time > datetime.utcnow() and
                self.status == 'pending')

    def get_effective_value(self) -> Any:
        """获取当前有效的配置值"""
        if self.is_pending_change():
            # 如果有待生效的变更，返回之前的值
            if self.previous_value is not None:
                return self._parse_value(self.previous_value)
            else:
                return self.get_typed_value()
        return self.get_typed_value()

    def _parse_value(self, value_str: str) -> Any:
        """解析字符串值为对应类型"""
        if self.config_type == 'number':
            try:
                if '.' not in value_str:
                    return int(value_str)
                else:
                    return float(value_str)
            except ValueError:
                return value_str
        elif self.config_type == 'boolean':
            return value_str.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'json':
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                return value_str
        else:
            return value_str
    
    def get_typed_value(self) -> Any:
        """根据配置类型返回对应类型的值"""
        if self.config_type == 'number':
            try:
                # 尝试转换为整数
                if '.' not in self.config_value:
                    return int(self.config_value)
                else:
                    return float(self.config_value)
            except ValueError:
                return self.config_value
        elif self.config_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'json':
            try:
                return json.loads(self.config_value)
            except json.JSONDecodeError:
                return self.config_value
        else:
            # string类型或其他类型直接返回字符串
            return self.config_value
    
    def set_typed_value(self, value: Any):
        """根据配置类型设置值"""
        if self.config_type == 'json':
            if isinstance(value, (dict, list)):
                self.config_value = json.dumps(value, ensure_ascii=False)
            else:
                self.config_value = str(value)
        elif self.config_type == 'boolean':
            self.config_value = 'true' if value else 'false'
        else:
            self.config_value = str(value)
        
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def get_config(cls, key: str, default_value: Any = None) -> Any:
        """获取当前有效的配置值"""
        config = cls.query.filter_by(config_key=key).first()
        if config:
            return config.get_effective_value()
        return default_value
    
    @classmethod
    def set_config(cls, key: str, value: Any, config_type: str = 'string', description: str = None) -> 'SystemConfig':
        """设置配置值"""
        config = cls.query.filter_by(config_key=key).first()
        if config:
            config.set_typed_value(value)
            if description:
                config.description = description
        else:
            config = cls(
                config_key=key,
                config_type=config_type,
                description=description
            )
            config.set_typed_value(value)
            db.session.add(config)
        
        db.session.commit()
        return config
    
    @classmethod
    def get_all_configs(cls) -> dict:
        """获取所有配置"""
        configs = cls.query.all()
        return {config.config_key: config.get_typed_value() for config in configs}
    
    @classmethod
    def get_configs_by_prefix(cls, prefix: str) -> dict:
        """根据前缀获取配置"""
        configs = cls.query.filter(cls.config_key.like(f'{prefix}%')).all()
        return {config.config_key: config.get_typed_value() for config in configs}
