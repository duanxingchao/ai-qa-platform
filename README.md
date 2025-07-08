# AI问答回流数据处理平台

## 📚 项目概述

本项目是一个**企业级AI问答回流数据处理平台**，专为处理和分析多种AI助手（自研AI、豆包、小天）的问答数据而设计。平台实现了从数据采集、清洗、智能分类、答案生成到多维度评分的**全流程自动化处理**，并提供现代化的可视化管理界面。

### 🎯 核心价值
- **自动化数据处理流水线**：减少人工干预，提高数据处理效率
- **多AI模型对比分析**：支持同时评估多个AI助手的回答质量
- **五维评分体系**：从准确性、完整性、清晰度、实用性、创新性全面评估
- **实时监控与审核**：提供实时数据监控和人工审核机制
- **现代化UI体验**：基于Ant Design的美观、响应式管理界面

### 🏢 应用场景
- **AI模型效果评估**：对比不同AI模型的回答质量
- **客服问答优化**：分析用户问题分布，优化回答策略
- **知识库管理**：构建高质量的问答知识库
- **数据驱动决策**：基于评分数据优化AI模型参数

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎨 前端展示层                                  │
│  React 18 + Ant Design 5.0 + ECharts 5.0                       │
│  ├─ 📊 数据大盘：统计图表、趋势分析                              │
│  ├─ 📋 问题管理：列表展示、筛选、详情查看                        │
│  ├─ 🔍 答案对比：多AI答案并列显示、评分对比                      │
│  ├─ ⭐ 评分管理：五维评分展示、评分历史                          │
│  └─ ✅ 审核工作台：待审核列表、批量操作                          │
├─────────────────────────────────────────────────────────────────┤
│                    ⚙️ 后端服务层                                  │
│  Flask 2.3 + SQLAlchemy 2.0 + APScheduler 3.10                 │
│  ├─ 🔄 数据同步服务：增量同步、去重处理、状态监控                │
│  ├─ 🧹 数据清洗服务：格式规范化、无效数据过滤                    │
│  ├─ 🏷️ 智能分类服务：16领域分类、API调用管理                     │
│  ├─ 🤖 答案生成服务：多AI并发调用、失败重试                      │
│  ├─ 📊 评分服务：五维评分、综合评分计算                          │
│  └─ ⏰ 定时任务调度：自动化处理流程                               │
├─────────────────────────────────────────────────────────────────┤
│                    🗄️ 数据持久层                                  │
│  PostgreSQL (兼容GaussDB-DWS)                                   │
│  ├─ 📝 questions：问题数据（16字段）+ 状态管理                   │
│  ├─ 💬 answers：AI答案数据（8字段）+ 类型标识                    │
│  ├─ ⭐ scores：评分数据（10字段）+ 五维评分                       │
│  └─ 🔍 review_status：审核状态（6字段）+ 审核记录                │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

### 后端技术栈
| 技术 | 版本 | 用途 | 状态 |
|------|------|------|------|
| **Python** | 3.8+ | 主要开发语言 | ✅ |
| **Flask** | 2.3.2 | Web框架 | ✅ |
| **SQLAlchemy** | 2.0.19 | ORM映射 | ✅ |
| **PostgreSQL** | - | 数据库 | ✅ |
| **APScheduler** | 3.10.1 | 定时任务 | ✅ |
| **Flask-CORS** | 4.0.0 | 跨域处理 | ✅ |
| **psycopg2** | 2.9.7 | 数据库驱动 | ✅ |
| **Flask-JWT-Extended** | 4.5.2 | 认证授权 | 🔄 |
| **requests** | 2.31.0 | HTTP请求 | ✅ |

### 前端技术栈
| 技术 | 版本 | 用途 | 状态 |
|------|------|------|------|
| **React** | 18+ | 前端框架 | 📋 计划中 |
| **Ant Design** | 5.0+ | UI组件库 | 📋 计划中 |
| **ECharts** | 5.0+ | 图表库 | 📋 计划中 |
| **Redux Toolkit** | - | 状态管理 | 📋 计划中 |
| **React Router** | v6 | 路由管理 | 📋 计划中 |
| **Axios** | - | HTTP客户端 | 📋 计划中 |

## 📊 功能模块详细设计

### 🔄 1. 数据同步模块
**核心功能**：从源表`table1`自动同步问答数据
- ✅ **增量同步**：基于`sendmessagetime`字段，只同步新增数据
- ✅ **业务主键**：MD5(pageid + sendmessagetime + query) 确保唯一性
- ✅ **去重机制**：避免重复数据插入
- ✅ **状态跟踪**：记录同步进度和结果
- 🔄 **监控告警**：同步失败自动告警（第二阶段）

```python
# 业务主键生成示例
def generate_business_id(pageid, sendmessagetime, query):
    data_str = f"{pageid}_{sendmessagetime}_{query.strip()}"
    return hashlib.md5(data_str.encode('utf-8')).hexdigest()
```

### 🧹 2. 数据清洗模块
**核心功能**：清理和规范化问题数据
- ✅ **空值检测**：过滤query字段为空的记录
- ✅ **格式规范化**：去除多余空格、特殊字符
- ✅ **软删除机制**：标记`is_deleted=true`而非物理删除
- 🔄 **清洗规则配置**：可配置的清洗规则（第二阶段）

### 🏷️ 3. 智能分类模块
**核心功能**：调用外部API进行问题领域分类
- 🔄 **API调用**：POST `/api/classify`
- 🔄 **16领域分类**：支持预定义的分类体系
- 🔄 **批量处理**：提高分类效率
- 🔄 **缓存机制**：避免重复分类同样问题

**API接口规范**：
```json
// 请求
POST /api/classify
{
  "input": {
    "query": "用户问题文本"
  }
}

// 响应
{
  "data": {
    "outputs": {
      "text": "分类结果"
    }
  }
}
```

### 🤖 4. 答案生成模块
**核心功能**：调用多个AI接口生成答案
- 🔄 **多AI支持**：豆包、小天、自研AI
- 🔄 **并发调用**：同时请求多个AI接口
- 🔄 **失败重试**：接口调用失败自动重试
- 🔄 **答案去重**：基于相似度检测的去重

**支持的AI类型**：
- `our_ai` - 自研AI
- `doubao` - 豆包AI  
- `xiaotian` - 小天AI

### ⭐ 5. 评分模块
**核心功能**：五维度评分体系
- 🔄 **五维评分**：准确性、完整性、清晰度、实用性、创新性（1-5分）
- 🔄 **综合评分**：加权平均计算
- 🔄 **评分理由**：AI生成评分解释
- 🔄 **批量评分**：支持批量评分操作

**评分维度**：
1. **准确性** (score_1)：答案内容的正确性
2. **完整性** (score_2)：答案内容的完整程度  
3. **清晰度** (score_3)：表达的清晰易懂程度
4. **实用性** (score_4)：对用户的实际帮助程度
5. **创新性** (score_5)：回答的创新和独特性

### 📊 6. 前端展示模块
**核心功能**：数据可视化和管理界面
- 📋 **响应式设计**：适配桌面端、平板、手机
- 📋 **实时数据**：WebSocket实时更新
- 📋 **高级筛选**：时间、分类、状态多维筛选
- 📋 **数据导出**：Excel、PDF格式导出

## 🗄️ 数据库设计

### 数据库连接信息
```
Database: ai_qa_platform
Host: test-huiliu-postgresql.ns-q8rah3y5.svc
Port: 5432
User: postgres
Password: l69jjd9n
URL: postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform
```

### 表结构设计

#### 📝 questions表（问题数据表）
| 字段 | 类型 | 说明 | 索引 |
|------|------|------|------|
| id | SERIAL | 自增主键 | ✅ |
| business_id | VARCHAR(64) | 业务主键（唯一） | ✅ |
| pageid | VARCHAR(100) | 页面ID | - |
| devicetypename | VARCHAR(50) | 设备类型 | - |
| query | TEXT | 问题内容 | - |
| sendmessagetime | TIMESTAMP | 发送时间 | ✅ |
| classification | VARCHAR(50) | 分类结果 | ✅ |
| serviceid | VARCHAR(50) | 服务ID | - |
| qatype | VARCHAR(50) | 问答类型 | - |
| intent | VARCHAR(100) | 意图识别 | - |
| iskeyboardinput | BOOLEAN | 是否键盘输入 | - |
| isstopanswer | BOOLEAN | 是否停止回答 | - |
| is_deleted | BOOLEAN | 软删除标记 | - |
| processing_status | VARCHAR(20) | 处理状态 | ✅ |
| created_at | TIMESTAMP | 创建时间 | - |
| updated_at | TIMESTAMP | 更新时间 | - |

**processing_status状态流转**：
```
pending -> cleaning -> classifying -> generating -> scoring -> completed
   ↓           ↓            ↓             ↓           ↓
failed    failed      failed       failed     failed
```

#### 💬 answers表（答案数据表）
| 字段 | 类型 | 说明 | 索引 |
|------|------|------|------|
| id | SERIAL | 自增主键 | ✅ |
| question_business_id | VARCHAR(64) | 关联问题 | ✅ |
| answer_text | TEXT | 答案内容 | - |
| assistant_type | VARCHAR(50) | AI类型 | ✅ |
| is_scored | BOOLEAN | 是否已评分 | - |
| answer_time | TIMESTAMP | 回答时间 | - |
| created_at | TIMESTAMP | 创建时间 | - |
| updated_at | TIMESTAMP | 更新时间 | - |

#### ⭐ scores表（评分数据表）
| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | SERIAL | 自增主键 | - |
| answer_id | INTEGER | 关联答案 | FK |
| score_1 | INTEGER | 准确性评分 | 1-5 |
| score_2 | INTEGER | 完整性评分 | 1-5 |
| score_3 | INTEGER | 清晰度评分 | 1-5 |
| score_4 | INTEGER | 实用性评分 | 1-5 |
| score_5 | INTEGER | 创新性评分 | 1-5 |
| average_score | DECIMAL(3,2) | 平均分 | - |
| comment | TEXT | 评分理由 | - |
| rated_at | TIMESTAMP | 评分时间 | - |

#### 🔍 review_status表（审核状态表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 自增主键 |
| question_business_id | VARCHAR(64) | 关联问题（唯一） |
| is_reviewed | BOOLEAN | 是否已审核 |
| reviewer_id | VARCHAR(50) | 审核人员ID |
| review_comment | TEXT | 审核备注 |
| reviewed_at | TIMESTAMP | 审核时间 |

## 🔌 API接口文档

### 当前已实现的API

#### 🔄 数据同步API
```http
# 获取同步状态
GET /api/sync/status
Response: {
  "status": "success",
  "data": {
    "last_sync": null,
    "status": "idle"
  }
}

# 手动触发同步
POST /api/sync/trigger
Response: {
  "status": "success", 
  "message": "数据同步已触发"
}
```

#### 📝 问题查询API
```http
# 获取问题列表（支持分页）
GET /api/questions?page=1&page_size=20
Response: {
  "status": "success",
  "data": {
    "items": [],
    "total": 0, 
    "page": 1,
    "page_size": 20
  }
}

# 获取问题详情
GET /api/questions/{id}
Response: {
  "status": "success",
  "data": { ... }
}
```

#### ⚙️ 数据处理API
```http
# 触发数据清洗
POST /api/process/clean
Response: {
  "status": "success",
  "message": "数据清洗已开始"
}

# 触发智能分类
POST /api/process/classify  
Response: {
  "status": "success",
  "message": "分类处理已开始"
}

# 触发答案生成
POST /api/process/generate
Response: {
  "status": "success", 
  "message": "答案生成已开始"
}

# 触发评分
POST /api/process/score
Response: {
  "status": "success",
  "message": "评分处理已开始"
}
```

#### 🔍 审核管理API
```http
# 更新审核状态
PUT /api/review/{business_id}
Request: {
  "is_reviewed": true,
  "reviewer_id": "user123", 
  "review_comment": "审核通过"
}

# 获取待审核列表
GET /api/review/pending?page=1&page_size=20

# 获取审核统计
GET /api/review/statistics
```

### 外部API集成

#### 分类API
```http
POST {CLASSIFY_API_URL}
Request: {
  "input": {
    "query": "用户问题"
  }
}
Response: {
  "data": {
    "outputs": {
      "text": "分类结果"
    }
  }
}
```

## 📁 项目结构

### 当前实际项目结构
```
project/
├── 📁 backend/                 # ✅ 后端代码（已完成）
│   ├── 📁 app/                 # Flask应用核心
│   │   ├── 📄 __init__.py      # ✅ 应用工厂 + 扩展初始化  
│   │   ├── 📄 config.py        # ✅ 配置管理（开发/生产/测试）
│   │   ├── 📁 models/          # ✅ 数据模型（4个表）
│   │   │   ├── 📄 __init__.py  # ✅ 模型导出
│   │   │   ├── 📄 question.py  # ✅ 问题模型（16字段）
│   │   │   ├── 📄 answer.py    # ✅ 答案模型（8字段）
│   │   │   ├── 📄 score.py     # ✅ 评分模型（10字段）
│   │   │   └── 📄 review.py    # ✅ 审核模型（6字段）
│   │   ├── 📁 api/             # ✅ API路由（4个蓝图）
│   │   │   ├── 📄 __init__.py  # ✅ 蓝图注册
│   │   │   ├── 📄 sync_api.py  # ✅ 同步API（2个端点）
│   │   │   ├── 📄 question_api.py # ✅ 问题API（2个端点）
│   │   │   ├── 📄 process_api.py  # ✅ 处理API（4个端点）
│   │   │   └── 📄 review_api.py   # ✅ 审核API（3个端点）
│   │   ├── 📁 services/        # ✅ 业务逻辑（占位实现）
│   │   │   ├── 📄 __init__.py  # ✅ 服务模块
│   │   │   ├── 📄 sync_service.py    # 🔄 同步服务（第二阶段）
│   │   │   └── 📄 clean_service.py   # 🔄 清洗服务（第二阶段）
│   │   └── 📁 utils/           # ✅ 工具函数
│   │       ├── 📄 __init__.py  # ✅ 工具导出
│   │       ├── 📄 database.py  # ✅ 数据库工具 + 连接管理
│   │       └── 📄 helpers.py   # ✅ 辅助函数（业务主键生成等）
│   ├── 📄 requirements.txt     # ✅ Python依赖（22个包）
│   ├── 📄 run.py              # ✅ 启动文件
│   ├── 📄 init_db.py          # ✅ 数据库初始化脚本
│   ├── 📄 test_api.py         # ✅ API测试脚本
│   ├── 📄 README.md           # ✅ 后端文档
│   └── 📄 app.log             # ✅ 运行日志
│
├── 📁 frontend/                # 📋 前端代码（计划中）
│   ├── 📁 public/             # 📋 静态资源
│   ├── 📁 src/                # 📋 源代码
│   │   ├── 📁 components/     # 📋 React组件
│   │   │   ├── 📁 Dashboard/  # 📋 数据大盘
│   │   │   ├── 📁 QuestionList/ # 📋 问题列表
│   │   │   ├── 📁 Charts/     # 📋 图表组件
│   │   │   └── 📁 common/     # 📋 通用组件
│   │   ├── 📁 pages/          # 📋 页面组件
│   │   │   ├── 📁 Home/       # 📋 首页
│   │   │   ├── 📁 Analysis/   # 📋 分析页
│   │   │   └── 📁 Review/     # 📋 审核页
│   │   ├── 📁 services/       # 📋 API服务
│   │   ├── 📁 store/          # 📋 Redux状态管理
│   │   ├── 📁 utils/          # 📋 前端工具函数
│   │   ├── 📄 App.jsx         # 📋 根组件
│   │   └── 📄 index.js        # 📋 入口文件
│   ├── 📄 package.json        # 📋 NPM配置
│   └── 📄 .env                # 📋 环境变量
│
├── 📄 .gitignore              # ✅ Git忽略文件
├── 📄 README.md               # ✅ 项目总览文档
└── 📄 docker-compose.yml      # 📋 Docker配置（可选）
```

## 🚀 快速开始

### 系统要求
- **Python**: 3.8+
- **Node.js**: 16+ (前端开发)  
- **PostgreSQL**: 12+
- **Git**: 2.0+

### 第一步：环境准备
```bash
# 1. 克隆项目
git clone <项目地址>
cd project

# 2. 创建Python虚拟环境（推荐）
python -m venv ai_qa_env
source ai_qa_env/bin/activate  # Linux/Mac
# 或 ai_qa_env\Scripts\activate  # Windows
```

### 第二步：后端环境搭建
```bash
# 1. 进入后端目录
cd backend

# 2. 安装Python依赖
pip install -r requirements.txt

# 3. 配置数据库连接（检查config.py中的DATABASE_URL）
# 当前配置：postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform

# 4. 初始化数据库
python init_db.py

# 5. 启动后端服务
python run.py
```

### 第三步：验证安装
```bash
# 测试API连接
curl http://localhost:5000/api/sync/status

# 运行完整API测试
python test_api.py

# 查看服务日志
tail -f app.log
```

### 第四步：前端环境搭建（第三阶段）
```bash
# 1. 进入前端目录
cd frontend

# 2. 配置NPM镜像
npm config set registry https://registry.npmmirror.com

# 3. 安装依赖
npm install

# 4. 启动开发服务器
npm start
```

## 🧪 测试说明

### API测试
```bash
# 1. 基础连通性测试
curl -X GET http://localhost:5000/api/sync/status

# 2. 问题列表查询测试
curl -X GET "http://localhost:5000/api/questions?page=1&page_size=5"

# 3. 数据处理测试  
curl -X POST http://localhost:5000/api/process/clean
curl -X POST http://localhost:5000/api/process/classify

# 4. 完整API测试套件
cd backend
python test_api.py
```

### 数据库测试
```bash
# 1. 检查表结构
python -c "
from app import create_app
from app.utils.database import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('数据库表:', tables)
    
    for table in ['questions', 'answers', 'scores', 'review_status']:
        columns = inspector.get_columns(table)
        print(f'{table}表字段数:', len(columns))
"

# 2. 测试数据连接
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
print('✅ 数据库连接成功')
conn.close()
"
```

## 📈 开发进度

### ✅ 第一阶段：后端基础架构（已完成）
- [x] **项目结构搭建**：完整的Flask应用架构
- [x] **数据库设计**：4张表的完整设计和创建
- [x] **数据模型定义**：SQLAlchemy ORM模型
- [x] **基础API框架**：11个API端点的基础实现
- [x] **配置管理**：开发/生产/测试环境配置
- [x] **工具函数**：业务主键生成、数据验证等
- [x] **定时任务框架**：APScheduler集成
- [x] **日志系统**：完整的日志记录机制

### 🔄 第二阶段：核心业务逻辑（进行中）
- [ ] **数据同步服务**：从table1同步数据的完整实现
  - [ ] 增量同步逻辑
  - [ ] 去重处理机制  
  - [ ] 同步状态监控
  - [ ] 错误处理和重试
- [ ] **数据清洗功能**：数据质量保证
  - [ ] 清洗规则引擎
  - [ ] 批量处理优化
  - [ ] 清洗统计报告
- [ ] **外部API调用封装**：
  - [ ] 分类API调用实现
  - [ ] 豆包API集成
  - [ ] 小天API集成  
  - [ ] 评分API集成
- [ ] **批处理优化**：
  - [ ] 队列机制
  - [ ] 并发处理
  - [ ] 性能监控

### 📋 第三阶段：前端界面开发（计划中）
- [ ] **React项目初始化**：
  - [ ] 项目脚手架搭建
  - [ ] 开发环境配置
  - [ ] 代码规范设置
- [ ] **核心组件开发**：
  - [ ] 数据大盘组件
  - [ ] 问题列表组件
  - [ ] 答案对比组件
  - [ ] 评分展示组件
- [ ] **页面开发**：
  - [ ] 首页设计实现
  - [ ] 数据分析页面
  - [ ] 审核工作台
- [ ] **图表集成**：
  - [ ] ECharts图表库集成
  - [ ] 统计图表实现
  - [ ] 实时数据更新

### 🔗 第四阶段：前后端联调（计划中）
- [ ] **API对接**：前后端数据交互
- [ ] **数据流测试**：完整业务流程测试
- [ ] **错误处理**：异常情况处理
- [ ] **性能优化**：响应速度优化

### 🎨 第五阶段：UI美化和优化（计划中）
- [ ] **主题设计**：现代化视觉设计
- [ ] **动画效果**：流畅的交互动画
- [ ] **响应式优化**：多设备适配
- [ ] **最终测试**：全功能测试

## ⚙️ 配置说明

### 环境变量配置
创建 `backend/.env` 文件：
```bash
# Flask配置
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 数据库配置
DATABASE_URL=postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform

# 外部API配置（需要实际API地址）
CLASSIFY_API_URL=http://your-classify-api.com/api/classify
DOUBAO_API_URL=http://your-doubao-api.com/api/chat
XIAOTIAN_API_URL=http://your-xiaotian-api.com/api/chat
SCORE_API_URL=http://your-score-api.com/api/score

# 服务配置
PORT=5000
```

### 定时任务配置
```python
# 在config.py中配置
SYNC_INTERVAL_MINUTES = 30    # 数据同步间隔（分钟）
CLEAN_INTERVAL_HOURS = 1      # 数据清洗间隔（小时）
BATCH_SIZE = 100              # 批处理大小
```

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. 数据库连接失败
```bash
# 问题：psycopg2.OperationalError: connection failed
# 解决：检查数据库服务是否启动，连接信息是否正确

# 测试连接
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:l69jjd9n@test-huiliu-postgresql.ns-q8rah3y5.svc:5432/ai_qa_platform')
    print('✅ 数据库连接成功')
    conn.close()
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

#### 2. 依赖包安装失败
```bash
# 问题：pip install失败
# 解决：使用国内镜像源

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 3. 端口占用问题
```bash
# 问题：Address already in use
# 解决：更换端口或杀死占用进程

# 查看端口占用
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 或更换端口
export PORT=5001
python run.py
```

#### 4. 模型导入错误
```bash
# 问题：ImportError: cannot import name 'Question'
# 解决：确保在应用上下文中导入模型

python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.models import Question, Answer, Score, ReviewStatus
    print('✅ 模型导入成功')
"
```

### 日志查看
```bash
# 查看实时日志
tail -f backend/app.log

# 查看错误日志
grep -i error backend/app.log

# 查看特定模块日志
grep "sync_service" backend/app.log
```

## 📊 性能监控

### 数据库性能
```sql
-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';

-- 查看索引使用情况
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('questions', 'answers', 'scores', 'review_status');
```

### API性能监控
```bash
# 接口响应时间测试
time curl -X GET http://localhost:5000/api/questions

# 并发测试（需要安装ab）
ab -n 100 -c 10 http://localhost:5000/api/sync/status
```

## 🔒 安全措施

### 当前安全配置
1. **CORS配置**：限制跨域访问
2. **输入验证**：API参数验证（开发中）
3. **SQL注入防护**：使用SQLAlchemy ORM
4. **环境变量**：敏感信息环境变量化

### 计划安全增强
- [ ] JWT认证授权
- [ ] API限流
- [ ] HTTPS配置
- [ ] 输入数据验证
- [ ] 审计日志

## 🤝 贡献指南

### 开发规范
1. **代码风格**：遵循PEP 8规范
2. **提交规范**：使用语义化提交信息
3. **分支管理**：feature/bugfix分支开发
4. **测试要求**：新功能需要对应测试

### 提交流程
```bash
# 1. 创建功能分支
git checkout -b feature/新功能名称

# 2. 开发和测试
# ... 编码 ...

# 3. 提交代码
git add .
git commit -m "feat: 添加新功能描述"

# 4. 推送分支
git push origin feature/新功能名称

# 5. 创建Pull Request
```

## 📝 更新日志

### v1.0.0 (2025-01-04)
- ✅ 完成后端基础架构搭建
- ✅ 实现4张表的数据库设计
- ✅ 完成11个基础API端点
- ✅ 集成定时任务调度框架
- ✅ 实现完整的配置管理系统

### 计划版本
- **v1.1.0**：核心业务逻辑实现
- **v1.2.0**：前端界面开发
- **v1.3.0**：前后端联调优化
- **v2.0.0**：完整功能发布

## 📞 技术支持

### 开发团队
- **架构设计**：AI Assistant
- **后端开发**：Flask + SQLAlchemy
- **前端开发**：React + Ant Design（计划中）
- **数据库**：PostgreSQL

### 联系方式
- **问题反馈**：通过GitHub Issues
- **功能建议**：通过Pull Request
- **技术讨论**：项目Wiki

---

## 🎯 项目愿景

**打造企业级AI问答数据处理标杆平台**

本平台致力于成为AI问答数据处理领域的标杆解决方案，通过全自动化的数据流水线、多维度的质量评估体系和现代化的可视化界面，帮助企业更好地理解和优化AI问答服务质量，推动AI技术在实际业务中的深度应用。

> **当前状态**: 第一阶段完成 ✅ | 第二阶段开发中 🔄 | 持续迭代优化 📈 