#!/bin/bash

echo "=== 启动后端服务 (生产模式) ==="

# 激活虚拟环境
echo "激活虚拟环境..."
cd backend
source venv/bin/activate

# 安装Python依赖
echo "检查Python依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 设置环境变量
export FLASK_ENV=production
export DEBUG=False

echo "启动后端服务 (生产模式, http://localhost:8088)..."

# 使用 gunicorn 启动生产服务器
exec gunicorn \
    --bind 0.0.0.0:8088 \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    run:app 