#!/usr/bin/env python3
"""
展示项目结构的工具
"""

import os
from pathlib import Path

def count_files_in_directory(directory):
    """统计目录中的文件数量"""
    try:
        return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
    except:
        return 0

def show_project_structure():
    """展示项目结构"""
    
    print("🎉 AI问答平台 - 项目整理完成！")
    print("=" * 60)
    print()
    
    # 项目结构
    structure = {
        "📚 docs/": {
            "description": "文档目录",
            "subdirs": {
                "guides/": "开发指南和使用说明",
                "reports/": "功能测试和修复报告", 
                "api/": "API文档和数据库结构"
            }
        },
        "🔧 scripts/": {
            "description": "脚本目录",
            "subdirs": {
                "deployment/": "部署相关脚本",
                "development/": "开发辅助脚本",
                "testing/": "测试脚本",
                "maintenance/": "维护脚本"
            }
        },
        "🛠️ tools/": {
            "description": "工具目录",
            "subdirs": {
                "cleanup/": "数据清理工具",
                "verification/": "验证工具",
                "debug/": "调试工具"
            }
        },
        "⚙️ config/": {
            "description": "配置文件",
            "subdirs": {}
        },
        "📦 backend/": {
            "description": "后端代码",
            "subdirs": {
                "app/": "Flask应用核心代码",
                "tests/": "测试代码",
                "tools/": "后端工具脚本"
            }
        },
        "🎨 frontend/": {
            "description": "前端代码",
            "subdirs": {
                "src/": "Vue.js源代码",
                "dist/": "构建产物"
            }
        },
        "📋 archive/": {
            "description": "归档文件",
            "subdirs": {
                "temp/": "临时文件归档",
                "logs/": "日志文件归档"
            }
        }
    }
    
    print("📁 项目目录结构:")
    print()
    
    for main_dir, info in structure.items():
        dir_name = main_dir.split()[1]  # 去掉emoji
        if os.path.exists(dir_name):
            file_count = count_files_in_directory(dir_name)
            print(f"{main_dir:<20} {info['description']}")
            
            for subdir, desc in info['subdirs'].items():
                full_path = os.path.join(dir_name, subdir)
                if os.path.exists(full_path):
                    sub_file_count = count_files_in_directory(full_path)
                    print(f"  ├── {subdir:<15} {desc} ({sub_file_count} 文件)")
                else:
                    print(f"  ├── {subdir:<15} {desc} (空)")
            print()
    
    print("=" * 60)
    print()
    
    # 统计信息
    print("📊 整理统计:")
    
    # 统计各目录文件数量
    stats = {}
    for main_dir, info in structure.items():
        dir_name = main_dir.split()[1]
        if os.path.exists(dir_name):
            total_files = 0
            for root, dirs, files in os.walk(dir_name):
                total_files += len(files)
            stats[main_dir] = total_files
    
    for dir_name, count in stats.items():
        print(f"  {dir_name:<20} {count} 个文件")
    
    print(f"\n  📁 总计: {sum(stats.values())} 个文件")
    print()
    
    # 主要功能说明
    print("🚀 主要功能:")
    print("  ✅ 数据同步与清洗")
    print("  ✅ AI智能分类 (16个领域)")
    print("  ✅ 多AI答案生成 (豆包、小天)")
    print("  ✅ 五维质量评分")
    print("  ✅ 人工审核工作流")
    print("  ✅ 实时数据大屏")
    print()
    
    # 快速启动提示
    print("🎯 快速启动:")
    print("  1. 后端服务: ./scripts/deployment/start_backend.sh")
    print("  2. 前端服务: ./scripts/deployment/start_frontend.sh")
    print("  3. Mock服务: ./scripts/deployment/start_mock_services.sh")
    print()
    
    print("📖 详细文档: docs/guides/QUICK_START.md")
    print("=" * 60)

if __name__ == "__main__":
    show_project_structure()
