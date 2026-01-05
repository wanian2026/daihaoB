# 🚀 Mac 快速启动指南

## ⚡ 3秒快速启动

### 最简单的方式：双击应用
1. 在Finder中双击 **TradingBot.app**
2. 按提示操作
3. 开始交易！

---

## 📖 四种启动方式

### 1️⃣ 双击 `.app` 应用（推荐⭐⭐⭐）
```
TradingBot.app
```
- ✅ 像普通Mac应用一样使用
- ✅ 支持Spotlight搜索
- ✅ 可固定到Dock栏

**安装**:
```bash
cp -R TradingBot.app /Applications/
```

---

### 2️⃣ 双击 Shell 脚本（推荐新手⭐⭐）
```
start_interactive.sh    # 交互式配置模式
start_trading.sh        # 直接运行模式
```

**使用**: 直接在Finder中双击文件

**首次运行需要设置权限**:
```bash
chmod +x start_interactive.sh start_trading.sh
```

---

### 3️⃣ 终端命令（适合高级用户）
```bash
# 交互式模式
python src/interactive/interactive_main.py

# 直接运行模式
python src/trading_main.py

# 后台运行
nohup python src/trading_main.py >> logs/trading.log 2>&1 &
```

---

### 4️⃣ 开机自启动（可选）
```bash
# 运行安装脚本
./install_launch_agent.sh

# 查看状态
launchctl list | grep tradingbot

# 停止服务
launchctl stop com.tradingbot
```

---

## 🎯 推荐使用场景

| 你的需求 | 推荐方式 |
|---------|---------|
| **第一次使用** | 双击 `start_interactive.sh` |
| **日常交易** | 双击 `TradingBot.app` |
| **固定策略** | 双击 `start_trading.sh` |
| **后台运行** | `nohup` 命令 |
| **开机自启** | LaunchAgents |

---

## 🔧 快速设置

### 设置Shell脚本权限（只需一次）
```bash
chmod +x start_interactive.sh start_trading.sh install_launch_agent.sh
```

### 安装.app应用到应用程序（只需一次）
```bash
cp -R TradingBot.app /Applications/
```

---

## 📝 详细文档

- **完整指南**: `docs/mac_launch_guide.md`
- **GitHub设置**: `docs/github_setup_guide.md`
- **图标自定义**: `TradingBot.app/Contents/Resources/ICON_README.md`

---

## ❓ 常见问题

**Q: 双击文件没反应？**
```bash
# 设置可执行权限
chmod +x start_interactive.sh
```

**Q: 提示"已损坏"？**
```bash
# 移除隔离属性
xattr -cr TradingBot.app
```

**Q: 如何停止程序？**
- 交互式: 直接关闭终端
- 后台运行: `pkill -f trading_main.py`
- LaunchAgents: `launchctl stop com.tradingbot`

**Q: 查看运行日志？**
```bash
tail -f logs/trading.log
```

---

## 💡 提示

- ✅ 首次使用建议选择**模拟交易**
- ✅ 确保已正确配置API密钥
- ✅ 定期查看日志确保正常运行
- ❌ 不要在多个终端同时运行相同策略

---

**开始交易吧！💰**
