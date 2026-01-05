#!/bin/bash
#
# LaunchAgents 安装脚本
# 用于设置加密货币交易系统的开机自启动
#

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║         LaunchAgents 自启动配置安装向导                  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 获取当前项目路径
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查项目路径
echo -e "${CYAN}项目路径: ${PROJECT_ROOT}${NC}"
echo ""

# 确认路径
read -p "这是正确的项目路径吗？(y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${RED}已取消安装${NC}"
    exit 1
fi

# 检查Python路径
PYTHON_PATH="${PROJECT_ROOT}/.venv/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}错误: 未找到Python解释器${NC}"
    echo "请先运行以下命令安装虚拟环境："
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 检查主程序路径
MAIN_SCRIPT="${PROJECT_ROOT}/src/trading_main.py"
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}错误: 未找到交易主程序${NC}"
    exit 1
fi

# 创建日志目录
LOG_DIR="${PROJECT_ROOT}/logs"
mkdir -p "$LOG_DIR"

# 创建LaunchAgents目录
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

# 生成plist文件
PLIST_FILE="$LAUNCH_AGENTS_DIR/com.tradingbot.plist"

echo -e "${CYAN}正在生成LaunchAgent配置文件...${NC}"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tradingbot</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${MAIN_SCRIPT}</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${PROJECT_ROOT}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/trading.stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/trading.stderr.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
</dict>
</plist>
EOF

echo -e "${GREEN}✓ 配置文件已生成: ${PLIST_FILE}${NC}"
echo ""

# 卸载旧版本（如果存在）
if launchctl list | grep -q "com.tradingbot"; then
    echo -e "${YELLOW}检测到旧版本，正在卸载...${NC}"
    launchctl unload "$PLIST_FILE" 2>/dev/null
fi

# 加载LaunchAgent
echo -e "${CYAN}正在加载LaunchAgent...${NC}"
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ LaunchAgent加载成功${NC}"
else
    echo -e "${RED}✗ LaunchAgent加载失败${NC}"
    exit 1
fi

# 启动服务
echo -e "${CYAN}正在启动交易服务...${NC}"
launchctl start com.tradingbot

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 交易服务已启动${NC}"
else
    echo -e "${YELLOW}⚠ 服务启动失败，可能需要手动启动${NC}"
fi

echo ""
echo -e "${GREEN}═════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}安装完成！${NC}"
echo -e "${GREEN}═════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}常用命令:${NC}"
echo "  查看服务状态:"
echo "    launchctl list | grep tradingbot"
echo ""
echo "  停止服务:"
echo "    launchctl stop com.tradingbot"
echo ""
echo "  启动服务:"
echo "    launchctl start com.tradingbot"
echo ""
echo "  重启服务:"
echo "    launchctl stop com.tradingbot && launchctl start com.tradingbot"
echo ""
echo "  查看日志:"
echo "    tail -f ${LOG_DIR}/trading.stdout.log"
echo ""
echo "  卸载服务:"
echo "    launchctl unload ${PLIST_FILE}"
echo ""
echo -e "${YELLOW}提示: 交易服务已设置为开机自启动${NC}"
echo -e "${YELLOW}如需禁用开机自启，请运行卸载命令${NC}"
echo ""

read -p "按回车键退出..."
