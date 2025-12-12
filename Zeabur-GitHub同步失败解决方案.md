# Zeabur GitHub 同步失败解决方案

## ❌ 错误：複製儲存庫失敗

当 Zeabur 提示"複製儲存庫失敗"时，按以下步骤解决：

## 🔧 解决方案

### 方案一：重新授权 GitHub（最常用）

1. **在 Zeabur 中**：
   - 进入项目设置
   - 找到 "来源" 或 "Source" 设置
   - 点击 "解除绑定 GitHub 仓库"
   - 然后重新连接 GitHub

2. **重新连接步骤**：
   - 点击 "连接 GitHub"
   - 重新授权 Zeabur 访问 GitHub
   - 选择仓库：`changchuan123/redink`
   - 选择分支：`main`
   - 保存

### 方案二：检查仓库访问权限

1. **确认仓库可见性**：
   - 访问：https://github.com/changchuan123/redink
   - 确认仓库是 **Public**（公开）还是 **Private**（私有）

2. **如果是私有仓库**：
   - 确保 Zeabur 有访问权限
   - 或者将仓库改为公开（Public）

3. **检查 GitHub 授权**：
   - 访问：https://github.com/settings/applications
   - 查看 "Authorized OAuth Apps"
   - 确认 Zeabur 在列表中
   - 如果没有，重新授权

### 方案三：手动输入仓库信息

在 Zeabur 的 "来源" 设置中：

1. **仓库 URL**：
   ```
   https://github.com/changchuan123/redink
   ```
   或
   ```
   changchuan123/redink
   ```

2. **分支**：
   ```
   main
   ```

3. **保存并重新部署**

### 方案四：使用 GitHub Token（如果 OAuth 失败）

1. **创建 GitHub Token**：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 名称：`Zeabur Deploy`
   - 权限选择：`repo`（完整仓库访问权限）
   - 生成并复制 Token

2. **在 Zeabur 中使用 Token**：
   - 在项目设置中找到 "源代码" 或 "Repository" 设置
   - 选择 "使用 Token" 或 "Personal Access Token"
   - 粘贴 Token
   - 输入仓库：`changchuan123/redink`
   - 输入分支：`main`

### 方案五：检查仓库名称和分支

确认以下信息：

- **仓库名称**：`changchuan123/redink`（不是 `redink` 或 `redlnk`）
- **分支名称**：`main`（不是 `master`）
- **完整 URL**：`https://github.com/changchuan123/redink.git`

### 方案六：清除缓存重新部署

1. **在 Zeabur 中**：
   - 进入项目设置
   - 找到 "部署" 或 "Deployment" 设置
   - 点击 "清除构建缓存"
   - 然后重新部署

2. **或者删除并重新创建项目**：
   - 删除当前项目
   - 创建新项目
   - 重新连接 GitHub 仓库

## 🔍 详细排查步骤

### 1. 检查 GitHub 仓库状态

访问仓库：https://github.com/changchuan123/redink

确认：
- ✅ 仓库存在且可访问
- ✅ 仓库不是空的（有代码）
- ✅ 默认分支是 `main`

### 2. 检查 Zeabur 授权

1. 访问：https://github.com/settings/applications
2. 查看 "Authorized OAuth Apps"
3. 找到 Zeabur
4. 检查权限是否包含：
   - ✅ `repo` - 仓库访问权限
   - ✅ `read:org` - 组织访问权限（如果需要）

### 3. 检查网络连接

在 Zeabur 日志中查看是否有网络错误：
- `Connection timeout`
- `Network error`
- `SSL error`

### 4. 查看详细错误信息

在 Zeabur 部署日志中：
1. 找到失败的那次部署
2. 查看详细错误信息
3. 常见错误：
   - `Repository not found` - 仓库不存在或无权访问
   - `Authentication failed` - 授权失败
   - `Branch not found` - 分支不存在
   - `Network error` - 网络问题

## 📋 快速检查清单

- [ ] GitHub 仓库可访问：https://github.com/changchuan123/redink
- [ ] 仓库名称正确：`changchuan123/redink`
- [ ] 分支名称正确：`main`
- [ ] Zeabur 已授权访问 GitHub
- [ ] 仓库不是空的
- [ ] 网络连接正常

## 🆘 如果所有方案都失败

1. **查看 Zeabur 详细错误日志**：
   - 进入项目 → 查看部署历史
   - 点击失败的部署
   - 查看详细错误信息
   - 截图或复制错误信息

2. **联系 Zeabur 支持**：
   - 提供错误截图
   - 提供仓库地址
   - 说明已尝试的解决方案

3. **临时解决方案**：
   - 使用 Docker 镜像部署
   - 或使用其他部署平台（Railway、Render）

## 💡 推荐操作顺序

1. **首先尝试**：重新授权 GitHub（方案一）
2. **如果失败**：检查仓库访问权限（方案二）
3. **如果还失败**：使用 GitHub Token（方案四）
4. **最后**：清除缓存重新部署（方案六）

## 📝 仓库信息确认

- **仓库地址**：https://github.com/changchuan123/redink
- **默认分支**：main
- **最新提交**：d27f8e8（已包含所有新功能）

请告诉我 Zeabur 的具体错误信息，我可以提供更精确的解决方案。

