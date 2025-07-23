# 🏗️ AI问答平台后端项目结构

## 📂 核心目录结构

```
backend/
├── app/                          # 主应用代码
│   ├── api/                     # API路由
│   ├── models/                  # 数据模型
│   ├── services/                # 业务服务层
│   └── utils/                   # 工具函数
├── tests/                       # 测试相关
│   ├── mock_*.py               # Mock API服务
│   ├── test_*.py               # 单元测试
│   ├── run_full_project_test.py # 完整项目测试
│   └── mock_data_manager.py     # 数据管理工具
├── migrations/                  # 数据库迁移（如果使用）
├── logs/                       # 日志目录
├── venv/                       # Python虚拟环境
├── immediate_full_test.py      # 快速全流程测试
├── init_db.py                  # 数据库初始化
├── run.py                      # 应用启动入口
└── requirements.txt            # Python依赖
```

## 🧪 测试文件说明

### 主要测试脚本
- **`immediate_full_test.py`** - 快速全流程测试（推荐）
- **`tests/run_full_project_test.py`** - 完整项目测试套件

### Mock服务
- **`tests/mock_classification_api.py`** - 分类API模拟
- **`tests/mock_ai_api.py`** - AI答案生成API模拟
- **`tests/mock_score_api.py`** - 评分API模拟

### 单元测试
- **`tests/test_core.py`** - 核心功能测试
- **`tests/test_api.py`** - API接口测试
- **`tests/test_scoring_system.py`** - 评分系统测试
- **`tests/test_answer_generation.py`** - 答案生成测试

### 数据管理
- **`tests/mock_data_manager.py`** - 统一数据管理工具

## 🚀 快速开始

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行快速测试
python immediate_full_test.py

# 运行完整测试
python tests/run_full_project_test.py
```

## 📋 文档说明

- **`README.md`** - 项目总体说明
- **`TESTING_GUIDE.md`** - 测试使用指南
- **`SCHEDULER_GUIDE.md`** - 定时任务说明
- **`ANSWER_GENERATION_GUIDE.md`** - 答案生成指南

## 🧹 已清理的重复文件

以下文件已被删除，避免混淆：
- ~~`create_test_data.py`~~ (功能重复)
- ~~`quick_scoring_test.py`~~ (功能重复)  
- ~~`tests/mock_table1_data.py`~~ (功能重复)
- ~~`tests/generate_today_data.py`~~ (功能重复)
- ~~`tests/quick_full_test.py`~~ (功能重复)
- ~~`migrate_scores_table.py`~~ (一次性脚本)
- ~~`*.log`~~ (日志文件，会自动重新生成) 