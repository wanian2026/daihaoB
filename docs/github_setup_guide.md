# GitHub 设置指南

本指南将帮助你将加密货币交易系统项目推送到GitHub。

## 📋 前置准备

### 1. GitHub账号
- 如果还没有GitHub账号，请访问 [https://github.com/](https://github.com/) 注册
- 记住你的GitHub用户名（例如：wanian2026）

### 2. Git工具
- 确保你的系统已安装Git
- 检查Git版本：`git --version`

## 🔐 GitHub认证设置（重要）

### 方式一：使用SSH密钥（推荐）

#### 1. 检查是否已有SSH密钥
```bash
ls ~/.ssh
```

如果看到 `id_rsa.pub` 或 `id_ed25519.pub`，说明已有SSH密钥。

#### 2. 生成新的SSH密钥（如果没有）
```bash
ssh-keygen -t ed25519 -C "你的邮箱@example.com"
```
- 按Enter使用默认路径
- 可选择设置密码，或直接按Enter跳过

#### 3. 查看并复制SSH公钥
```bash
cat ~/.ssh/id_ed25519.pub
```
复制输出的整个内容（从 ssh-ed25519 开头到结尾）

#### 4. 添加SSH密钥到GitHub
1. 登录 GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单选择 "SSH and GPG keys"
4. 点击 "New SSH key"
5. Title: 输入一个描述（如：MacBook Pro）
6. Key: 粘刚才复制的SSH公钥
7. 点击 "Add SSH key"

#### 5. 测试SSH连接
```bash
ssh -T git@github.com
```
看到 `Hi wanian2026! You've successfully authenticated...` 表示成功

#### 6. 更改远程仓库URL为SSH
```bash
# 当前项目已连接的仓库
git remote -v

# 如果显示的是 https://github.com/...，改为SSH
git remote set-url origin git@github.com:wanian2026/daihaoA.git

# 验证更改
git remote -v
```

### 方式二：使用Personal Access Token

#### 1. 生成Personal Access Token
1. 登录 GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单最底部选择 "Developer settings"
4. 选择 "Personal access tokens" → "Tokens (classic)"
5. 点击 "Generate new token (classic)"
6. 设置过期时间（建议选择30天或90天）
7. 勾选所需权限：
   - ✅ repo（完整的仓库访问权限）
   - ✅ workflow（如果需要使用GitHub Actions）
8. 点击 "Generate token"
9. **重要：** 复制token（只显示一次）

#### 2. 推送时使用Token
```bash
git push origin main
```
当提示输入用户名时，输入你的GitHub用户名  
当提示输入密码时，粘贴刚才生成的token（不是GitHub密码）

## 📤 推送代码到GitHub

### 1. 检查当前Git状态
```bash
git status
```

### 2. 添加所有更改
```bash
git add .
```

### 3. 提交更改
```bash
git commit -m "你的提交信息"
```

### 4. 推送到GitHub
```bash
# 如果使用SSH认证（推荐）
git push origin main

# 如果使用HTTPS认证，会提示输入用户名和token
```

## 🔧 日常工作流程

### 修改代码后提交推送
```bash
# 1. 查看修改
git status

# 2. 添加修改的文件
git add <文件名>          # 添加特定文件
git add .                # 添加所有修改

# 3. 提交
git commit -m "描述你的修改"

# 4. 推送
git push origin main
```

### 拉取最新代码
```bash
git pull origin main
```

### 查看提交历史
```bash
git log --oneline
```

## 🚨 安全注意事项

### ⚠️ 绝对不要推送到GitHub的文件
项目已配置 `.gitignore` 文件，以下内容会被自动排除：
- API密钥配置文件（`config/api_keys.json`）
- 环境变量文件（`.env`）
- Python缓存文件（`__pycache__/`）
- 虚拟环境（`.venv/`）
- 临时文件和日志

### ✅ 验证.gitignore配置
```bash
# 检查哪些文件被忽略
git check-ignore -v config/api_keys.json

# 查看被忽略的文件列表
git ls-files --others --ignored --exclude-standard
```

### 🔒 敏感信息处理
如果意外推送了敏感信息：
1. 立即在GitHub上删除敏感文件
2. 在本地使用 `git filter-branch` 或 `BFG Repo-Cleaner` 清除历史记录
3. 撤销API密钥并重新生成

## 📝 项目当前的Git状态

### 当前远程仓库
```
origin: https://github.com/wanian2026/daihaoA.git
```

### 最新提交
```
commit 4e6a848
Author: 更新.gitignore，排除敏感文件和临时文件
```

## 🎯 下一步操作

### 推送最新代码
```bash
# 1. 确保所有更改已提交
git status

# 2. 如果有未提交的更改，先提交
git add .
git commit -m "你的提交信息"

# 3. 推送到GitHub
git push origin main
```

### 验证GitHub仓库
访问你的GitHub仓库：
```
https://github.com/wanian2026/daihaoA
```

确认：
- ✅ 代码已成功推送
- ✅ 没有 `config/api_keys.json` 等敏感文件
- ✅ 代码结构完整

## 🆘 常见问题

### 1. 推送时出现 "fatal: could not read Username"
**原因：** 使用HTTPS认证但没有正确的凭证  
**解决：** 使用SSH认证（推荐）或生成Personal Access Token

### 2. 提示 "Updates were rejected because the tip of your current branch is behind"
**原因：** 远程仓库有新的提交  
**解决：** 
```bash
git pull origin main
# 或强制推送（谨慎使用）
git push origin main --force
```

### 3. 想撤销最后一次提交
```bash
# 撤销提交但保留更改
git reset --soft HEAD~1

# 撤销提交和更改
git reset --hard HEAD~1
```

## 📚 更多资源

- [GitHub官方文档](https://docs.github.com/)
- [Pro Git book](https://git-scm.com/book/zh/v2)
- [GitHub SSH密钥设置](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)

## ✅ 检查清单

在推送到GitHub之前，确保：

- [ ] 已设置GitHub认证（SSH或Token）
- [ ] .gitignore 文件已配置正确
- [ ] 敏感文件（API密钥）没有被添加
- [ ] 提交信息清晰描述了更改内容
- [ ] 代码可以在本地正常运行

完成后，你的项目就成功托管在GitHub上了！
