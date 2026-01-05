# 加密货币自动化交易程序

支持币安（Binance）和欧易（OKX）平台的对冲网格策略自动化交易系统。

## 策略说明

这是一个基于对冲逻辑的趋势跟踪策略，核心机制如下：

### 策略逻辑

1. **初始化**：同时开一个多单和一个空单
2. **上涨触发**：当价格 ≥ 多单成本价 × (1 + 上涨阈值)
   - 平仓所有达到阈值的多单
   - 每个平仓的多单开1个新的多单
3. **下跌触发**：当价格 ≤ 空单成本价 × (1 - 下跌阈值)
   - 平仓所有达到阈值的空单
   - 每个平仓的空单开1个新的空单
4. **止损保护**：
   - 多单：价格 ≤ 成本价 × (1 - 止损比例)
   - 空单：价格 ≥ 成本价 × (1 + 止损比例)
5. **亏损仓位**：
   - 要么止损
   - 要么价格回到盈利状态并达到阈值
   - 否则一直持有

### 策略特点

- **对冲保护**：多空双向开单，降低单边风险
- **趋势跟随**：盈利时滚动开新仓位，捕捉趋势
- **止损保护**：防止亏损扩大
- **灵活配置**：支持自定义阈值、止损比例、仓位大小

## 系统架构

```
trading-system/
├── config/                    # 配置文件
│   ├── api_keys.json         # API密钥配置
│   └── strategy_config.json   # 策略参数配置
├── src/
│   ├── exchanges/            # 交易所适配器
│   │   ├── base_exchange.py  # 基础接口
│   │   ├── binance_exchange.py
│   │   ├── okx_exchange.py
│   │   └── exchange_factory.py
│   ├── strategy/             # 策略引擎
│   │   └── trading_engine.py
│   ├── storage/              # 数据持久化
│   │   ├── database/
│   │   │   ├── shared/model.py
│   │   │   ├── position_manager.py
│   │   │   ├── trade_log_manager.py
│   │   │   └── strategy_config_manager.py
│   │   └── db.py
│   └── trading_main.py       # 程序入口
├── requirements.txt
└── README.md
```

## 环境要求

- Python 3.12 或 3.13（不支持 3.14，尚未发布）
- 数据库：PostgreSQL（已集成）
- 依赖包：ccxt

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `ccxt`: 加密货币交易所API库
- `sqlalchemy`: ORM框架
- `pydantic`: 数据验证

### 2. 配置API密钥

编辑 `config/api_keys.json`，填入你的交易所API密钥：

```json
{
  "exchanges": {
    "binance": {
      "api_key": "YOUR_BINANCE_API_KEY",
      "secret": "YOUR_BINANCE_SECRET",
      "passphrase": null,
      "sandbox": false
    },
    "okx": {
      "api_key": "YOUR_OKX_API_KEY",
      "secret": "YOUR_OKX_SECRET",
      "passphrase": "YOUR_OKX_PASSPHRASE",
      "sandbox": false
    }
  }
}
```

**重要提示**：
- API密钥需要具有交易权限（现货或合约）
- 生产环境建议使用IP白名单
- 沙盒环境可用于测试（设置 `sandbox: true`）

### 3. 配置策略参数

编辑 `config/strategy_config.json`：

```json
{
  "strategy": {
    "exchange": "binance",
    "symbol": "BTC/USDT",
    "long_threshold": 0.02,
    "short_threshold": 0.02,
    "stop_loss_ratio": 0.05,
    "position_size": 100,
    "leverage": 1,
    "monitor_interval": 1
  }
}
```

**参数说明**：
- `exchange`: 交易所（binance/okx）
- `symbol`: 交易对（如 BTC/USDT）
- `long_threshold`: 上涨阈值（0.02 表示 2%）
- `short_threshold`: 下跌阈值（0.02 表示 2%）
- `stop_loss_ratio`: 止损比例（0.05 表示 5%）
- `position_size`: 仓位大小（USDT）
- `leverage`: 杠杆倍数（1表示无杠杆）
- `monitor_interval`: 价格监控间隔（秒）

### 4. 运行程序

```bash
cd src
python trading_main.py
```

程序会：
1. 连接到指定的交易所
2. 初始化策略（开多单和空单）
3. 开始监控价格并自动执行交易
4. 按 `Ctrl+C` 停止程序

## 数据库说明

程序使用PostgreSQL数据库存储以下数据：

### 表结构

1. **positions** - 仓位表
   - 存储所有持仓信息（多单/空单）
   - 记录开仓价格、当前价格、数量、状态等

2. **trade_logs** - 交易日志表
   - 记录所有交易操作
   - 包括开仓、平仓、止损等操作

3. **strategy_configs** - 策略配置表
   - 存储策略参数配置
   - 支持多策略配置

### 数据库连接

数据库配置已集成在系统中，无需手动配置。

## 安全建议

1. **API密钥安全**
   - 不要将API密钥提交到代码仓库
   - 定期更换API密钥
   - 使用API密钥权限最小化原则

2. **风险管理**
   - 建议先在沙盒环境测试
   - 设置合理的止损比例
   - 控制仓位大小，避免过度杠杆

3. **监控告警**
   - 定期查看交易日志
   - 监控账户余额
   - 设置异常告警

## 常见问题

### Q: 如何切换交易所？
A: 修改 `config/strategy_config.json` 中的 `exchange` 字段为 "binance" 或 "okx"。

### Q: 如何调整策略参数？
A: 编辑 `config/strategy_config.json`，调整 `long_threshold`、`short_threshold`、`stop_loss_ratio` 等参数。

### Q: 如何查看交易记录？
A: 交易记录存储在数据库的 `trade_logs` 表中，也可以查看 `trading.log` 文件。

### Q: 支持哪些交易对？
A: 支持币安和欧易的所有现货和合约交易对，如 BTC/USDT、ETH/USDT 等。

### Q: 如何停止策略？
A: 按 `Ctrl+C` 停止程序，程序会优雅退出，不会强制关闭未平仓订单。

## 技术支持

如有问题或建议，请提交 Issue 或 Pull Request。

## 免责声明

本程序仅供学习和研究使用，不构成投资建议。使用本程序进行交易的任何盈亏均由使用者自行承担。请在充分理解策略逻辑和风险的前提下谨慎使用。

## 许可证

MIT License
