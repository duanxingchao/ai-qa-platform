#!/usr/bin/env python3
"""
🚀 立即执行完整AI问答平台测试
1. 生成今天的测试数据到table1
2. 执行完整流程：同步→分类→答案生成→评分
3. 验证所有功能正常
"""
import sys
import os
import time
import random
import psycopg2
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, '.')

# 修正评分API端口
os.environ['SCORE_API_URL'] = 'http://localhost:8004'

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_step(step, title):
    print(f"\n📋 步骤 {step}: {title}")
    print('-'*50)

def generate_today_data():
    """生成50条今天的测试数据到table1"""
    print_step(1, "生成今天的测试数据到table1")
    
    # 数据库连接
    DB_CONFIG = {
        'host': "test-huiliu-postgresql.ns-q8rah3y5.svc",
        'port': 5432,
        'user': "postgres", 
        'password': "l69jjd9n",
        'database': "ai_qa_platform"
    }
    
    # 问题模板
    questions = [
        "什么是人工智能？请详细解释其概念和应用领域。",
        "如何学习Python编程？有什么推荐的学习路径吗？",
        "机器学习和深度学习有什么区别？",
        "什么是云计算？它有哪些优势？",
        "区块链技术的工作原理是什么？",
        "数据科学家需要掌握哪些技能？",
        "什么是DevOps？它如何改善软件开发流程？",
        "网络安全有哪些常见的威胁？如何防范？",
        "大数据分析有哪些常用工具？",
        "什么是微服务架构？它有什么优缺点？"
    ]
    
    # 答案模板
    answers = [
        "人工智能(AI)是计算机科学的一个分支，它致力于创建能够模拟人类智能的系统。",
        "学习Python编程建议从基础语法开始，然后学习数据结构、面向对象编程等。",
        "机器学习是人工智能的一个子集，深度学习是机器学习的一个分支。",
        "云计算是通过互联网提供计算资源和服务的模式，具有成本节约等优势。",
        "区块链是一种分布式账本技术，通过密码学和共识机制确保数据安全。"
    ]
    
    try:
        # 连接数据库
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 生成50条今天的数据
        now = datetime.now()
        success_count = 0
        
        for i in range(50):
            # 随机选择问题和答案
            query = random.choice(questions)
            answer = random.choice(answers)
            
            # 生成今天内的随机时间
            random_seconds = random.randint(0, 24*60*60-1)
            send_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=random_seconds)
            
            try:
                cursor.execute("""
                    INSERT INTO table1 (
                        pageid, devicetypename, sendmessagetime, query, answer,
                        serviceid, qatype, intent, classification, 
                        iskeyboardinput, isstopanswer
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"page_{random.randint(10000, 99999)}",
                    random.choice(['mobile', 'desktop', 'tablet']),
                    send_time,
                    query,
                    answer,
                    random.randint(1, 10),
                    random.choice(['问答', '咨询', '投诉', '建议']),
                    None, None,  # intent, classification
                    True, False
                ))
                success_count += 1
            except Exception as e:
                print(f"❌ 插入第{i+1}条数据失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ 成功生成 {success_count} 条今天的测试数据")
        return True
    except Exception as e:
        print(f"❌ 生成数据失败: {e}")
        return False

def run_full_workflow():
    """运行完整的AI处理工作流程"""
    print_step(2, "执行完整AI处理工作流程")
    try:
        from app import create_app
        from app.services.sync_service import sync_service
        from app.services.ai_processing_service import AIProcessingService

        app = create_app('development')
        with app.app_context():
            ai_service = AIProcessingService()

            # 2.1 数据同步
            print("\n🔄 执行数据同步...")
            sync_result = sync_service.perform_sync(force_full_sync=True)
            if sync_result.get('success'):
                print(f"✅ 数据同步成功: {sync_result.get('message')}")
                print(f"   同步问题数: {sync_result.get('synced_questions', 0)}")
                print(f"   同步答案数: {sync_result.get('synced_answers', 0)}")
            else:
                print(f"❌ 数据同步失败: {sync_result.get('message')}")
                return False

            # 2.2 问题分类
            print("\n🏷️ 执行问题分类...")
            classification_result = ai_service.process_classification_batch(limit=50, days_back=1)
            if classification_result.get('success'):
                print(f"✅ 问题分类成功: {classification_result.get('message')}")
                print(f"   处理问题数: {classification_result.get('processed_count', 0)}")
                print(f"   成功分类数: {classification_result.get('success_count', 0)}")
            else:
                print(f"❌ 问题分类失败: {classification_result.get('message')}")

            # 2.3 答案生成
            print("\n🤖 执行答案生成...")
            answer_result = ai_service.process_answer_generation_batch(limit=50, days_back=1)
            if answer_result.get('success'):
                print(f"✅ 答案生成成功: {answer_result.get('message')}")
                print(f"   处理问题数: {answer_result.get('processed_count', 0)}")
            else:
                print(f"❌ 答案生成失败: {answer_result.get('message')}")

            # 2.4 评分
            print("\n⭐ 执行评分...")
            score_result = ai_service.process_scoring_batch(limit=50, days_back=1)
            if score_result.get('success'):
                print(f"✅ 评分成功: {score_result.get('message')}")
                print(f"   处理问题数: {score_result.get('processed_count', 0)}")
                print(f"   成功评分数: {score_result.get('success_count', 0)}")
            else:
                print(f"❌ 评分失败: {score_result.get('message')}")
        return True
    except Exception as e:
        print(f"❌ 流程执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print_header("AI问答平台完整流程测试")
    if generate_today_data():
        run_full_workflow()
    print("\n🎉 测试流程全部完成！") 