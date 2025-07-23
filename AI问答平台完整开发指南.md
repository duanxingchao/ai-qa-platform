# 🤖 AI问答回流数据处理平台 - 完整开发指南

## 📋 目录
- [项目概述](#项目概述)
- [核心需求](#核心需求)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [数据库设计](#数据库设计)
- [核心功能模块](#核心功能模块)
- [快速开始](#快速开始)
- [开发指南](#开发指南)
- [API文档](#api文档)
- [测试指南](#测试指南)
- [部署指南](#部署指南)
- [开发进度](#开发进度)

---

## 🎯 项目概述

### 核心价值定位
本项目是一个**企业级AI问答回流数据处理平台**，专为处理和分析多种AI助手（自研AI、豆包、小天）的问答数据而设计。平台实现了从数据采集、清洗、智能分类、答案生成到多维度评分的**全流程自动化处理**。

### 业务背景
- **数据来源**：table1表的回流问答数据
- **处理目标**：自动化分类、生成多AI答案、智能评分
- **应用场景**：AI模型效果评估、客服问答优化、知识库管理

### 核心特性
- ✅ **全流程自动化**：数据同步→分类→答案生成→评分→审核
- ✅ **多AI模型对比**：支持原始、豆包、小天三种AI模型
- ✅ **动态五维评分**：16个领域的不同评分维度
- ✅ **实时监控**：完整的状态监控和执行历史
- ✅ **现代化界面**：基于React + Ant Design的管理界面

---

## 📊 核心需求

### 1. 数据处理流程
```mermaid
graph LR
    A[table1原始数据] --> B[数据同步]
    B --> C[智能分类16领域]
    C --> D[多AI答案生成]
    D --> E[五维评分]
    E --> F[人工审核]
    F --> G[数据展示]
```

### 2. 功能需求
- **数据同步**：从table1增量同步到questions/answers表
- **智能分类**：16个领域的自动分类（技术问题、业务咨询、产品使用等）
- **答案生成**：调用豆包、小天API生成多样化答案
- **评分系统**：动态五维评分（准确性、完整性、清晰度、实用性、创新性）
- **审核管理**：人工审核机制和状态管理
- **可视化展示**：数据大盘、趋势分析、对比图表

### 3. 性能需求
- **数据处理**：支持批量处理，单批次100-500条记录
- **API响应**：平均响应时间 < 2秒
- **并发处理**：支持多线程并行处理
- **容错机制**：API失败自动重试，错误恢复

---

## 🏗️ 系统架构

### 整体架构图
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
│  ├─ ⭐ scores：评分数据（15字段）+ 动态维度                       │
│  └─ 🔍 review_status：审核状态（6字段）+ 审核记录                │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件
1. **SyncService** - 数据同步服务
2. **AIProcessingService** - AI处理服务
3. **SchedulerService** - 定时任务调度
4. **APIClientFactory** - 外部API客户端工厂

---

## 🛠️ 技术栈

### 后端技术栈
```python
# 核心框架
Flask 2.3.3                 # Web框架
SQLAlchemy 2.0.21           # ORM框架
PostgreSQL 13+              # 数据库
APScheduler 3.10.4          # 定时任务

# 数据处理
psycopg2-binary 2.9.7      # PostgreSQL驱动
requests 2.31.0             # HTTP客户端
pandas 2.0.3                # 数据分析（可选）

# 开发工具
pytest 7.4.2               # 测试框架
python-dotenv 1.0.0         # 环境变量管理
```

### 前端技术栈
```javascript
// 核心框架
React 18.2.0                // UI框架
Ant Design 5.0+             // UI组件库
TypeScript 5.0+             // 类型系统

// 数据可视化
ECharts 5.4+                // 图表库
@ant-design/charts 1.4+     // Ant Design图表

// 状态管理
Zustand 4.4+                // 轻量状态管理
React Query 4.0+            // 数据获取

// 开发工具
Vite 4.4+                   // 构建工具
ESLint + Prettier           // 代码规范
```

---

## 🗄️ 数据库设计

### 表关系图
```
table1 (原始数据)
    ↓ (sync_service)
questions (1) ←→ (n) answers ←→ (n) scores
    ↓ (1:1)
review_status
```

### 核心表结构

#### 1. questions表（问题数据）
```sql
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    business_id VARCHAR(64) UNIQUE NOT NULL,  -- MD5业务主键
    pageid VARCHAR(100),
    devicetypename VARCHAR(50),
    query TEXT NOT NULL,                      -- 问题内容
    sendmessagetime TIMESTAMP,
    classification VARCHAR(50),               -- 智能分类结果
    serviceid VARCHAR(50),
    qatype VARCHAR(50),
    intent VARCHAR(100),
    iskeyboardinput BOOLEAN DEFAULT FALSE,
    isstopanswer BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(20) DEFAULT 'pending',  -- 处理状态
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. answers表（答案数据）
```sql
CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    question_business_id VARCHAR(64) NOT NULL,
    answer_text TEXT NOT NULL,                -- 答案内容
    assistant_type VARCHAR(20) NOT NULL,      -- original/doubao/xiaotian
    answer_time TIMESTAMP,
    is_scored BOOLEAN DEFAULT FALSE,          -- 是否已评分
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_business_id) REFERENCES questions(business_id)
);
```

#### 3. scores表（评分数据）- 支持动态维度
```sql
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER NOT NULL,
    -- 固定五维评分
    score_1 INTEGER CHECK (score_1 >= 1 AND score_1 <= 5),
    score_2 INTEGER CHECK (score_2 >= 1 AND score_2 <= 5),
    score_3 INTEGER CHECK (score_3 >= 1 AND score_3 <= 5),
    score_4 INTEGER CHECK (score_4 >= 1 AND score_4 <= 5),
    score_5 INTEGER CHECK (score_5 >= 1 AND score_5 <= 5),
    -- 动态维度名称（新增）
    dimension_1_name VARCHAR(50),  -- 如"信息准确性"
    dimension_2_name VARCHAR(50),  -- 如"逻辑性"
    dimension_3_name VARCHAR(50),  -- 如"流畅性"
    dimension_4_name VARCHAR(50),  -- 如"创新性"
    dimension_5_name VARCHAR(50),  -- 如"完整性"
    -- 综合评分
    average_score DECIMAL(3,2),
    comment TEXT,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (answer_id) REFERENCES answers(id)
);
```

#### 4. review_status表（审核状态）
```sql
CREATE TABLE review_status (
    id SERIAL PRIMARY KEY,
    question_business_id VARCHAR(64) UNIQUE NOT NULL,
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewer_id VARCHAR(50),
    review_comment TEXT,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (question_business_id) REFERENCES questions(business_id)
);
```

### 16个分类领域配置
```python
CLASSIFICATION_CATEGORIES = {
    '技术问题': ['编程', '系统', '网络', '数据库'],
    '业务咨询': ['流程', '政策', '合作', '服务'],
    '产品使用': ['功能', '操作', '故障', '优化'],
    '故障排查': ['错误', '异常', '恢复', '诊断'],
    '功能建议': ['改进', '新功能', '用户体验'],
    '其他': ['未分类', '杂项']
    # ... 共16个领域
}
```

---

## 🔧 核心功能模块

### 1. 数据同步服务 (SyncService)
**功能**：从table1增量同步数据到questions/answers表

**核心特性**：
- ✅ 增量同步（基于sendmessagetime）
- ✅ 数据去重（MD5 business_id）
- ✅ 错误处理和重试机制
- ✅ 同步状态监控

**使用方式**：
```python
from app.services.sync_service import sync_service

# 执行同步
result = sync_service.perform_sync(force_full_sync=False)
print(f"同步结果: {result['message']}")
```

### 2. AI处理服务 (AIProcessingService)
**功能**：批量处理问题分类、答案生成、评分

**处理流程**：
```python
# 1. 问题分类
classification_result = ai_service.process_classification_batch(limit=50)

# 2. 答案生成
answer_result = ai_service.process_answer_generation_batch(limit=50)

# 3. 答案评分
score_result = ai_service.process_scoring_batch(limit=50)
```

**批处理特性**：
- 支持批量大小配置（默认50条）
- 并发API调用（ThreadPoolExecutor）
- 失败重试机制（最多3次）
- 详细的处理日志

### 3. 定时任务调度 (SchedulerService)
**功能**：自动化执行完整数据处理工作流

**工作流配置**：
```python
WORKFLOW_PHASES = {
    'data_sync': '数据同步',
    'classification': '问题分类', 
    'answer_generation': '答案生成',
    'scoring': '答案评分',
    'review': '人工审核'
}
```

**调度策略**：
- 每2分钟执行一次完整工作流
- 支持手动触发单个阶段
- 阶段依赖检查和状态管理
- 执行历史记录

### 4. 外部API客户端 (APIClientFactory)
**功能**：统一管理外部API调用

**支持的API**：
```python
# 分类API
classification_client = APIClientFactory.get_classification_client()

# 豆包AI API
doubao_client = APIClientFactory.get_doubao_client()

# 小天AI API
xiaotian_client = APIClientFactory.get_xiaotian_client()

# 评分API
score_client = APIClientFactory.get_score_client()
```

**客户端特性**：
- 统一的重试机制
- 请求/响应日志记录
- 性能统计监控
- 错误分类处理

---

## 🔧 自动化处理配置

### 新增功能特性
- ✅ **启动时立即处理**：后端启动后立即处理已有数据
- ✅ **智能数据检测**：检测是否有可处理数据，无数据时自动挂起
- ✅ **可配置调度间隔**：通过环境变量配置工作流执行间隔（默认3分钟）
- ✅ **Mock服务管理**：提供服务状态检查和启动脚本生成
- ✅ **全自动化链路**：数据插入→同步→分类→答案生成→评分→审核

### 配置文件
```python
# backend/app/config.py

# 自动化处理配置
AUTO_PROCESS_ON_STARTUP = True  # 启动时立即处理已有数据
WORKFLOW_INTERVAL_MINUTES = int(os.environ.get('WORKFLOW_INTERVAL_MINUTES', 3))  # 工作流执行间隔（分钟）
DATA_CHECK_ENABLED = True  # 是否启用数据检测
AUTO_SUSPEND_WHEN_NO_DATA = True  # 无数据时自动挂起
MIN_BATCH_SIZE = 1  # 最小批处理大小，小于此数量时挂起

# Mock服务配置
MOCK_SERVICES_ENABLED = True  # Mock服务是否启用
```

### 环境变量配置
```bash
# 自定义工作流间隔（分钟）
export WORKFLOW_INTERVAL_MINUTES=5

# 其他配置
export AUTO_PROCESS_ON_STARTUP=true
export DATA_CHECK_ENABLED=true
```

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+
- PostgreSQL 13+

### 1. 环境准备
```bash
# 1. 克隆项目
git clone <repository-url>
cd ai-qa-platform

# 2. 安装Node.js（如果需要）
chmod +x install_nodejs.sh
./install_nodejs.sh

# 3. 创建Python虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 4. 安装Python依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 1. 创建数据库
createdb ai_qa_platform

# 2. 初始化数据库表
python init_db.py

# 3. 验证数据库连接
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app.utils.database import db
    print('数据库连接成功')
"
```

### 3. 启动服务
```bash
# 启动后端 (端口8088)
chmod +x start_backend.sh
./start_backend.sh

# 启动前端 (端口5173) - 新终端
chmod +x start_frontend.sh  
./start_frontend.sh
```

### 4. 访问系统
- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8088
- **API文档**: http://localhost:8088/api/docs

### 5. 快速测试
```bash
# 运行完整流程测试
cd backend
source venv/bin/activate
python immediate_full_test.py
```

---

## 👨‍💻 开发指南

### 项目结构
```
ai-qa-platform/
├── backend/                    # 后端代码
│   ├── app/                   # 主应用
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务服务
│   │   └── utils/            # 工具函数
│   ├── tests/                # 测试代码
│   ├── migrations/           # 数据库迁移
│   └── requirements.txt      # Python依赖
├── frontend/                  # 前端代码
│   ├── src/                  # 源代码
│   │   ├── components/       # 组件库
│   │   ├── pages/            # 页面组件
│   │   ├── services/         # API服务
│   │   └── utils/            # 工具函数
│   └── package.json          # Node.js依赖
└── docs/                     # 文档目录
```

### 开发流程

#### 1. 后端开发
```bash
# 1. 激活虚拟环境
cd backend
source venv/bin/activate

# 2. 创建新的API接口
# 编辑 app/api/new_api.py
# 注册路由到 app/__init__.py

# 3. 创建数据模型
# 编辑 app/models/new_model.py
# 添加数据库迁移

# 4. 创建业务服务
# 编辑 app/services/new_service.py

# 5. 运行测试
python -m pytest tests/

# 6. 启动开发服务器
python run.py
```

#### 2. 前端开发
```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 启动开发服务器
npm run dev

# 3. 创建新组件
# 编辑 src/components/NewComponent.tsx

# 4. 创建新页面
# 编辑 src/pages/NewPage.tsx
# 添加路由到 src/App.tsx

# 5. 构建生产版本
npm run build
```

### 代码规范

#### Python代码规范
```python
# 使用类型注解
def process_data(data: List[Dict]) -> Dict[str, Any]:
    """处理数据的函数"""
    pass

# 使用枚举定义常量
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"

# 异常处理
try:
    result = api_call()
except APIException as e:
    logger.error(f"API调用失败: {e}")
    raise
```

#### TypeScript代码规范
```typescript
// 定义接口
interface Question {
  id: number;
  query: string;
  classification: string;
  created_at: string;
}

// 使用泛型
interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

// React组件
const QuestionList: React.FC<QuestionListProps> = ({ filters }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  // ...
};
```

---

## 📡 API文档

### 认证说明
所有API请求需要包含认证头：
```http
Authorization: Bearer <token>
Content-Type: application/json
```

### 核心API端点

#### 1. 数据同步API
```http
# 获取同步状态
GET /api/sync/status
Response: {
  "success": true,
  "data": {
    "last_sync": "2024-01-01T00:00:00Z",
    "status": "idle"
  }
}

# 手动触发同步
POST /api/sync/trigger
Request: {
  "force_full_sync": false
}
Response: {
  "success": true,
  "message": "数据同步已触发"
}

# 获取同步统计
GET /api/sync/statistics
Response: {
  "success": true,
  "data": {
    "questions_count": 1000,
    "answers_count": 2500,
    "table1_total_count": 1500
  }
}
```

#### 2. 问题管理API
```http
# 获取问题列表
GET /api/questions?page=1&page_size=20&classification=技术问题
Response: {
  "success": true,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}

# 获取问题详情
GET /api/questions/{business_id}
Response: {
  "success": true,
  "data": {
    "id": 1,
    "business_id": "abc123",
    "query": "问题内容",
    "answers": [...],
    "scores": [...]
  }
}
```

#### 3. 数据处理API
```http
# 触发分类处理
POST /api/process/classify
Request: {
  "limit": 50,
  "days_back": 1
}
Response: {
  "success": true,
  "processed_count": 45,
  "success_count": 43,
  "error_count": 2
}

# 触发答案生成
POST /api/process/generate
Request: {
  "limit": 50,
  "days_back": 1
}

# 触发评分处理
POST /api/process/score
Request: {
  "limit": 50,
  "days_back": 1
}
```

#### 4. 调度管理API
```http
# 获取调度器状态
GET /api/scheduler/status
Response: {
  "success": true,
  "data": {
    "scheduler_running": true,
    "active_jobs": 2,
    "workflow_status": {...}
  }
}

# 手动执行工作流
POST /api/scheduler/manual/workflow
Response: {
  "success": true,
  "workflow_id": "workflow_20240101_120000"
}

# 手动执行阶段
POST /api/scheduler/manual/{phase}
Request: {
  "limit": 50,
  "days_back": 1
}
```

#### 5. 审核管理API
```http
# 更新审核状态
PUT /api/review/{business_id}
Request: {
  "is_reviewed": true,
  "reviewer_id": "user123",
  "review_comment": "审核通过"
}

# 批量审核
POST /api/review/batch
Request: {
  "business_ids": ["id1", "id2"],
  "is_reviewed": true,
  "reviewer_id": "user123"
}
```

---

## 🧪 测试指南

### 测试文件结构
```
backend/tests/
├── mock_*.py              # Mock API服务
├── test_*.py              # 单元测试
├── run_full_project_test.py  # 完整测试套件
└── mock_data_manager.py   # 数据管理工具
```

### 1. 运行测试

#### 快速测试（推荐）
```bash
cd backend
source venv/bin/activate
python immediate_full_test.py
```

#### 完整测试套件
```bash
python tests/run_full_project_test.py
```

#### 单元测试
```bash
# 核心功能测试
python tests/test_core.py

# API接口测试
python tests/test_api.py

# 评分系统测试
python tests/test_scoring_system.py
```

### 2. Mock服务

#### 启动Mock API服务
```bash
cd backend/tests

# 分类API (端口8001)
python mock_classification_api.py --port 8001 &

# 豆包AI API (端口8002)
python mock_ai_api.py --service doubao --port 8002 &

# 小天AI API (端口8003)  
python mock_ai_api.py --service xiaotian --port 8003 &

# 评分API (端口8004)
python mock_score_api.py --port 8004 &
```

#### Mock数据管理
```bash
# 创建测试数据
python tests/mock_data_manager.py

# 生成今日数据
python tests/mock_data_manager.py --today-data 50
```

### 3. 测试数据验证
```bash
# 检查数据库状态
python -c "
from app import create_app
from app.models import Question, Answer, Score
app = create_app()
with app.app_context():
    print(f'Questions: {Question.query.count()}')
    print(f'Answers: {Answer.query.count()}')
    print(f'Scores: {Score.query.count()}')
"
```

---

## 🚀 部署指南

### 生产环境配置

#### 1. 环境变量配置
```bash
# .env文件
DATABASE_URL=postgresql://user:pass@host:5432/ai_qa_platform
SECRET_KEY=your-secret-key
FLASK_ENV=production

# API配置
CLASSIFY_API_URL=https://api.classify.com
CLASSIFY_API_KEY=your-api-key
DOUBAO_API_URL=https://api.doubao.com
DOUBAO_API_KEY=your-api-key
XIAOTIAN_API_URL=https://api.xiaotian.com
XIAOTIAN_API_KEY=your-api-key
SCORE_API_URL=https://api.score.com
SCORE_API_KEY=your-api-key
```

#### 2. Docker部署
```dockerfile
# Dockerfile.backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8088", "run:app"]
```

```dockerfile
# Dockerfile.frontend  
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8088:8088"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_qa_platform
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ai_qa_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 3. 部署命令
```bash
# 构建和启动
docker-compose up -d

# 初始化数据库
docker-compose exec backend python init_db.py

# 查看日志
docker-compose logs -f backend
```

### 监控和运维

#### 1. 日志配置
```python
# logging.conf
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_app]
level=DEBUG
handlers=fileHandler
qualname=app

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=logging.handlers.RotatingFileHandler
level=DEBUG
formatter=simpleFormatter
args=('app.log', 'a', 10*1024*1024, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### 2. 性能监控
```python
# app/utils/monitoring.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # 记录性能指标
        logger.info(f"{func.__name__} 执行时间: {end_time - start_time:.2f}s")
        return result
    return wrapper
```

#### 3. 健康检查
```python
# app/api/health.py
@health_bp.route('/health')
def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查Redis连接（如果使用）
        # redis_client.ping()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': 'ok',
                'cache': 'ok'
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

---

## 📈 开发进度

### 完成情况总览
| 模块 | 完成度 | 说明 |
|------|--------|------|
| 🗄️ 数据库设计 | 95% | 完成4张表设计，支持动态评分维度 |
| 🔄 数据同步服务 | 85% | 完成增量同步、去重、状态监控 |
| 🏷️ 智能分类服务 | 80% | 完成16领域分类、API集成 |
| 🤖 答案生成服务 | 75% | 完成多AI并发调用、重试机制 |
| ⭐ 评分服务 | 70% | 完成五维评分、API集成 |
| ⏰ 定时任务调度 | 85% | 完成工作流调度、状态管理 |
| 📡 API接口 | 80% | 完成核心API、文档完善 |
| 🧪 测试框架 | 90% | 完成Mock服务、单元测试 |
| 🎨 前端界面 | 60% | 基础框架完成，组件开发中 |

### 近期开发重点

#### 📋 本周任务
- [ ] 完善评分API集成测试
- [ ] 优化批处理性能
- [ ] 补充前端数据大盘组件
- [ ] 完善错误处理机制

#### 🎯 下周计划
- [ ] 前端问题管理页面
- [ ] 答案对比功能
- [ ] 评分管理界面
- [ ] 审核工作台

#### 🚀 月度目标
- [ ] 完整前端界面上线
- [ ] 性能优化和压测
- [ ] 生产环境部署
- [ ] 用户使用文档

### 技术债务
1. **API错误处理**：需要统一错误码和错误信息格式
2. **性能优化**：大批量数据处理需要优化
3. **监控完善**：需要添加更多性能监控指标
4. **文档更新**：API文档需要持续更新

---

## 📞 开发支持

### 常见问题

#### Q1: 如何重置数据库？
```bash
# 删除所有数据
python -c "
from app import create_app
from app.utils.database import db
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print('数据库重置完成')
"
```

#### Q2: 如何添加新的评分维度？
```python
# 1. 更新分类配置
CLASSIFICATION_DIMENSIONS = {
    '新领域': ['维度1', '维度2', '维度3', '维度4', '维度5']
}

# 2. 更新Mock评分API
# 编辑 tests/mock_score_api.py

# 3. 重启服务
```

#### Q3: 如何调试API调用？
```python
# 启用调试日志
import logging
logging.getLogger('app.services.api_client').setLevel(logging.DEBUG)

# 查看API调用日志
tail -f backend/app.log | grep -i api
```

### 联系方式
- **技术支持**：请提交Issue到项目仓库
- **文档问题**：请查看项目Wiki或README
- **部署问题**：请参考部署指南或联系运维团队

### 参考资料
- [Flask官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [React官方文档](https://react.dev/)
- [Ant Design文档](https://ant.design/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)

---

## 📄 附录

### 配置文件模板

#### backend/config.py
```python
class Config:
    # 数据库配置
    DATABASE_URL = 'postgresql://user:pass@localhost:5432/ai_qa_platform'
    
    # API配置
    CLASSIFY_API_URL = 'http://localhost:8001'
    DOUBAO_API_URL = 'http://localhost:8002'
    XIAOTIAN_API_URL = 'http://localhost:8003'
    SCORE_API_URL = 'http://localhost:8004'
    
    # API密钥
    CLASSIFY_API_KEY = 'your-key'
    DOUBAO_API_KEY = 'your-key'
    XIAOTIAN_API_KEY = 'your-key'
    SCORE_API_KEY = 'your-key'
    
    # 性能配置
    BATCH_SIZE = 50
    API_TIMEOUT = 30
    API_RETRY_TIMES = 3
```

#### frontend/.env
```bash
VITE_API_BASE_URL=http://localhost:8088/api
VITE_APP_TITLE=AI问答回流数据处理平台
```

### SQL脚本

#### 创建索引
```sql
-- 优化查询性能
CREATE INDEX idx_questions_classification ON questions(classification);
CREATE INDEX idx_questions_status ON questions(processing_status);
CREATE INDEX idx_questions_created_at ON questions(created_at);
CREATE INDEX idx_answers_question_id ON answers(question_business_id);
CREATE INDEX idx_answers_type ON answers(assistant_type);
CREATE INDEX idx_scores_answer_id ON scores(answer_id);
```

#### 数据清理
```sql
-- 清理测试数据
DELETE FROM scores WHERE answer_id IN (
    SELECT id FROM answers WHERE question_business_id LIKE 'test_%'
);
DELETE FROM answers WHERE question_business_id LIKE 'test_%';
DELETE FROM review_status WHERE question_business_id LIKE 'test_%';
DELETE FROM questions WHERE business_id LIKE 'test_%';
```

---

*最后更新时间：2024年1月1日* 