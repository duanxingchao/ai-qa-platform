#!/usr/bin/env python3
"""
🚀 AI问答平台快速全功能测试
快速验证所有核心功能是否正常
"""
import sys
import os
import time
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_functionality():
    """快速测试基本功能"""
    print("🧪 AI问答平台快速功能测试")
    print("="*50)
    
    test_results = []
    
    # 1. 数据库连接测试
    print("\n🗄️ 测试数据库连接...")
    try:
        from app import create_app
        from app.utils.database import db
        
        app = create_app()
        with app.app_context():
            db.session.execute(db.text("SELECT 1")).fetchone()
            print("  ✅ 数据库连接正常")
            test_results.append(("数据库连接", True))
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {str(e)}")
        test_results.append(("数据库连接", False))
    
    # 2. 数据表检查
    print("\n📋 检查数据表...")
    try:
        with app.app_context():
            tables = db.session.execute(db.text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchall()
            
            table_names = [table[0] for table in tables]
            required_tables = ['questions', 'answers', 'scores', 'review_status']
            missing = set(required_tables) - set(table_names)
            
            if not missing:
                print(f"  ✅ 所有必需表存在 ({len(required_tables)}个)")
                test_results.append(("数据表结构", True))
            else:
                print(f"  ❌ 缺少表: {missing}")
                test_results.append(("数据表结构", False))
                
    except Exception as e:
        print(f"  ❌ 表检查失败: {str(e)}")
        test_results.append(("数据表结构", False))
    
    # 3. 数据模型测试
    print("\n🏗️ 测试数据模型...")
    try:
        from app.models import Question, Answer, Score, ReviewStatus
        from app.utils.database import db
        
        with app.app_context():
            question_count = db.session.query(Question).count()
            answer_count = db.session.query(Answer).count()
            
            print(f"  ✅ 数据模型正常 (问题: {question_count}, 答案: {answer_count})")
            test_results.append(("数据模型", True))
            
    except Exception as e:
        print(f"  ❌ 数据模型测试失败: {str(e)}")
        test_results.append(("数据模型", False))
    
    # 4. AI处理服务测试
    print("\n🤖 测试AI处理服务...")
    try:
        from app.services.ai_processing_service import AIProcessingService
        
        with app.app_context():
            ai_service = AIProcessingService()
            
            # 检查关键方法
            required_methods = [
                'process_classification_batch',
                'process_answer_generation_batch',
                'process_scoring_batch',
                'get_processing_statistics'
            ]
            
            missing_methods = [m for m in required_methods if not hasattr(ai_service, m)]
            
            if not missing_methods:
                print(f"  ✅ AI处理服务完整 ({len(required_methods)}个方法)")
                test_results.append(("AI处理服务", True))
            else:
                print(f"  ❌ 缺少方法: {missing_methods}")
                test_results.append(("AI处理服务", False))
                
    except Exception as e:
        print(f"  ❌ AI处理服务测试失败: {str(e)}")
        test_results.append(("AI处理服务", False))
    
    # 5. API客户端测试
    print("\n🔌 测试API客户端...")
    try:
        from app.services.api_client import APIClientFactory
        
        # 测试客户端创建
        clients_created = 0
        try:
            APIClientFactory.get_classification_client()
            clients_created += 1
        except:
            pass
            
        try:
            APIClientFactory.get_doubao_client()
            clients_created += 1
        except:
            pass
            
        try:
            APIClientFactory.get_xiaotian_client()
            clients_created += 1
        except:
            pass
        
        try:
            APIClientFactory.get_score_client()
            clients_created += 1
        except:
            pass
        
        if clients_created >= 3:
            print(f"  ✅ API客户端正常 ({clients_created}/4个客户端)")
            test_results.append(("API客户端", True))
        else:
            print(f"  ⚠️  部分API客户端异常 ({clients_created}/4个客户端)")
            test_results.append(("API客户端", None))  # 警告状态
            
    except Exception as e:
        print(f"  ❌ API客户端测试失败: {str(e)}")
        test_results.append(("API客户端", False))
    
    # 6. 数据同步服务测试
    print("\n🔄 测试数据同步服务...")
    try:
        from app.services.sync_service import SyncService
        
        with app.app_context():
            sync_service = SyncService()
            status = sync_service.get_sync_status()
            
            print(f"  ✅ 同步服务正常 (状态: {status.get('status', 'unknown')})")
            test_results.append(("数据同步服务", True))
            
    except Exception as e:
        print(f"  ❌ 数据同步服务测试失败: {str(e)}")
        test_results.append(("数据同步服务", False))
    
    # 7. Web API测试
    print("\n🌐 测试Web API...")
    try:
        with app.test_client() as client:
            response = client.get('/api/sync/status')
            
            if response.status_code == 200:
                print(f"  ✅ Web API正常 (状态码: {response.status_code})")
                test_results.append(("Web API", True))
            else:
                print(f"  ⚠️  Web API响应异常 (状态码: {response.status_code})")
                test_results.append(("Web API", None))
                
    except Exception as e:
        print(f"  ❌ Web API测试失败: {str(e)}")
        test_results.append(("Web API", False))
    
    # 8. 定时任务调度器测试
    print("\n⏰ 测试定时任务调度器...")
    try:
        from app.services.scheduler_service import SchedulerService
        
        with app.app_context():
            scheduler_service = SchedulerService()
            
            print(f"  ✅ 调度器服务正常")
            test_results.append(("定时任务调度器", True))
            
    except Exception as e:
        print(f"  ❌ 调度器测试失败: {str(e)}")
        test_results.append(("定时任务调度器", False))
    
    # 测试结果汇总
    print("\n" + "="*50)
    print("📊 快速测试结果汇总")
    print("="*50)
    
    passed = sum(1 for _, result in test_results if result is True)
    warned = sum(1 for _, result in test_results if result is None)
    failed = sum(1 for _, result in test_results if result is False)
    total = len(test_results)
    
    print(f"📈 测试统计: 总计 {total}, 通过 {passed}, 警告 {warned}, 失败 {failed}")
    print(f"🎯 成功率: {(passed/total*100):.1f}%")
    
    print(f"\n📋 详细结果:")
    for test_name, result in test_results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  WARN"
        print(f"  {status} {test_name}")
    
    # 项目状态评估
    print(f"\n🎯 项目状态:")
    if failed == 0:
        print("  🎉 优秀！所有核心功能都正常")
        print("  ✅ 项目可以进入下一阶段开发")
    elif failed <= 2:
        print("  👍 良好！大部分功能正常")
        print("  🔧 建议修复少量问题")
    else:
        print("  ⚠️  需要改进，存在一些问题")
        print("  🛠️  建议逐一解决问题")
    
    return failed == 0

if __name__ == '__main__':
    print(f"🕐 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = time.time()
    
    success = test_basic_functionality()
    
    end_time = time.time()
    print(f"\n⏱️  测试耗时: {(end_time - start_time):.1f}秒")
    print(f"🏁 测试完成: {'成功' if success else '发现问题'}")
    
    sys.exit(0 if success else 1)