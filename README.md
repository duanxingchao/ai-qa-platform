# 🤖 AI问答平台

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
