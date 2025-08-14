#!/usr/bin/env python3
"""
改进版Mock数据管理工具 - 确保生成的数据不重复
解决原版本中问题模板有限导致的重复问题

主要改进:
1. 动态生成唯一问题，避免重复
2. 支持生成大量不重复数据
3. 更丰富的数据变化
4. 更好的数据分布控制

使用方式:
python mock_data_manager_improved.py --action add_data --count 200
"""

import sys
import os
import argparse
import psycopg2
import random
import uuid
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

# 基础配置数据
DEVICE_TYPES = ['PC', 'Mobile', 'Tablet', 'TV', 'Smart Speaker', 'Watch']
# Mock分类API的标准16分类（与mock_classification_api.py保持一致）
CLASSIFICATIONS = [
    '技术问题', '产品使用', '业务咨询', '功能建议', '故障排查',
    '其他', '工程问题', '科学问题', '教育问题', '经济问题',
    '账户管理', '系统优化', '安全设置', '数据分析',
    '用户体验', '性能优化'
]
SERVICE_IDS = [
    'service_001', 'service_002', 'service_003', 'service_004', 'service_005',
    'service_006', 'service_007', 'service_008', 'service_009', 'service_010'
]
QA_TYPES = ['FAQ', 'CHAT', 'SEARCH', 'HELP', 'GUIDE', 'TUTORIAL']
INTENTS = ['查询', '咨询', '投诉', '建议', '帮助', '学习', '购买', '退款', '升级', '配置']

# 问题模板组件 - 用于动态生成唯一问题
QUESTION_PREFIXES = [
    "如何", "怎么", "为什么", "什么是", "哪里可以", "能否", "是否支持", "如何设置",
    "怎样配置", "如何优化", "为什么会", "什么时候", "哪个版本", "如何解决",
    "怎么处理", "如何避免", "什么原因", "如何提升", "怎样改进", "如何实现"
]

QUESTION_SUBJECTS = [
    "登录功能", "支付系统", "数据导出", "权限管理", "API接口", "移动端应用",
    "桌面客户端", "云存储", "数据备份", "安全认证", "用户界面", "报表生成",
    "邮件通知", "短信服务", "文件上传", "图片处理", "视频播放", "音频录制",
    "地图定位", "二维码", "条形码", "人脸识别", "语音识别", "机器学习",
    "人工智能", "区块链", "物联网", "大数据", "云计算", "边缘计算"
]

QUESTION_ACTIONS = [
    "配置", "使用", "集成", "部署", "维护", "监控", "调试", "测试", "升级",
    "迁移", "备份", "恢复", "优化", "扩展", "定制", "开发", "设计", "分析",
    "管理", "控制", "访问", "共享", "同步", "导入", "导出", "转换", "压缩",
    "加密", "解密", "验证", "授权", "审计", "日志", "统计", "预测", "推荐"
]

QUESTION_CONTEXTS = [
    "在生产环境中", "在测试环境中", "在开发环境中", "在移动设备上", "在PC端",
    "在服务器端", "在客户端", "在云平台上", "在本地部署时", "在集群环境中",
    "在高并发场景下", "在大数据量情况下", "在网络不稳定时", "在离线模式下",
    "在多用户环境中", "在企业级应用中", "在个人使用时", "在团队协作中",
    "在跨平台部署时", "在国际化场景中"
]

class ImprovedMockDataManager:
    """改进版Mock数据管理类"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.generated_questions = set()  # 用于跟踪已生成的问题，避免重复
        self.generated_pageids = set()    # 用于跟踪已生成的页面ID，避免重复
    
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
    
    def generate_unique_question(self):
        """生成唯一的问题"""
        max_attempts = 1000  # 最大尝试次数，避免无限循环
        attempts = 0
        
        while attempts < max_attempts:
            # 随机组合生成问题
            prefix = random.choice(QUESTION_PREFIXES)
            subject = random.choice(QUESTION_SUBJECTS)
            action = random.choice(QUESTION_ACTIONS)
            context = random.choice(QUESTION_CONTEXTS)
            
            # 生成不同格式的问题
            question_formats = [
                f"{prefix}{action}{subject}？",
                f"{prefix}{context}{action}{subject}？",
                f"{context}，{prefix}{action}{subject}？",
                f"{prefix}在{subject}中{action}？",
                f"{subject}的{action}功能{prefix}使用？",
                f"{context}如何{action}{subject}？"
            ]
            
            question = random.choice(question_formats)
            
            # 检查是否重复
            if question not in self.generated_questions:
                self.generated_questions.add(question)
                return question
            
            attempts += 1
        
        # 如果尝试次数过多，使用UUID确保唯一性
        unique_id = str(uuid.uuid4())[:8]
        question = f"关于{random.choice(QUESTION_SUBJECTS)}的{random.choice(QUESTION_ACTIONS)}问题_{unique_id}？"
        self.generated_questions.add(question)
        return question
    
    def generate_unique_pageid(self):
        """生成唯一的页面ID"""
        max_attempts = 1000
        attempts = 0
        
        while attempts < max_attempts:
            pageid = f'page_{random.randint(10000, 99999)}'
            if pageid not in self.generated_pageids:
                self.generated_pageids.add(pageid)
                return pageid
            attempts += 1
        
        # 使用UUID确保唯一性
        unique_id = str(uuid.uuid4())[:8]
        pageid = f'page_{unique_id}'
        self.generated_pageids.add(pageid)
        return pageid
    
    def generate_contextual_answer(self, question):
        """根据问题生成相关的答案"""
        # 答案模板组件
        answer_prefixes = [
            "根据您的问题，", "针对这个问题，", "关于您提到的", "对于这种情况，",
            "基于我们的经验，", "通常来说，", "一般情况下，", "建议您"
        ]
        
        answer_solutions = [
            "可以通过以下步骤解决", "建议采用以下方案", "推荐使用以下方法",
            "可以参考以下操作", "建议按照以下流程", "可以尝试以下解决方案"
        ]
        
        answer_details = [
            "1. 首先检查相关配置 2. 然后验证权限设置 3. 最后测试功能是否正常",
            "1. 登录管理后台 2. 找到相应设置项 3. 按照提示进行配置",
            "1. 备份现有数据 2. 执行相关操作 3. 验证结果并记录",
            "1. 查看系统日志 2. 分析错误原因 3. 采取相应措施解决",
            "1. 联系技术支持 2. 提供详细信息 3. 等待专业指导"
        ]
        
        prefix = random.choice(answer_prefixes)
        solution = random.choice(answer_solutions)
        detail = random.choice(answer_details)
        
        return f"{prefix}{solution}：{detail}。如有其他问题，请随时联系我们的客服团队。"

    def generate_unique_mock_data(self, count=200, include_answers=True, include_incomplete=False):
        """生成唯一的mock数据

        Args:
            count: 生成数据数量
            include_answers: 是否包含答案
            include_incomplete: 是否包含不完整数据（问题或答案为空）
        """
        print(f"🚀 生成 {count} 条唯一mock数据 (包含answer: {include_answers})")
        if include_incomplete:
            print("   包含不完整数据")
        print("-" * 50)

        if not self.cursor or not self.conn:
            print("❌ 数据库连接无效")
            return 0

        try:
            # 清空已生成记录，重新开始
            self.generated_questions.clear()
            self.generated_pageids.clear()

            # 生成数据
            new_records = []
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            for i in range(count):
                print(f"\r生成进度: {i+1}/{count}", end="", flush=True)

                # 决定数据完整性
                if include_incomplete:
                    # 20% 问题为空，15% 答案为空，5% 都为空，60% 完整数据
                    data_type = random.choices(
                        ['empty_query', 'empty_answer', 'both_empty', 'complete'],
                        weights=[20, 15, 5, 60]
                    )[0]
                else:
                    data_type = 'complete'

                # 生成唯一问题和答案
                query = None
                answer = None

                if data_type == 'empty_query':
                    query = None
                    if include_answers:
                        answer = self.generate_contextual_answer("通用问题")
                elif data_type == 'empty_answer':
                    query = self.generate_unique_question()
                    answer = None
                elif data_type == 'both_empty':
                    query = None
                    answer = None
                else:  # complete
                    query = self.generate_unique_question()
                    if include_answers:
                        answer = self.generate_contextual_answer(query)

                # 生成当天内的随机时间
                total_seconds_today = int((now - today_start).total_seconds())
                if total_seconds_today > 0:
                    random_seconds = random.randint(0, total_seconds_today)
                    send_time = today_start + timedelta(seconds=random_seconds)
                else:
                    send_time = now

                # 生成唯一的pageid
                pageid = self.generate_unique_pageid()

                record = {
                    'pageid': pageid,
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

            print()  # 换行

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
            print(f"✅ 成功插入 {inserted_count} 条唯一mock数据")
            print(f"📊 数据唯一性统计:")
            print(f"  唯一问题数量: {len(self.generated_questions)}")
            print(f"  唯一页面ID数量: {len(self.generated_pageids)}")

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

            # 唯一问题数量
            self.cursor.execute("SELECT COUNT(DISTINCT query) FROM table1 WHERE query IS NOT NULL AND query != ''")
            result = self.cursor.fetchone()
            unique_questions = result[0] if result else 0

            # 唯一页面ID数量
            self.cursor.execute("SELECT COUNT(DISTINCT pageid) FROM table1 WHERE pageid IS NOT NULL")
            result = self.cursor.fetchone()
            unique_pages = result[0] if result else 0

            return {
                'total_count': total_count,
                'query_count': query_count,
                'answer_count': answer_count,
                'complete_count': complete_count,
                'unique_questions': unique_questions,
                'unique_pages': unique_pages
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
        print(f"  唯一问题数量: {stats['unique_questions']}")
        print(f"  唯一页面ID数量: {stats['unique_pages']}")

        if stats['total_count'] > 0:
            print(f"  数据完整率: {(stats['complete_count']/stats['total_count']*100):.1f}%")
            if stats['query_count'] > 0:
                print(f"  问题唯一率: {(stats['unique_questions']/stats['query_count']*100):.1f}%")

        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='改进版Mock数据管理工具 - 确保数据不重复')
    parser.add_argument('--action', required=True,
                        choices=['create_table', 'add_data', 'add_incomplete_data', 'stats', 'full_setup'],
                        help='操作类型')
    parser.add_argument('--count', type=int, default=200, help='生成数据数量(默认200)')
    parser.add_argument('--incomplete', action='store_true', help='生成包含不完整数据（问题或答案为空）')

    args = parser.parse_args()

    # 创建管理器实例
    manager = ImprovedMockDataManager()

    # 连接数据库
    if not manager.connect_db():
        return False

    try:
        print("🔄 改进版Mock数据管理工具")
        print("=" * 60)
        print("✨ 特性：确保生成的数据不重复")
        print("=" * 60)

        if args.action == 'create_table':
            # 创建表
            success = manager.create_table1()

        elif args.action == 'add_data':
            # 添加唯一数据
            success = manager.generate_unique_mock_data(
                count=args.count,
                include_answers=True,
                include_incomplete=args.incomplete
            ) > 0

        elif args.action == 'add_incomplete_data':
            # 添加包含不完整的唯一数据
            success = manager.generate_unique_mock_data(
                count=args.count,
                include_answers=True,
                include_incomplete=True
            ) > 0

        elif args.action == 'stats':
            # 显示统计
            success = manager.show_stats()

        elif args.action == 'full_setup':
            # 完整设置
            manager.create_table1()
            manager.generate_unique_mock_data(args.count)
            success = manager.show_stats()

        print("\n" + "=" * 60)
        if success:
            print("✅ 操作完成！")
            if args.action in ['add_data', 'add_incomplete_data', 'full_setup']:
                print(f"🎉 成功生成 {args.count} 条唯一数据，无重复问题！")
        else:
            print("❌ 操作失败！")

        return success

    finally:
        manager.close_db()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
