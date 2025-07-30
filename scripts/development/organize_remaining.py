#!/usr/bin/env python3
"""
整理剩余文件的脚本
"""

import os
import shutil
from pathlib import Path

def organize_remaining_files():
    """整理剩余的文件"""
    
    # 移动docs目录下的文件
    remaining_mappings = {
        'docs/guides/': [
            'docs/README_启动说明.md',
            'docs/前端Dashboard功能详细文档.md',
        ],
        'docs/api/': [
            'docs/数据库结构总结',
        ],
        'config/': [
            'mock_services_config.json',
        ],
        'scripts/development/': [
            'organize_project.py',
        ],
        'archive/temp/': [
            'frontend/设计参考文档',
        ]
    }
    
    # 创建config目录
    Path('config').mkdir(exist_ok=True)
    
    # 执行文件移动
    for target_dir, files in remaining_mappings.items():
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        for file_path in files:
            if os.path.exists(file_path):
                try:
                    file_name = os.path.basename(file_path)
                    target_path = os.path.join(target_dir, file_name)
                    shutil.move(file_path, target_path)
                    print(f"✅ 移动: {file_path} -> {target_path}")
                except Exception as e:
                    print(f"❌ 移动失败: {file_path} - {str(e)}")

def clean_backend_directory():
    """清理backend目录中的临时文件"""
    backend_cleanup = [
        'backend/add_sample_scores.py',
        'backend/generate_realtime_events.py', 
        'backend/immediate_full_test.py',
        'backend/test_answer_api.py',
        'backend/test_auto_workflow.py',
        'backend/app.log',
    ]
    
    # 创建backend/tools目录
    Path('backend/tools').mkdir(exist_ok=True)
    
    for file_path in backend_cleanup:
        if os.path.exists(file_path):
            try:
                file_name = os.path.basename(file_path)
                if file_name.endswith('.log'):
                    # 日志文件移动到archive
                    target_path = f"archive/logs/{file_name}"
                    Path('archive/logs').mkdir(exist_ok=True)
                else:
                    # 工具文件移动到backend/tools
                    target_path = f"backend/tools/{file_name}"
                
                shutil.move(file_path, target_path)
                print(f"✅ 清理backend: {file_path} -> {target_path}")
            except Exception as e:
                print(f"❌ 清理失败: {file_path} - {str(e)}")

def create_project_index():
    """创建项目索引文件"""
    
    # 创建scripts/README.md
    scripts_readme = """# Scripts 脚本目录

## 📁 目录结构

- `deployment/` - 部署相关脚本
- `development/` - 开发辅助脚本  
- `testing/` - 测试脚本
- `maintenance/` - 维护脚本

## 🚀 常用脚本

### 部署脚本
- `deployment/start_backend.sh` - 启动后端服务
- `deployment/start_frontend.sh` - 启动前端服务
- `deployment/start_mock_services.sh` - 启动Mock服务

### 维护脚本
- `maintenance/stop_scheduler_and_cleanup.py` - 停止调度器并清理数据
"""
    
    with open('scripts/README.md', 'w', encoding='utf-8') as f:
        f.write(scripts_readme)
    
    # 创建tools/README.md
    tools_readme = """# Tools 工具目录

## 📁 目录结构

- `cleanup/` - 数据清理工具
- `verification/` - 验证工具
- `debug/` - 调试工具

## 🛠️ 常用工具

### 数据清理
- `cleanup/delete_all_week_data.py` - 删除本周所有数据

### 验证工具
- `verification/verify_api_after_cleanup.py` - 验证API清理后状态

### 调试工具
- `debug/debug_display_api.py` - 调试大屏API
"""
    
    with open('tools/README.md', 'w', encoding='utf-8') as f:
        f.write(tools_readme)
    
    # 创建docs/README.md
    docs_readme = """# Documentation 文档目录

## 📁 目录结构

- `guides/` - 开发指南和使用说明
- `reports/` - 功能测试报告和问题修复报告
- `api/` - API文档和数据库结构

## 📖 主要文档

### 开发指南
- `guides/AI问答平台完整开发指南.md` - 完整的开发指南
- `guides/QUICK_START.md` - 快速启动指南

### 功能报告
- `reports/` - 各种功能测试和修复报告
"""
    
    with open('docs/README.md', 'w', encoding='utf-8') as f:
        f.write(docs_readme)
    
    print("✅ 创建项目索引文件")

def update_main_readme():
    """更新主README文件"""
    readme_content = """# 🤖 AI问答平台

一个基于多AI模型的智能问答处理平台，支持自动分类、答案生成、质量评分和人工审核。

## 📁 项目结构

```
ai-qa-platform/
├── 📚 docs/                    # 📖 文档目录
│   ├── guides/                 # 开发指南和使用说明
│   ├── reports/                # 功能测试和修复报告
│   └── api/                    # API文档和数据库结构
├── 🔧 scripts/                 # 🚀 脚本目录
│   ├── deployment/             # 部署相关脚本
│   ├── development/            # 开发辅助脚本
│   ├── testing/                # 测试脚本
│   └── maintenance/            # 维护脚本
├── 🛠️ tools/                   # 🔨 工具目录
│   ├── cleanup/                # 数据清理工具
│   ├── verification/           # 验证工具
│   └── debug/                  # 调试工具
├── ⚙️ config/                  # 📋 配置文件
├── 📦 backend/                 # 🔙 后端代码
│   ├── app/                    # Flask应用
│   ├── tests/                  # 测试代码
│   └── tools/                  # 后端工具
├── 🎨 frontend/                # 🔜 前端代码
│   ├── src/                    # 源代码
│   └── dist/                   # 构建产物
└── 📋 archive/                 # 🗃️ 归档文件
    ├── temp/                   # 临时文件
    └── logs/                   # 日志文件
```

## 🚀 快速开始

```bash
# 1. 启动后端服务
./scripts/deployment/start_backend.sh

# 2. 启动前端服务  
./scripts/deployment/start_frontend.sh

# 3. 启动Mock服务（开发环境）
./scripts/deployment/start_mock_services.sh
```

详细说明请查看: [快速启动指南](docs/guides/QUICK_START.md)

## 📖 主要文档

- 📋 [完整开发指南](docs/guides/AI问答平台完整开发指南.md)
- 🔄 [自动化工作流说明](docs/guides/自动化工作流使用说明.md)
- 🎯 [前端Dashboard功能文档](docs/guides/前端Dashboard功能详细文档.md)
- 📊 [功能测试报告](docs/reports/)

## 🔧 常用操作

### 🚀 服务管理
```bash
# 启动服务
./scripts/deployment/start_backend.sh
./scripts/deployment/start_frontend.sh

# 停止服务
./scripts/maintenance/stop_scheduler_and_cleanup.py
```

### 🧹 数据管理
```bash
# 清理本周数据
python3 tools/cleanup/delete_all_week_data.py

# 验证API状态
python3 tools/verification/verify_api_after_cleanup.py
```

### 🐛 调试工具
```bash
# 调试大屏API
python3 tools/debug/debug_display_api.py

# 调试同步逻辑
python3 tools/debug/debug_sync_logic.py
```

## 🏗️ 系统架构

- **数据同步**: 从table1增量同步到questions/answers表
- **智能分类**: 16个领域的自动分类
- **答案生成**: 豆包、小天AI多模型答案生成
- **质量评分**: 五维度智能评分系统
- **人工审核**: 完整的审核工作流
- **可视化**: 实时数据大屏展示

## 📞 技术支持

如有问题，请查看相关文档或联系开发团队。

---
*最后更新: 2025-07-29*
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 更新主README文件")

def main():
    """主函数"""
    print("🔄 继续整理剩余文件...")
    print("=" * 50)
    
    # 1. 整理剩余文件
    print("\n📋 整理剩余文件...")
    organize_remaining_files()
    
    # 2. 清理backend目录
    print("\n🧹 清理backend目录...")
    clean_backend_directory()
    
    # 3. 创建项目索引
    print("\n📝 创建项目索引...")
    create_project_index()
    
    # 4. 更新主README
    print("\n📖 更新主README...")
    update_main_readme()
    
    print("\n" + "=" * 50)
    print("🎉 项目整理完全完成！")

if __name__ == "__main__":
    main()
