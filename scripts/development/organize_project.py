#!/usr/bin/env python3
"""
项目目录整理脚本
将杂乱的文件重新组织到合理的目录结构中
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """创建标准的目录结构"""
    directories = [
        'docs/guides',           # 开发指南和说明文档
        'docs/reports',          # 测试报告和问题修复报告
        'docs/api',              # API文档
        'scripts/deployment',    # 部署脚本
        'scripts/development',   # 开发辅助脚本
        'scripts/testing',       # 测试脚本
        'scripts/maintenance',   # 维护脚本
        'tools/cleanup',         # 数据清理工具
        'tools/verification',    # 验证工具
        'tools/debug',           # 调试工具
        'archive/temp',          # 临时文件归档
        'archive/logs',          # 日志归档
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def organize_files():
    """整理文件到对应目录"""

    # 文件分类映射
    file_mappings = {
        # 文档类
        'docs/guides/': [
            'AI问答平台完整开发指南.md',
            'QUICK_START.md',
            'README.md',
            '自动化工作流使用说明.md',
            'docs/README_启动说明.md',
            'docs/前端Dashboard功能详细文档.md',
        ],
        'docs/reports/': [
            '大屏展示功能测试报告.md',
            '大屏展示空白问题修复报告.md',
            '热门问题分类饼图功能说明.md',
            '答案管理页面开发完成报告.md',
            '网络连接问题修复报告.md',
            '饼图布局优化报告.md',
            '饼图显示问题修复报告.md',
        ],
        'docs/api/': [
            'docs/数据库结构总结',
        ],
        
        # 脚本类
        'scripts/deployment/': [
            'start_backend.sh',
            'start_backend_prod.sh',
            'start_frontend.sh',
            'start_mock_services.sh',
            'stop_mock_services.sh',
            'enable_mock_services.sh',
            'install_nodejs.sh',
        ],
        'scripts/testing/': [
            'test_fixed_sql.py',
            'test_improved_sync.py',
            'test_sync_logic.py',
        ],
        'scripts/maintenance/': [
            'pause_scheduler_and_cleanup.py',
            'stop_scheduler_and_cleanup.py',
            'final_stop_and_cleanup.py',
            'thorough_cleanup.py',
        ],
        
        # 工具类
        'tools/cleanup/': [
            'delete_all_week_data.py',
            'delete_this_week_data.py',
            'clear_this_week_data_complete.py',
            'clear_week_data_sql.py',
        ],
        'tools/verification/': [
            'verify_api_after_cleanup.py',
            'verify_cleanup_result.py',
            'verify_final_result.py',
            'verify_sync_logic.py',
            'final_sync_verification.py',
            'final_verification.py',
            'check_actual_data.py',
        ],
        'tools/debug/': [
            'debug_competitor_stats.py',
            'debug_display_api.py',
            'debug_sync_logic.py',
            'analyze_sync_issue.py',
        ],
        
        # 归档类
        'archive/temp/': [
            'system_health.html',
            'test-ai-chart.html',
            'app.log',
            'nohup.out',
        ],
    }
    
    # 执行文件移动
    for target_dir, files in file_mappings.items():
        for file_name in files:
            if os.path.exists(file_name):
                try:
                    shutil.move(file_name, target_dir + file_name)
                    print(f"✅ 移动文件: {file_name} -> {target_dir}")
                except Exception as e:
                    print(f"❌ 移动失败: {file_name} - {str(e)}")
            else:
                print(f"⚠️  文件不存在: {file_name}")

def cleanup_redundant_files():
    """清理冗余文件"""
    
    # 需要删除的冗余文件
    redundant_files = [
        'README_启动说明.md',  # 已有QUICK_START.md
        'venv',               # 项目根目录的venv，应该只保留backend/venv
        'logs',               # 空的logs目录
    ]
    
    for item in redundant_files:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"🗑️  删除目录: {item}")
                else:
                    os.remove(item)
                    print(f"🗑️  删除文件: {item}")
            except Exception as e:
                print(f"❌ 删除失败: {item} - {str(e)}")

def create_new_readme():
    """创建新的项目README"""
    readme_content = """# AI问答平台

## 📁 项目结构

```
ai-qa-platform/
├── 📚 docs/                    # 文档目录
│   ├── guides/                 # 开发指南
│   ├── reports/                # 测试报告
│   └── api/                    # API文档
├── 🔧 scripts/                 # 脚本目录
│   ├── deployment/             # 部署脚本
│   ├── development/            # 开发脚本
│   ├── testing/                # 测试脚本
│   └── maintenance/            # 维护脚本
├── 🛠️ tools/                   # 工具目录
│   ├── cleanup/                # 数据清理工具
│   ├── verification/           # 验证工具
│   └── debug/                  # 调试工具
├── 📦 backend/                 # 后端代码
├── 🎨 frontend/                # 前端代码
└── 📋 archive/                 # 归档文件
```

## 🚀 快速开始

详细的启动说明请查看: [QUICK_START.md](docs/guides/QUICK_START.md)

## 📖 文档

- [完整开发指南](docs/guides/AI问答平台完整开发指南.md)
- [自动化工作流说明](docs/guides/自动化工作流使用说明.md)
- [功能测试报告](docs/reports/)

## 🔧 常用脚本

### 部署相关
- `scripts/deployment/start_backend.sh` - 启动后端服务
- `scripts/deployment/start_frontend.sh` - 启动前端服务
- `scripts/deployment/start_mock_services.sh` - 启动Mock服务

### 维护相关
- `scripts/maintenance/stop_scheduler_and_cleanup.py` - 停止调度器并清理
- `tools/cleanup/delete_all_week_data.py` - 删除本周数据

### 验证相关
- `tools/verification/verify_api_after_cleanup.py` - 验证API状态

## 📞 支持

如有问题，请查看相关文档或联系开发团队。
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 创建新的README.md")

def main():
    """主函数"""
    print("🚀 开始整理项目目录...")
    print("=" * 50)
    
    # 1. 创建目录结构
    print("\n📁 创建目录结构...")
    create_directory_structure()
    
    # 2. 整理文件
    print("\n📋 整理文件...")
    organize_files()
    
    # 3. 清理冗余文件
    print("\n🧹 清理冗余文件...")
    cleanup_redundant_files()
    
    # 4. 创建新的README
    print("\n📝 更新README...")
    create_new_readme()
    
    print("\n" + "=" * 50)
    print("🎉 项目目录整理完成！")
    print("\n📋 整理后的目录结构:")
    print("├── docs/          # 文档")
    print("├── scripts/       # 脚本")
    print("├── tools/         # 工具")
    print("├── backend/       # 后端")
    print("├── frontend/      # 前端")
    print("└── archive/       # 归档")

if __name__ == "__main__":
    main()
