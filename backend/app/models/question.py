"""
问题数据模型
"""
from datetime import datetime
from app.utils.database import db

class Question(db.Model):
    """问题表模型"""
    __tablename__ = 'questions'
    
    # 主键和业务主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # 基础字段
    pageid = db.Column(db.String(100))
    devicetypename = db.Column(db.String(50))
    query = db.Column(db.Text, nullable=False)
    sendmessagetime = db.Column(db.DateTime, index=True)
    classification = db.Column(db.String(50), index=True)  # API分类结果
    serviceid = db.Column(db.String(50))
    qatype = db.Column(db.String(50))
    intent = db.Column(db.String(100))
    iskeyboardinput = db.Column(db.Boolean, default=False)
    isstopanswer = db.Column(db.Boolean, default=False)
    
    # 状态管理字段
    is_deleted = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(20), default='pending', index=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    review_status = db.relationship('ReviewStatus', backref='question', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.id}: {self.query[:50]}...>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'business_id': self.business_id,
            'pageid': self.pageid,
            'devicetypename': self.devicetypename,
            'query': self.query,
            'sendmessagetime': self.sendmessagetime.isoformat() if self.sendmessagetime else None,
            'classification': self.classification,
            'serviceid': self.serviceid,
            'qatype': self.qatype,
            'intent': self.intent,
            'iskeyboardinput': self.iskeyboardinput,
            'isstopanswer': self.isstopanswer,
            'is_deleted': self.is_deleted,
            'processing_status': self.processing_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_status(self, status):
        """更新处理状态"""
        self.processing_status = status
        self.updated_at = datetime.utcnow()
        db.session.commit() 