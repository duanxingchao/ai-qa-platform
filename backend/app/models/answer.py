"""
答案数据模型
"""
from datetime import datetime
from app.utils.database import db
from app.utils.datetime_helper import utc_to_beijing_str

class Answer(db.Model):
    """答案表模型"""
    __tablename__ = 'answers'
    __table_args__ = (
        # 同一问题+助手类型应当唯一，避免重复生成相同助手的答案
        db.UniqueConstraint('question_business_id', 'assistant_type', name='uq_answers_question_assistant'),
    )
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键
    question_business_id = db.Column(db.String(64), db.ForeignKey('questions.business_id'), nullable=False, index=True)
    
    # 答案内容
    answer_text = db.Column(db.Text)
    assistant_type = db.Column(db.String(50), nullable=False, index=True)  # yoyo/doubao/xiaotian
    
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
            'answer_time': utc_to_beijing_str(self.answer_time) if self.answer_time else None,
            'created_at': utc_to_beijing_str(self.created_at) if self.created_at else None,
            'updated_at': utc_to_beijing_str(self.updated_at) if self.updated_at else None
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
            'yoyo': '自研AI',
            'doubao': '豆包',
            'xiaotian': '小天'
        }
        return type_map.get(assistant_type, assistant_type) 