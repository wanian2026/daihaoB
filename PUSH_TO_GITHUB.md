# 📤 推送代码到GitHub

当前代码已提交到本地Git仓库，但推送到GitHub时遇到认证问题。

## ⚠️ 当前状态

```
On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)
```

## 🔐 解决认证问题

### 推荐方式一：使用GitHub CLI（最简单）

```bash
# 1. 安装GitHub CLI
brew install gh

# 2. 登录GitHub
gh auth login

# 3. 推送代码
git push origin main
```

### 推荐方式二：使用SSH（最安全）

```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 复制公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到GitHub
# 访问：https://github.com/settings/ssh/new
# 粘贴公钥并保存

# 4. 测试连接
ssh -T git@github.com

# 5. 更改远程URL为SSH
git remote set-url origin git@github.com:wanian2026/daihaoA.git

# 6. 推送代码
git push origin main
```

### 备选方式：使用Personal Access Token

```bash
# 1. 生成Token
# 访问：https://github.com/settings/tokens
# 生成新token，勾选repo权限

# 2. 配置凭证
git config --global credential.helper store

# 3. 推送时输入token
git push origin main
# 用户名：wanian2026
# 密码：粘贴token
```

## 📖 详细指南

完整的认证配置说明，请查看：`docs/git_push_guide.md`

## ✅ 配置完成后的操作

```bash
# 推送所有本地提交
git push origin main

# 验证
# 访问：https://github.com/wanian2026/daihaoA
```

## 💡 提示

- 首次推送需要配置GitHub认证，之后就可以直接推送
- 推荐使用GitHub CLI或SSH方式
- 记住你的Token或SSH密钥，不要泄露
