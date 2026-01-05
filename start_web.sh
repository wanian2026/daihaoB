#!/bin/bash
#
# Web管理界面启动脚本
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印欢迎信息
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║              加密货币交易系统 - Web管理界面                ║"
echo "║                                                          ║"
║              极简风格 · 功能完整 · 易于使用                   ║"
echo "║                                                          ║"
╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="${SCRIPT_DIR}"

# 进入项目目录
cd "${PROJECT_ROOT}"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.12 或更高版本${NC}"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "${PROJECT_ROOT}/.venv" ]; then
    echo -e "${YELLOW}警告: 未找到虚拟环境${NC}"
    echo "正在创建虚拟环境..."
    python3 -m venv .venv

    if [ $? -ne 0 ]; then
        echo -e "${RED}虚拟环境创建失败${NC}"
        read -p "按回车键退出..."
        exit 1
    fi

    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${CYAN}正在激活虚拟环境...${NC}"
source "${PROJECT_ROOT}/.venv/bin/activate"

if [ $? -ne 0 ]; then
    echo -e "${RED}虚拟环境激活失败${NC}"
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖是否安装
if [ ! -f "${PROJECT_ROOT}/.venv/.installed" ]; then
    echo -e "${YELLOW}首次运行，正在安装依赖...${NC}"

    if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
        pip install -r "${PROJECT_ROOT}/requirements.txt"

        if [ $? -eq 0 ]; then
            touch "${PROJECT_ROOT}/.venv/.installed"
            echo -e "${GREEN}✓ 依赖安装成功${NC}"
        else
            echo -e "${RED}依赖安装失败${NC}"
            read -p "按回车键退出..."
            exit 1
        fi
    else
        echo -e "${YELLOW}未找到 requirements.txt，跳过依赖安装${NC}"
    fi
fi

# 检查是否需要安装FastAPI和uvicorn
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}正在安装Web服务器依赖...${NC}"
    pip install fastapi uvicorn[standard] python-multipart

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Web依赖安装成功${NC}"
    else
        echo -e "${RED}Web依赖安装失败${NC}"
        read -p "按回车键退出..."
        exit 1
    fi
fi

# 显示Python版本
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python版本: ${PYTHON_VERSION}${NC}"

# 设置端口
PORT=${PORT:-8000}

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}启动Web服务器${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}✓ Web界面地址: ${CYAN}http://localhost:${PORT}${NC}"
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务器${NC}"
echo ""

# 启动Web服务器
cd "${PROJECT_ROOT}"
python3 -m uvicorn src.web.api:app --host 0.0.0.0 --port ${PORT} --reload

# 程序结束
EXIT_CODE=$?

echo ""
echo -e "${CYAN}Web服务器已停止${NC}"

# 根据退出码显示不同消息
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}正常退出${NC}"
else
    echo -e "${YELLOW}退出码: ${EXIT_CODE}${NC}"
fi

read -p "按回车键关闭窗口..."
