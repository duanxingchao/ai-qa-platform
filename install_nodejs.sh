#!/bin/bash

echo "=== Node.js 安装脚本 ==="

# 检查系统类型
if command -v apt-get &> /dev/null; then
    echo "检测到 Ubuntu/Debian 系统"
    echo "安装 Node.js 18..."
    
    # 更新包列表
    sudo apt-get update
    
    # 安装 curl
    sudo apt-get install -y curl
    
    # 添加 NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    
    # 安装 Node.js
    sudo apt-get install -y nodejs
    
elif command -v yum &> /dev/null; then
    echo "检测到 CentOS/RHEL 系统"
    echo "安装 Node.js 18..."
    
    # 添加 NodeSource repository
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    
    # 安装 Node.js
    sudo yum install -y nodejs
    
elif command -v dnf &> /dev/null; then
    echo "检测到 Fedora 系统"
    echo "安装 Node.js 18..."
    
    # 添加 NodeSource repository
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
    
    # 安装 Node.js
    sudo dnf install -y nodejs
    
else
    echo "未识别的系统类型，请手动安装 Node.js"
    echo "访问: https://nodejs.org/en/download/"
    exit 1
fi

# 验证安装
echo ""
echo "=== 验证安装 ==="
node --version
npm --version

echo ""
echo "Node.js 安装完成！"
echo "现在可以运行: ./start_frontend.sh" 