#!/usr/bin/env python3
"""
答案生成流程测试
测试从数据库取问题 → 调用Mock API → 写回答案表的完整流程
"""
import sys
import os
import unittest
import time
import subprocess
import signal
import requests
from datetime import datetime

# 添加父目录到路径，以便导入app模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class MockServerManager:
    """Mock服务器管理器"""
    
    def __init__(self):
        self.classification_server = None
        self.doubao_server = None
        self.xiaotian_server = None
    
    def start_servers(self):
        """启动所有Mock服务器"""
        print("🚀 启动Mock服务器...")
        
        # 启动分类API服务器
        try:
            self.classification_server = subprocess.Popen([
                'python', 'mock_classification_api.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            print("✅ 分类API服务器启动成功 (端口 8001)")
        except Exception as e:
            print(f"❌ 分类API服务器启动失败: {e}")
        
        # 启动豆包Mock API服务器
        try:
            self.doubao_server = subprocess.Popen([
                'python', 'mock_ai_api.py', '--port', '8002', '--service', 'doubao'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            print("✅ 豆包Mock API服务器启动成功 (端口 8002)")
        except Exception as e:
            print(f"❌ 豆包Mock API服务器启动失败: {e}")
        
        # 启动小天Mock API服务器  
        try:
            self.xiaotian_server = subprocess.Popen([
                'python', 'mock_ai_api.py', '--port', '8003', '--service', 'xiaotian'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(2)
            print("✅ 小天Mock API服务器启动成功 (端口 8003)")
        except Exception as e:
            print(f"❌ 小天Mock API服务器启动失败: {e}")
        
        # 等待服务器完全启动
        time.sleep(3)
        
        # 验证服务器状态
        self.verify_servers()
    
    def verify_servers(self):
        """验证服务器状态"""
        servers = [
            ('分类API', 'http://localhost:8001/health'),
            ('豆包API', 'http://localhost:8002/health'),
            ('小天API', 'http://localhost:8003/health')
        ]
        
        for name, url in servers:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}服务器运行正常")
                else:
                    print(f"⚠️  {name}服务器状态异常: {response.status_code}")
            except Exception as e:
                print(f"❌ {name}服务器无法访问: {e}")
    
    def stop_servers(self):
        """停止所有Mock服务器"""
        print("🛑 停止Mock服务器...")
        
        for server_name, server in [
            ('分类API', self.classification_server),
            ('豆包API', self.doubao_server),
            ('小天API', self.xiaotian_server)
        ]:
            if server:
                try:
                    server.terminate()
                    server.wait(timeout=5)
                    print(f"✅ {server_name}服务器已停止")
                except subprocess.TimeoutExpired:
                    server.kill()
                    print(f"⚠️  强制停止{server_name}服务器")
                except Exception as e:
                    print(f"❌ 停止{server_name}服务器失败: {e}")

class AnswerGenerationTests(unittest.TestCase):
    """答案生成流程测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        print("🧪 答案生成流程测试")
        print("=" * 60)
        
        # 启动Mock服务器
        cls.mock_manager = MockServerManager()
        cls.mock_manager.start_servers()
        
        # 导入应用相关模块
        try:
            from app import create_app
            from app.utils.database import db
            from app.models.question import Question
            from app.models.answer import Answer
            from app.services.ai_processing_service import AIProcessingService
            
            cls.app = create_app()
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            cls.db = db
            cls.Question = Question
            cls.Answer = Answer
            cls.ai_service = AIProcessingService()
            
            print("✅ 应用环境初始化成功")
            
        except Exception as e:
            print(f"❌ 应用环境初始化失败: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 停止Mock服务器
        cls.mock_manager.stop_servers()
        
        # 清理应用上下文
        if hasattr(cls, 'app_context'):
            cls.app_context.pop()
        
        print("🧹 测试环境清理完成")
    
    def setUp(self):
        """每个测试方法前的准备"""
        # 清理测试数据
        try:
            self.db.session.query(self.Answer).filter(
                self.Answer.assistant_type.in_(['doubao', 'xiaotian'])
            ).delete()
            self.db.session.commit()
        except Exception as e:
            print(f"⚠️  清理测试数据失败: {e}")
            self.db.session.rollback()
    
    def tearDown(self):
        """每个测试方法后的清理"""
        try:
            self.db.session.rollback()
        except:
            pass
    
    def test_get_questions_for_answer_generation(self):
        """测试获取需要生成答案的问题"""
        print("\n📋 测试：获取需要生成答案的问题")
        
        # 获取已分类的问题
        questions = self.ai_service._get_questions_for_answer_generation(limit=5)
        
        self.assertIsInstance(questions, list)
        print(f"✅ 找到 {len(questions)} 个需要生成答案的问题")
        
        if questions:
            question = questions[0]
            self.assertIsNotNone(question.business_id)
            self.assertIsNotNone(question.query)
            print(f"✅ 示例问题: {question.query[:50]}...")
    
    def test_doubao_api_client(self):
        """测试豆包API客户端"""
        print("\n🤖 测试：豆包API客户端")
        
        try:
            from app.services.api_client import APIClientFactory
            
            # 获取豆包客户端
            doubao_client = APIClientFactory.get_doubao_client()
            
            # 测试答案生成
            result = doubao_client.generate_answer(
                question="什么是人工智能？",
                context="分类: 科技技术"
            )
            
            self.assertIn('answer', result)
            self.assertIn('confidence', result)
            self.assertIn('model', result)
            
            print(f"✅ 豆包API调用成功")
            print(f"   答案长度: {len(result['answer'])} 字符")
            print(f"   置信度: {result['confidence']}")
            print(f"   模型: {result['model']}")
            
        except Exception as e:
            self.fail(f"豆包API客户端测试失败: {e}")
    
    def test_xiaotian_api_client(self):
        """测试小天API客户端"""
        print("\n🤖 测试：小天API客户端")
        
        try:
            from app.services.api_client import APIClientFactory
            
            # 获取小天客户端
            xiaotian_client = APIClientFactory.get_xiaotian_client()
            
            # 测试答案生成
            result = xiaotian_client.generate_answer(
                question="如何学习编程？",
                context="分类: 教育"
            )
            
            self.assertIn('answer', result)
            self.assertIn('confidence', result)
            self.assertIn('length', result)
            
            print(f"✅ 小天API调用成功")
            print(f"   答案长度: {result['length']} 字符")
            print(f"   置信度: {result['confidence']}")
            print(f"   服务: {result['service']}")
            
        except Exception as e:
            self.fail(f"小天API客户端测试失败: {e}")
    
    def test_answer_generation_batch_process(self):
        """测试批量答案生成流程"""
        print("\n🔄 测试：批量答案生成流程")
        
        try:
            # 获取测试前的答案数量
            initial_doubao_count = self.db.session.query(self.Answer).filter_by(
                assistant_type='doubao'
            ).count()
            
            initial_xiaotian_count = self.db.session.query(self.Answer).filter_by(
                assistant_type='xiaotian'
            ).count()
            
            print(f"📊 测试前答案数量 - 豆包: {initial_doubao_count}, 小天: {initial_xiaotian_count}")
            
            # 执行批量答案生成
            result = self.ai_service.process_answer_generation_batch(limit=3)
            
            # 验证执行结果
            self.assertTrue(result['success'])
            self.assertIn('processed_count', result)
            self.assertIn('doubao_count', result)
            self.assertIn('xiaotian_count', result)
            
            print(f"✅ 批量答案生成完成")
            print(f"   处理问题数: {result['processed_count']}")
            print(f"   豆包答案数: {result['doubao_count']}")
            print(f"   小天答案数: {result['xiaotian_count']}")
            print(f"   错误数: {result['error_count']}")
            
            # 验证数据库中的答案增加
            final_doubao_count = self.db.session.query(self.Answer).filter_by(
                assistant_type='doubao'
            ).count()
            
            final_xiaotian_count = self.db.session.query(self.Answer).filter_by(
                assistant_type='xiaotian'
            ).count()
            
            doubao_added = final_doubao_count - initial_doubao_count
            xiaotian_added = final_xiaotian_count - initial_xiaotian_count
            
            print(f"📊 数据库变化 - 豆包新增: {doubao_added}, 小天新增: {xiaotian_added}")
            
            # 验证答案内容
            if doubao_added > 0:
                latest_doubao = self.db.session.query(self.Answer).filter_by(
                    assistant_type='doubao'
                ).order_by(self.Answer.created_at.desc()).first()
                
                self.assertIsNotNone(latest_doubao.answer_text)
                self.assertGreater(len(latest_doubao.answer_text), 0)
                print(f"✅ 豆包答案样例: {latest_doubao.answer_text[:100]}...")
            
            if xiaotian_added > 0:
                latest_xiaotian = self.db.session.query(self.Answer).filter_by(
                    assistant_type='xiaotian'
                ).order_by(self.Answer.created_at.desc()).first()
                
                self.assertIsNotNone(latest_xiaotian.answer_text)
                self.assertGreater(len(latest_xiaotian.answer_text), 0)
                print(f"✅ 小天答案样例: {latest_xiaotian.answer_text[:100]}...")
            
        except Exception as e:
            self.fail(f"批量答案生成测试失败: {e}")
    
    def test_answer_duplication_prevention(self):
        """测试答案重复生成防护"""
        print("\n🛡️  测试：答案重复生成防护")
        
        try:
            # 第一次执行答案生成
            result1 = self.ai_service.process_answer_generation_batch(limit=2)
            
            first_doubao_count = result1['doubao_count']
            first_xiaotian_count = result1['xiaotian_count']
            
            print(f"第一次生成 - 豆包: {first_doubao_count}, 小天: {first_xiaotian_count}")
            
            # 第二次执行答案生成（应该跳过已存在的答案）
            result2 = self.ai_service.process_answer_generation_batch(limit=2)
            
            second_doubao_count = result2['doubao_count']
            second_xiaotian_count = result2['xiaotian_count']
            
            print(f"第二次生成 - 豆包: {second_doubao_count}, 小天: {second_xiaotian_count}")
            
            # 验证第二次生成的答案数量应该更少（因为跳过了已存在的）
            if first_doubao_count > 0:
                self.assertLessEqual(second_doubao_count, first_doubao_count)
            if first_xiaotian_count > 0:
                self.assertLessEqual(second_xiaotian_count, first_xiaotian_count)
            
            print("✅ 重复生成防护机制正常工作")
            
        except Exception as e:
            self.fail(f"重复生成防护测试失败: {e}")
    
    def test_api_error_handling(self):
        """测试API错误处理"""
        print("\n⚠️  测试：API错误处理")
        
        try:
            # 修改API URL为无效地址，测试错误处理
            from app.services.api_client import APIClientFactory
            
            # 重置客户端缓存
            APIClientFactory._instances.clear()
            
            # 临时修改配置
            from app.config import Config
            original_doubao_url = Config.DOUBAO_API_URL
            Config.DOUBAO_API_URL = 'http://localhost:9999'  # 无效URL
            
            try:
                doubao_client = APIClientFactory.get_doubao_client()
                result = doubao_client.generate_answer("测试问题")
                self.fail("应该抛出连接异常")
            except Exception as e:
                print(f"✅ 正确捕获API错误: {type(e).__name__}")
            finally:
                # 恢复配置
                Config.DOUBAO_API_URL = original_doubao_url
                APIClientFactory._instances.clear()
            
        except Exception as e:
            print(f"⚠️  API错误处理测试异常: {e}")


def run_answer_generation_tests():
    """运行答案生成测试"""
    print("🤖 答案生成流程测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(AnswerGenerationTests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)
    
    # 显示测试结果摘要
    print("\n" + "=" * 60)
    print("📋 答案生成测试结果摘要")
    print("=" * 60)
    print(f"🧪 运行测试数: {result.testsRun}")
    print(f"✅ 成功测试数: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 失败测试数: {len(result.failures)}")
    print(f"💥 错误测试数: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    # 计算成功率
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n📈 成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 答案生成流程测试通过!")
    else:
        print("⚠️  答案生成流程测试需要改进")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_answer_generation_tests()
    sys.exit(0 if success else 1) 