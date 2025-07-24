# 🚀 项目启动说明

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
# 1. 赋予脚本执行权限
chmod +x start_backend.sh start_frontend.sh

# 2. 启动后端服务（在一个终端窗口）
./start_backend.sh

# 3. 启动前端服务（在另一个终端窗口）
cc
```

### 方式二：手动启动

#### 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

- **前端管理界面**: http://localhost:5173
- **后端API服务**: http://localhost:8088

## 项目功能概览

### ✅ 已完成功能

#### 仪表板页面 (`/dashboard`)
- 📊 实时数据统计卡片
- 📈 趋势图表展示
- 🎯 AI模型雷达对比图
- 🔍 系统状态监控

#### 问题管理页面 (`/questions`)  
- 🔍 高级搜索和过滤
- 📋 分页数据列表
- 🔍 问题详情抽屉
- 🏷️ 分类管理
- 📊 批量操作

#### 后端AI处理系统
- 🤖 多模型评分系统（原始/豆包/小天）
- 📊 5维度评分算法
- 🔄 完整的数据处理流程
- 🧪 100%测试通过率

### 🚧 开发中功能

- **答案管理** (`/answers`): 答案对比、评分详情  
- **评分分析** (`/scores`): 评分统计、模型对比
- **系统监控** (`/monitor`): API状态、性能监控
- **系统设置** (`/settings`): 配置管理

## 技术栈

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **图表**: Apache ECharts
- **路由**: Vue Router
- **HTTP**: Axios

### 后端
- **框架**: Flask + SQLAlchemy
- **数据库**: SQLite
- **AI集成**: 多模型API客户端
- **测试**: PyTest

## 开发须知

1. **前端开发**: 默认端口5173，支持热重载
2. **后端开发**: 默认端口8088，Flask调试模式
3. **API代理**: 前端已配置代理转发到后端
4. **数据库**: SQLite文件位于 `backend/instance/app.db`

## 故障排除

### Node.js环境
如果Node.js未安装，请参考 `frontend/START_GUIDE.md`

### Python环境
确保Python 3.7+已安装：
```bash
python3 --version
```

### 端口冲突
- 前端：5173端口被占用时，Vite会自动选择其他端口
- 后端：8088端口被占用时，需要手动修改配置

### 依赖安装失败
```bash
# 清除npm缓存
npm cache clean --force

# 清除pip缓存
pip cache purge
```

## 下一步开发计划

1. **完善答案管理页面**: 多模型答案对比界面
2. **评分分析功能**: 评分趋势、模型性能分析
3. **系统监控界面**: API状态、响应时间监控
4. **导出功能**: 数据导出为Excel/CSV
5. **用户权限管理**: 多用户角色支持

---

🎉 **现在您可以开始测试前端界面了！**

请按照上述说明启动服务，然后在浏览器中访问 http://localhost:5173 来体验管理界面。 