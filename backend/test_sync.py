#!/usr/bin/env python3
"""
数据同步功能测试脚本
"""
import os
import sys
import logging

# 设置路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.services.sync_service import sync_service

def test_sync():
    """测试数据同步功能"""
    print("🚀 开始测试数据同步功能...")
    
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        try:
            # 1. 获取同步状态
            print("\n📊 获取同步状态:")
            status = sync_service.get_sync_status()
            for key, value in status.items():
                print(f"  {key}: {value}")
            
            # 2. 获取同步统计
            print("\n📈 获取同步统计:")
            stats = sync_service.get_sync_statistics()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            # 3. 执行数据同步
            print("\n🔄 执行数据同步:")
            result = sync_service.perform_sync()
            print(f"  同步结果: {result}")
            
            # 4. 再次获取统计信息
            print("\n📈 同步后统计:")
            stats_after = sync_service.get_sync_statistics()
            for key, value in stats_after.items():
                print(f"  {key}: {value}")
                
            print("\n✅ 数据同步测试完成!")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    test_sync() 