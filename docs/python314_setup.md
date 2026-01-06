# Python 3.14 依赖安装指南

## 问题描述

在 Python 3.14 环境下安装依赖时遇到以下错误：

```
RuntimeError: Expected exactly one LICENSE file in cffi distribution, got 0
```

**原因**：`coincurve==21.0.0` 包与 Python 3.14 不兼容。

## 解决方案

### 方案1：使用更新后的 requirements.txt（推荐）

项目已更新 `requirements.txt`，移除了 `coincurve` 依赖：

```bash
# 卸载旧依赖（如果有）
pip uninstall coincurve -y

# 重新安装依赖
pip install -r requirements.txt
```

### 方案2：单独安装核心依赖

如果完整安装仍有问题，可以使用核心依赖文件：

```bash
pip install -r requirements-core.txt
```

### 方案3：使用 Python 3.12 或 3.13

如果遇到其他兼容性问题，建议使用更稳定的 Python 版本：

```bash
# 安装 pyenv（如果没有）
brew install pyenv

# 安装 Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# 重新创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## coincurve 依赖说明

### 为什么移除 coincurve？

- **项目不需要**：`coincurve` 主要用于加密货币交易的密码学签名
- **本项目特点**：仅使用公开API获取市场数据，无需交易签名功能
- **兼容性**：Python 3.14 对某些C扩展库有兼容性问题

### 功能影响

移除 `coincurve` 后：
- ✅ **正常功能**：获取K线数据、订单簿、行情等
- ✅ **正常功能**：FVG分析、流动性分析、信号生成
- ✅ **正常功能**：Web界面、API接口
- ❌ **不可用**：私有API交易（本项目不需要）

## 完整安装流程

### 1. 检查Python版本

```bash
python3 --version
# 推荐：3.12 或 3.13
# 也可以：3.14（使用更新后的 requirements.txt）
```

### 2. 创建/激活虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 升级pip

```bash
pip install --upgrade pip
```

### 4. 安装依赖

```bash
# 方式1：完整安装（推荐）
pip install -r requirements.txt

# 方式2：核心依赖安装
pip install -r requirements-core.txt
```

### 5. 验证安装

```bash
# 检查关键库
pip list | grep -E 'fastapi|uvicorn|ccxt|websockets'

# 测试导入
python3 -c "import fastapi; import ccxt; import websockets; print('✅ 依赖安装成功')"
```

### 6. 启动服务

```bash
USE_MOCK_EXCHANGE=false python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

## 常见问题

### Q1: 安装其他包时出错

**症状**：安装过程中某个包失败

**解决**：
```bash
# 跳过失败的包，继续安装其他包
pip install -r requirements.txt --no-deps

# 或逐个安装关键依赖
pip install fastapi uvicorn ccxt pandas numpy websockets
```

### Q2: coincurve 是必需的吗？

**答案**：不是。

- 本项目使用公开API（无需签名）
- coincurve 主要用于私有API交易
- 移除后所有核心功能正常

### Q3: 如何确认项目正常工作？

**检查清单**：
- [ ] 服务启动成功（无错误）
- [ ] 访问 http://127.0.0.1:8080 正常
- [ ] 测试交易所连接成功
- [ ] 扫描合约功能正常
- [ ] WebSocket连接正常

## 依赖清单

### 核心依赖

| 包名 | 用途 | 是否必需 |
|------|------|---------|
| fastapi | Web框架 | ✅ 必需 |
| uvicorn | ASGI服务器 | ✅ 必需 |
| ccxt | 交易所API | ✅ 必需 |
| pandas | 数据处理 | ✅ 必需 |
| numpy | 数值计算 | ✅ 必需 |
| websockets | WebSocket支持 | ✅ 必需 |

### 可选依赖

| 包名 | 用途 | 说明 |
|------|------|------|
| APScheduler | 任务调度 | 用于定时扫描 |
| httpx | HTTP客户端 | ccxt备用 |
| requests | HTTP客户端 | ccxt备用 |

## 推荐配置

### Python版本
- ✅ **推荐**：Python 3.12.x（最稳定）
- ✅ **可用**：Python 3.13.x
- ⚠️ **实验性**：Python 3.14.x（使用更新后的requirements.txt）

### 虚拟环境
- venv（Python内置）
- conda（可选）

### 包管理
- pip（推荐）
- Poetry（可选）
- conda（可选）

## 故障排除

### 问题：pip install 持续失败

```bash
# 清理pip缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 问题：ccxt 导入失败

```bash
# 重新安装ccxt
pip uninstall ccxt -y
pip install ccxt==4.5.30
```

### 问题：WebSocket连接失败

```bash
# 检查websockets安装
pip list | grep websocket

# 重新安装
pip install --upgrade websockets
```

## 更新日志

### 2025-01-06
- ✅ 移除 `coincurve==21.0.0`（Python 3.14不兼容）
- ✅ 更新 `requirements.txt` 以支持 Python 3.14
- ✅ 创建 `requirements-core.txt`（核心依赖）
- ✅ 添加 Python 3.14 安装指南

## 支持

如遇问题，请检查：
1. Python版本是否合适
2. 虚拟环境是否正确激活
3. pip是否为最新版本
4. 是否有网络或代理问题

更多技术细节，请参考：
- [Python 3.14 发行说明](https://docs.python.org/3.14/whatsnew/3.14.html)
- [ccxt 文档](https://docs.ccxt.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
