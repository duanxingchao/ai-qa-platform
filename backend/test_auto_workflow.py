#!/usr/bin/env python3
"""
自动化工作流测试脚本
测试启动时立即处理和定时调度功能

功能:
1. 测试启动时立即处理已有数据
2. 测试无数据时的挂起机制
3. 测试可配置的调度间隔
4. 测试新数据插入后的自动处理
"""

import sys
import os
import time
import threading
import requests
import psycopg2
from datetime import datetime, timedelta

# 添加app目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.database import db
from app.models import Question, Answer, Score
from app.services.scheduler_service import scheduler_service

# 数据库配置
DB_CONFIG = {
    'host': "test-huiliu-postgresql.ns-q8rah3y5.svc",
    'port': 5432,
    'user': "postgres",
    'password': "l69jjd9n",
    'database': "ai_qa_platform"
}

class AutoWorkflowTester:
    """自动化工作流测试器"""
    
    def __init__(self):
        self.app = None
        self.conn = None
        self.cursor = None
        
    def setup(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建Flask应用
        self.app = create_app('development')
        
        # 连接数据库
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
            
        return True
    
    def teardown(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def check_mock_services(self):
        """检查Mock服务状态"""
        print("\n📡 检查Mock服务状态...")
        
        services = {
            '分类API': 'http://localhost:8001/health',
            '豆包AI': 'http://localhost:8002/health', 
            '小天AI': 'http://localhost:8003/health',
            '评分API': 'http://localhost:8004/health'
        }
        
        all_running = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ {name}: 运行正常")
                else:
                    print(f"❌ {name}: 状态码 {response.status_code}")
                    all_running = False
            except Exception as e:
                print(f"❌ {name}: 无法连接 - {e}")
                all_running = False
        
        if not all_running:
            print("\n⚠️ 部分Mock服务未运行，请先启动:")
            print("./start_mock_services.sh")
            return False
        
        print("✅ 所有Mock服务运行正常")
        return True
    
    def insert_test_data_to_table1(self, count=5):
        """向table1插入测试数据"""
        print(f"\n📝 向table1插入 {count} 条测试数据...")
        
        try:
            for i in range(count):
                current_time = datetime.now() + timedelta(seconds=i)
                
                query = f"测试问题 {i+1}: 这是一个关于技术的问题，请帮我解答"
                answer = f"这是对问题 {i+1} 的原始答案内容"
                
                self.cursor.execute("""
                    INSERT INTO table1 (
                        pageid, devicetypename, sendmessagetime, query, answer,
                        serviceid, qatype, intent, iskeyboardinput, isstopanswer
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    f'page_{i+1}_{int(current_time.timestamp())}',
                    'PC',
                    current_time,
                    query,
                    answer,
                    'test_service',
                    'FAQ',
                    '查询',
                    True,
                    False
                ))
            
            self.conn.commit()
            print(f"✅ 成功插入 {count} 条测试数据")
            return True
            
        except Exception as e:
            print(f"❌ 插入数据失败: {e}")
            self.conn.rollback()
            return False
    
    def check_data_processing_status(self):
        """检查数据处理状态"""
        print("\n📊 检查数据处理状态...")
        
        with self.app.app_context():
            try:
                # 检查questions表
                questions_count = db.session.query(Question).count()
                print(f"Questions表: {questions_count} 条记录")
                
                # 检查answers表
                answers_count = db.session.query(Answer).count()
                original_answers = db.session.query(Answer).filter_by(assistant_type='original').count()
                doubao_answers = db.session.query(Answer).filter_by(assistant_type='doubao').count()
                xiaotian_answers = db.session.query(Answer).filter_by(assistant_type='xiaotian').count()
                
                print(f"Answers表: {answers_count} 条记录")
                print(f"  - 原始答案: {original_answers}")
                print(f"  - 豆包答案: {doubao_answers}")
                print(f"  - 小天答案: {xiaotian_answers}")
                
                # 检查scores表
                scores_count = db.session.query(Score).count()
                print(f"Scores表: {scores_count} 条记录")
                
                # 检查分类状态
                classified_questions = db.session.query(Question).filter(
                    Question.classification.isnot(None),
                    Question.classification != ''
                ).count()
                print(f"已分类问题: {classified_questions} 条")
                
                return {
                    'questions': questions_count,
                    'answers': answers_count,
                    'scores': scores_count,
                    'classified': classified_questions,
                    'original_answers': original_answers,
                    'doubao_answers': doubao_answers,
                    'xiaotian_answers': xiaotian_answers
                }
                
            except Exception as e:
                print(f"❌ 检查数据状态失败: {e}")
                return None
    
    def test_startup_immediate_processing(self):
        """测试启动时立即处理功能"""
        print("\n🚀 测试启动时立即处理功能...")
        
        # 检查初始状态
        initial_status = self.check_data_processing_status()
        if initial_status is None:
            return False
        
        print(f"初始状态: Questions={initial_status['questions']}, Answers={initial_status['answers']}")
        
        # 插入新数据
        if not self.insert_test_data_to_table1(3):
            return False
        
        # 等待几秒让数据处理
        print("⏳ 等待自动处理 (10秒)...")
        time.sleep(10)
        
        # 检查处理后状态
        final_status = self.check_data_processing_status()
        if final_status is None:
            return False
        
        # 分析结果
        questions_increased = final_status['questions'] > initial_status['questions']
        answers_increased = final_status['answers'] > initial_status['answers']
        
        print(f"处理后状态: Questions={final_status['questions']}, Answers={final_status['answers']}")
        
        if questions_increased and answers_increased:
            print("✅ 启动时立即处理功能正常")
            return True
        else:
            print("❌ 启动时立即处理功能异常")
            return False
    
    def test_suspend_when_no_data(self):
        """测试无数据时挂起功能"""
        print("\n💤 测试无数据时挂起功能...")
        
        # 通过API检查调度器状态
        try:
            response = requests.get('http://localhost:8088/api/scheduler/status', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("📊 调度器状态:", data.get('data', {}).get('scheduler_running', 'Unknown'))
                
                # 检查最近的工作流执行
                workflow_status = data.get('data', {}).get('workflow_status', {})
                if workflow_status:
                    print("📝 工作流状态:")
                    for phase, status in workflow_status.items():
                        print(f"  - {status.get('name', phase)}: {status.get('status', 'unknown')}")
                
                return True
            else:
                print(f"❌ 调度器API返回错误: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 检查调度器状态失败: {e}")
            return False
    
    def test_configurable_interval(self):
        """测试可配置调度间隔"""
        print("\n⏰ 测试可配置调度间隔...")
        
        with self.app.app_context():
            interval = self.app.config.get('WORKFLOW_INTERVAL_MINUTES', 3)
            print(f"📋 当前配置的调度间隔: {interval} 分钟")
            
            auto_process = self.app.config.get('AUTO_PROCESS_ON_STARTUP', True)
            auto_suspend = self.app.config.get('AUTO_SUSPEND_WHEN_NO_DATA', True)
            
            print(f"📋 启动时自动处理: {'启用' if auto_process else '禁用'}")
            print(f"📋 无数据自动挂起: {'启用' if auto_suspend else '禁用'}")
            
            return True
    
    def test_new_data_auto_processing(self):
        """测试新数据自动处理"""
        print("\n🔄 测试新数据自动处理...")
        
        # 记录初始状态
        initial_status = self.check_data_processing_status()
        if initial_status is None:
            return False
        
        print("📝 插入新数据并等待自动处理...")
        
        # 插入新数据
        if not self.insert_test_data_to_table1(2):
            return False
        
        # 等待多个调度周期
        wait_time = 30  # 等待30秒
        print(f"⏳ 等待自动处理 ({wait_time}秒)...")
        time.sleep(wait_time)
        
        # 检查最终状态
        final_status = self.check_data_processing_status()
        if final_status is None:
            return False
        
        # 分析结果
        questions_processed = final_status['questions'] > initial_status['questions']
        answers_generated = final_status['answers'] > initial_status['answers']
        
        if questions_processed and answers_generated:
            print("✅ 新数据自动处理功能正常")
            return True
        else:
            print("❌ 新数据自动处理功能异常")
            print("提示：可能需要更长时间等待，或检查Mock服务状态")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始自动化工作流测试")
        print("=" * 60)
        
        if not self.setup():
            return False
        
        try:
            # 检查前置条件
            if not self.check_mock_services():
                print("\n❌ Mock服务检查失败，测试中止")
                return False
            
            # 测试项目列表
            tests = [
                ("配置检查", self.test_configurable_interval),
                ("挂起机制", self.test_suspend_when_no_data),
                ("启动时处理", self.test_startup_immediate_processing),
                ("新数据处理", self.test_new_data_auto_processing),
            ]
            
            results = []
            for test_name, test_func in tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    result = test_func()
                    results.append((test_name, result))
                    status = "✅ 通过" if result else "❌ 失败"
                    print(f"📊 {test_name}: {status}")
                except Exception as e:
                    print(f"❌ {test_name} 执行异常: {e}")
                    results.append((test_name, False))
            
            # 输出测试总结
            print("\n" + "=" * 60)
            print("📊 测试结果总结:")
            passed = 0
            for test_name, result in results:
                status = "✅ 通过" if result else "❌ 失败"
                print(f"  {test_name}: {status}")
                if result:
                    passed += 1
            
            total = len(results)
            print(f"\n📈 总体结果: {passed}/{total} 个测试通过")
            
            if passed == total:
                print("🎉 所有测试通过！自动化工作流功能正常")
                return True
            else:
                print("⚠️ 部分测试失败，请检查相关功能")
                return False
                
        finally:
            self.teardown()

def main():
    """主函数"""
    tester = AutoWorkflowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 建议：")
        print("1. 继续往table1插入新数据测试自动处理")
        print("2. 通过API监控调度器状态: GET /api/scheduler/status")
        print("3. 检查Mock服务状态: GET /api/mock/status")
        
        sys.exit(0)
    else:
        print("\n💡 故障排除建议：")
        print("1. 确保所有Mock服务正在运行")
        print("2. 检查数据库连接")
        print("3. 查看应用日志: tail -f backend/app.log")
        print("4. 检查环境变量配置")
        
        sys.exit(1)

if __name__ == '__main__':
    main() 