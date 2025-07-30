#!/bin/bash

echo "=== 启动前端服务 ==="

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: Node.js 未安装"
    echo "请参考 frontend/START_GUIDE.md 安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "错误: npm 未安装"
    exit 1
fi

echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"

# 进入前端目录
cd frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
else
    echo "依赖已安装，跳过..."
fi

# 启动开发服务器
echo "启动前端开发服务器..."
echo "访问地址: http://localhost:5173"
npm run dev 