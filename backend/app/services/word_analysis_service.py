"""
热词分析服务
提供问题文本的热词统计和分析功能
"""
import jieba
import jieba.analyse
import logging
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models.question import Question
from app.utils.database import db
from app.utils.time_utils import TimeRangeUtils


class WordAnalysisService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 停用词列表
        self.stop_words = {
            # 基础停用词
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
            '都', '一', '上', '也', '很', '到', '说', '要', '去', '你',
            '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', 
            '怎么', '为什么', '怎样', '如何', '能否', '可以', '可能',
            '应该', '需要', '想要', '希望', '觉得', '认为', '知道',
            '了解', '明白', '清楚', '发现', '出现', '存在', '产生',
            '进行', '实现', '完成', '处理', '解决', '操作', '使用',
            '工作', '运行', '执行', '开始', '结束', '继续', '停止',
            
            # 业务相关停用词
            '问题', '系统', '功能', '服务', '平台', '软件', '程序',
            '应用', '工具', '设备', '机器', '产品', '项目', '方案',
            '方法', '方式', '技术', '算法', '模型', '数据', '信息',
            '内容', '文件', '文档', '资料', '材料', '报告', '记录',
            '用户', '客户', '管理员', '开发者', '测试', '维护',
            '配置', '设置', '参数', '选项', '属性', '字段', '变量',
            '接口', '协议', '标准', '规范', '流程', '步骤', '阶段',
            '状态', '结果', '效果', '影响', '作用', '意义', '价值',
            '时间', '日期', '年', '月', '日', '小时', '分钟', '秒',
            '地方', '位置', '地址', '路径', '目录', '文件夹', '页面',
            '界面', '窗口', '按钮', '菜单', '选项卡', '链接', '图标'
        }
        
        # 初始化jieba
        jieba.initialize()
    
    def get_word_cloud_data(self, time_range='week', limit=20):
        """
        获取词云数据
        
        Args:
            time_range: 时间范围 ('week', 'month', 'all')
            limit: 返回热词数量限制
            
        Returns:
            dict: 包含词云数据的字典
        """
        try:
            self.logger.info(f"开始获取热词分析数据，时间范围: {time_range}, 限制: {limit}")
            
            # 获取时间范围内的问题
            questions = self._get_questions_by_time_range(time_range)

            if not questions:
                self.logger.warning(f"未找到符合条件的问题数据，时间范围: {time_range}")
                return {
                    'word_cloud': [],
                    'total_questions': 0,
                    'unique_words': 0,
                    'analysis_period': '无数据',
                    'time_range': time_range
                }
            
            # 提取并分析文本
            word_freq = self._analyze_text(questions)
            
            if not word_freq:
                self.logger.warning("文本分析未产生有效热词")
                return {
                    'word_cloud': [],
                    'total_questions': len(questions),
                    'unique_words': 0,
                    'analysis_period': '无有效热词',
                    'time_range': time_range
                }
            
            # 生成词云数据
            word_cloud_data = [
                {"name": word, "value": freq} 
                for word, freq in word_freq.most_common(limit)
            ]
            
            # 获取时间范围显示文本
            start_time, end_time = TimeRangeUtils.get_time_range(time_range)
            period_text = f"{start_time.strftime('%Y-%m-%d')} 至 {end_time.strftime('%Y-%m-%d')}"
            
            result = {
                'word_cloud': word_cloud_data,
                'total_questions': len(questions),
                'unique_words': len(word_freq),
                'analysis_period': period_text,
                'time_range': time_range
            }
            
            self.logger.info(f"热词分析完成，共分析 {len(questions)} 个问题，生成 {len(word_cloud_data)} 个热词")
            return result
            
        except Exception as e:
            self.logger.error(f"获取词云数据时出错: {str(e)}")
            return {
                'word_cloud': [],
                'total_questions': 0,
                'unique_words': 0,
                'analysis_period': '数据处理错误',
                'time_range': time_range
            }
    
    def _get_questions_by_time_range(self, time_range):
        """根据时间范围获取问题列表"""
        try:
            # 验证时间范围参数
            if not TimeRangeUtils.validate_range_type(time_range):
                self.logger.error(f"无效的时间范围参数: {time_range}")
                return []
            
            # 获取时间范围
            start_time, end_time = TimeRangeUtils.get_time_range(time_range)
            
            # 查询问题
            questions = db.session.query(Question).filter(
                and_(
                    Question.created_at >= start_time,
                    Question.created_at <= end_time,
                    Question.query.isnot(None),     # 确保有问题文本
                    Question.query != '',           # 确保问题文本不为空
                    Question.is_deleted == False    # 排除已删除的数据
                )
            ).all()

            self.logger.info(f"查询到 {len(questions)} 个问题，时间范围: {start_time} 至 {end_time}")
            
            return questions
            
        except Exception as e:
            self.logger.error(f"查询问题数据时出错: {str(e)}")
            return []
    
    def _analyze_text(self, questions):
        """分析文本并统计词频"""
        try:
            # 合并所有问题文本
            all_text = ""
            valid_questions = 0
            for question in questions:
                # 使用问题的query字段
                query_text = question.query or ""
                if query_text.strip():
                    all_text += query_text + " "
                    valid_questions += 1
                    if valid_questions <= 3:  # 记录前3个问题用于调试
                        self.logger.info(f"问题样本 {valid_questions}: {query_text[:50]}...")

            self.logger.info(f"有效问题文本数: {valid_questions}, 总文本长度: {len(all_text)}")
            
            if not all_text.strip():
                return Counter()
            
            # 使用jieba进行分词
            words = jieba.cut(all_text)
            
            # 过滤停用词和短词
            filtered_words = []
            for word in words:
                word = word.strip()
                # 过滤条件：长度>=2，不在停用词中，不是纯数字，不是纯标点
                if (len(word) >= 2 and 
                    word not in self.stop_words and 
                    not word.isdigit() and 
                    not all(c in '，。！？；：""''（）【】《》、' for c in word)):
                    filtered_words.append(word)
            
            # 统计词频
            word_freq = Counter(filtered_words)
            
            self.logger.info(f"文本分析完成，原始词汇: {len(list(jieba.cut(all_text)))}, 过滤后: {len(filtered_words)}, 唯一词汇: {len(word_freq)}")
            return word_freq
            
        except Exception as e:
            self.logger.error(f"文本分析时出错: {str(e)}")
            return Counter()
    



# 创建全局实例
word_analysis_service = WordAnalysisService()
