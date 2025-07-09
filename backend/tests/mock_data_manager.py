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
    
    def generate_mock_data(self, count=30, include_answers=True):
        """生成mock数据"""
        print(f"🚀 生成 {count} 条mock数据 (包含answer: {include_answers})")
        print("-" * 50)
        
        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return 0
            
        if not MOCK_QUESTIONS:
            print("⚠️  MOCK_QUESTIONS为空，请先添加问题模板")
            return 0
        
        try:
            # 生成数据
            new_records = []
            base_time = datetime.now()
            
            for i in range(count):
                # 随机选择或生成数据
                query = random.choice(MOCK_QUESTIONS) if MOCK_QUESTIONS else f"测试问题 {i+1}"
                answer = None
                
                if include_answers:
                    if MOCK_ANSWERS:
                        answer = random.choice(MOCK_ANSWERS)
                    else:
                        answer = f"这是对问题'{query}'的回答..."
                
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
            
            self.conn.commit()
            print(f"✅ 成功插入 {inserted_count} 条mock数据")
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
                        choices=['create_table', 'add_data', 'update_answers', 'stats', 'full_setup'],
                        help='操作类型')
    parser.add_argument('--count', type=int, default=30, help='生成数据数量(默认30)')
    
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
            # 添加数据
            manager.add_answer_column_if_not_exists()
            success = manager.generate_mock_data(args.count) > 0
            
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