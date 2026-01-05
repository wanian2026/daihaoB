# Mac 启动指南

## 🚀 快速启动（3种方式）

### 方式一：交互式界面（推荐新手）⭐⭐⭐

适合：首次使用、需要每次配置的交易场景

```bash
# 方法1：双击启动（最简单）
open start_interactive.sh

# 方法2：终端运行
bash start_interactive.sh
```

**特点**：
- ✅ 完全交互式操作
- ✅ 实时行情显示
- ✅ ATR分析和参数建议
- ✅ 实时监控持仓

---

### 方式二：Web管理界面（推荐进阶用户）⭐⭐⭐

适合：需要可视化界面、远程管理、长期运行

```bash
# 启动Web服务器
bash start_web.sh

# 或指定端口（如8001）
PORT=8001 bash start_web.sh
```

**访问地址**：http://localhost:8000

**特点**：
- ✅ 极简风格界面
- ✅ 实时监控Dashboard
- ✅ 策略配置
- ✅ 持仓管理
- ✅ 交易历史
- ✅ WebSocket实时推送

---

### 方式三：命令行直接运行（适合高级用户）

适合：自动化脚本、自定义参数

```bash
# 交互式模式
cd src
python interactive/interactive_main.py

# 交易模式（需要先配置好策略）
cd src
python trading_main.py
```

---

## 📋 完整启动流程

### 第一步：准备Python环境

```bash
# 1. 检查Python版本（需要3.12+）
python3 --version

# 2. 如果没有安装，使用Homebrew安装
brew install python@3.12

# 3. 创建虚拟环境（脚本会自动创建，也可手动创建）
python3 -m venv .venv

# 4. 激活虚拟环境
source .venv/bin/activate

# 5. 安装依赖（脚本会自动安装，也可手动安装）
pip install -r requirements.txt
```

---

### 第二步：初始化数据库

```bash
# 进入项目目录
cd ~/daihaoA

# 激活虚拟环境
source .venv/bin/activate

# 初始化数据库（创建表结构）
python scripts/init_db.py
```

**数据库位置**：默认使用SQLite，文件为 `trading.db`

---

### 第三步：配置API密钥

#### 选项A：使用交互式界面配置（推荐）

运行交互式界面时，会提示你输入API密钥：

```bash
bash start_interactive.sh
```

按照提示选择交易所和输入API密钥。

#### 选项B：手动配置文件

编辑配置文件：

```bash
# 编辑API密钥配置
vim config/api_keys.json
```

配置模板：

```json
{
  "binance": {
    "api_key": "your_binance_api_key",
    "secret": "your_binance_secret",
    "testnet": true
  },
  "okx": {
    "api_key": "your_okx_api_key",
    "secret": "your_okx_secret",
    "password": "your_okx_password",
    "testnet": true
  }
}
```

#### 获取API密钥指南：

**币安（Binance）**：
- 测试网：https://testnet.binancefuture.com/
- 正式网：https://www.binance.com/en/my/settings/api-management

**欧易（OKX）**：
- 模拟交易：https://www.okx.com/demo/trade-balance
- 正式网：https://www.okx.com/account/my-api

⚠️ **安全提示**：
- API密钥要开启"只读"权限（模拟交易时）
- 不要泄露API密钥
- 使用模拟账户测试，确保策略稳定后再用实盘

---

### 第四步：选择启动方式

根据你的需求选择：

#### 场景1：第一次测试交易
```bash
# 推荐使用交互式界面
bash start_interactive.sh
```

#### 场景2：需要长期运行和监控
```bash
# 启动Web界面
bash start_web.sh
# 然后在浏览器打开 http://localhost:8000
```

#### 场景3：需要自定义参数运行
```bash
# 直接运行脚本
source .venv/bin/activate
cd src
python trading_main.py
```

---

## 🎯 使用示例

### 示例1：交互式界面使用流程

```bash
# 1. 启动交互式界面
bash start_interactive.sh

# 2. 按照提示操作：
#    → 选择交易所（币安/欧易）
#    → 输入API密钥
#    → 查看实时行情
#    → 选择交易对（如BTC/USDT）
#    → 等待ATR分析
#    → 确认或修改策略参数
#    → 开始交易

# 3. 实时监控持仓和盈亏
#    → 查看持仓列表
#    → 查看交易日志
#    → 手动平仓（如需要）
```

### 示例2：Web界面使用流程

```bash
# 1. 启动Web服务器
bash start_web.sh

# 2. 在浏览器打开：http://localhost:8000

# 3. 使用Web界面操作：
#    → Dashboard：查看实时状态
#    → 策略配置：设置交易参数
#    → 交易控制：开始/停止/暂停交易
#    → 持仓监控：查看当前持仓
#    → 交易历史：查看历史记录
```

---

## 🔧 常见问题

### Q1: Python版本不满足要求

```bash
# 检查版本
python3 --version

# 如果低于3.12，安装新版本
brew install python@3.12
```

### Q2: 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --no-cache-dir
```

### Q3: 数据库初始化失败

```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 重新初始化
python scripts/init_db.py
```

### Q4: API连接失败

- 检查API密钥是否正确
- 确认使用的是测试网/模拟交易
- 检查网络连接
- 查看错误日志

### Q5: 脚本无法双击运行

```bash
# 给脚本添加执行权限
chmod +x start_interactive.sh
chmod +x start_web.sh

# 再次尝试双击或使用
bash start_interactive.sh
```

### Q6: Web界面无法访问

```bash
# 检查端口是否被占用
lsof -i :8000

# 使用其他端口
PORT=8001 bash start_web.sh
```

---

## 📚 进一步阅读

- [交互式界面使用指南](INTERACTIVE_README.md)
- [Web界面使用指南](WEB_INTERFACE.md)
- [币安测试网指南](docs/binance_testnet_guide.md)
- [Mac快速启动指南](docs/mac_launch_guide.md)

---

## ✅ 启动检查清单

在启动前，请确认：

- [ ] Python 3.12+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包已安装
- [ ] 数据库已初始化
- [ ] API密钥已获取并配置
- [ ] 首次使用：选择测试网/模拟交易

祝你交易顺利！🚀
