#!/bin/bash

# 🚀 AI问答平台 API流程测试启动脚本

echo "🚀 AI问答平台 - API流程完整测试"
echo "=================================="
echo "⏰ 启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  检测到未激活虚拟环境"
    echo "💡 激活虚拟环境："
    echo "   cd backend && source venv/bin/activate"
    echo
fi

# 创建日志目录
mkdir -p logs

echo "📋 测试流程："
echo "1. 🤖 启动Mock分类API服务器 (端口8001)"
echo "2. ⏰ 等待服务器启动"
echo "3. 🧪 运行API流程测试"
echo "4. 📊 显示测试结果"
echo

# 步骤1：启动Mock API服务器
echo "🤖 启动Mock分类API服务器..."
cd backend
python mock_classification_api.py > ../logs/mock_api.log 2>&1 &
MOCK_API_PID=$!
echo "   PID: $MOCK_API_PID"
echo "   日志: logs/mock_api.log"

# 等待服务器启动
echo "⏰ 等待服务器启动..."
sleep 3

# 检查服务器是否启动成功
echo "🔍 检查服务器状态..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Mock API服务器启动成功"
else
    echo "❌ Mock API服务器启动失败"
    echo "📋 查看日志: cat logs/mock_api.log"
    kill $MOCK_API_PID 2>/dev/null
    exit 1
fi

# 步骤2：运行测试
echo
echo "🧪 开始API流程测试..."
echo "=================================="
python test_api_flow.py

# 获取测试结果
TEST_EXIT_CODE=$?

echo
echo "=================================="
echo "📋 测试完成"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ 测试成功完成"
else
    echo "⚠️  测试过程中出现问题 (退出码: $TEST_EXIT_CODE)"
fi

# 清理：停止Mock API服务器
echo
echo "🧹 清理资源..."
echo "   停止Mock API服务器 (PID: $MOCK_API_PID)"
kill $MOCK_API_PID 2>/dev/null

echo "✅ 清理完成"
echo
echo "📁 日志文件:"
echo "   Mock API日志: logs/mock_api.log"
echo
echo "�� 如需重新测试，请再次运行此脚本" 