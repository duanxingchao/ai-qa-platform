# AI问答平台后端

## 快速开始

### 1. 安装依赖
```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，配置数据库连接等信息
```

### 3. 初始化数据库
```bash
# 创建数据库表
python init_db.py
```

### 4. 启动服务
```bash
# 开发模式启动
python run.py

# 或使用gunicorn（生产环境）
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 5. 测试API
```bash
# 在另一个终端运行测试脚本
python test_api.py
```

## API文档

服务启动后，访问以下地址查看API文档：
- http://localhost:5000/api/docs (即将实现)

## 项目结构
```
backend/
├── app/
│   ├── __init__.py          # Flask应用工厂
│   ├── config.py            # 配置文件
│   ├── models/              # 数据模型
│   │   ├── question.py      # 问题模型
│   │   ├── answer.py        # 答案模型
│   │   ├── score.py         # 评分模型
│   │   └── review.py        # 审核状态模型
│   ├── services/            # 业务逻辑层
│   │   ├── sync_service.py  # 数据同步服务
│   │   ├── clean_service.py # 数据清洗服务
│   │   └── ...              # 其他服务
│   ├── api/                 # API路由
│   │   ├── sync_api.py      # 同步API
│   │   ├── question_api.py  # 问题API
│   │   └── process_api.py   # 处理API
│   └── utils/               # 工具函数
│       ├── database.py      # 数据库工具
│       └── helpers.py       # 辅助函数
├── requirements.txt         # 依赖列表
├── run.py                  # 启动文件
├── init_db.py              # 数据库初始化
└── test_api.py             # API测试脚本
```

## 开发说明

### 添加新的API端点
1. 在`app/api/`目录下的相应文件中添加路由
2. 在`app/services/`中实现业务逻辑
3. 更新测试脚本

### 数据库迁移
目前使用SQLAlchemy的`create_all()`方法创建表。后续可考虑集成Alembic进行数据库迁移管理。

### 日志
日志文件保存在`app.log`中，同时输出到控制台。

## 注意事项
1. 确保PostgreSQL数据库已启动并可访问
2. 外部API地址需要在`.env`文件中正确配置
3. 生产环境部署时务必修改SECRET_KEY等敏感配置 