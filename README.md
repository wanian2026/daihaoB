# 合约信号扫描系统

基于 FVG（Fair Value Gap）和流动性分析的智能合约交易信号系统。

## 功能特性

- ✅ 支持币安和欧易交易所
- ✅ 自动扫描所有合约
- ✅ 基于 FVG 算法识别交易机会
- ✅ 流动性分析（订单簿深度）
- ✅ 智能止盈止损计算
- ✅ 按信心度排序显示
- ✅ 手动刷新功能
- ✅ Web 界面实时展示

## 技术栈

- Python 3.12+
- FastAPI (Web框架)
- CCXT (交易所API)
- Tailwind CSS (前端样式)
- Alpine.js (前端交互)

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 配置 API 密钥

访问 Web 界面：`http://localhost:8000`

在"API配置"区域填写：
- 选择交易所（欧易/币安）
- 选择交易模式（模拟/真实）
- 填写 API Key、Secret（OKX还需填写Password）

### 2. 获取 API 密钥

#### 欧易 (OKX)
1. 访问 https://www.okx.com
2. 登录后进入"模拟交易"模式
3. 点击右上角头像 → API管理
4. 创建新 API，勾选"读取"和"交易"权限
5. 保存 API Key、Secret、Password

#### 币安 (Binance)
1. 访问 https://www.binance.com
2. 进入期货测试网：https://testnet.binancefuture.com
3. API管理 → 创建API
4. 保存 API Key、Secret

### 3. 开始扫描

1. 点击"测试连接"验证API配置
2. 选择扫描数量（20/50/100个合约）
3. 点击"开始扫描"
4. 等待扫描完成，查看交易信号
5. 点击"刷新"重新扫描

### 4. 查看信号

信号列表包含：
- 交易对名称
- 交易方向（做多/做空）
- 入场价、止盈价、止损价
- 信心度评分
- 盈亏比
- FVG详细信息
- 流动性分析

## 启动服务

```bash
# 设置 Python 路径
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 启动 Web 服务
python -m uvicorn src.web.api:app --host 0.0.0.0 --port 8000 --reload
```

## 项目结构

```
workspace/projects/
├── src/
│   ├── exchanges/      # 交易所连接模块
│   ├── analysis/       # 分析模块（FVG、流动性）
│   ├── scanner/        # 扫描器
│   └── web/           # Web API
├── web/
│   └── index.html     # 前端界面
├── config/
│   └── api_keys.json  # API配置
└── requirements.txt   # 依赖包
```

## 信号说明

### FVG (Fair Value Gap)

FVG 是价格行为分析中的价格缺口，表示市场中未填补的价格区域。

- **牛市 FVG**：价格快速上涨，留下下方价格缺口
- **熊市 FVG**：价格快速下跌，留下上方价格缺口

### 信心度评分

综合以下因素计算：
- FVG 大小和强度 (40%)
- 流动性评分 (30%)
- 市场波动率 (15%)
- 买卖不平衡 (15%)

### 风险提示

- 本系统仅供学习和研究使用
- 实盘交易风险自负
- 建议先在模拟环境测试
- 请设置合理的止损

## License

MIT
