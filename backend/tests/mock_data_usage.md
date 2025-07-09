# Mock数据管理工具使用说明

## 概述

`mock_data_manager.py` 是统一的mock数据管理工具，合并了 `create_test_data.py` 和 `update_table1_mock_data.py` 的所有功能。

## 主要功能

1. **创建table1表** - 包含完整的字段结构（含answer字段）
2. **添加/更新表结构** - 检查并添加缺失的字段
3. **生成mock数据** - 支持批量生成测试数据
4. **数据统计和验证** - 查看数据状态和完整性
5. **灵活的参数控制** - 支持不同的操作模式

## 使用方式

### 1. 创建表结构
```bash
python mock_data_manager.py --action create_table
```

### 2. 添加mock数据
```bash
# 添加30条数据（默认）
python mock_data_manager.py --action add_data

# 添加指定数量的数据
python mock_data_manager.py --action add_data --count 50
```

### 3. 更新现有数据的answer字段
```bash
python mock_data_manager.py --action update_answers
```

### 4. 查看数据统计
```bash
python mock_data_manager.py --action stats
```

### 5. 完整设置（一键完成所有操作）
```bash
# 完整设置，生成30条数据
python mock_data_manager.py --action full_setup

# 完整设置，生成指定数量数据
python mock_data_manager.py --action full_setup --count 100
```

## 数据模板自定义

### 1. 问题模板 (MOCK_QUESTIONS)
在脚本中找到 `MOCK_QUESTIONS` 列表，添加您的问题模板：

```python
MOCK_QUESTIONS = [
    "如何提高工作效率？",
    "Python编程的最佳实践是什么？",
    "如何学习机器学习？",
    # 添加更多问题...
]
```

### 2. 答案模板 (MOCK_ANSWERS)
在脚本中找到 `MOCK_ANSWERS` 列表，添加您的答案模板：

```python
MOCK_ANSWERS = [
    "建议制定清晰的工作计划，使用时间管理工具...",
    "遵循PEP 8编码规范，使用虚拟环境...",
    "从基础数学和统计学开始，学习Python...",
    # 添加更多答案...
]
```

### 3. 基础配置数据
您也可以自定义这些基础配置：

- `DEVICE_TYPES` - 设备类型
- `CLASSIFICATIONS` - 分类标签
- `SERVICE_IDS` - 服务ID
- `QA_TYPES` - QA类型
- `INTENTS` - 意图分类

## 输出示例

### 数据统计输出
```
📊 数据统计
--------------------------------------------------
📈 数据统计:
  总数据量: 60
  有query的数据: 60
  有answer的数据: 60
  完整数据量: 60
  唯一页面数: 55
  数据完整率: 100.0%
  时间范围: 2023-11-15 10:30:45 ~ 2024-01-15 16:22:33
```

### 操作成功输出
```
🔄 Mock数据管理工具
============================================================
🚀 生成 30 条mock数据 (包含answer: True)
--------------------------------------------------
✅ 成功插入 30 条mock数据
============================================================
✅ 操作完成！
```

## 注意事项

1. **数据模板为空时**：如果 `MOCK_QUESTIONS` 或 `MOCK_ANSWERS` 为空，脚本会自动生成简单的示例数据
2. **数据库连接**：确保数据库服务正常运行，连接配置正确
3. **批量操作**：建议一次性操作不超过1000条数据，避免内存问题
4. **数据完整性**：脚本会自动检查数据完整性，确保query和answer字段的一致性

## 错误处理

脚本包含完善的错误处理机制：
- 自动检查数据库连接状态
- 事务回滚保证数据一致性
- 详细的错误信息输出
- 优雅的异常处理

## 扩展建议

1. **增加数据类型**：可以扩展支持更多数据类型和字段
2. **批量导入**：可以添加从CSV/JSON文件批量导入数据的功能
3. **数据验证**：可以添加更严格的数据验证规则
4. **性能优化**：对于大量数据可以考虑批量插入优化 