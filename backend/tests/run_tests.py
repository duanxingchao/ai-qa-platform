#!/usr/bin/env python3
"""
测试运行器 - 统一运行所有测试
"""
import sys
import os
import argparse
from datetime import datetime

# 添加父目录到路径，以便导入app模块  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_core_tests():
    """运行核心功能测试"""
    print("🧪 核心功能测试")
    print("=" * 60)
    
    try:
        from test_core import run_core_tests
        return run_core_tests()
    except Exception as e:
        print(f"❌ 核心功能测试失败: {str(e)}")
        return False

def run_api_tests():
    """运行API测试"""
    print("\n🌐 API接口测试")
    print("=" * 60)
    
    try:
        from test_api import run_api_tests
        return run_api_tests()
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 AI问答平台 - 完整测试套件")
    print("=" * 80)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    
    tests = [
        ("核心功能测试", run_core_tests),
        ("API测试", run_api_tests)
    ]
    
    results = {}
    total_passed = 0
    
    for name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"🧪 运行 {name}")
        print(f"{'='*80}")
        
        try:
            result = test_func()
            results[name] = result
            if result:
                total_passed += 1
                print(f"✅ {name} 通过!")
            else:
                print(f"❌ {name} 失败!")
        except Exception as e:
            print(f"💥 {name} 异常: {str(e)}")
            results[name] = False
    
    # 测试总结
    print("\n" + "=" * 80)
    print("📋 测试总结报告")
    print("=" * 80)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15} : {status}")
    
    print(f"\n📊 总体结果:")
    print(f"   🧪 总测试数: {len(tests)}")
    print(f"   ✅ 通过数量: {total_passed}")
    print(f"   ❌ 失败数量: {len(tests) - total_passed}")
    print(f"   📈 成功率: {(total_passed/len(tests)*100):.1f}%")
    
    if total_passed == len(tests):
        print("\n🎉 所有测试通过! 系统状态良好!")
        return True
    else:
        print(f"\n⚠️  有 {len(tests) - total_passed} 个测试类别失败")
        print("\n💡 建议:")
        for name, result in results.items():
            if not result:
                if name == "核心功能测试":
                    print(f"   - 检查数据库连接、同步服务和数据模型")
                elif name == "API测试":
                    print(f"   - 确保Flask应用正在运行")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI问答平台测试运行器')
    parser.add_argument('--type', '-t', 
                       choices=['all', 'core', 'api'],
                       default='all',
                       help='指定运行的测试类型')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细输出')
    
    args = parser.parse_args()
    
    if args.type == 'all':
        success = run_all_tests()
    elif args.type == 'core':
        success = run_core_tests()
    elif args.type == 'api':
        success = run_api_tests()
    else:
        print(f"❌ 未知的测试类型: {args.type}")
        success = False
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 