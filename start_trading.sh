#!/bin/bash
#
# 加密货币交易系统 - 直接运行模式启动脚本
# 使用配置文件直接运行策略
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
echo "║           加密货币自动化交易系统 - 直接运行模式              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${YELLOW}注意: 此模式使用配置文件运行，请确保已正确配置${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="${SCRIPT_DIR}"

# 进入项目目录
cd "${PROJECT_ROOT}"

# 检查配置文件是否存在
if [ ! -f "${PROJECT_ROOT}/config/strategy_config.json" ]; then
    echo -e "${RED}错误: 未找到策略配置文件${NC}"
    echo "文件位置: config/strategy_config.json"
    echo -e "${YELLOW}请先运行交互式模式进行配置，或手动创建配置文件${NC}"
    read -p "按回车键退出..."
    exit 1
fi

if [ ! -f "${PROJECT_ROOT}/config/api_keys.json" ]; then
    echo -e "${RED}错误: 未找到API密钥配置文件${NC}"
    echo "文件位置: config/api_keys.json"
    echo -e "${YELLOW}请先运行交互式模式进行配置${NC}"
    read -p "按回车键退出..."
    exit 1
fi

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

# 显示Python版本
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python版本: ${PYTHON_VERSION}${NC}"

# 显示配置信息
echo ""
echo -e "${CYAN}配置信息:${NC}"
echo "  交易所: $(python3 -c "import json; print(json.load(open('config/strategy_config.json'))['strategy']['exchange'])")"
echo "  交易对: $(python3 -c "import json; print(json.load(open('config/strategy_config.json'))['strategy']['symbol'])")"
echo ""

# 确认运行
echo -e "${YELLOW}按 Ctrl+C 可随时停止程序${NC}"
read -p "按回车键开始运行策略..."

# 运行交易程序
echo -e "${CYAN}正在启动策略...${NC}"
echo ""
echo -e "${GREEN}─────────────────────────────────────────────────────${NC}"
echo ""

# 运行主程序
python3 -u src/trading_main.py

# 程序结束
EXIT_CODE=$?

echo ""
echo -e "${GREEN}─────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${CYAN}程序已退出${NC}"

# 根据退出码显示不同消息
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}正常退出${NC}"
else
    echo -e "${YELLOW}退出码: ${EXIT_CODE}${NC}"
fi

read -p "按回车键关闭窗口..."
