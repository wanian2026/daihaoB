# WebSocket 功能说明

## 问题描述

启动服务时看到以下警告和错误：

```
WARNING:  No supported WebSocket library detected. Please use "pip install 'uvicorn[standard]', or install 'websockets' or 'wsproto' manually.
INFO:     127.0.0.1:56396 - "GET /ws/monitoring HTTP/1.1" 404 Not Found
```

## 原因分析

1. **缺少WebSocket库**：本地虚拟环境未安装 `websockets` 或 `wsproto` 库
2. **前端尝试连接WebSocket**：前端代码尝试连接 `/ws/monitoring` 进行实时监测
3. **服务端支持WebSocket**：代码中已定义了WebSocket路由 `src/web/api.py:353`

## 解决方案

### 方法1：重新安装所有依赖（推荐）

```bash
# 在项目根目录下
pip install -r requirements.txt
```

### 方法2：单独安装WebSocket库

```bash
# 方案A：安装uvicorn标准版（包含WebSocket支持）
pip install 'uvicorn[standard]'

# 方案B：单独安装websockets库
pip install websockets

# 方案C：安装wsproto库
pip install wsproto
```

### 方法3：更新虚拟环境

如果您使用的是旧的虚拟环境：

```bash
# 删除旧的虚拟环境
deactivate
rm -rf venv

# 创建新的虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 验证安装

安装完成后，检查WebSocket库是否已安装：

```bash
pip list | grep websocket
```

应该看到类似输出：

```
websockets    15.0.1
```

## WebSocket功能说明

### 路由
- **WebSocket路由**: `/ws/monitoring`
- **功能**: 实时推送监测合约的信号更新

### API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/ws/monitoring` | WebSocket | 实时监测信号推送 |
| `/api/monitoring/add` | POST | 添加监测合约 |
| `/api/monitoring/remove` | POST | 移除监测合约 |
| `/api/monitoring/list` | GET | 获取监测列表 |
| `/api/monitoring/signals` | GET | 获取最新信号 |

### WebSocket消息格式

**服务器推送消息**:
```json
{
  "type": "signal",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "data": {
    "has_signal": true,
    "direction": "long",
    "entry_price": 95000.0,
    "take_profit": 96500.0,
    "take_profit_reason": "流动性密集区（订单量:1000, 距离:1.58%, 得分:0.93）",
    "stop_loss": 94500.0,
    "confidence": 75.5
  }
}
```

## 完整启动流程

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 确保依赖已安装
pip install -r requirements.txt

# 3. 启动服务
USE_MOCK_EXCHANGE=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

启动成功后，应该看到：

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
启动监测管理器...
监测管理器已启动，扫描间隔: 30秒
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080
```

而不再是WebSocket警告。

## 故障排除

### 问题1：仍然出现WebSocket警告

```bash
# 检查已安装的库
pip list | grep -E 'uvicorn|websocket'

# 如果缺少，强制重新安装
pip install --upgrade uvicorn[standard] websockets
```

### 问题2：WebSocket连接失败

1. 检查防火墙设置
2. 确认端口8080未被占用
3. 查看浏览器控制台错误信息

### 问题3：实时监测无信号推送

- 检查是否已添加监测合约
- 查看后端日志是否有信号生成
- 确认WebSocket连接状态（前端状态指示器）

## 依赖清单

WebSocket功能依赖的核心库：

- `websockets` - WebSocket协议实现
- `uvicorn` - ASGI服务器（支持WebSocket）
- `fastapi` - Web框架（支持WebSocket路由）

这些库已在 `requirements.txt` 中声明，确保完整安装即可。
