# Mac 快速启动指南

本指南将帮助你在Mac电脑上方便地启动和使用加密货币交易系统。

## 📋 目录

- [方法一：双击Shell脚本](#方法一双击shell脚本)
- [方法二：使用.app应用](#方法二使用app应用)
- [方法三：终端运行](#方法三终端运行)
- [方法四：LaunchAgents自启动（可选）](#方法四launchagents自启动可选)
- [常见问题](#常见问题)

---

## 方法一：双击Shell脚本（推荐新手）

### 交互式模式启动

这是最简单的启动方式，适合新手和需要每次配置的交易场景。

**文件位置**: `start_interactive.sh`

**使用步骤**:

1. **找到启动脚本**
   - 在Finder中打开项目目录
   - 找到 `start_interactive.sh` 文件

2. **双击运行**
   - 直接双击 `start_interactive.sh` 文件
   - 如果提示"无法打开此文件"，继续下一步

3. **设置文件权限（如果需要）**
   - 在终端中运行：
   ```bash
   cd /path/to/your/project
   chmod +x start_interactive.sh
   ```
   - 然后再次双击文件

4. **首次运行**
   - 脚本会自动创建虚拟环境
   - 自动安装依赖包
   - 启动交互式界面

5. **按提示操作**
   - 选择交易所（OKX 或 Binance）
   - 选择交易模式（模拟交易或正式交易）
   - 输入API密钥
   - 选择交易对
   - 配置策略参数
   - 开始交易

### 直接运行模式启动

使用预设配置直接运行策略，适合固定交易场景。

**文件位置**: `start_trading.sh`

**使用步骤**:

1. **配置参数**
   - 确保 `config/strategy_config.json` 已正确配置
   - 确保 `config/api_keys.json` 已正确配置

2. **双击运行**
   - 直接双击 `start_trading.sh` 文件

3. **确认配置**
   - 脚本会显示当前配置信息
   - 确认无误后按回车开始运行

---

## 方法二：使用.app应用（推荐日常使用）

创建了一个Mac应用包，可以像普通Mac应用一样双击启动。

### 安装应用

```bash
# 进入项目目录
cd /path/to/your/project

# 复制应用到应用程序文件夹
cp -R TradingBot.app /Applications/
```

### 启动应用

1. **从Finder启动**
   - 打开 "应用程序" 文件夹
   - 找到 "加密货币交易系统" 应用
   - 双击启动

2. **从Launchpad启动**
   - 点击Launchpad图标
   - 找到 "加密货币交易系统" 应用
   - 点击启动

3. **从Spotlight启动**
   - 按 `Cmd + Space` 打开Spotlight搜索
   - 输入 "TradingBot" 或 "加密货币"
   - 按回车启动

### 添加图标（可选）

应用目前使用默认图标，你可以添加自定义图标：

```bash
# 1. 准备图标文件（PNG格式，1024x1024像素）
# 2. 转换为ICNS格式
#    参考：TradingBot.app/Contents/Resources/ICON_README.md

# 3. 复制到应用包
cp AppIcon.icns TradingBot.app/Contents/Resources/AppIcon.icns

# 4. 刷新Finder
killall Dock
```

---

## 方法三：终端运行（适合高级用户）

### 交互式模式

```bash
# 进入项目目录
cd /path/to/your/project

# 激活虚拟环境
source .venv/bin/activate

# 运行交互式程序
python src/interactive/interactive_main.py
```

### 直接运行模式

```bash
# 进入项目目录
cd /path/to/your/project

# 激活虚拟环境
source .venv/bin/activate

# 运行交易程序
python src/trading_main.py
```

### 后台运行（持续交易）

```bash
# 进入项目目录
cd /path/to/your/project

# 激活虚拟环境
source .venv/bin/activate

# 后台运行并保存日志
nohup python src/trading_main.py >> logs/trading.log 2>&1 &

# 查看运行状态
ps aux | grep trading_main.py

# 停止运行
pkill -f trading_main.py
```

---

## 方法四：LaunchAgents自启动（可选）

### 创建LaunchAgent配置文件

```bash
# 创建配置目录
mkdir -p ~/Library/LaunchAgents

# 创建配置文件
cat > ~/Library/LaunchAgents/com.tradingbot.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tradingbot</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/your/project/.venv/bin/python</string>
        <string>/path/to/your/project/src/trading_main.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/path/to/your/project</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/path/to/your/project/logs/trading.log</string>
    
    <key>StandardErrorPath</key>
    <string>/path/to/your/project/logs/trading.error.log</string>
</dict>
</plist>
EOF
```

**重要**: 将 `/path/to/your/project` 替换为你的实际项目路径

### 加载LaunchAgent

```bash
# 加载配置
launchctl load ~/Library/LaunchAgents/com.tradingbot.plist

# 启动服务
launchctl start com.tradingbot

# 查看状态
launchctl list | grep tradingbot

# 停止服务
launchctl stop com.tradingbot

# 卸载配置
launchctl unload ~/Library/LaunchAgents/com.tradingbot.plist
```

---

## 🎯 推荐使用场景

| 场景 | 推荐方式 | 说明 |
|------|----------|------|
| **新手首次使用** | 双击 `start_interactive.sh` | 最简单，有完整向导 |
| **日常交易** | 双击 `TradingBot.app` | 像普通应用一样使用 |
| **固定策略** | 双击 `start_trading.sh` | 使用预设配置快速启动 |
| **后台运行** | `nohup` 命令 | 持续运行，关闭终端不影响 |
| **开机自启** | LaunchAgents | 开机自动启动交易 |

---

## 📁 文件结构

```
项目根目录/
├── start_interactive.sh          # 交互式模式启动脚本 ⭐
├── start_trading.sh              # 直接运行模式启动脚本 ⭐
├── TradingBot.app/               # Mac应用包 ⭐⭐⭐
│   └── Contents/
│       ├── MacOS/
│       │   ├── TradingBot        # 主执行脚本
│       │   └── trading_env.sh    # 环境配置
│       ├── Resources/
│       │   └── ICON_README.md    # 图标说明
│       └── Info.plist            # 应用配置
├── src/
│   ├── interactive/
│   │   └── interactive_main.py   # 交互式主程序
│   └── trading_main.py           # 交易主程序
├── config/                       # 配置文件目录
│   ├── strategy_config.json      # 策略配置
│   └── api_keys.json             # API密钥配置
└── logs/                         # 日志目录
```

---

## 🔧 常见问题

### Q1: 双击.sh文件时提示"无法打开此文件"

**解决方案**:
```bash
# 在终端中设置可执行权限
chmod +x start_interactive.sh
chmod +x start_trading.sh
```

### Q2: 运行时报"command not found: python3"

**解决方案**:
- 确保已安装Python 3.12或更高版本
- 下载地址: https://www.python.org/downloads/

### Q3: 首次运行时提示"未找到虚拟环境"

**解决方案**:
- 这是正常的，脚本会自动创建虚拟环境
- 耐心等待安装完成

### Q4: 运行.app应用时提示"已损坏"

**解决方案**:
```bash
# 移除隔离属性
xattr -cr /Applications/TradingBot.app

# 或允许运行
sudo spctl --master-disable
```

### Q5: 如何停止正在运行的程序

**交互式模式**: 直接关闭终端或按 `Ctrl+C`

**后台运行**:
```bash
# 查找进程
ps aux | grep python

# 停止进程
pkill -f trading_main.py
```

### Q6: 如何查看运行日志

```bash
# 查看实时日志
tail -f logs/trading.log

# 查看最近100行
tail -n 100 logs/trading.log

# 查看错误日志
cat logs/trading.error.log
```

### Q7: 如何更新程序

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖（如果需要）
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 快速开始（3分钟上手）

### 第一次使用

1. **下载项目**
   ```bash
   git clone https://github.com/wanian2026/daihaoA.git
   cd daihaoA
   ```

2. **启动交互式模式**
   - 在Finder中双击 `start_interactive.sh`

3. **按向导配置**
   - 选择交易所: OKX（推荐新手）
   - 选择模式: 模拟交易
   - 输入API密钥
   - 选择交易对: BTC/USDT
   - 配置策略参数

4. **开始交易**

### 日常使用

1. **双击 `TradingBot.app` 应用**

2. **按提示操作**

3. **享受自动化交易**

---

## 💡 提示

- ✅ **推荐使用模拟交易**熟悉流程后再用真实资金
- ✅ **定期检查日志**确保程序正常运行
- ✅ **备份配置文件**方便恢复设置
- ✅ **使用强密码**保护API密钥安全
- ❌ **不要将API密钥上传到GitHub**
- ❌ **不要在多个终端同时运行**相同策略

---

## 📞 获取帮助

- 查看项目文档: `docs/`
- 查看GitHub仓库: https://github.com/wanian2026/daihaoA
- 查看错误日志: `logs/trading.log`

---

**祝你交易愉快！💰**
