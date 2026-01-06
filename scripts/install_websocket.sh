#!/bin/bash
# WebSocket依赖安装脚本

echo "=========================================="
echo "WebSocket依赖安装脚本"
echo "=========================================="
echo ""

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "建议先激活虚拟环境: source venv/bin/activate"
    echo ""
fi

echo "📦 检查已安装的WebSocket库..."
pip list | grep -E 'uvicorn|websocket|wsproto'

echo ""
echo "🔧 安装WebSocket支持..."

# 方案1：安装uvicorn标准版（推荐）
echo "方案1：安装 uvicorn[standard]（包含WebSocket支持）"
pip install 'uvicorn[standard]'

# 方案2：单独安装websockets
echo ""
echo "方案2：安装 websockets 库"
pip install websockets

# 方案3：安装wsproto
echo ""
echo "方案3：安装 wsproto 库"
pip install wsproto

echo ""
echo "✅ 安装完成！"
echo ""
echo "=========================================="
echo "验证安装结果"
echo "=========================================="
pip list | grep -E 'uvicorn|websocket|wsproto'

echo ""
echo "📋 接下来的步骤:"
echo "1. 重启服务: USE_MOCK_EXCHANGE=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8080"
echo "2. 访问: http://127.0.0.1:8080"
echo "3. WebSocket警告应该消失"
echo ""
