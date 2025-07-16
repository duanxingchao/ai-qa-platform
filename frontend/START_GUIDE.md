# 前端项目启动指南

## 环境要求

- Node.js 16+ 
- npm 或 yarn

## 安装和启动步骤

### 1. 检查环境
```bash
node --version
npm --version
```

### 2. 安装依赖
```bash
cd frontend
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
```

### 4. 访问应用
浏览器打开: http://localhost:5173

## 确保后端运行

前端依赖后端API，请确保后端服务在运行：

```bash
# 在项目根目录
cd backend
python app.py
```

后端默认运行在: http://localhost:8088

## 如果Node.js未安装

### Ubuntu/Debian:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### CentOS/RHEL:
```bash
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### 使用NVM (推荐):
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

## 项目功能说明

### 已完成的页面：
- **仪表板** (`/dashboard`): 数据统计、图表展示、系统状态
- **问题管理** (`/questions`): 问题列表、搜索、分类、详情查看

### 开发中的页面：
- **答案管理** (`/answers`): 答案对比、评分详情  
- **评分分析** (`/scores`): 评分统计、模型对比
- **系统监控** (`/monitor`): API状态、性能监控
- **系统设置** (`/settings`): 配置管理

## 开发信息

- 框架：Vue 3 + Vite
- UI组件：Element Plus
- 图表：ECharts
- 路由：Vue Router
- HTTP：Axios

## 故障排除

1. **端口占用**: 如果5173端口被占用，Vite会自动选择其他端口
2. **依赖安装失败**: 尝试清除缓存 `npm cache clean --force`
3. **API连接失败**: 确保后端服务在localhost:8088运行

## 下一步开发

如需完善其他页面功能，请参考已完成的Dashboard和Questions页面的实现模式。 