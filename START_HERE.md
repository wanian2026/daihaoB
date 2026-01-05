# 🚀 快速启动卡片

## ⚡ 3秒启动

### 交互式界面（推荐新手）
```bash
bash start_interactive.sh
```

### Web界面（推荐进阶）
```bash
bash start_web.sh
# 然后打开: http://localhost:8000
```

---

## 📋 完整步骤

```bash
# 1. 创建虚拟环境（首次运行）
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖（首次运行）
pip install -r requirements.txt

# 4. 初始化数据库（首次运行）
python scripts/init_db.py

# 5. 启动程序（选择其中一种）
bash start_interactive.sh  # 交互式界面
# 或
bash start_web.sh          # Web界面
```

---

## 🔑 获取API密钥

### 币安测试网（推荐）
- 地址：https://testnet.binancefuture.com/
- 注册账号 → API管理 → 创建API密钥

### 欧易模拟交易
- 地址：https://www.okx.com/demo/trade-balance
- 模拟交易 → API管理 → 创建API密钥

---

## ⚙️ 配置文件

- API密钥：`config/api_keys.json`
- 策略配置：`config/strategy_config.json`

---

## 📖 详细文档

- [完整启动指南](docs/mac_startup_guide.md)
- [交互式界面说明](INTERACTIVE_README.md)
- [Web界面说明](WEB_INTERFACE.md)

---

## 🆘 常见问题

### Python版本不够？
```bash
brew install python@3.12
```

### 依赖安装失败？
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### 端口被占用？
```bash
PORT=8001 bash start_web.sh
```

---

## ⚠️ 安全提示

- ✅ 优先使用测试网/模拟交易
- ✅ API密钥开启"只读"权限
- ✅ 不要泄露API密钥
- ✅ 测试稳定后再用实盘

---

祝你交易顺利！🎯
