# 荣耀API集成部署指南

## 📋 概述

本项目已完成与荣耀内部API的集成，支持问题分类和答案评分功能。Mock API和生产API使用完全相同的接口格式，确保开发和生产环境的一致性。

## 🔧 API接口信息

### 分类API
- **地址**: `http://aipipeline.ipd.hihonor.com/v1/workflows/run`
- **认证**: 无需认证
- **请求格式**:
```json
{
    "inputs": {
        "QUERY": "用户问题文本",
        "ANSWER": "yoyo答案文本"
    },
    "response_mode": "blocking",
    "user": "00031559"
}
```
- **响应格式**:
```json
{
    "success": true,
    "data": {
        "outputs": {
            "text": "技术问题"
        }
    }
}
```

### 评分API
- **地址**: `http://aipipeline.ipd.hihonor.com/v1/workflows/run`
- **认证**: `Authorization: Bearer app-SXgaGHIf25NtJXEFmc9ecRSc`
- **请求格式**:
```json
{
    "inputs": {
        "QUERY": "用户问题文本",
        "ANSWER": "yoyo答案文本",
        "ANSWER_DOUBAO": "豆包答案文本",
        "ANSWER_XIAOTIAN": "小天答案文本",
        "RESORT": "问题分类结果"
    },
    "response_mode": "blocking",
    "user": "user"
}
```
- **响应格式**:
```json
{
    "success": true,
    "data": {
        "outputs": {
            "text": "[{\"模型名称\":\"yoyo\",\"信息准确性\":4,\"逻辑性\":3,\"流畅性\":4,\"创新性\":3,\"实用性\":4,\"理由\":\"评分理由\"}]"
        }
    }
}
```

## 🚀 部署步骤

### 1. 开发环境
```bash
# 加载开发环境配置
source backend/development.env

# 启动Mock服务
python3 backend/tests/mock_classification_api.py --port 8001 &
python3 backend/tests/mock_score_api.py --port 8004 &

# 测试API集成
python3 backend/test_honor_api_integration.py
```

### 2. 生产环境
```bash
# 加载生产环境配置
source backend/production.env

# 测试API连通性
python3 backend/test_honor_api_integration.py

# 启动应用
python3 backend/app.py
```

## 📊 数据流转

### 分类流程
1. 从`questions`表获取问题文本
2. 从`answers`表获取yoyo答案（`assistant_type='yoyo'`）
3. 调用分类API
4. 将分类结果写入`questions.classification`字段

### 评分流程
1. 从`questions`表获取问题文本和分类结果
2. 从`answers`表获取三个模型的答案
3. 调用评分API
4. 解析评分结果并写入`scores`表
5. 更新`answers.is_scored`字段为`true`

## 🔍 测试验证

### API客户端测试
```bash
python3 backend/test_honor_api_integration.py
```

### 手动API测试
```bash
# 测试分类API
curl -X POST http://aipipeline.ipd.hihonor.com/v1/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "QUERY": "如何优化数据库性能？",
      "ANSWER": "可以通过索引优化等方式"
    },
    "response_mode": "blocking",
    "user": "00031559"
  }'

# 测试评分API
curl -X POST http://aipipeline.ipd.hihonor.com/v1/workflows/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer app-SXgaGHIf25NtJXEFmc9ecRSc" \
  -d '{
    "inputs": {
      "QUERY": "如何优化数据库性能？",
      "ANSWER": "可以通过索引优化等方式",
      "ANSWER_DOUBAO": "建议使用索引和缓存",
      "ANSWER_XIAOTIAN": "从多个维度进行优化",
      "RESORT": "技术问题"
    },
    "response_mode": "blocking",
    "user": "user"
  }'
```

## ⚙️ 配置说明

### 环境变量
- `CLASSIFY_API_URL`: 分类API地址
- `SCORE_API_URL`: 评分API地址
- `SCORE_API_KEY`: 评分API认证密钥
- `API_ENVIRONMENT`: 环境标识（development/production）

### 数据库字段映射
- `questions.classification`: 分类结果
- `scores.dimension_*_name`: 动态维度名称
- `scores.score_*`: 各维度评分
- `scores.average_score`: 平均分
- `scores.comment`: 评分理由

## 🛠️ 故障排查

### 常见问题
1. **API连接失败**: 检查网络连通性和URL配置
2. **认证失败**: 确认评分API的Bearer token正确
3. **数据格式错误**: 确认请求体格式符合荣耀API规范
4. **评分写入失败**: 检查数据库连接和字段映射

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看API调用日志
grep "API" logs/app.log
```

## 📈 监控指标

### API调用统计
- 分类API成功率
- 评分API成功率
- 平均响应时间
- 错误率统计

### 数据处理统计
- 分类处理数量
- 评分处理数量
- 数据库写入成功率

## 🔄 版本升级

如需升级API版本或修改接口格式：
1. 更新Mock API服务
2. 修改API客户端代码
3. 运行集成测试
4. 更新生产环境配置

---

**注意**: 本集成已确保开发环境Mock API与生产环境荣耀API格式完全一致，可以无缝切换。
