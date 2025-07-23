# 🤖 AI问答回流数据处理平台

## 📋 项目简介

本项目是一个**企业级AI问答回流数据处理平台**，专为处理和分析多种AI助手（自研AI、豆包、小天）的问答数据而设计。

### 🎯 核心功能
- ✅ **全流程自动化**：数据同步→分类→答案生成→评分→审核
- ✅ **多AI模型对比**：支持原始、豆包、小天三种AI模型
- ✅ **动态五维评分**：16个领域的不同评分维度
- ✅ **实时监控**：完整的状态监控和执行历史
- ✅ **现代化界面**：基于React + Ant Design的管理界面

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+
- PostgreSQL 13+

### 一键启动
```bash
# 1. 安装Node.js
chmod +x install_nodejs.sh && ./install_nodejs.sh

# 2. 启动后端 (端口8088)
chmod +x start_backend.sh && ./start_backend.sh

# 3. 启动前端 (端口5173) - 新终端
chmod +x start_frontend.sh && ./start_frontend.sh
```

### 访问地址
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8088

### 快速测试
```bash
cd backend && source venv/bin/activate && python immediate_full_test.py
```

## 📖 完整文档

**📚 查看完整开发指南：[AI问答平台完整开发指南.md](./AI问答平台完整开发指南.md)**

该文档包含：
- 📊 详细的系统架构和数据库设计
- 🔧 核心功能模块说明
- 👨‍💻 开发指南和代码规范
- 📡 完整的API文档
- 🧪 测试指南和Mock服务使用
- 🚀 部署指南和运维配置
- 📈 开发进度和技术债务跟踪

## 🏗️ 项目结构

```
ai-qa-platform/
├── backend/                    # 后端代码
│   ├── app/                   # 主应用
│   ├── tests/                 # 测试代码
│   ├── immediate_full_test.py # 快速测试脚本
│   └── PROJECT_STRUCTURE.md   # 后端结构说明
├── frontend/                  # 前端代码
│   └── src/                  # 源代码
├── docs/                     # 保留的核心文档
│   ├── 数据库结构总结         # 数据库设计参考
│   ├── 前端Dashboard功能详细文档.md
│   └── README_启动说明.md
├── AI问答平台完整开发指南.md  # 📚 主要开发文档
├── QUICK_START.md            # 快速启动指南
└── README.md                 # 本文件
```

## 🛠️ 核心技术栈

**后端**：Flask 2.3 + SQLAlchemy 2.0 + PostgreSQL + APScheduler  
**前端**：React 18 + Ant Design 5.0 + TypeScript + ECharts  
**部署**：Docker + Nginx + Gunicorn

## 📊 开发状态

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 🗄️ 数据库设计 | 95% | ✅ 完成 |
| 🔄 数据同步服务 | 85% | ✅ 可用 |
| 🏷️ 智能分类服务 | 80% | ✅ 可用 |
| 🤖 答案生成服务 | 75% | ✅ 可用 |
| ⭐ 评分服务 | 70% | ✅ 可用 |
| ⏰ 定时任务调度 | 85% | ✅ 完成 |
| 📡 API接口 | 80% | ✅ 完成 |
| 🧪 测试框架 | 90% | ✅ 完成 |
| 🎨 前端界面 | 60% | 🚧 开发中 |

## 🔧 常用操作

```bash
# 检查数据库状态
cd backend && source venv/bin/activate
python -c "from app.models import Question; print(f'Questions: {Question.query.count()}')"

# 运行单元测试
python tests/test_core.py

# 启动Mock服务（用于测试）
cd backend/tests
python mock_classification_api.py --port 8001 &
python mock_ai_api.py --service doubao --port 8002 &
python mock_score_api.py --port 8004 &

# 重置数据库（开发环境）
python -c "from app import create_app; from app.utils.database import db; app=create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

## 📞 支持与问题

- **完整文档**：[AI问答平台完整开发指南.md](./AI问答平台完整开发指南.md)
- **快速启动**：[QUICK_START.md](./QUICK_START.md)
- **项目结构**：[backend/PROJECT_STRUCTURE.md](./backend/PROJECT_STRUCTURE.md)

---

*最后更新：2024年1月1日* 