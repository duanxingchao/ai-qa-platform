#!/usr/bin/env python3
"""
Mock数据管理工具 - 统一管理table1表的测试数据


功能:
1. 创建table1表(包含answer字段)
2. 添加/更新表结构
3. 生成mock数据
4. 数据统计和验证
5. 支持批量数据管理


python mock_data_manager.py --action create_table
python3 mock_data_manager.py --action add_data --count 30
python3 mock_data_manager.py --action add_data --count 100 --incomplete  # 生成包含不完整数据
python mock_data_manager.py --action add_incomplete_data --count 100    # 专门生成不完整数据
python mock_data_manager.py --action update_answers
python mock_data_manager.py --action stats
python mock_data_manager.py --action full_setup --count 50
"""

import sys
import os
import argparse
import psycopg2
import random
from datetime import datetime, timedelta

# 添加父目录到路径，以便导入app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 数据库连接配置
DB_CONFIG = {
    'host': "test-huiliu-postgresql.ns-q8rah3y5.svc",
    'port': 5432,
    'user': "postgres",
    'password': "l69jjd9n",
    'database': "ai_qa_platform"
}

# 问答对应模板 - 建立问题和答案的逻辑对应关系
QA_TEMPLATES = {
    "功能使用类": [
        {
            "question_template": "如何使用{feature}功能？",
            "answer_template": "您可以通过{method}来使用{feature}功能。具体步骤：{steps}",
            "variables": {
                "feature": ["数据导出", "批量操作", "权限设置", "API调用", "数据备份", "性能监控", "用户管理", "报表生成"],
                "method": ["点击左侧菜单", "进入设置页面", "使用快捷键Ctrl+E", "右键菜单选择", "顶部工具栏"],
                "steps": ["1.登录系统 2.选择功能模块 3.按提示操作", "1.进入管理界面 2.配置参数 3.保存设置", "1.选择数据源 2.设置导出格式 3.确认导出"]
            }
        },
        {
            "question_template": "{feature}在哪里可以找到？",
            "answer_template": "{feature}功能位于{location}，您可以{access_method}进行访问。",
            "variables": {
                "feature": ["用户设置", "数据统计", "系统日志", "帮助文档", "API文档", "账单信息"],
                "location": ["主菜单的设置选项中", "仪表板的右上角", "系统管理模块", "帮助中心"],
                "access_method": ["直接点击进入", "通过搜索功能查找", "使用快捷导航"]
            }
        }
    ],
    "价格咨询类": [
        {
            "question_template": "{product}的价格是多少？",
            "answer_template": "{product}有{plan_count}种价格方案：{plans}。详情请{contact_method}。",
            "variables": {
                "product": ["基础版", "专业版", "企业版", "旗舰版", "定制版"],
                "plan_count": ["三", "四", "多"],
                "plans": ["基础版99元/月，专业版299元/月，企业版999元/月", "免费版0元，标准版199元/月，高级版499元/月", "按需定价，联系销售获取报价"],
                "contact_method": ["联系在线客服", "拨打销售热线400-123-4567", "发送邮件至sales@example.com"]
            }
        },
        {
            "question_template": "是否有{discount_type}优惠？",
            "answer_template": "我们提供{discount_type}优惠：{discount_detail}。{additional_info}",
            "variables": {
                "discount_type": ["学生", "企业批量", "年付", "新用户", "升级"],
                "discount_detail": ["学生用户可享受5折优惠", "企业用户购买10个席位以上享受8折", "年付用户享受2个月免费", "新用户首月免费试用"],
                "additional_info": ["需要提供相关证明材料", "优惠政策可能会调整，以实际为准", "详情请咨询客服"]
            }
        }
    ],
    "技术问题": [
        {
            "question_template": "为什么{action}失败了？",
            "answer_template": "{action}失败可能是由于{reasons}导致。建议您{solutions}。",
            "variables": {
                "action": ["登录", "数据上传", "文件下载", "支付", "注册", "密码重置"],
                "reasons": ["网络连接不稳定", "账户信息错误", "系统维护中", "文件格式不支持", "权限不足"],
                "solutions": ["检查网络连接后重试", "确认账户信息是否正确", "联系技术支持", "稍后再试", "清除浏览器缓存"]
            }
        },
        {
            "question_template": "{system}出现{error_type}错误怎么办？",
            "answer_template": "遇到{error_type}错误时，请尝试以下解决方案：{solutions}。如问题持续存在，请{escalation}。",
            "variables": {
                "system": ["系统", "页面", "功能模块", "API接口"],
                "error_type": ["500", "404", "超时", "权限", "数据"],
                "solutions": ["刷新页面重试", "清除浏览器缓存", "检查网络连接", "重新登录", "联系管理员"],
                "escalation": ["联系技术支持", "提交工单", "查看帮助文档", "联系在线客服"]
            }
        }
    ],
    "账户管理": [
        {
            "question_template": "如何{account_action}？",
            "answer_template": "{account_action}请{steps}。{additional_note}",
            "variables": {
                "account_action": ["修改密码", "更新个人信息", "绑定手机号", "设置安全问题", "注销账户"],
                "steps": ["进入个人设置页面，选择相应选项进行修改", "登录后点击头像，选择账户设置", "在安全设置中找到对应功能"],
                "additional_note": ["为了账户安全，建议定期更新密码", "修改重要信息可能需要验证身份", "如有疑问请联系客服"]
            }
        }
    ],
    "业务咨询": [
        {
            "question_template": "{business_topic}相关的{question_type}？",
            "answer_template": "关于{business_topic}的{question_type}，{answer_content}。{contact_info}",
            "variables": {
                "business_topic": ["合作", "代理", "定制开发", "技术支持", "培训服务"],
                "question_type": ["政策", "流程", "要求", "费用", "时间"],
                "answer_content": ["我们有专门的商务团队为您服务", "具体政策请参考官网说明", "我们提供灵活的合作方案"],
                "contact_info": ["详情请联系商务经理", "可发送邮件至business@example.com", "请拨打商务热线400-888-9999"]
            }
        }
    ]
}

# 基础配置数据
DEVICE_TYPES = ['PC', 'Mobile', 'Tablet', 'TV']
# Mock分类API的标准16分类（与mock_classification_api.py保持一致）
CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]
SERVICE_IDS = ['service_001', 'service_002', 'service_003', 'service_004']
QA_TYPES = ['FAQ', 'CHAT', 'SEARCH', 'HELP']
INTENTS = ['查询', '咨询', '投诉', '建议', '帮助']

class MockDataManager:
    """Mock数据管理类"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect_db(self):
        """连接数据库"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            return False
    
    def close_db(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def create_table1(self):
        """创建table1表(包含answer字段)"""
        print("🔧 创建table1表")
        print("-" * 50)
        
        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return False
        
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS table1 (
                    id SERIAL PRIMARY KEY,
                    pageid VARCHAR(100),
                    devicetypename VARCHAR(50),
                    sendmessagetime TIMESTAMP,
                    query TEXT,
                    answer TEXT,
                    serviceid VARCHAR(50),
                    qatype VARCHAR(50),
                    intent VARCHAR(100),
                    iskeyboardinput BOOLEAN,
                    isstopanswer BOOLEAN
                );
            """)
            self.conn.commit()
            print("✅ table1表创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建table1表失败: {str(e)}")
            return False
    
    def add_answer_column_if_not_exists(self):
        """检查并添加answer字段"""
        print("🔧 检查并添加answer字段")
        print("-" * 50)
        
        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return False
        
        try:
            # 检查answer字段是否存在
            self.cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'table1' AND column_name = 'answer'
            """)
            
            result = self.cursor.fetchone()
            if result:
                print("✅ answer字段已存在")
                return True
            
            # 添加answer字段
            print("➕ 添加answer字段...")
            self.cursor.execute("ALTER TABLE table1 ADD COLUMN answer TEXT")
            self.conn.commit()
            print("✅ answer字段添加成功")
            return True
            
        except Exception as e:
            print(f"❌ 添加answer字段失败: {str(e)}")
            return False
    
    def get_table_stats(self):
        """获取表统计信息"""
        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return None
            
        try:
            # 总数据量
            self.cursor.execute("SELECT COUNT(*) FROM table1")
            result = self.cursor.fetchone()
            total_count = result[0] if result else 0
            
            # 有query的数据量
            self.cursor.execute("SELECT COUNT(*) FROM table1 WHERE query IS NOT NULL AND query != ''")
            result = self.cursor.fetchone()
            query_count = result[0] if result else 0
            
            # 有answer的数据量
            self.cursor.execute("SELECT COUNT(*) FROM table1 WHERE answer IS NOT NULL AND answer != ''")
            result = self.cursor.fetchone()
            answer_count = result[0] if result else 0
            
            # 完整数据量
            self.cursor.execute("""
                SELECT COUNT(*) FROM table1 
                WHERE query IS NOT NULL AND query != '' 
                AND answer IS NOT NULL AND answer != ''
            """)
            result = self.cursor.fetchone()
            complete_count = result[0] if result else 0
            
            # 时间范围
            self.cursor.execute("""
                SELECT 
                    MIN(sendmessagetime) as earliest_time,
                    MAX(sendmessagetime) as latest_time,
                    COUNT(DISTINCT pageid) as unique_pages
                FROM table1
                WHERE sendmessagetime IS NOT NULL
            """)
            time_result = self.cursor.fetchone()
            
            return {
                'total_count': total_count,
                'query_count': query_count,
                'answer_count': answer_count,
                'complete_count': complete_count,
                'earliest_time': time_result[0] if time_result and time_result[0] else None,
                'latest_time': time_result[1] if time_result and time_result[1] else None,
                'unique_pages': time_result[2] if time_result and time_result[2] else 0
            }
            
        except Exception as e:
            print(f"❌ 获取统计信息失败: {str(e)}")
            return None
    
    def show_stats(self):
        """显示数据统计"""
        print("📊 数据统计")
        print("-" * 50)
        
        stats = self.get_table_stats()
        if not stats:
            return False
        
        print(f"📈 数据统计:")
        print(f"  总数据量: {stats['total_count']}")
        print(f"  有query的数据: {stats['query_count']}")
        print(f"  有answer的数据: {stats['answer_count']}")
        print(f"  完整数据量: {stats['complete_count']}")
        print(f"  唯一页面数: {stats['unique_pages']}")
        
        if stats['total_count'] > 0:
            print(f"  数据完整率: {(stats['complete_count']/stats['total_count']*100):.1f}%")
        
        if stats['earliest_time'] and stats['latest_time']:
            print(f"  时间范围: {stats['earliest_time']} ~ {stats['latest_time']}")
        
        return True
    
    def generate_qa_from_template(self, category, template):
        """从模板生成问答对"""
        question_template = template["question_template"]
        answer_template = template["answer_template"]
        variables = template["variables"]

        # 为每个变量随机选择值
        selected_vars = {}
        for var_name, var_options in variables.items():
            selected_vars[var_name] = random.choice(var_options)

        # 替换模板中的变量
        question = question_template.format(**selected_vars)
        answer = answer_template.format(**selected_vars)

        return question, answer

    def generate_smart_answer(self, query, all_templates):
        """基于问题内容智能生成答案"""
        if not query:
            return "感谢您的咨询，请提供更具体的问题以便我们为您提供准确的帮助。"

        # 简单的关键词匹配来选择合适的答案模板
        query_lower = query.lower()

        # 根据问题关键词选择最合适的模板类别
        if any(keyword in query_lower for keyword in ['价格', '费用', '多少钱', '收费', '优惠']):
            category_templates = [t for c, t in all_templates if c == "价格咨询"]
        elif any(keyword in query_lower for keyword in ['如何', '怎么', '怎样', '使用', '操作']):
            category_templates = [t for c, t in all_templates if c == "产品使用"]
        elif any(keyword in query_lower for keyword in ['错误', '失败', '问题', '故障', '异常']):
            category_templates = [t for c, t in all_templates if c == "技术问题"]
        elif any(keyword in query_lower for keyword in ['账户', '密码', '登录', '注册', '个人']):
            category_templates = [t for c, t in all_templates if c == "账户管理"]
        elif any(keyword in query_lower for keyword in ['合作', '代理', '商务', '定制']):
            category_templates = [t for c, t in all_templates if c == "业务咨询"]
        else:
            category_templates = [t for c, t in all_templates]

        if category_templates:
            template = random.choice(category_templates)
            _, answer = self.generate_qa_from_template("", template)
            return answer
        else:
            return f"关于您提到的'{query}'，我们的专业团队会为您提供详细解答。请联系客服获取更多信息。"

    def generate_mock_data(self, count=30, include_answers=True, include_incomplete=False):
        """生成mock数据

        Args:
            count: 生成数据数量
            include_answers: 是否包含答案
            include_incomplete: 是否包含不完整数据（问题或答案为空）
        """
        incomplete_info = ""
        if include_incomplete:
            incomplete_info = " (包含不完整数据)"

        print(f"🚀 生成 {count} 条mock数据 (包含answer: {include_answers}){incomplete_info}")
        print("-" * 50)

        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return 0

        try:
            # 生成数据
            new_records = []
            now = datetime.now()
            # 今天的开始时间（00:00:00）
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # 收集所有可用的模板
            all_templates = []
            for category, templates in QA_TEMPLATES.items():
                for template in templates:
                    all_templates.append((category, template))

            print(f"📝 使用 {len(all_templates)} 个问答模板生成数据")

            for _ in range(count):
                # 决定数据完整性
                if include_incomplete:
                    # 30% 问题为空，20% 答案为空，10% 都为空，40% 完整数据
                    data_type = random.choices(
                        ['empty_query', 'empty_answer', 'both_empty', 'complete'],
                        weights=[30, 20, 10, 40]
                    )[0]
                else:
                    data_type = 'complete'

                # 生成基础数据
                query = None
                answer = None

                if data_type == 'empty_query':
                    # 问题为空，答案有值
                    query = None
                    if include_answers:
                        # 从模板随机生成答案
                        category, template = random.choice(all_templates)
                        _, answer = self.generate_qa_from_template(category, template)
                elif data_type == 'empty_answer':
                    # 问题有值，答案为空
                    category, template = random.choice(all_templates)
                    query, _ = self.generate_qa_from_template(category, template)
                    answer = None
                elif data_type == 'both_empty':
                    # 问题和答案都为空
                    query = None
                    answer = None
                else:  # complete
                    # 完整数据 - 使用模板生成对应的问答
                    category, template = random.choice(all_templates)
                    query, generated_answer = self.generate_qa_from_template(category, template)
                    if include_answers:
                        answer = generated_answer
                
                # 生成当天内且不超过当前时间的随机时间
                # 计算从今天开始到现在的总秒数
                total_seconds_today = int((now - today_start).total_seconds())
                if total_seconds_today > 0:
                    # 在今天的时间范围内随机选择
                    random_seconds = random.randint(0, total_seconds_today)
                    send_time = today_start + timedelta(seconds=random_seconds)
                else:
                    # 如果是刚好午夜，使用当前时间
                    send_time = now

                record = {
                    'pageid': f'page_{random.randint(1000, 9999)}',
                    'devicetypename': random.choice(DEVICE_TYPES),
                    'sendmessagetime': send_time,
                    'query': query,
                    'answer': answer,
                    'serviceid': random.choice(SERVICE_IDS),
                    'qatype': random.choice(QA_TYPES),
                    'intent': random.choice(INTENTS),
                    'iskeyboardinput': random.choice([True, False]),
                    'isstopanswer': random.choice([True, False])
                }
                new_records.append(record)
            
            # 插入数据
            insert_sql = """
                INSERT INTO table1
                (pageid, devicetypename, sendmessagetime, query, answer, serviceid, qatype, intent, iskeyboardinput, isstopanswer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            inserted_count = 0
            data_summary = {'complete': 0, 'empty_query': 0, 'empty_answer': 0, 'both_empty': 0}

            for record in new_records:
                self.cursor.execute(insert_sql, (
                    record['pageid'],
                    record['devicetypename'],
                    record['sendmessagetime'],
                    record['query'],
                    record['answer'],
                    record['serviceid'],
                    record['qatype'],
                    record['intent'],
                    record['iskeyboardinput'],
                    record['isstopanswer']
                ))
                inserted_count += 1
                
                # 统计数据类型
                if record['query'] is None and record['answer'] is None:
                    data_summary['both_empty'] += 1
                elif record['query'] is None:
                    data_summary['empty_query'] += 1
                elif record['answer'] is None:
                    data_summary['empty_answer'] += 1
                else:
                    data_summary['complete'] += 1
            
            self.conn.commit()
            print(f"✅ 成功插入 {inserted_count} 条mock数据")
            
            if include_incomplete:
                print(f"📊 数据分布:")
                print(f"  完整数据: {data_summary['complete']} 条")
                print(f"  仅问题为空: {data_summary['empty_query']} 条")
                print(f"  仅答案为空: {data_summary['empty_answer']} 条")
                print(f"  问题答案都为空: {data_summary['both_empty']} 条")
            
            return inserted_count
            
        except Exception as e:
            print(f"❌ 生成mock数据失败: {str(e)}")
            self.conn.rollback()
            return 0
    
    def update_answers_for_existing_data(self):
        """为现有数据补齐answer字段"""
        print("📝 为现有数据补齐answer字段")
        print("-" * 50)
        
        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return 0
        
        try:
            # 查找没有answer的记录
            self.cursor.execute("""
                SELECT id, query 
                FROM table1 
                WHERE (answer IS NULL OR answer = '') 
                AND query IS NOT NULL 
                AND query != ''
            """)
            
            records = self.cursor.fetchall()
            print(f"找到 {len(records)} 条需要补齐answer的记录")
            
            if not records:
                print("✅ 所有记录都已有answer数据")
                return 0
            
            # 为每条记录生成answer
            updated_count = 0
            all_templates = []
            for category, templates in QA_TEMPLATES.items():
                for template in templates:
                    all_templates.append((category, template))

            for record_id, query in records:
                # 基于问题内容智能生成答案
                answer = self.generate_smart_answer(query, all_templates)
                
                self.cursor.execute("""
                    UPDATE table1 
                    SET answer = %s 
                    WHERE id = %s
                """, (answer, record_id))
                
                updated_count += 1
            
            self.conn.commit()
            print(f"✅ 成功为 {updated_count} 条记录补齐了answer数据")
            return updated_count
            
        except Exception as e:
            print(f"❌ 补齐answer数据失败: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return 0

    def generate_badcase_dimension_scores(self, count=100):
        """
        生成badcase维度评分测试数据

        Args:
            count: 生成数据数量
        """
        print(f"🎯 生成 {count} 条badcase维度评分数据")
        print("-" * 50)

        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return 0

        try:
            # 首先检查是否有questions表和scores表
            self.cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('questions', 'scores')
            """)
            existing_tables = [row[0] for row in self.cursor.fetchall()]

            if 'questions' not in existing_tables:
                print("❌ questions表不存在，请先创建questions表")
                return 0

            if 'scores' not in existing_tables:
                print("❌ scores表不存在，请先创建scores表")
                return 0

            # 获取现有的badcase问题及其答案数据
            self.cursor.execute("""
                SELECT q.id, q.classification, a.id as answer_id
                FROM questions q
                JOIN answers a ON q.id = a.question_id
                WHERE q.is_badcase = true
                LIMIT %s
            """, (count,))

            badcase_data = self.cursor.fetchall()

            if not badcase_data:
                print("❌ 未找到badcase问题及答案数据，请先生成badcase问题和答案")
                return 0

            print(f"找到 {len(badcase_data)} 个badcase问题及答案")

            # 维度定义
            dimensions = [
                '准确性',
                '完整性',
                '相关性',
                '时效性',
                '有用性',
                '满意度'
            ]

            # 为不同分类设置不同的分数倾向
            category_score_ranges = {
                '技术问题': (1.5, 2.8),    # 技术问题分数偏低
                '故障排查': (1.8, 3.0),    # 故障排查分数中等偏低
                '业务咨询': (2.0, 3.2),    # 业务咨询分数中等
                '产品使用': (2.2, 3.5),    # 产品使用分数中等偏高
                '功能建议': (2.5, 3.8),    # 功能建议分数较高
                '其他': (2.0, 3.5)         # 其他分数中等
            }

            inserted_count = 0

            for question_id, classification, answer_id in badcase_data:
                # 获取该分类的分数范围
                score_range = category_score_ranges.get(classification, (2.0, 3.5))

                for dimension in dimensions:
                    # 为每个维度生成评分
                    # 80%的概率生成低分（模拟badcase特征）
                    if random.random() < 0.8:
                        # 生成低分
                        score = round(random.uniform(score_range[0], min(score_range[1], 2.5)), 1)
                    else:
                        # 生成正常分数
                        score = round(random.uniform(2.5, score_range[1]), 1)

                    # 插入评分数据
                    self.cursor.execute("""
                        INSERT INTO scores (question_id, dimension_name, score, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (question_id, dimension_name) DO UPDATE SET
                        score = EXCLUDED.score,
                        created_at = EXCLUDED.created_at
                    """, (
                        question_id,
                        dimension,
                        score,
                        datetime.now()
                    ))

                    inserted_count += 1

            self.conn.commit()
            print(f"✅ 成功生成 {inserted_count} 条维度评分数据")

            # 显示统计信息
            self.cursor.execute("""
                SELECT dimension_name,
                       COUNT(*) as count,
                       ROUND(AVG(score), 2) as avg_score,
                       MIN(score) as min_score,
                       MAX(score) as max_score
                FROM scores
                WHERE dimension_name IS NOT NULL
                GROUP BY dimension_name
                ORDER BY avg_score
            """)

            stats = self.cursor.fetchall()
            print("\n📊 维度评分统计:")
            for dim_name, count, avg_score, min_score, max_score in stats:
                print(f"  {dim_name}: {count}条, 平均{avg_score}, 范围{min_score}-{max_score}")

            return inserted_count

        except Exception as e:
            print(f"❌ 生成维度评分数据失败: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Mock数据管理工具')
    parser.add_argument('--action', required=True,
                        choices=['create_table', 'add_data', 'add_incomplete_data', 'update_answers', 'stats', 'full_setup', 'generate_scores'],
                        help='操作类型')
    parser.add_argument('--count', type=int, default=30, help='生成数据数量(默认30)')
    parser.add_argument('--incomplete', action='store_true', help='生成包含不完整数据（问题或答案为空）')
    
    args = parser.parse_args()
    
    # 创建管理器实例
    manager = MockDataManager()
    
    # 连接数据库
    if not manager.connect_db():
        return False
    
    try:
        print("🔄 Mock数据管理工具")
        print("=" * 60)
        
        if args.action == 'create_table':
            # 创建表
            success = manager.create_table1()
            
        elif args.action == 'add_data':
            # 添加完整数据
            manager.add_answer_column_if_not_exists()
            success = manager.generate_mock_data(
                count=args.count, 
                include_answers=True, 
                include_incomplete=args.incomplete
            ) > 0
            
        elif args.action == 'add_incomplete_data':
            # 添加不完整数据
            manager.add_answer_column_if_not_exists()
            success = manager.generate_mock_data(
                count=args.count, 
                include_answers=True, 
                include_incomplete=True
            ) > 0
            
        elif args.action == 'update_answers':
            # 更新答案
            manager.add_answer_column_if_not_exists()
            success = manager.update_answers_for_existing_data() >= 0
            
        elif args.action == 'stats':
            # 显示统计
            success = manager.show_stats()
            
        elif args.action == 'full_setup':
            # 完整设置
            manager.create_table1()
            manager.add_answer_column_if_not_exists()
            manager.generate_mock_data(args.count)
            success = manager.show_stats()

        elif args.action == 'generate_scores':
            # 生成badcase维度评分数据
            success = manager.generate_badcase_dimension_scores(args.count) > 0

        print("\n" + "=" * 60)
        if success:
            print("✅ 操作完成！")
        else:
            print("❌ 操作失败！")
            
        return success
        
    finally:
        manager.close_db()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 