# 🔧 依赖安装问题修复指南

## 问题描述

在使用 Python 3.14 安装依赖时，遇到 `coincurve` 包安装失败：

```
RuntimeError: Expected exactly one LICENSE file in cffi distribution, got 0
```

---

## ✅ 快速解决方案

### 方案一：使用修复脚本（推荐）⭐⭐⭐

```bash
# 运行修复脚本
bash fix_dependencies.sh
```

这个脚本会自动：
1. 检测 Python 版本
2. 清理旧依赖
3. 安装核心依赖（已移除有问题的包）

---

### 方案二：手动重新安装依赖

```bash
# 1. 进入项目目录
cd ~/daihaoA

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 升级pip
pip install --upgrade pip

# 4. 清理旧依赖
pip freeze | xargs pip uninstall -y

# 5. 重新安装依赖
pip install -r requirements.txt
```

---

### 方案三：降级 Python 版本（最稳定）⭐⭐⭐

如果你使用的是 Python 3.14，建议降级到 Python 3.12 或 3.13：

```bash
# 1. 使用 Homebrew 安装 Python 3.12
brew install python@3.12

# 2. 创建新的虚拟环境
python3.12 -m venv .venv

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

---

## 📋 详细步骤

### 步骤1：检查Python版本

```bash
python3 --version
```

- ✅ Python 3.12 或 3.13：可以直接使用
- ⚠️ Python 3.14：存在兼容性问题，建议降级或使用方案一

### 步骤2：运行修复脚本

```bash
# 进入项目目录
cd ~/daihaoA

# 运行修复脚本
bash fix_dependencies.sh
```

### 步骤3：验证安装

```bash
# 激活虚拟环境
source .venv/bin/activate

# 检查关键包
python3 -c "import ccxt, fastapi, uvicorn, sqlalchemy, pandas"
```

如果没有错误，说明安装成功！

### 步骤4：启动程序

```bash
# 交互式界面
bash start_interactive.sh

# 或Web界面
bash start_web.sh
```

---

## 🔍 问题原因

`coincurve` 是一个用于加密操作的优化库，主要功能：
- ECDSA 签名优化
- 加密操作加速

**问题**：在 Python 3.14 上，`coincurve` 的构建系统存在兼容性问题。

**解决方案**：
- `coincurve` 是 **可选依赖**，不是必需的
- 移除后不影响核心功能
- 仍然可以正常使用 ccxt 进行交易

---

## ✨ 精简后的依赖

我们已将 `requirements.txt` 精简为仅包含核心依赖：

| 类别 | 依赖包 | 用途 |
|------|--------|------|
| 交易所API | ccxt | 连接币安、欧易等交易所 |
| Web框架 | fastapi, uvicorn | Web管理界面 |
| 数据库 | sqlalchemy, psycopg2-binary | 数据存储 |
| 数据处理 | pandas, numpy | 数据分析 |
| 交互界面 | questionary, rich | 命令行界面 |
| HTTP请求 | requests, httpx, aiohttp | API调用 |
| 任务调度 | APScheduler | 定时任务 |
| 数据验证 | pydantic | 数据验证 |

**移除的依赖**：
- ❌ coincurve（Python 3.14兼容性问题）
- ❌ 所有 langchain 相关包（不需要AI功能）
- ❌ 所有 opencv 相关（不需要图像处理）
- ❌ 所有 s3 相关（不需要对象存储）
- ❌ 测试工具（pytest, coverage等）
- ❌ 开发工具（pylint, isort等）

---

## 🚀 常见问题

### Q1: 修复脚本运行失败

```bash
# 检查Python版本
python3 --version

# 如果是Python 3.14，建议降级
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Q2: 提示权限错误

```bash
# 使用--user参数
pip install --user -r requirements.txt
```

### Q3: 网络连接失败

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 虚拟环境创建失败

```bash
# 删除旧的虚拟环境
rm -rf .venv

# 重新创建
python3 -m venv .venv
```

---

## ✅ 验证清单

安装完成后，请确认：

- [ ] Python 版本为 3.12 或 3.13
- [ ] 虚拟环境已激活
- [ ] 核心依赖已安装（ccxt, fastapi等）
- [ ] 运行 `python3 -c "import ccxt, fastapi"` 无错误
- [ ] 可以启动交互式界面或Web界面

---

## 📞 获取帮助

如果问题仍然存在，请：

1. 检查 Python 版本：`python3 --version`
2. 查看详细错误日志
3. 尝试使用国内镜像源
4. 考虑降级到 Python 3.12

---

## 🎯 推荐方案

**对于Mac用户**：

1. ✅ 使用 Python 3.12（通过 Homebrew 安装）
2. ✅ 运行修复脚本：`bash fix_dependencies.sh`
3. ✅ 启动程序：`bash start_interactive.sh` 或 `bash start_web.sh`

**这是最稳定可靠的方案！** 🚀
