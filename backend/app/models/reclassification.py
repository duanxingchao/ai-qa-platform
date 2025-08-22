"""
问题重新分类历史记录模型
"""
from datetime import datetime
from app.utils.database import db
from app.config import Config


class QuestionReclassification(db.Model):
    """问题重新分类历史记录"""
    __tablename__ = 'question_reclassifications'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 采用业务主键以便跨表关联
    question_business_id = db.Column(db.String(64), db.ForeignKey('questions.business_id'), index=True, nullable=False)
    old_classification = db.Column(db.String(50))
    new_classification = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.Text)
    changed_by = db.Column(db.String(50))  # 用户名或ID，后续可调整类型
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'question_business_id': self.question_business_id,
            'old_classification': self.old_classification,
            'new_classification': self.new_classification,
            'reason': self.reason,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
        }

