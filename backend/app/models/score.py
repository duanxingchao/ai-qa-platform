"""
评分数据模型
"""
from datetime import datetime
from app.utils.database import db

class Score(db.Model):
    """评分表模型"""
    __tablename__ = 'scores'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    
    # 五个维度评分（1-5分）
    score_1 = db.Column(db.Integer)  # 准确性
    score_2 = db.Column(db.Integer)  # 完整性
    score_3 = db.Column(db.Integer)  # 清晰度
    score_4 = db.Column(db.Integer)  # 实用性
    score_5 = db.Column(db.Integer)  # 创新性
    
    # 综合评分和评价
    average_score = db.Column(db.Numeric(3, 2))  # 平均分
    comment = db.Column(db.Text)  # 评分理由
    
    # 时间戳
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 约束
    __table_args__ = (
        db.CheckConstraint('score_1 >= 1 AND score_1 <= 5', name='check_score_1_range'),
        db.CheckConstraint('score_2 >= 1 AND score_2 <= 5', name='check_score_2_range'),
        db.CheckConstraint('score_3 >= 1 AND score_3 <= 5', name='check_score_3_range'),
        db.CheckConstraint('score_4 >= 1 AND score_4 <= 5', name='check_score_4_range'),
        db.CheckConstraint('score_5 >= 1 AND score_5 <= 5', name='check_score_5_range'),
    )
    
    def __repr__(self):
        return f'<Score {self.id}: avg={self.average_score}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'answer_id': self.answer_id,
            'score_1': self.score_1,
            'score_2': self.score_2,
            'score_3': self.score_3,
            'score_4': self.score_4,
            'score_5': self.score_5,
            'average_score': float(self.average_score) if self.average_score else None,
            'comment': self.comment,
            'rated_at': self.rated_at.isoformat() if self.rated_at else None,
            'dimensions': self.get_dimensions_detail()
        }
    
    def get_dimensions_detail(self):
        """获取各维度详细信息"""
        return {
            '准确性': self.score_1,
            '完整性': self.score_2,
            '清晰度': self.score_3,
            '实用性': self.score_4,
            '创新性': self.score_5
        }
    
    def calculate_average(self):
        """计算平均分"""
        scores = [self.score_1, self.score_2, self.score_3, self.score_4, self.score_5]
        valid_scores = [s for s in scores if s is not None]
        
        if valid_scores:
            avg = sum(valid_scores) / len(valid_scores)
            self.average_score = round(avg, 2)
        else:
            self.average_score = None
            
        return self.average_score
    
    @classmethod
    def create_from_api_response(cls, answer_id, api_response):
        """从API响应创建评分记录"""
        score = cls(
            answer_id=answer_id,
            score_1=api_response.get('score_1'),
            score_2=api_response.get('score_2'),
            score_3=api_response.get('score_3'),
            score_4=api_response.get('score_4'),
            score_5=api_response.get('score_5'),
            comment=api_response.get('comment', '')
        )
        score.calculate_average()
        return score 