#!/bin/bash
# Mock服务停止脚本
# 用于停止所有Mock API服务

echo "🛑 停止AI问答平台Mock服务..."
echo "=================================================="

# 停止所有Mock服务进程
echo "🔄 正在停止Mock服务进程..."

# 方法1: 通过进程名停止
pkill -f "mock_classification_api.py" && echo "✅ 分类API服务已停止"
pkill -f "mock_ai_api.py.*doubao" && echo "✅ 豆包AI服务已停止"
pkill -f "mock_ai_api.py.*xiaotian" && echo "✅ 小天AI服务已停止"
pkill -f "mock_score_api.py" && echo "✅ 评分API服务已停止"

# 方法2: 通过端口停止（备用方案）
echo ""
echo "🔄 检查端口占用情况..."

for port in 8001 8002 8003 8004; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "⚠️  端口 $port 仍被进程 $PID 占用，强制停止..."
        kill -9 $PID 2>/dev/null && echo "✅ 端口 $port 已释放"
    else
        echo "✅ 端口 $port 已空闲"
    fi
done

echo ""
echo "🔍 验证服务状态..."

# 检查是否还有Mock服务在运行
REMAINING=$(ps aux | grep -E "(mock_.*_api)" | grep -v grep | wc -l)
if [ $REMAINING -eq 0 ]; then
    echo "✅ 所有Mock服务已完全停止"
else
    echo "⚠️  仍有 $REMAINING 个Mock服务进程在运行:"
    ps aux | grep -E "(mock_.*_api)" | grep -v grep
fi

echo ""
echo "🔍 端口状态检查:"
for port in 8001 8002 8003 8004; do
    if lsof -i:$port >/dev/null 2>&1; then
        echo "❌ 端口 $port: 仍被占用"
    else
        echo "✅ 端口 $port: 空闲"
    fi
done

echo ""
echo "🎉 Mock服务停止操作完成！"
echo ""
echo "💡 提示:"
echo "   - 如需重新启动Mock服务，运行: ./start_mock_services.sh"
echo "   - 如需检查服务状态，运行: ps aux | grep mock"
echo "   - 如需检查端口占用，运行: lsof -i:8001-8004"
