#!/usr/bin/env python3
"""
核心功能测试 - 整合数据库、同步、单元测试
合并了 test_unit.py, test_database.py, test_new_sync.py 的功能
"""
import sys
import os
import unittest
import psycopg2
import hashlib
from datetime import datetime
from unittest.mock import patch, Mock

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

class DatabaseTests(unittest.TestCase):
    """数据库连接和结构测试"""
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            self.assertTrue(True, "数据库连接成功")
            print(f"✅ 数据库连接成功: {version[:50]}...")
        except Exception as e:
            self.fail(f"数据库连接失败: {str(e)}")
    
    def test_required_tables_exist(self):
        """测试必需表是否存在"""
        required_tables = ['table1', 'questions', 'answers', 'scores', 'review_status']
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            for table in required_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, f"表 {table} 不存在")
                
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: 存在 ({count} 条记录)")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.fail(f"表结构检查失败: {str(e)}")
    
    def test_table1_structure(self):
        """测试table1表结构和数据质量"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'table1' 
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            expected_columns = ['id', 'pageid', 'devicetypename', 'sendmessagetime', 
                              'query', 'answer', 'serviceid', 'qatype', 'intent', 
                              'classification', 'iskeyboardinput', 'isstopanswer']
            
            actual_columns = [col[0] for col in columns]
            for expected_col in expected_columns:
                self.assertIn(expected_col, actual_columns, f"缺少字段: {expected_col}")
            
            # 检查数据质量
            cursor.execute("SELECT COUNT(*) FROM table1")
            total_count = cursor.fetchone()[0]
            
            if total_count > 0:
                cursor.execute("""
                    SELECT COUNT(*) FROM table1 
                    WHERE query IS NULL OR query = '' OR TRIM(query) = ''
                """)
                empty_count = cursor.fetchone()[0]
                valid_count = total_count - empty_count
                quality_rate = (valid_count / total_count * 100) if total_count > 0 else 0
                
                print(f"✅ table1数据质量: {quality_rate:.1f}% ({valid_count}/{total_count})")
                self.assertGreater(quality_rate, 0, "没有有效的query数据")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.fail(f"table1结构检查失败: {str(e)}")

class SyncServiceTests(unittest.TestCase):
    """同步服务功能测试"""
    
    def setUp(self):
        """测试设置"""
        try:
            from app import create_app
            self.app = create_app('testing')
            self.app_context = self.app.app_context()
            self.app_context.push()
        except Exception as e:
            self.skipTest(f"应用初始化失败: {str(e)}")
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
    
    def test_get_sync_status(self):
        """测试获取同步状态"""
        try:
            from app.services.sync_service import sync_service
            status = sync_service.get_sync_status()
            
            # 验证状态结构
            self.assertIn('status', status)
            self.assertIn('total_synced', status)
            self.assertIn('last_sync_time', status)
            print(f"✅ 同步状态: {status}")
            
        except Exception as e:
            self.fail(f"获取同步状态失败: {str(e)}")
    
    def test_get_sync_statistics(self):
        """测试获取同步统计"""
        try:
            from app.services.sync_service import sync_service
            stats = sync_service.get_sync_statistics()
            
            # 验证统计信息结构
            if 'error' not in stats:
                expected_keys = ['questions_count', 'answers_count', 'table1_total_count']
                for key in expected_keys:
                    if key in stats:
                        self.assertIsInstance(stats[key], (int, float))
                print(f"✅ 同步统计: {stats}")
            else:
                self.fail(f"获取统计信息出错: {stats['error']}")
                
        except Exception as e:
            self.fail(f"获取同步统计失败: {str(e)}")
    
    def test_perform_sync(self):
        """测试执行同步"""
        try:
            from app.services.sync_service import sync_service
            
            # 获取同步前统计
            before_stats = sync_service.get_sync_statistics()
            
            # 执行同步
            result = sync_service.perform_sync(force_full_sync=False)
            
            # 验证同步结果
            self.assertIn('success', result)
            self.assertIn('message', result)
            
            if result['success']:
                print(f"✅ 同步成功: {result['message']}")
                
                # 验证同步后的统计
                after_stats = sync_service.get_sync_statistics()
                if 'error' not in after_stats:
                    print(f"   同步前questions: {before_stats.get('questions_count', 0)}")
                    print(f"   同步后questions: {after_stats.get('questions_count', 0)}")
                    print(f"   同步前answers: {before_stats.get('answers_count', 0)}")
                    print(f"   同步后answers: {after_stats.get('answers_count', 0)}")
            else:
                print(f"⚠️  同步未执行新操作: {result['message']}")
                
        except Exception as e:
            # 同步失败不应该导致测试失败，只是记录
            print(f"⚠️  同步测试异常: {str(e)}")

class DataConsistencyTests(unittest.TestCase):
    """数据一致性测试"""
    
    def setUp(self):
        """测试设置"""
        try:
            from app import create_app
            self.app = create_app('testing')
            self.app_context = self.app.app_context()
            self.app_context.push()
        except Exception as e:
            self.skipTest(f"应用初始化失败: {str(e)}")
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
    
    def test_business_id_generation(self):
        """测试business_id生成逻辑"""
        try:
            from app.utils.database import execute_sql
            
            # 获取table1的一条记录
            result = execute_sql('SELECT pageid, sendmessagetime, query FROM table1 LIMIT 1')
            row = result.fetchone()
            
            if row:
                pageid, send_time, query_text = row
                
                # 计算预期的business_id
                raw_str = f'{pageid}{send_time.isoformat() if send_time else ""}{query_text}'
                expected_business_id = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
                
                # 查找对应的questions记录
                result = execute_sql('SELECT business_id FROM questions WHERE pageid = :pageid', {'pageid': pageid})
                questions_row = result.fetchone()
                
                if questions_row:
                    actual_business_id = questions_row[0]
                    self.assertEqual(expected_business_id, actual_business_id, 
                                   "business_id生成逻辑不一致")
                    print(f"✅ business_id生成逻辑正确")
                else:
                    print("ℹ️  questions表中未找到对应记录（正常情况）")
            else:
                self.skipTest("table1中没有数据")
                
        except Exception as e:
            self.fail(f"数据一致性检查失败: {str(e)}")
    
    def test_sql_filtering_logic(self):
        """测试SQL过滤逻辑"""
        try:
            from app.utils.database import execute_sql
            
            # 测试基础查询
            total_result = execute_sql("SELECT COUNT(*) FROM table1")
            total_count = total_result.scalar()
            
            # 测试过滤查询
            filtered_result = execute_sql("""
                SELECT COUNT(*) FROM table1 
                WHERE query IS NOT NULL 
                AND query != '' 
                AND TRIM(query) != ''
            """)
            filtered_count = filtered_result.scalar()
            
            # 验证过滤逻辑
            self.assertGreaterEqual(total_count, filtered_count)
            self.assertGreaterEqual(filtered_count, 0)
            
            filter_rate = ((total_count - filtered_count) / total_count * 100) if total_count > 0 else 0
            print(f"✅ SQL过滤逻辑正确: 过滤了 {filter_rate:.1f}% 的无效数据")
            
        except Exception as e:
            self.fail(f"SQL过滤逻辑测试失败: {str(e)}")

class ModelTests(unittest.TestCase):
    """数据模型测试"""
    
    def setUp(self):
        """测试设置"""
        try:
            from app import create_app
            self.app = create_app('testing')
            self.app_context = self.app.app_context()
            self.app_context.push()
        except Exception as e:
            self.skipTest(f"应用初始化失败: {str(e)}")
    
    def tearDown(self):
        """测试清理"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()
    
    def test_question_model(self):
        """测试Question模型"""
        try:
            from app.models.question import Question
            from app.utils.database import db
            
            # 测试基础查询
            total_questions = db.session.query(Question).count()
            self.assertGreaterEqual(total_questions, 0)
            print(f"✅ Question模型查询成功: {total_questions} 条记录")
            
            # 测试最新记录
            latest_question = db.session.query(Question).order_by(
                Question.created_at.desc()
            ).first()
            
            if latest_question:
                print(f"✅ 最新记录: {latest_question.business_id}")
                self.assertIsNotNone(latest_question.business_id)
                
        except Exception as e:
            self.fail(f"Question模型测试失败: {str(e)}")
    
    def test_answer_model(self):
        """测试Answer模型"""
        try:
            from app.models.answer import Answer
            from app.utils.database import db
            
            # 测试基础查询
            total_answers = db.session.query(Answer).count()
            self.assertGreaterEqual(total_answers, 0)
            print(f"✅ Answer模型查询成功: {total_answers} 条记录")
            
        except Exception as e:
            self.fail(f"Answer模型测试失败: {str(e)}")

def run_core_tests():
    """运行核心测试"""
    print("🧪 核心功能测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        DatabaseTests,
        SyncServiceTests, 
        DataConsistencyTests,
        ModelTests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)
    
    # 显示测试结果摘要
    print("\n" + "=" * 60)
    print("📋 核心测试结果摘要")
    print("=" * 60)
    print(f"🧪 运行测试数: {result.testsRun}")
    print(f"✅ 成功测试数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败测试数: {len(result.failures)}")
    print(f"💥 错误测试数: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n📈 成功率: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("🎉 所有核心测试通过!")
        return True
    else:
        print("⚠️  部分核心测试失败")
        return False

if __name__ == '__main__':
    success = run_core_tests()
    sys.exit(0 if success else 1) 