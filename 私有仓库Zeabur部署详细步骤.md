# 私有仓库 Zeabur 部署详细步骤

## 📋 操作步骤

### 第一步：创建 GitHub Personal Access Token

1. **访问 GitHub Token 设置页面**：
   - 打开：https://github.com/settings/tokens
   - 或：GitHub 头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **创建新 Token**：
   - 点击 **"Generate new token"** 按钮
   - 选择 **"Generate new token (classic)"**

3. **配置 Token**：
   - **Note（备注）**：填写 `Zeabur Deploy` 或 `Zeabur Redink`
   - **Expiration（过期时间）**：
     - 选择 **"No expiration"**（永不过期，推荐）
     - 或选择较长时间（如 1 年）
   - **Select scopes（选择权限）**：
     - ✅ 勾选 **`repo`** - 完整仓库访问权限
       - 这会自动勾选所有子权限：
         - `repo:status`
         - `repo_deployment`
         - `public_repo`
         - `repo:invite`
         - `security_events`

4. **生成 Token**：
   - 滚动到底部
   - 点击 **"Generate token"** 按钮
   - ⚠️ **重要**：立即复制 Token（格式类似：`ghp_xxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ **注意**：Token 只显示一次，关闭页面后就看不到了！

5. **保存 Token**：
   - 将 Token 保存到安全的地方（如密码管理器）
   - 不要分享给他人

### 第二步：在 Zeabur 中使用 Token

1. **进入 Zeabur 项目设置**：
   - 登录 Zeabur
   - 进入你的项目
   - 点击服务名称
   - 进入 **"设置"** 或 **"Settings"**

2. **找到源代码设置**：
   - 找到 **"来源"** 或 **"Source"** 标签
   - 或找到 **"Repository"** 设置

3. **解除现有绑定**（如果有）：
   - 如果已经绑定了 GitHub 仓库
   - 点击 **"解除绑定 GitHub 仓库"** 或 **"Unbind GitHub Repository"**

4. **使用 Token 连接**：
   - 点击 **"连接 GitHub"** 或 **"Connect GitHub"**
   - 选择 **"使用 Personal Access Token"** 或 **"Use Personal Access Token"**
   - 如果没有这个选项，可能需要：
     - 先解除绑定
     - 然后选择 "从 GitHub 仓库部署"
     - 在连接方式中选择 "Token"

5. **输入 Token 和仓库信息**：
   - **Token**：粘贴刚才复制的 GitHub Token
   - **Repository**：输入 `changchuan123/redink`
   - **Branch**：输入 `main`
   - 点击 **"保存"** 或 **"Connect"**

6. **等待部署**：
   - Zeabur 会自动开始部署
   - 查看部署日志，确认是否成功

### 第三步：验证部署

1. **查看部署日志**：
   - 在 Zeabur 中查看部署状态
   - 应该看到 "Building" 或 "Deploying"
   - 等待部署完成

2. **检查启动日志**：
   - 部署完成后，查看服务日志
   - 应该看到：
     ```
     🚀 正在启动 红墨 AI图文生成器...
     ✅ 同步服务已启用
     ✅ Notion 同步服务已初始化
     ```

3. **测试应用**：
   - 访问 Zeabur 提供的域名
   - 测试生成笔记功能
   - 检查是否正常

## 🔍 如果遇到问题

### 问题 1：找不到 "使用 Token" 选项

**解决方法**：
- 在 Zeabur 的 "来源" 设置中
- 先点击 "解除绑定"
- 然后重新连接时，应该会看到 Token 选项
- 或者联系 Zeabur 支持

### 问题 2：Token 无效

**检查**：
- Token 是否正确复制（没有多余空格）
- Token 是否过期
- Token 是否有 `repo` 权限

**解决**：
- 重新创建 Token
- 确保勾选了 `repo` 权限

### 问题 3：仍然无法访问仓库

**检查**：
- 仓库名称是否正确：`changchuan123/redink`
- Token 是否有访问该仓库的权限
- 仓库是否真的存在

**解决**：
- 确认仓库地址
- 重新创建 Token 并确保有 `repo` 权限

## 📝 Token 安全提示

1. **不要分享 Token**：
   - Token 等同于你的 GitHub 密码
   - 不要提交到代码仓库
   - 不要分享给他人

2. **定期检查 Token**：
   - 在 GitHub 设置中查看已创建的 Token
   - 如果发现异常，立即删除并重新创建

3. **最小权限原则**：
   - 只给 Token 必要的权限（`repo`）
   - 不要给过多权限

## ✅ 完成检查清单

- [ ] GitHub Token 已创建
- [ ] Token 已保存到安全位置
- [ ] Token 有 `repo` 权限
- [ ] 在 Zeabur 中已输入 Token
- [ ] 仓库名称正确：`changchuan123/redink`
- [ ] 分支名称正确：`main`
- [ ] Zeabur 部署成功
- [ ] 服务正常启动
- [ ] 同步服务已初始化

## 🎯 快速操作流程

```
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. 勾选 repo 权限
4. 生成并复制 Token
5. Zeabur → 项目设置 → 来源
6. 解除绑定（如果有）
7. 使用 Token 连接
8. 输入 Token、仓库、分支
9. 保存并等待部署
```

## 💡 提示

- Token 创建后，可以在 GitHub 设置中随时查看和管理
- 如果 Token 泄露，立即删除并重新创建
- 部署成功后，Token 会安全存储在 Zeabur 中

按照以上步骤操作，应该可以成功部署私有仓库！

