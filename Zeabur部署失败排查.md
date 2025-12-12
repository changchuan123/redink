# Zeabur 部署失败排查指南

## ❌ 错误：複製儲存庫失敗

如果 Zeabur 提示"複製儲存庫失敗"，请按以下步骤排查：

## 🔍 排查步骤

### 1. 检查 GitHub 仓库状态

确认仓库是否可访问：
- 仓库地址：https://github.com/changchuan123/redink
- 确认仓库是公开的（Public）或 Zeabur 有访问权限

### 2. 检查仓库名称

确认 Zeabur 中配置的仓库名称是否正确：
- 正确：`changchuan123/redink`
- 错误示例：`redink`、`redlnk`、`redink.git`

### 3. 重新连接 GitHub

在 Zeabur 中：
1. 进入项目设置
2. 断开 GitHub 连接
3. 重新连接 GitHub
4. 重新选择仓库：`changchuan123/redink`

### 4. 检查 GitHub 权限

确保 Zeabur 有权限访问仓库：
1. 进入 GitHub 设置：https://github.com/settings/applications
2. 查看已授权的应用
3. 确认 Zeabur 有访问 `changchuan123/redink` 的权限

### 5. 手动指定仓库

如果自动检测失败，可以手动指定：
1. 在 Zeabur 项目设置中
2. 找到"源代码"或"Repository"设置
3. 手动输入：`changchuan123/redink`
4. 或使用完整 URL：`https://github.com/changchuan123/redink.git`

### 6. 检查分支名称

确认分支名称：
- 默认分支应该是：`main`
- 如果不是，在 Zeabur 中手动指定分支

### 7. 清除缓存重试

1. 在 Zeabur 中删除当前项目
2. 重新创建项目
3. 重新连接 GitHub 仓库

## 🔧 常见解决方案

### 方案一：重新授权 GitHub

1. 进入 Zeabur Dashboard
2. 点击右上角头像 → Settings
3. 找到 GitHub 连接
4. 断开连接
5. 重新授权并选择仓库

### 方案二：使用 GitHub Token

如果 OAuth 授权失败，可以使用 Personal Access Token：

1. 在 GitHub 创建 Token：
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 权限选择：`repo`（完整仓库访问权限）
   - 生成并复制 Token

2. 在 Zeabur 中使用 Token：
   - 在项目设置中找到"源代码"设置
   - 选择"使用 Token"
   - 粘贴 Token

### 方案三：检查仓库可见性

如果仓库是私有的：
1. 确保 Zeabur 有访问权限
2. 或者将仓库改为公开（Public）

### 方案四：使用 Docker 镜像部署

如果 GitHub 连接一直失败，可以使用 Docker 镜像：

1. 在 Docker Hub 构建镜像
2. 在 Zeabur 中选择"从 Docker 镜像部署"
3. 使用镜像地址：`histonemax/redink:latest`

## 📋 检查清单

- [ ] GitHub 仓库可访问
- [ ] 仓库名称正确：`changchuan123/redink`
- [ ] 分支名称正确：`main`
- [ ] Zeabur 有 GitHub 访问权限
- [ ] 仓库不是空的（有代码）
- [ ] 网络连接正常

## 🆘 如果仍然失败

1. **查看 Zeabur 详细错误日志**：
   - 进入项目 → 查看部署日志
   - 查看具体的错误信息

2. **联系 Zeabur 支持**：
   - 提供错误截图
   - 提供仓库地址
   - 说明具体错误信息

3. **尝试其他部署方式**：
   - 使用 Docker 镜像部署
   - 使用其他平台（如 Railway、Render）

## 📝 仓库信息

- **仓库地址**：https://github.com/changchuan123/redink
- **默认分支**：main
- **仓库类型**：应该是 Public 或 Zeabur 有访问权限

## 💡 快速解决

最快的解决方法：

1. 在 Zeabur 中删除当前项目
2. 创建新项目
3. 选择 "Import from GitHub"
4. 搜索并选择：`changchuan123/redink`
5. 点击 "Deploy"

如果还是失败，请提供 Zeabur 的详细错误信息，我可以进一步帮你排查。

