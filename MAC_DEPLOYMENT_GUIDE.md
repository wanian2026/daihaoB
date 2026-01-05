# Mac 本地部署指南

## 前置要求

### 1. 安装必要软件

#### Python 3.12+
```bash
# 检查Python版本
python3 --version

# 如果没有安装，使用Homebrew安装
brew install python@3.12
```

#### PostgreSQL 数据库
```bash
# 使用Homebrew安装PostgreSQL
brew install postgresql@16

# 启动PostgreSQL服务
brew services start postgresql@16

# 创建数据库
createdb trading_db
```

#### Git
```bash
# Mac通常已预装Git，检查版本
git --version

# 如果没有安装
brew install git
```

### 2. 创建GitHub Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置token名称（如 "Trading Bot"）
4. 选择权限：勾选 `repo`（完整仓库访问权限）
5. 点击 "Generate token"
6. **重要**：复制并保存token（只会显示一次）

## 部署步骤

### 步骤1: 克隆代码仓库

```bash
# 创建项目目录
cd ~/Documents  # 或其他你喜欢的位置

# 克隆仓库（会提示输入用户名和token）
git clone https://github.com/wanian2026/daihaoA.git
cd daihaoA
```

**认证提示**：
- Username: 输入你的GitHub用户名
- Password: 粘贴刚才生成的Personal Access Token

### 步骤2: 创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境（应该显示 (venv)）
which python
```

### 步骤3: 安装Python依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

如果没有 `requirements.txt`，手动安装核心依赖：

```bash
pip install sqlalchemy psycopg2-binary ccxt rich questionary python-dotenv pydantic
```

### 步骤4: 配置环境变量

创建 `.env` 文件：

```bash
# 在项目根目录创建.env文件
touch .env
```

编辑 `.env` 文件，添加数据库连接信息：

```env
# PostgreSQL数据库连接
PGDATABASE_URL=postgresql://用户名:密码@localhost:5432/trading_db

# 或者如果使用系统用户
# PGDATABASE_URL=postgresql://@localhost:5432/trading_db
```

**获取PostgreSQL用户名和密码**：

```bash
# 查看PostgreSQL用户
psql postgres -c "\du"

# 创建新用户（可选）
psql postgres
CREATE USER trading_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;
\q
```

### 步骤5: 初始化数据库

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 设置Python路径
export PYTHONPATH=$(pwd)/src:$PYTHONPATH

# 初始化数据库
python scripts/init_db.py
```

如果提示重新初始化，使用：
```bash
python scripts/reinit_db.py
```

### 步骤6: 测试新功能

```bash
# 运行测试脚本
python scripts/test_new_features.py
```

预期输出：
```
============================================================
新功能测试
============================================================

=== 测试仓位模型新字段 ===
✓ 创建仓位成功，ID: 1
  - 杠杆倍数: 5x
  - 独立止损价格: $49000.0
  - 初始余额: $10000.0
✓ 更新独立止损成功: $48500.0
✓ 清理测试数据完成

=== 测试策略配置模型新字段 ===
✓ 创建固定仓位配置成功，ID: 1
✓ 创建比例仓位配置成功，ID: 2
✓ 清理测试数据完成

=== 测试交易成本计算 ===
✓ 固定仓位计算成功
✓ 比例仓位计算成功

============================================================
✓ 所有测试通过！
============================================================
```

### 步骤7: 启动交易系统

```bash
# 运行交互式交易系统
python src/interactive/interactive_main.py
```

## 常见问题解决

### 1. PostgreSQL连接失败

**问题**：`psycopg2.OperationalError: could not connect to server`

**解决方案**：
```bash
# 检查PostgreSQL是否运行
brew services list | grep postgresql

# 启动PostgreSQL
brew services start postgresql@16

# 检查端口
lsof -i :5432
```

### 2. Python依赖安装失败

**问题**：某些包安装失败

**解决方案**：
```bash
# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 单独安装问题包
pip install ccxt --no-cache-dir
```

### 3. 权限错误

**问题**：Permission denied

**解决方案**：
```bash
# 修复Python环境权限
chmod +x venv/bin/activate

# 或使用sudo（不推荐）
sudo chown -R $USER:$(id -gn $USER) ~/.pyenv
```

### 4. 数据库表不存在

**问题**：`UndefinedColumn: column does not exist`

**解决方案**：
```bash
# 重新初始化数据库
python scripts/reinit_db.py
```

### 5. Git认证失败

**问题**：`could not read Username`

**解决方案**：

**方法1：使用Personal Access Token**
```bash
git clone https://your_token@github.com/wanian2026/daihaoA.git
```

**方法2：配置SSH密钥**
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到GitHub：Settings → SSH and GPG keys → New SSH key

# 克隆仓库
git clone git@github.com:wanian2026/daihaoA.git
```

## 项目目录结构

```
daihaoA/
├── src/                          # 源代码目录
│   ├── exchanges/               # 交易所接口
│   ├── interactive/             # 交互式界面
│   ├── storage/                 # 数据库存储
│   ├── strategy/                # 交易策略
│   └── utils/                   # 工具函数
├── scripts/                     # 脚本文件
│   ├── init_db.py              # 数据库初始化
│   ├── reinit_db.py            # 数据库重新初始化
│   └── test_new_features.py    # 功能测试
├── requirements.txt             # Python依赖列表
├── .env                         # 环境变量配置（需手动创建）
└── README.md                    # 项目说明
```

## 配置交易所API

### 币安 (Binance)

1. 访问 https://www.binance.com/zh-CN/my/settings/api-management
2. 创建API Key
3. 需要的权限：
   - 现货交易
   - 合约交易
4. 将API Key和Secret保存到安全位置

### 欧易 (OKX)

1. 访问 https://www.okx.com/account/my-api
2. 创建API Key
3. 需要的权限：
   - 读取
   - 交易
4. 会生成 API Key、Secret、Passphrase，全部保存

### 测试连接

首次启动程序时，按照提示输入API凭证，系统会自动测试连接。

## 安全建议

1. **永远不要**将 `.env` 文件提交到Git
2. **不要**在代码中硬编码API密钥
3. 定期轮换API密钥
4. 限制API权限，只给必要的权限
5. 在生产环境使用沙盒环境测试

## 更新代码

当GitHub仓库有更新时：

```bash
# 拉取最新代码
git pull origin main

# 重新安装依赖（如有变化）
pip install -r requirements.txt

# 重新初始化数据库（如有表结构变化）
python scripts/reinit_db.py
```

## 下一步

1. 完成上述部署步骤
2. 运行测试脚本验证功能
3. 在沙盒环境测试交易策略
4. 配置真实的API密钥（建议先测试）
5. 根据ATR分析调整策略参数

## 需要帮助？

如果遇到问题：
1. 查看错误日志
2. 运行测试脚本排查
3. 检查PostgreSQL服务状态
4. 验证Python环境配置

祝部署顺利！🚀
