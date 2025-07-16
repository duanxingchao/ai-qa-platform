#!/bin/bash

echo "=== 启动后端服务 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 进入后端目录
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 设置环境变量
export FLASK_APP=run.py
export FLASK_ENV=development

# 启动后端服务
echo "启动后端服务 (http://localhost:8088)..."
python run.py 