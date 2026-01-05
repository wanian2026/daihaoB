#!/bin/bash
#
# 依赖安装修复脚本
# 解决 Python 3.14 兼容性问题
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           加密货币交易系统 - 依赖修复工具                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${SCRIPT_DIR}"

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "${CYAN}检测到Python版本: ${PYTHON_VERSION}${NC}"

# 检查是否是Python 3.14
if [ "$PYTHON_MAJOR" = "3" ] && [ "$PYTHON_MINOR" = "14" ]; then
    echo -e "${YELLOW}警告: Python 3.14 存在兼容性问题${NC}"
    echo -e "${YELLOW}建议: 使用 Python 3.12 或 3.13${NC}"
    echo ""
    echo -e "${CYAN}是否继续使用当前Python版本？(y/N)${NC}"
    read -r choice

    if [[ ! "$choice" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}请安装Python 3.12或3.13后重试${NC}"
        echo "安装命令:"
        echo "  brew install python@3.12"
        echo ""
        exit 0
    fi
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}虚拟环境创建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${CYAN}激活虚拟环境...${NC}"
source .venv/bin/activate

# 升级pip
echo -e "${CYAN}升级pip...${NC}"
pip install --upgrade pip --quiet

# 清理旧的依赖
echo -e "${CYAN}清理旧的依赖...${NC}"
pip freeze | xargs pip uninstall -y --quiet 2>/dev/null

# 安装核心依赖
echo -e "${CYAN}安装核心依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 依赖安装成功${NC}"
    else
        echo -e "${RED}依赖安装失败${NC}"
        echo -e "${YELLOW}请检查错误信息并重试${NC}"
        exit 1
    fi
else
    echo -e "${RED}未找到 requirements.txt${NC}"
    exit 1
fi

# 标记为已安装
touch .venv/.installed

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ 依赖修复完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}现在可以启动程序了：${NC}"
echo -e "  ${GREEN}交互式界面:${NC} bash start_interactive.sh"
echo -e "  ${GREEN}Web界面:${NC}    bash start_web.sh"
echo ""

read -p "按回车键退出..."
