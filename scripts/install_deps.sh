#!/bin/bash
# 快速安装依赖脚本 - Python 3.14 兼容版本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "合约信号扫描系统 - 依赖安装脚本"
echo "=========================================="
echo ""

# 检查Python版本
echo "🔍 检查Python版本..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 提取主版本号
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo ""

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo ""
    echo "建议先创建并激活虚拟环境："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ 虚拟环境: $VIRTUAL_ENV"
fi

echo ""

# 检查pip
echo "📦 检查pip..."
pip --version

echo ""
echo "🔧 升级pip..."
pip install --upgrade pip

echo ""
echo "=========================================="
echo "开始安装依赖..."
echo "=========================================="
echo ""

# 卸载可能存在的冲突包
echo "🗑️  清理冲突包..."
pip uninstall coincurve -y 2>/dev/null || echo "  coincurve 未安装，跳过"

echo ""
echo "📥 安装核心依赖..."

# 使用requirements.txt（已移除coincurve）
if [ -f "requirements.txt" ]; then
    echo "使用 requirements.txt..."
    pip install -r requirements.txt
elif [ -f "requirements-core.txt" ]; then
    echo "使用 requirements-core.txt..."
    pip install -r requirements-core.txt
else
    echo "❌ 错误: 未找到 requirements.txt 或 requirements-core.txt"
    exit 1
fi

echo ""
echo "=========================================="
echo "验证安装..."
echo "=========================================="
echo ""

# 检查关键库
echo "📋 检查已安装的关键库："
pip list | grep -E 'fastapi|uvicorn|ccxt|websockets|pandas|numpy'

echo ""
echo "🧪 测试导入..."
python3 -c "
import fastapi
import uvicorn
import ccxt
import websockets
import pandas
import numpy
print('✅ 所有依赖安装成功！')
"

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "📌 接下来的步骤："
echo "1. 启动服务:"
echo "   USE_MOCK_EXCHANGE=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8080"
echo ""
echo "2. 访问页面:"
echo "   http://127.0.0.1:8080"
echo ""
echo "3. API文档:"
echo "   http://127.0.0.1:8080/docs"
echo ""
echo "💡 提示: 如遇到问题，请查看 docs/python314_setup.md"
echo ""
