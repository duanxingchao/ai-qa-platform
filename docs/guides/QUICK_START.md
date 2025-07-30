# 🚀 快速启动指南

## ❌ 当前问题

1. **Node.js 未安装** - 前端需要Node.js环境
2. **端口冲突** - 5000和5001端口被占用

## ✅ 解决方案

### 步骤1: 安装Node.js

```bash
# 赋予执行权限
chmod +x install_nodejs.sh

# 运行安装脚本
./install_nodejs.sh

# 验证安装
node --version
npm --version
```

### 步骤2: 启动服务

#### 启动后端 (端口8088)
```bash
chmod +x start_backend.sh
./start_backend.sh
```

#### 启动前端 (端口5173)
```bash
# 在新的终端窗口
chmod +x start_frontend.sh
./start_frontend.sh
```

## 📱 访问地址

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8088

## 🔧 如果仍有问题

### Node.js安装失败
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install curl
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

### 端口仍被占用
如果8088端口也被占用，编辑 `backend/run.py`:
```python
port = int(os.environ.get('PORT', 9999))  # 改为其他端口
```

然后编辑 `frontend/vite.config.js`:
```javascript
target: 'http://localhost:9999',  # 改为相同端口
```

## 🎯 下一步

1. 安装Node.js: `./install_nodejs.sh`
2. 启动后端: `./start_backend.sh`  
3. 启动前端: `./start_frontend.sh`
4. 访问: http://localhost:5173

## 📞 需要帮助？

如果遇到其他问题，请查看：
- `README_启动说明.md` - 完整启动文档
- `frontend/START_GUIDE.md` - 前端详细说明 