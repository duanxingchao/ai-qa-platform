#!/usr/bin/env python3
"""
评分系统完整测试脚本
测试新的多模型评分功能
"""
import sys
import os
import time
import requests
import subprocess
import signal
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class ScoringSystemTest:
    """评分系统测试类"""
    
    def __init__(self):
        self.mock_server_process = None
        self.base_url = "http://localhost:5000"
        self.mock_score_url = "http://localhost:8004"
        
    def start_mock_score_server(self):
        """启动Mock评分API服务器"""
        print("🚀 启动Mock评分API服务器...")
        
        try:
            self.mock_server_process = subprocess.Popen([
                'python', 'tests/mock_score_api.py', '--port', '8004'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            time.sleep(3)
            
            # 验证服务器状态
            try:
                response = requests.get(f'{self.mock_score_url}/health', timeout=5)
                if response.status_code == 200:
                    print("✅ Mock评分API服务器启动成功")
                    return True
                else:
                    print(f"❌ Mock评分API服务器状态异常: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Mock评分API服务器无法访问: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Mock评分API服务器启动失败: {e}")
            return False
    
    def stop_mock_server(self):
        """停止Mock服务器"""
        if self.mock_server_process:
            try:
                self.mock_server_process.terminate()
                self.mock_server_process.wait(timeout=5)
                print("✅ Mock评分API服务器已停止")
            except subprocess.TimeoutExpired:
                self.mock_server_process.kill()
                print("⚠️ 强制停止Mock评分API服务器")
            except Exception as e:
                print(f"❌ 停止Mock服务器失败: {e}")
    
    def test_mock_api_directly(self):
        """直接测试Mock评分API"""
        print("\n🧪 测试Mock评分API...")
        
        test_data = {
            "inputs": {
                "question": "什么是人工智能？",
                "our_answer": "人工智能是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。",
                "doubao_answer": "人工智能（AI）是一种让机器具备类似人类智能的技术，包括学习、推理和决策能力。",
                "xiaotian_answer": "人工智能是指通过计算机程序实现的智能行为，能够处理复杂任务和问题。",
                "classification": "技术问题"
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'test-api-key'
        }
        
        try:
            response = requests.post(
                f'{self.mock_score_url}/score',
                json=test_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Mock评分API调用成功")
                
                # 解析评分结果
                text_result = result["data"]["outputs"]["text"]
                import json
                score_results = json.loads(text_result)
                
                print(f"📊 评分结果预览:")
                for i, score in enumerate(score_results, 1):
                    model_name = score.get("模型名称", "未知")
                    avg_score = (score.get("准确性", 0) + score.get("完整性", 0) + 
                               score.get("清晰度", 0) + score.get("相关性", 0) + 
                               score.get("有用性", 0)) / 5
                    print(f"   {i}. {model_name}: 平均分 {avg_score:.1f}")
                
                return True
            else:
                print(f"❌ Mock评分API调用失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Mock评分API测试异常: {e}")
            return False
    
    def test_score_client(self):
        """测试评分API客户端"""
        print("\n🔌 测试评分API客户端...")
        
        try:
            from app.services.api_client import APIClientFactory
            
            # 创建评分客户端
            score_client = APIClientFactory.get_score_client()
            
            # 测试多模型评分
            score_results = score_client.score_multiple_answers(
                question="什么是Python编程语言？",
                our_answer="Python是一种高级编程语言，以简洁和可读性著称。",
                doubao_answer="Python是一种解释型、面向对象的编程语言，广泛用于各种应用开发。",
                xiaotian_answer="Python是一种功能强大的编程语言，适合初学者学习和专业开发使用。",
                classification="编程技术"
            )
            
            print("✅ 评分API客户端调用成功")
            print(f"📊 获得 {len(score_results)} 个模型的评分结果")
            
            for score in score_results:
                model_name = score.get("模型名称", "未知")
                reason = score.get("理由", "无理由")
                print(f"   {model_name}: {reason[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ 评分API客户端测试失败: {e}")
            return False
    
    def test_ai_processing_service(self):
        """测试AI处理服务的评分功能"""
        print("\n🤖 测试AI处理服务评分功能...")
        
        try:
            from app import create_app
            from app.services.ai_processing_service import AIProcessingService
            
            app = create_app()
            with app.app_context():
                ai_service = AIProcessingService()
                
                # 获取待评分问题
                question_groups = ai_service._get_questions_for_scoring(limit=3)
                print(f"📋 找到 {len(question_groups)} 个待评分问题组")
                
                if question_groups:
                    # 测试评分处理
                    result = ai_service.process_scoring_batch(limit=1)
                    
                    if result.get('success'):
                        print("✅ AI处理服务评分测试成功")
                        print(f"   {result.get('message', '')}")
                        return True
                    else:
                        print(f"❌ AI处理服务评分失败: {result.get('message', '')}")
                        return False
                else:
                    print("⚠️ 没有找到待评分的问题，测试跳过")
                    return True
                
        except Exception as e:
            print(f"❌ AI处理服务测试异常: {e}")
            return False
    
    def test_web_api_endpoint(self):
        """测试Web API端点"""
        print("\n🌐 测试Web API评分端点...")
        
        # 检查Flask应用是否运行
        try:
            response = requests.get(f"{self.base_url}/api/sync/health", timeout=5)
            if response.status_code != 200:
                print("⚠️ Flask应用未运行，跳过Web API测试")
                return True
        except:
            print("⚠️ Flask应用未运行，跳过Web API测试")
            return True
        
        try:
            # 测试手动触发评分
            response = requests.post(
                f"{self.base_url}/api/scheduler/manual/scoring",
                json={"limit": 1, "days_back": 1},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ Web API评分端点测试成功")
                    print(f"   {result.get('message', '')}")
                    return True
                else:
                    print(f"❌ Web API评分失败: {result.get('message', '')}")
                    return False
            else:
                print(f"❌ Web API评分端点调用失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Web API测试异常: {e}")
            return False
    
    def test_database_integration(self):
        """测试数据库集成"""
        print("\n🗄️ 测试数据库集成...")
        
        try:
            from app import create_app
            from app.models.score import Score
            from app.models.answer import Answer
            from app.utils.database import db
            
            app = create_app()
            with app.app_context():
                # 统计评分数据
                total_scores = db.session.query(Score).count()
                recent_scores = db.session.query(Score).filter(
                    Score.rated_at >= datetime.now().replace(hour=0, minute=0, second=0)
                ).count()
                
                # 统计答案数据
                total_answers = db.session.query(Answer).count()
                scored_answers = db.session.query(Answer).filter(Answer.is_scored == True).count()
                
                print("✅ 数据库集成测试成功")
                print(f"   总评分记录: {total_scores}")
                print(f"   今日新增评分: {recent_scores}")
                print(f"   总答案数: {total_answers}")
                print(f"   已评分答案: {scored_answers}")
                
                return True
                
        except Exception as e:
            print(f"❌ 数据库集成测试失败: {e}")
            return False
    
    def run_complete_test(self):
        """运行完整的评分系统测试"""
        print("🎬 开始评分系统完整测试")
        print("="*60)
        print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        try:
            # 1. 启动Mock服务器
            if self.start_mock_score_server():
                test_results.append(("Mock服务器启动", True))
                
                # 2. 测试Mock API
                test_results.append(("Mock API直接测试", self.test_mock_api_directly()))
                
                # 3. 测试API客户端
                test_results.append(("API客户端测试", self.test_score_client()))
                
                # 4. 测试AI处理服务
                test_results.append(("AI处理服务测试", self.test_ai_processing_service()))
                
                # 5. 测试Web API端点
                test_results.append(("Web API端点测试", self.test_web_api_endpoint()))
                
                # 6. 测试数据库集成
                test_results.append(("数据库集成测试", self.test_database_integration()))
            else:
                test_results.append(("Mock服务器启动", False))
        
        except KeyboardInterrupt:
            print(f"\n🛑 用户中断测试")
        finally:
            # 清理资源
            self.stop_mock_server()
        
        # 显示测试结果
        print("\n" + "="*60)
        print("📊 评分系统测试结果")
        print("="*60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {status} {test_name}")
        
        print(f"\n📈 测试统计: {passed}/{total} 通过")
        print(f"🎯 成功率: {(passed/total*100):.1f}%" if total > 0 else "🎯 成功率: 0%")
        
        if passed == total:
            print("🎉 评分系统测试完全成功！")
            print("✅ 评分功能已就绪，可以投入使用")
        elif passed > total * 0.8:
            print("👍 评分系统测试基本成功")
            print("🔧 少量功能需要修复")
        else:
            print("⚠️ 评分系统需要进一步完善")
            print("🛠️ 请检查失败的测试项")
        
        return passed == total

def main():
    """主函数"""
    test_suite = ScoringSystemTest()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print(f"\n🛑 收到中断信号，正在清理...")
        test_suite.stop_mock_server()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 运行测试
    success = test_suite.run_complete_test()
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 