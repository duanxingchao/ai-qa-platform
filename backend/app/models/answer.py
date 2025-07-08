"""
答案数据模型
"""
from datetime import datetime
from app.utils.database import db

class Answer(db.Model):
    """答案表模型"""
    __tablename__ = 'answers'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键
    question_business_id = db.Column(db.String(64), db.ForeignKey('questions.business_id'), nullable=False, index=True)
    
    # 答案内容
    answer_text = db.Column(db.Text)
    assistant_type = db.Column(db.String(50), nullable=False, index=True)  # our_ai/doubao/xiaotian
    
    # 状态字段
    is_scored = db.Column(db.Boolean, default=False)
    
    # 时间戳
    answer_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    scores = db.relationship('Score', backref='answer', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Answer {self.id}: {self.assistant_type}>'
    
    def to_dict(self, include_score=False):
        """转换为字典格式"""
        result = {
            'id': self.id,
            'question_business_id': self.question_business_id,
            'answer_text': self.answer_text,
            'assistant_type': self.assistant_type,
            'is_scored': self.is_scored,
            'answer_time': self.answer_time.isoformat() if self.answer_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_score and self.is_scored:
            # 获取最新的评分
            from .score import Score
            latest_score = self.scores.order_by(Score.rated_at.desc()).first()
            if latest_score:
                result['score'] = latest_score.to_dict()
        
        return result
    
    def get_average_score(self):
        """获取平均分"""
        from .score import Score
        latest_score = self.scores.order_by(Score.rated_at.desc()).first()
        if latest_score:
            return latest_score.average_score
        return None
    
    @staticmethod
    def get_assistant_type_display(assistant_type):
        """获取助手类型的显示名称"""
        type_map = {
            'our_ai': '自研AI',
            'doubao': '豆包',
            'xiaotian': '小天'
        }
        return type_map.get(assistant_type, assistant_type) 