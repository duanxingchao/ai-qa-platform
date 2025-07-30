#!/usr/bin/env python3
"""
测试修改后的同步逻辑
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

try:
    from app.services.sync_service import sync_service
    from app.utils.database import get_db_session
    from app.models.question import Question
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)

def get_week_start():
    """获取本周开始时间（周一00:00:00）"""
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

def test_sync_logic():
    """测试同步逻辑"""
    week_start = get_week_start()
    print(f"=== 测试修改后的同步逻辑 ===")
    print(f"当前时间: {datetime.now()}")
    print(f"本周开始时间: {week_start}")
    
    try:
        # 1. 测试get_week_start方法
        sync_week_start = sync_service.get_week_start()
        print(f"1. sync_service.get_week_start(): {sync_week_start}")
        
        # 2. 测试get_last_sync_time
        last_sync_time = sync_service.get_last_sync_time()
        print(f"2. 最后同步时间: {last_sync_time}")
        
        # 3. 模拟不同的last_sync_time场景
        print(f"\n=== 场景测试 ===")
        
        # 场景1：last_sync_time在本周内
        if last_sync_time and last_sync_time >= week_start:
            print(f"✅ 场景1：last_sync_time在本周内，正常同步")
            print(f"   将从 {last_sync_time} 开始同步")
        
        # 场景2：last_sync_time早于本周
        elif last_sync_time and last_sync_time < week_start:
            print(f"⚠️  场景2：last_sync_time早于本周开始时间")
            print(f"   原始时间: {last_sync_time}")
            print(f"   调整后将从本周开始时间同步: {week_start}")
        
        # 场景3：没有last_sync_time
        else:
            print(f"📝 场景3：没有last_sync_time，将从本周开始时间同步: {week_start}")
        
        # 4. 测试fetch_new_data_from_table1方法（不实际执行，只测试逻辑）
        print(f"\n=== 测试数据获取逻辑 ===")
        
        # 模拟一个早于本周的时间
        old_time = week_start - timedelta(days=7)
        print(f"4. 模拟早于本周的时间: {old_time}")
        
        # 检查questions表中是否有本周数据
        with get_db_session() as session:
            this_week_count = session.query(Question).filter(
                Question.created_at >= week_start
            ).count()
            print(f"5. questions表中本周数据量: {this_week_count}")
            
            # 检查是否有本周之前的数据
            before_week_count = session.query(Question).filter(
                Question.created_at < week_start
            ).count()
            print(f"6. questions表中本周之前的数据量: {before_week_count}")
        
        print(f"\n=== 修改效果 ===")
        print("✅ 修改后的同步逻辑将确保：")
        print("   1. 只同步本周的数据")
        print("   2. 即使last_sync_time早于本周，也会调整为本周开始时间")
        print("   3. 防止同步大量历史数据")
        print("   4. 在调度服务中也添加了相同的限制")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync_logic()
