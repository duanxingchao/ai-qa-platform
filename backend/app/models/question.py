"""
问题数据模型
"""
from datetime import datetime
from app.utils.database import db
from app.config import Config
from app.utils.datetime_helper import utc_to_beijing_str

class Question(db.Model):
    """问题表模型"""
    __tablename__ = 'questions'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}
    
    # 主键和业务主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    
    # 基础字段 (所有字段类型为VARCHAR以匹配源表)
    pageid = db.Column(db.String(255))
    devicetypename = db.Column(db.String(255))
    query = db.Column(db.String(4000), nullable=False)
    sendmessagetime = db.Column(db.String(255), index=True)
    classification = db.Column(db.String(255), index=True)  # API分类结果
    serviceid = db.Column(db.String(255))
    qatype = db.Column(db.String(255))
    intent = db.Column(db.String(255))
    iskeyboardinput = db.Column(db.String(255), default='false')
    isstopanswer = db.Column(db.String(255), default='false')
    
    # 状态管理字段
    is_deleted = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(20), default='pending', index=True)

    # Badcase相关字段
    is_badcase = db.Column(db.Boolean, default=False, index=True)
    badcase_detected_at = db.Column(db.DateTime)
    badcase_review_status = db.Column(db.String(20), default='pending', index=True)
    badcase_dimensions = db.Column(db.Text)  # JSON格式存储低分维度信息
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer)  # 复核人员ID

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
            'sendmessagetime': utc_to_beijing_str(self.sendmessagetime) if self.sendmessagetime else None,
            'classification': self.classification,
            'serviceid': self.serviceid,
            'qatype': self.qatype,
            'intent': self.intent,
            'iskeyboardinput': self.iskeyboardinput,
            'isstopanswer': self.isstopanswer,
            'is_deleted': self.is_deleted,
            'processing_status': self.processing_status,
            'is_badcase': self.is_badcase,
            'badcase_detected_at': utc_to_beijing_str(self.badcase_detected_at) if self.badcase_detected_at else None,
            'badcase_review_status': self.badcase_review_status,
            'badcase_dimensions': self.badcase_dimensions,
            'reviewed_at': utc_to_beijing_str(self.reviewed_at) if self.reviewed_at else None,
            'created_at': utc_to_beijing_str(self.created_at) if self.created_at else None,
            'updated_at': utc_to_beijing_str(self.updated_at) if self.updated_at else None
        }
    
    def update_status(self, status):
        """更新处理状态"""
        self.processing_status = status
        self.updated_at = datetime.utcnow()
        db.session.commit() 