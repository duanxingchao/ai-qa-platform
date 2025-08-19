# 🏗️ AI问答平台后端项目结构

## 📂 核心目录结构

```
backend/
├── app/                          # 主应用代码
│   ├── api/                     # API路由层 (20个API模块)
│   ├── models/                  # 数据模型层 (9个核心表模型)
│   ├── services/                # 业务服务层 (12个服务模块)
│   └── utils/                   # 工具函数
├── tests/                       # 测试和Mock服务
│   ├── mock_*.py               # Mock API服务 (开发必需)
│   ├── run_full_project_test.py # 完整项目测试
│   └── mock_data_manager.py     # 数据管理工具
├── tools/                       # 开发工具
│   ├── add_sample_scores.py    # 样本数据生成
│   └── generate_realtime_events.py # 实时事件生成
├── scripts/                     # 数据库维护脚本
│   ├── check_table1_structure.py
│   └── fix_table1_structure.py
├── migrations/                  # 数据库迁移
├── venv/                       # Python虚拟环境
├── init_db.py                  # 数据库初始化
├── run.py                      # 应用启动入口
└── requirements.txt            # Python依赖
```

## 🧪 开发和测试

### Mock服务 (开发环境必需)
- **`tests/mock_classification_api.py`** - 分类API模拟
- **`tests/mock_ai_api.py`** - AI答案生成API模拟
- **`tests/mock_score_api.py`** - 评分API模拟
- **`tests/mock_data_manager.py`** - 统一数据管理工具

### 完整测试
- **`tests/run_full_project_test.py`** - 完整项目测试套件

## 🚀 快速开始

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动应用
python run.py

# 运行完整测试
python tests/run_full_project_test.py
```

## 📋 项目特点

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