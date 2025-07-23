#!/bin/bash
# Mock服务启动脚本
# 用于快速启动所有必需的Mock API服务

echo "🚀 启动AI问答平台Mock服务..."
echo "=" * 50

# 检查是否在正确的目录
if [ ! -d "backend" ]; then
    echo "❌ 错误：请在项目根目录执行此脚本"
    echo "当前目录应包含backend文件夹"
    exit 1
fi

# 进入backend目录
cd backend

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  警告：未发现venv虚拟环境，使用系统Python"
else
    echo "🔄 激活Python虚拟环境..."
    source venv/bin/activate
fi

# 检查tests目录
if [ ! -d "tests" ]; then
    echo "❌ 错误：tests目录不存在"
    exit 1
fi

# 进入tests目录
cd tests

echo ""
echo "🔄 启动Mock服务..."

# 启动分类API服务 (端口8001)
echo "启动分类API服务 (端口:8001)"
python mock_classification_api.py --port 8001 &
CLASSIFY_PID=$!
sleep 2

# 启动豆包AI服务 (端口8002)
echo "启动豆包AI服务 (端口:8002)"
python mock_ai_api.py --service doubao --port 8002 &
DOUBAO_PID=$!
sleep 2

# 启动小天AI服务 (端口8003)
echo "启动小天AI服务 (端口:8003)"
python mock_ai_api.py --service xiaotian --port 8003 &
XIAOTIAN_PID=$!
sleep 2

# 启动评分API服务 (端口8004)
echo "启动评分API服务 (端口:8004)"
python mock_score_api.py --port 8004 &
SCORE_PID=$!
sleep 2

# 返回上级目录
cd ..

echo ""
echo "✅ 所有Mock服务启动完成！"
echo ""
echo "📊 服务状态检查:"
echo "分类API:   curl http://localhost:8001/health"
echo "豆包API:   curl http://localhost:8002/health"
echo "小天API:   curl http://localhost:8003/health"
echo "评分API:   curl http://localhost:8004/health"
echo ""
echo "🔄 或通过后端API检查: curl http://localhost:8088/api/mock/status"
echo ""
echo "📝 进程ID记录:"
echo "分类API PID: $CLASSIFY_PID"
echo "豆包API PID: $DOUBAO_PID"
echo "小天API PID: $XIAOTIAN_PID"
echo "评分API PID: $SCORE_PID"
echo ""
echo "🛑 停止所有服务: kill $CLASSIFY_PID $DOUBAO_PID $XIAOTIAN_PID $SCORE_PID"

# 等待用户输入或Ctrl+C
echo ""
echo "按 Ctrl+C 停止所有服务..."
trap 'echo ""; echo "🛑 正在停止所有Mock服务..."; kill $CLASSIFY_PID $DOUBAO_PID $XIAOTIAN_PID $SCORE_PID 2>/dev/null; echo "✅ 所有服务已停止"; exit 0' INT

# 保持脚本运行
wait 