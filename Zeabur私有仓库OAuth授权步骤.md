# Zeabur 私有仓库 OAuth 授权步骤

## 🔍 问题分析

Zeabur 使用 OAuth 方式连接 GitHub，不支持直接使用 Token。对于私有仓库，需要确保 OAuth 授权有正确的权限。

## ✅ 解决方案：正确授权 Zeabur 访问私有仓库

### 方法一：在 Zeabur 中重新授权（推荐）

1. **在 Zeabur 绑定界面**：
   - 点击 **"配置 GitHub"** 按钮
   - 这会打开 GitHub 授权页面

2. **在 GitHub 授权页面**：
   - 查看授权范围（Scopes）
   - **确保勾选了以下权限**：
     - ✅ `repo` - 完整仓库访问权限（包括私有仓库）
     - ✅ `read:org` - 组织访问权限（如果需要）

3. **授权范围选择**：
   - 如果看到 "授权访问所有仓库" 或 "授权访问特定仓库"
   - **推荐选择 "授权访问所有仓库"**（更简单）
   - 或选择 "授权访问特定仓库"，然后选择 `changchuan123/redink`

4. **完成授权**：
   - 点击 "Authorize Zeabur" 或 "授权"
   - 返回 Zeabur，应该可以看到仓库列表

5. **选择仓库**：
   - 在仓库列表中找到 `changchuan123/redink`
   - 点击选择
   - 选择分支：`main`
   - 保存

### 方法二：检查现有授权权限

如果已经授权过，但无法访问私有仓库：

1. **检查 GitHub 授权**：
   - 访问：https://github.com/settings/applications
   - 查看 "Authorized OAuth Apps"
   - 找到 **Zeabur**
   - 点击查看权限

2. **检查权限**：
   - 确认是否有 `repo` 权限
   - 如果没有，需要重新授权

3. **重新授权**：
   - 在 Zeabur 中点击 "配置 GitHub"
   - 在 GitHub 授权页面，**撤销现有授权**
   - 然后重新授权，确保勾选 `repo` 权限

### 方法三：在 GitHub 中直接授权仓库

1. **访问仓库设置**：
   - 访问：https://github.com/changchuan123/redink/settings/access
   - 或：仓库 → Settings → Collaborators

2. **添加 Zeabur 为协作者**（不推荐，复杂）

3. **或者使用 GitHub App**：
   - 在仓库设置中查看已安装的 GitHub Apps
   - 确认 Zeabur 应用已安装并有权限

## 🔧 详细操作步骤

### 步骤 1：在 Zeabur 中配置 GitHub

1. 在 Zeabur 的 "绑定 GitHub 仓库" 界面
2. 点击 **"配置 GitHub"** 按钮
3. 会跳转到 GitHub 授权页面

### 步骤 2：在 GitHub 授权页面

**重要**：查看授权范围，确保包含：

```
✅ repo
   - repo:status
   - repo_deployment
   - public_repo
   - repo:invite
   - security_events
```

**如果没有 `repo` 权限**：
- 点击 "Authorize" 旁边的下拉菜单
- 选择 "Edit permissions" 或 "编辑权限"
- 勾选 `repo` 权限
- 保存

### 步骤 3：选择仓库访问范围

在授权页面，会看到：

- **"All repositories"**（所有仓库）- 推荐选择这个
- **"Only select repositories"**（仅选定的仓库）- 需要手动选择

**推荐选择 "All repositories"**，因为：
- 更简单，不需要每次添加新仓库都重新授权
- Zeabur 只会访问你授权的仓库

### 步骤 4：完成授权

1. 点击 **"Authorize Zeabur"** 或 **"授权 Zeabur"**
2. 返回 Zeabur
3. 应该可以看到仓库列表，包括私有仓库
4. 选择 `changchuan123/redink`
5. 选择分支 `main`
6. 保存

## ⚠️ 常见问题

### 问题 1：授权后仍然看不到私有仓库

**原因**：
- OAuth 授权时没有选择 `repo` 权限
- 或选择了 "Only select repositories" 但没有选择该仓库

**解决**：
1. 访问：https://github.com/settings/applications
2. 找到 Zeabur，点击查看
3. 点击 "Revoke"（撤销）
4. 在 Zeabur 中重新授权
5. 确保勾选 `repo` 权限
6. 选择 "All repositories" 或选择 `changchuan123/redink`

### 问题 2：授权页面没有 `repo` 选项

**原因**：
- GitHub 可能限制了某些应用的权限范围

**解决**：
- 联系 Zeabur 支持，询问如何访问私有仓库
- 或考虑使用其他部署方式

### 问题 3：授权后仍然提示"複製儲存庫失敗"

**可能原因**：
- 网络问题
- GitHub API 限制
- 仓库名称错误

**解决**：
1. 检查仓库名称：`changchuan123/redink`
2. 检查分支名称：`main`
3. 等待几分钟后重试
4. 查看 Zeabur 详细错误日志

## 📋 检查清单

- [ ] 在 Zeabur 中点击了 "配置 GitHub"
- [ ] 在 GitHub 授权页面看到了授权范围
- [ ] 确认授权包含 `repo` 权限
- [ ] 选择了 "All repositories" 或选择了 `changchuan123/redink`
- [ ] 完成了授权
- [ ] 在 Zeabur 中可以看到 `changchuan123/redink` 仓库
- [ ] 选择了正确的分支 `main`
- [ ] 保存并等待部署

## 💡 关键点

**最重要的**：确保 GitHub OAuth 授权时，**勾选了 `repo` 权限**，这样才能访问私有仓库。

如果授权时没有 `repo` 权限，Zeabur 就无法访问私有仓库，会提示"複製儲存庫失敗"。

## 🆘 如果还是失败

1. **查看 Zeabur 详细错误日志**：
   - 进入项目 → 查看部署日志
   - 查看具体的错误信息

2. **检查 GitHub 授权状态**：
   - 访问：https://github.com/settings/applications
   - 查看 Zeabur 的授权权限
   - 确认是否有 `repo` 权限

3. **联系 Zeabur 支持**：
   - 提供错误截图
   - 说明是私有仓库
   - 询问如何正确授权

按照以上步骤操作，应该可以成功绑定私有仓库！

