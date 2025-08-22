"""
评分数据模型
"""
from datetime import datetime
from app.utils.database import db
from app.config import Config
from app.utils.datetime_helper import utc_to_beijing_str

class Score(db.Model):
    """评分表模型"""
    __tablename__ = 'scores'
    __table_args__ = {'schema': Config.DATABASE_SCHEMA}
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    
    # 五个维度评分（1-5分）
    score_1 = db.Column(db.Integer)
    score_2 = db.Column(db.Integer)
    score_3 = db.Column(db.Integer)
    score_4 = db.Column(db.Integer)
    score_5 = db.Column(db.Integer)
    
    # 动态维度名称字段（新增）
    dimension_1_name = db.Column(db.String(50))  # 第一个维度名称，如"信息准确性"
    dimension_2_name = db.Column(db.String(50))  # 第二个维度名称，如"逻辑性"
    dimension_3_name = db.Column(db.String(50))  # 第三个维度名称，如"流畅性"
    dimension_4_name = db.Column(db.String(50))  # 第四个维度名称，如"创新性"
    dimension_5_name = db.Column(db.String(50))  # 第五个维度名称，如"完整性"
    
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
            'dimension_1_name': self.dimension_1_name,
            'dimension_2_name': self.dimension_2_name,
            'dimension_3_name': self.dimension_3_name,
            'dimension_4_name': self.dimension_4_name,
            'dimension_5_name': self.dimension_5_name,
            'average_score': float(self.average_score) if self.average_score else None,
            'comment': self.comment,
            'rated_at': utc_to_beijing_str(self.rated_at) if self.rated_at else None,
            'dimensions': self.get_dimensions_detail()
        }
    
    def get_dimensions_detail(self):
        """获取各维度详细信息（动态维度名称）"""
        return {
            self.dimension_1_name or '维度1': self.score_1,
            self.dimension_2_name or '维度2': self.score_2,
            self.dimension_3_name or '维度3': self.score_3,
            self.dimension_4_name or '维度4': self.score_4,
            self.dimension_5_name or '维度5': self.score_5
        }
    
    def calculate_average(self):
        """计算平均分，确保精度正确"""
        scores = [self.score_1, self.score_2, self.score_3, self.score_4, self.score_5]
        valid_scores = [s for s in scores if s is not None]

        if valid_scores:
            avg = sum(valid_scores) / len(valid_scores)
            self.average_score = round(avg, 2)  # 确保保留2位小数
        else:
            self.average_score = None
            
        return self.average_score
    
    @classmethod
    def create_from_api_response(cls, answer_id, api_response_item):
        """从API响应创建评分记录（支持动态维度名称）
        
        Args:
            answer_id: 答案ID
            api_response_item: API返回的单个模型评分数据，格式如：
            {
                "模型名称": "模型1",
                "信息准确性": 4,
                "逻辑性": 3, 
                "流畅性": 4,
                "创新性": 3,
                "完整性": 4,
                "理由": "具体评分理由"
            }
        """
        score = cls(answer_id=answer_id)
        
        # 提取评分理由
        score.comment = api_response_item.get('理由', '')
        
        # 动态提取维度名称和分数
        dimension_keys = []
        dimension_scores = []
        
        for key, value in api_response_item.items():
            if key not in ['模型名称', '理由']:
                try:
                    # 尝试将值转换为整数
                    score_value = int(value) if isinstance(value, str) else value
                    if isinstance(score_value, int) and 1 <= score_value <= 5:
                        dimension_keys.append(key)
                        dimension_scores.append(score_value)
                except (ValueError, TypeError):
                    # 如果转换失败，跳过这个字段
                    continue
        
        # 按顺序赋值（最多5个维度）
        for i, (dim_name, dim_score) in enumerate(zip(dimension_keys[:5], dimension_scores[:5])):
            if i == 0:
                score.dimension_1_name = dim_name
                score.score_1 = dim_score
            elif i == 1:
                score.dimension_2_name = dim_name
                score.score_2 = dim_score
            elif i == 2:
                score.dimension_3_name = dim_name
                score.score_3 = dim_score
            elif i == 3:
                score.dimension_4_name = dim_name
                score.score_4 = dim_score
            elif i == 4:
                score.dimension_5_name = dim_name
                score.score_5 = dim_score
        
        # 计算平均分
        score.calculate_average()
        return score 