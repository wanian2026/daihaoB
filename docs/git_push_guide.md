# Git 推送认证配置指南

由于遇到了GitHub认证问题，你需要配置Git凭证才能推送代码。

## 🔐 问题原因

当前错误：`fatal: could not read Username for 'https://github.com': No such device or address`

这是因为使用HTTPS方式推送需要用户名和密码/Token认证，但当前环境无法交互式输入。

## ✅ 解决方案

### 方案一：使用SSH（强烈推荐）

#### 1. 生成SSH密钥
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
按Enter使用默认路径，可选设置密码或直接按Enter跳过

#### 2. 查看并复制SSH公钥
```bash
cat ~/.ssh/id_ed25519.pub
```
复制输出的整个内容

#### 3. 添加SSH密钥到GitHub
1. 访问：https://github.com/settings/ssh/new
2. 点击 "New SSH key"
3. Title: 输入一个描述（如：MacBook Pro）
4. Key: 粘贴刚才复制的SSH公钥
5. 点击 "Add SSH key"

#### 4. 测试SSH连接
```bash
ssh -T git@github.com
```

#### 5. 更改远程仓库URL
```bash
# 进入项目目录
cd /path/to/your/project

# 将HTTPS URL改为SSH URL
git remote set-url origin git@github.com:wanian2026/daihaoA.git

# 验证
git remote -v
```

#### 6. 推送代码
```bash
git push origin main
```

---

### 方案二：使用Personal Access Token

#### 1. 生成Token
1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 设置过期时间（建议30天或90天）
4. 勾选权限：
   - ✅ repo（完整的仓库访问权限）
   - ✅ workflow（如果需要GitHub Actions）
5. 点击 "Generate token"
6. **重要：** 复制token（只显示一次）

#### 2. 配置Git凭证
```bash
# 方法A：临时使用（每次推送都需要输入）
git push origin main
# 用户名：wanian2026
# 密码：粘贴刚才生成的token

# 方法B：永久保存（推荐）
git config --global credential.helper store
git push origin main
# 用户名：wanian2026
# 密码：粘贴刚才生成的token（只需一次）
```

---

### 方案三：使用GitHub CLI（推荐）

#### 1. 安装GitHub CLI
```bash
# 使用Homebrew
brew install gh

# 或使用其他方式
# 访问: https://cli.github.com/
```

#### 2. 登录GitHub
```bash
gh auth login
```

按提示操作：
1. 选择 "GitHub.com"
2. 选择 "HTTPS"
3. 选择 "Login with a web browser"
4. 按提示授权

#### 3. 推送代码
```bash
git push origin main
```

---

## 🎯 推荐操作流程

### 最简单的方式（GitHub CLI）

```bash
# 1. 安装GitHub CLI
brew install gh

# 2. 登录
gh auth login

# 3. 推送
git push origin main
```

### 最安全的方式（SSH）

```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 复制公钥到GitHub（参考上面步骤）

# 3. 更改远程URL
git remote set-url origin git@github.com:wanian2026/daihaoA.git

# 4. 推送
git push origin main
```

## 📋 验证配置

### 检查远程仓库
```bash
git remote -v
```

应该显示：
```
origin  git@github.com:wanian2026/daihaoA.git (fetch)
origin  git@github.com:wanian2026/daihaoA.git (push)
```

### 检查Git凭证
```bash
git config --global user.name
git config --global user.email
```

如果没有设置，可以设置：
```bash
git config --global user.name "你的用户名"
git config --global user.email "你的邮箱@example.com"
```

## 🔍 常见问题

### Q1: ssh -T git@github.com 提示 Permission denied
**解决方案**：
- 检查SSH密钥是否正确添加到GitHub
- 确保使用的是正确的私钥：`~/.ssh/id_ed25519`
- 检查SSH代理：`ssh-add ~/.ssh/id_ed25519`

### Q2: 推送时提示 "Updates were rejected"
**解决方案**：
```bash
# 拉取远程代码
git pull origin main

# 如果有冲突，解决后提交
git add .
git commit -m "merge changes"

# 再次推送
git push origin main
```

### Q3: Token过期了怎么办
**解决方案**：
- 访问：https://github.com/settings/tokens
- 重新生成新的token
- 更新Git凭证

## 📚 更多资源

- [GitHub官方文档 - SSH](https://docs.github.com/zh/authentication/connecting-to-github-with-ssh)
- [GitHub官方文档 - Personal Access Tokens](https://docs.github.com/zh/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [GitHub CLI文档](https://cli.github.com/)

---

**配置完成后，就可以成功推送代码到GitHub了！**
