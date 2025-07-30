#!/bin/bash
# Mock服务启用脚本
# 用于重新启用Mock API服务

echo "🔄 启用AI问答平台Mock服务..."
echo "=================================================="

# 检查配置文件是否存在
if [ ! -f "mock_services_config.json" ]; then
    echo "⚠️  配置文件不存在，创建默认配置..."
    cat > mock_services_config.json << 'EOF'
{
  "mock_services": {
    "enabled": true,
    "auto_start": false,
    "services": {
      "classification_api": {
        "port": 8001,
        "enabled": true,
        "script": "backend/tests/mock_classification_api.py"
      },
      "doubao_ai_api": {
        "port": 8002,
        "enabled": true,
        "script": "backend/tests/mock_ai_api.py",
        "args": ["--service", "doubao"]
      },
      "xiaotian_ai_api": {
        "port": 8003,
        "enabled": true,
        "script": "backend/tests/mock_ai_api.py",
        "args": ["--service", "xiaotian"]
      },
      "score_api": {
        "port": 8004,
        "enabled": true,
        "script": "backend/tests/mock_score_api.py"
      }
    },
    "last_enabled": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "enabled_by": "user_request",
    "notes": "Mock services enabled by user request"
  }
}
EOF
else
    # 修改现有配置文件
    echo "🔄 更新配置文件..."
    python3 -c "
import json
with open('mock_services_config.json', 'r') as f:
    config = json.load(f)
config['mock_services']['enabled'] = True
config['mock_services']['last_enabled'] = '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
config['mock_services']['enabled_by'] = 'user_request'
with open('mock_services_config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
fi

echo "✅ Mock服务已启用"
echo ""
echo "💡 现在可以运行以下命令启动Mock服务:"
echo "   ./start_mock_services.sh"
echo ""
echo "💡 或者手动启动单个服务:"
echo "   cd backend/tests"
echo "   python mock_classification_api.py --port 8001 &"
echo "   python mock_ai_api.py --service doubao --port 8002 &"
echo "   python mock_ai_api.py --service xiaotian --port 8003 &"
echo "   python mock_score_api.py --port 8004 &"
