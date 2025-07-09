# AI问答平台测试指南

## 📋 测试架构概览

经过重构整理，测试体系现在更加简洁高效：

### 🏗️ 核心测试文件
1. **`test_core.py`** - 核心功能测试（数据库、同步、单元测试）
2. **`test_api.py`** - API接口测试（REST API、客户端、流程测试）
3. **`run_tests.py`** - 统一测试运行器
4. **`mock_data_manager.py`** - Mock数据管理工具

### 🗑️ 已清理的文件
- `test_unit.py` → 合并到 `test_core.py`
- `test_database.py` → 合并到 `test_core.py`
- `test_new_sync.py` → 合并到 `test_core.py`
- `test_api_simplified.py` → 合并到 `test_api.py`
- `test_api_flow.py` → 合并到 `test_api.py`
- `test_api_client.py` → 合并到 `test_api.py`
- `comprehensive_test.py` → 功能分散到核心测试中
- `test_simple_sync.py` → 合并到核心测试中

## 🚀 快速开始

### 1. 环境准备
```bash
cd backend
source venv/bin/activate
cd tests
```

### 2. 运行所有测试
```bash
python run_tests.py
```

### 3. 运行特定类型测试
```bash
# 只运行核心功能测试
python run_tests.py --type core

# 只运行API测试
python run_tests.py --type api
```

### 4. 直接运行单个测试文件
```bash
# 核心功能测试
python test_core.py

# API测试
python test_api.py
```

## 📊 测试内容详解

### 🧪 核心功能测试 (`test_core.py`)

#### 数据库测试
- ✅ 数据库连接测试
- ✅ 必需表存在性检查（table1, questions, answers, scores, review_status）
- ✅ table1表结构和数据质量验证
- ✅ 字段完整性检查

#### 同步服务测试
- ✅ 获取同步状态
- ✅ 获取同步统计信息
- ✅ 执行数据同步操作
- ✅ 验证双表同步逻辑（questions + answers）

#### 数据一致性测试
- ✅ business_id生成逻辑验证
- ✅ SQL过滤逻辑测试
- ✅ 数据完整性检查

#### 数据模型测试
- ✅ Question模型基础操作
- ✅ Answer模型基础操作
- ✅ ORM集成测试

### 🌐 API测试 (`test_api.py`)

#### 同步API测试
- ✅ GET `/api/sync/status` - 同步状态
- ✅ GET `/api/sync/statistics` - 统计信息
- ✅ POST `/api/sync/trigger` - 触发同步
- ✅ GET `/api/sync/health` - 健康检查
- ✅ GET `/api/sync/data` - 数据分页查看

#### API客户端测试
- ✅ API客户端工厂模式
- ✅ 单例模式验证
- ✅ 统计信息收集
- ✅ Mock API调用测试

#### API流程测试
- ✅ 数据库到API的完整流程
- ✅ 问题分类流程测试
- ✅ 性能和错误处理测试

## 📝 测试结果解读

### 成功输出示例
```
🧪 核心功能测试
============================================================
✅ 数据库连接成功: PostgreSQL 13.x...
✅ table1: 存在 (60 条记录)
✅ questions: 存在 (30 条记录)
✅ answers: 存在 (30 条记录)
✅ table1数据质量: 100.0% (60/60)
✅ 同步状态: {'status': 'idle', 'total_synced': 30}
✅ business_id生成逻辑正确
✅ Question模型查询成功: 30 条记录
✅ Answer模型查询成功: 30 条记录

📈 成功率: 100.0%
🎉 所有核心测试通过!
```

### 常见错误处理

#### 数据库连接问题
```
❌ 数据库连接失败: could not connect to server
```
**解决方案**: 检查数据库服务状态和连接配置

#### Flask服务器未启动
```
⚠️ 所有API测试都被跳过了，请检查服务器状态
💡 提示: Flask服务器未启动，请运行 'python run.py' 启动服务器
```
**解决方案**: 启动Flask应用

#### Mock API服务器问题
```
⚠️ Mock API服务器未启动
💡 提示: Mock API服务器未启动，请运行 'python mock_classification_api.py' 启动Mock服务
```
**解决方案**: 启动Mock API服务器

## 🛠️ Mock数据管理

### 查看数据状态
```bash
python mock_data_manager.py --action stats
```

### 添加测试数据
```bash
# 添加30条数据
python mock_data_manager.py --action add_data --count 30

# 为现有数据补齐answer字段
python mock_data_manager.py --action update_answers
```

### 完整设置
```bash
# 一键完成表创建、数据生成、字段补齐
python mock_data_manager.py --action full_setup --count 50
```

## 🔧 高级测试选项

### 测试特定功能
```bash
# 只测试数据库连接
python -c "from test_core import DatabaseTests; import unittest; unittest.main(module=None, argv=[''], testLoader=unittest.TestLoader().loadTestsFromTestCase(DatabaseTests), exit=False)"

# 只测试同步服务
python -c "from test_core import SyncServiceTests; import unittest; unittest.main(module=None, argv=[''], testLoader=unittest.TestLoader().loadTestsFromTestCase(SyncServiceTests), exit=False)"
```

### 详细输出
```bash
python run_tests.py --verbose
```

## 📈 持续集成建议

### 推荐的测试流程
1. **开发阶段**: 运行 `python test_core.py`
2. **功能测试**: 运行 `python test_api.py`
3. **完整测试**: 运行 `python run_tests.py`
4. **部署前**: 运行完整测试套件并确保100%通过

### 测试覆盖率目标
- 🎯 核心功能测试: 100% 通过
- 🎯 API测试: 90%+ 通过（允许部分跳过）
- 🎯 整体成功率: 95%+

## 🐛 故障排除

### 常见问题及解决方案

#### 1. 导入错误
```bash
ModuleNotFoundError: No module named 'app'
```
**解决**: 确保在backend目录下运行，并激活虚拟环境

#### 2. 数据库表不存在
```bash
relation "questions" does not exist
```
**解决**: 运行数据库迁移或重新创建表结构

#### 3. 测试数据不足
```bash
没有有效的query数据
```
**解决**: 使用mock_data_manager.py添加测试数据

#### 4. 网络超时
```bash
requests.exceptions.Timeout
```
**解决**: 检查网络连接，增加超时时间

## 📚 扩展开发

### 添加新测试
1. 在`test_core.py`中添加新的测试类
2. 在`test_api.py`中添加新的API测试
3. 更新测试指南文档

### 测试最佳实践
- ✅ 使用描述性的测试方法名
- ✅ 每个测试只验证一个功能点
- ✅ 提供清晰的错误信息
- ✅ 适当使用setUp和tearDown
- ✅ 测试边界条件和错误情况

---

**🎯 目标**: 通过简化的测试架构，提高测试效率，降低维护成本，确保系统稳定性。 