#!/usr/bin/env python3
"""
Mock数据管理工具 - 统一管理table1表的测试数据
合并了create_test_data.py和update_table1_mock_data.py的功能

功能:
1. 创建table1表(包含answer字段)
2. 添加/更新表结构
3. 生成mock数据
4. 数据统计和验证
5. 支持批量数据管理

使用方式:
python mock_data_manager.py --action create_table
python mock_data_manager.py --action add_data --count 30
python mock_data_manager.py --action add_data --count 100 --incomplete  # 生成包含不完整数据
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

# Mock数据模板 - 可根据需要扩展
MOCK_QUESTIONS = [
    # 在这里添加您的问题模板
    "示例问题1",
    "示例问题2",
    "示例问题3",
]

MOCK_ANSWERS = [
    # 在这里添加您的答案模板
    "示例答案1：详细的回答内容...",
    "示例答案2：详细的回答内容...",
    "示例答案3：详细的回答内容...",
]

# 基础配置数据
DEVICE_TYPES = ['PC', 'Mobile', 'Tablet', 'TV']
CLASSIFICATIONS = ['技术问题', '业务咨询', '产品使用', '故障排查', '功能建议', '其他']
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
                    classification VARCHAR(50),
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
            base_time = datetime.now()
            
            # 扩展问题模板
            extended_questions = [
                "如何使用这个功能？",
                "这个产品的价格是多少？",
                "如何联系客服？",
                "为什么登录失败了？",
                "如何修改密码？",
                "产品有什么优势？",
                "支持哪些支付方式？",
                "如何申请退款？",
                "系统出现错误怎么办？",
                "如何升级账户？",
                "数据安全如何保障？",
                "移动端和PC端有什么区别？",
                "如何导出数据？",
                "支持批量操作吗？",
                "如何设置权限？",
                "API调用频率限制是多少？",
                "如何集成第三方服务？",
                "数据备份策略是什么？",
                "如何优化性能？",
                "技术支持时间是什么时候？"
            ]
            
            # 扩展答案模板  
            extended_answers = [
                "您可以通过点击左侧菜单中的相应选项来使用这个功能。详细步骤请参考用户手册。",
                "我们的产品有多种价格方案，基础版每月99元，专业版每月299元，企业版需要联系销售定制。",
                "您可以通过在线客服、电话400-123-4567或邮件support@example.com联系我们的客服团队。",
                "登录失败可能是用户名密码错误、账户被锁定或网络问题导致。请检查输入信息或联系客服。",
                "修改密码请进入个人设置页面，点击安全设置，然后选择修改密码选项。",
                "我们的产品具有高性能、易使用、安全可靠等优势，已服务超过10万家企业客户。",
                "支持支付宝、微信支付、银行卡、企业转账等多种支付方式。",
                "退款申请请在订单页面提交，我们会在3-5个工作日内处理完成。",
                "系统错误时请先刷新页面，如问题持续存在请联系技术支持团队。",
                "账户升级请进入账户管理页面，选择合适的套餐进行升级操作。",
                "我们采用企业级加密技术，数据传输和存储都经过严格的安全防护。",
                "移动端支持基础功能，PC端提供完整功能体验，建议重要操作在PC端进行。",
                "数据导出功能在设置菜单中，支持Excel、CSV、JSON等多种格式。",
                "系统支持批量导入、批量编辑、批量删除等操作，提高工作效率。",
                "权限设置在管理员面板中，可以按角色、部门、功能模块进行细粒度控制。",
                "API调用频率限制为每小时1000次，如需更高频率请联系商务升级套餐。",
                "我们提供详细的API文档和SDK，支持主流编程语言的第三方集成。",
                "数据每日自动备份，异地多重备份确保数据安全，可快速恢复。",
                "性能优化建议包括：合理使用索引、优化查询语句、定期清理无用数据等。",
                "技术支持时间为工作日9:00-18:00，紧急问题可拨打24小时热线。"
            ]
            
            for i in range(count):
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
                        answer = random.choice(extended_answers)
                elif data_type == 'empty_answer':
                    # 问题有值，答案为空
                    query = random.choice(extended_questions)
                    answer = None
                elif data_type == 'both_empty':
                    # 问题和答案都为空
                    query = None
                    answer = None
                else:  # complete
                    # 完整数据
                    query = random.choice(extended_questions)
                    if include_answers:
                        answer = random.choice(extended_answers)
                
                record = {
                    'pageid': f'page_{random.randint(1000, 9999)}',
                    'devicetypename': random.choice(DEVICE_TYPES),
                    'sendmessagetime': base_time + timedelta(
                        days=random.randint(-30, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    ),
                    'query': query,
                    'answer': answer,
                    'serviceid': random.choice(SERVICE_IDS),
                    'qatype': random.choice(QA_TYPES),
                    'intent': random.choice(INTENTS),
                    'classification': random.choice(CLASSIFICATIONS),
                    'iskeyboardinput': random.choice([True, False]),
                    'isstopanswer': random.choice([True, False])
                }
                new_records.append(record)
            
            # 插入数据
            insert_sql = """
                INSERT INTO table1 
                (pageid, devicetypename, sendmessagetime, query, answer, serviceid, qatype, intent, classification, iskeyboardinput, isstopanswer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    record['classification'],
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
            for record_id, query in records:
                # 生成答案
                if MOCK_ANSWERS:
                    answer = random.choice(MOCK_ANSWERS)
                else:
                    answer = f"这是对问题'{query}'的回答..."
                
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

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Mock数据管理工具')
    parser.add_argument('--action', required=True, 
                        choices=['create_table', 'add_data', 'add_incomplete_data', 'update_answers', 'stats', 'full_setup'],
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