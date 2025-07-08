"""
审核状态数据模型
"""
from datetime import datetime
from app.utils.database import db

class ReviewStatus(db.Model):
    """审核状态表模型"""
    __tablename__ = 'review_status'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键
    question_business_id = db.Column(db.String(64), db.ForeignKey('questions.business_id'), unique=True, nullable=False)
    
    # 审核状态
    is_reviewed = db.Column(db.Boolean, default=False)
    reviewer_id = db.Column(db.String(50))  # 审核人员ID
    review_comment = db.Column(db.Text)  # 审核备注
    reviewed_at = db.Column(db.DateTime)  # 审核时间
    
    def __repr__(self):
        return f'<ReviewStatus {self.id}: reviewed={self.is_reviewed}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'question_business_id': self.question_business_id,
            'is_reviewed': self.is_reviewed,
            'reviewer_id': self.reviewer_id,
            'review_comment': self.review_comment,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
    
    def mark_as_reviewed(self, reviewer_id, comment=None):
        """标记为已审核"""
        self.is_reviewed = True
        self.reviewer_id = reviewer_id
        self.review_comment = comment
        self.reviewed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_unreviewed(self):
        """标记为未审核"""
        self.is_reviewed = False
        self.reviewer_id = None
        self.review_comment = None
        self.reviewed_at = None
        db.session.commit()
    
    @classmethod
    def get_or_create(cls, question_business_id):
        """获取或创建审核状态记录"""
        review_status = cls.query.filter_by(question_business_id=question_business_id).first()
        if not review_status:
            review_status = cls(question_business_id=question_business_id)
            db.session.add(review_status)
            db.session.commit()
        return review_status 