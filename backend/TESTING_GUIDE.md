# 🧪 AI问答平台测试指南

## 📋 测试文件结构

### 🚀 主要测试套件
- `run_full_project_test.py` - **全面测试套件**，测试所有功能模块
- `quick_full_test.py` - **快速测试套件**，快速验证核心功能

### 🔧 专业测试文件
- `tests/test_core.py` - 核心功能测试（数据库、模型、同步服务）
- `tests/test_api.py` - API接口测试（Web API、客户端测试）
- `tests/test_answer_generation.py` - 答案生成功能测试
- `tests/run_tests.py` - 专业测试运行器

### 🎭 Mock服务
- `tests/mock_classification_api.py` - 分类API Mock服务器
- `tests/mock_ai_api.py` - AI API Mock服务器（豆包、小天）
- `tests/mock_score_api.py` - 评分API Mock服务器（多模型评分）
- `tests/mock_data_manager.py` - 数据管理Mock服务

## 🎯 使用方法

### 1. 快速验证（推荐）
```bash
cd backend
python quick_full_test.py
```
**用途**: 快速检查所有核心功能是否正常，耗时约30秒

### 2. 全面测试
```bash
cd backend  
python run_full_project_test.py
```
**用途**: 深度测试所有功能，包括性能测试，耗时约5-10分钟

### 3. 专业测试
```bash
cd backend/tests
python run_tests.py
```
**用途**: 运行所有专业测试套件，适合开发时使用

### 4. 单独测试
```bash
cd backend/tests
python test_core.py        # 测试核心功能
python test_api.py         # 测试API接口  
python test_answer_generation.py  # 测试答案生成
```

### 5. 评分系统专门测试
```bash
cd backend
python test_scoring_system.py    # 评分系统完整测试
```
**用途**: 专门测试评分功能，包括Mock API、客户端、AI服务和数据库集成

## ⚙️ Mock服务器

### 启动所有Mock服务
```bash
cd backend/tests
python mock_classification_api.py --auto-port &
python mock_ai_api.py --service doubao --auto-port &
python mock_ai_api.py --service xiaotian --auto-port &
python mock_score_api.py --auto-port &
```

### 单独启动
```bash
# 启动分类API Mock (端口8001)
python mock_classification_api.py

# 启动豆包AI Mock (端口8002)  
python mock_ai_api.py --service doubao --port 8002

# 启动小天AI Mock (端口8003)
python mock_ai_api.py --service xiaotian --port 8003

# 启动评分API Mock (端口8004)
python mock_score_api.py --port 8004
```

## 📊 测试报告解读

### 测试状态
- ✅ **PASS** - 测试通过
- ❌ **FAIL** - 测试失败，需要修复
- ⚠️ **WARN** - 测试警告，建议检查

### 关键指标
- **成功率** - 应该 > 90%
- **核心功能** - 数据库、API客户端、AI服务必须通过
- **性能指标** - 数据库查询 < 1000ms

## 🔍 常见问题

### 1. 端口占用
```bash
# 查看端口占用
sudo lsof -i :8001

# 停止占用进程
pkill -f "mock_classification_api.py"
```

### 2. 数据库连接失败
- 检查数据库是否启动
- 验证DATABASE_URL配置
- 确认数据库表是否存在

### 3. API客户端创建失败
- 检查API配置（URL、密钥）
- 确认Mock服务器是否启动
- 验证网络连接

## 🎯 测试最佳实践

### 开发阶段
1. **提交前**: 运行 `quick_full_test.py`
2. **功能开发**: 运行相关的专业测试
3. **重构后**: 运行 `run_full_project_test.py`

### 部署阶段  
1. **部署前**: 运行完整测试套件
2. **部署后**: 运行快速测试验证
3. **定期检查**: 每日运行核心功能测试

## 📈 测试覆盖范围

- ✅ 数据库连接和表结构
- ✅ 数据模型定义和关系
- ✅ 数据同步服务功能
- ✅ API客户端工厂模式
- ✅ 外部API调用（分类、AI、评分）
- ✅ AI处理服务业务逻辑
- ✅ 多模型评分系统（原始模型、豆包、小天）
- ✅ 评分结果数据库存储和匹配
- ✅ 定时任务调度器
- ✅ Web API端点响应
- ✅ 错误处理和异常情况
- ✅ 性能基准测试

---
**更新时间**: 2024年12月
**维护人员**: AI开发团队 