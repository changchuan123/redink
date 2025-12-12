# Zeabur 部署指南

## 📋 快速部署步骤

### 1. 准备工作

确保项目已推送到 GitHub 仓库。

### 2. 在 Zeabur 创建项目

1. 访问 [Zeabur Dashboard](https://zeabur.com/projects)
2. 点击 **"New Project"** 或 **"Create Project"**
3. 选择 **"Import from GitHub"**
4. 选择你的仓库：`redink`（或你的仓库名）
5. 点击 **"Deploy"**

### 3. 配置 API Keys

部署完成后，需要在 Zeabur 中配置 API Keys。有两种方式：

#### 方式一：通过 Web 界面配置（推荐）

1. 部署完成后，访问 Zeabur 提供的域名
2. 进入 **设置页面** (`/settings`)
3. 在 **文本生成服务商** 中添加 DeepSeek：
   - 服务商名称：`deepseek`
   - 类型：`openai_compatible`
   - API Key：`你的DeepSeek API Key`（从 https://platform.deepseek.com/ 获取）
   - Base URL：`https://api.deepseek.com/v1`
   - Model：`deepseek-chat`
   - 设置为激活服务商

4. 在 **图片生成服务商** 中添加 Gemini：
   - 服务商名称：`gemini`
   - 类型：`google_genai`
   - API Key：`你的Gemini API Key`（从 https://aistudio.google.com/app/apikey 获取）
   - Model：`gemini-3-pro-image-preview`
   - 设置为激活服务商

#### 方式二：通过文件编辑

1. 在 Zeabur 项目设置中找到 **"File Manager"** 或 **"Code"**
2. 编辑 `text_providers.yaml`：
```yaml
active_provider: deepseek
providers:
  deepseek:
    type: openai_compatible
    api_key: 你的DeepSeek API Key
    base_url: https://api.deepseek.com/v1
    model: deepseek-chat
```

3. 编辑 `image_providers.yaml`：
```yaml
active_provider: gemini
providers:
  gemini:
    type: google_genai
    api_key: 你的Gemini API Key
    model: gemini-3-pro-image-preview
    high_concurrency: false
```

### 4. 环境变量（可选）

如果需要通过环境变量配置，可以在 Zeabur 项目设置中添加：

- `PORT`: 端口号（Zeabur 会自动设置）
- `FLASK_DEBUG`: `False`（生产环境）
- `CORS_ORIGINS`: 允许的 CORS 来源（逗号分隔）

### 5. 访问应用

部署完成后，Zeabur 会提供一个域名，例如：
- `https://your-project.zeabur.app`

访问该域名即可使用应用。

## 🔧 配置说明

### 端口配置

- Zeabur 会自动设置 `PORT` 环境变量
- 应用会自动读取 `PORT` 环境变量
- 默认端口：10008（如果未设置 PORT）

### 健康检查

- 路径：`/api/health`
- Zeabur 会自动配置健康检查

### 文件存储

- 生成的图片存储在 `output/` 目录
- Zeabur 使用临时存储，重启后数据会丢失
- 如需持久化，建议使用 Zeabur 的存储服务或外部存储（如 S3）

## 📝 注意事项

1. **API Key 安全**
   - 不要在代码中硬编码 API Key
   - 使用 Zeabur 的文件管理或环境变量配置
   - 确保配置文件不会被提交到公开仓库

2. **网络访问**
   - 确保 Zeabur 可以访问外部 API（DeepSeek、Gemini 等）
   - 某些地区可能需要配置代理

3. **资源限制**
   - 注意 Zeabur 的资源限制
   - 图片生成可能需要较多内存和 CPU
   - 建议使用合适的 Zeabur 计划

4. **域名配置**
   - Zeabur 会自动分配域名（如 `your-project.zeabur.app`）
   - 可以配置自定义域名

5. **自动部署**
   - 推送到 GitHub 主分支会自动触发部署
   - 可以在 Zeabur 设置中配置自动部署规则

## 🚀 部署后验证

1. **检查健康状态**
   ```bash
   curl https://your-project.zeabur.app/api/health
   ```
   应该返回：`{"message": "服务正常运行", "success": true}`

2. **访问首页**
   - 打开 `https://your-project.zeabur.app`
   - 应该能看到应用界面

3. **测试功能**
   - 进入设置页面配置 API Key
   - 尝试生成一个简单的大纲
   - 测试图片生成功能

## 🔄 更新部署

当代码更新后：

1. **自动部署**：推送到 GitHub 主分支会自动触发部署
2. **手动部署**：在 Zeabur Dashboard 中点击 "Redeploy"

## 📚 相关文档

- [Zeabur 文档](https://zeabur.com/docs)
- [Zeabur Docker 部署](https://zeabur.com/docs/deploy/docker)
- [Zeabur 环境变量](https://zeabur.com/docs/environment-variables)
- [Zeabur 文件管理](https://zeabur.com/docs/file-management)

## 🆘 故障排查

### 部署失败

1. 检查 Dockerfile 是否正确
2. 查看 Zeabur 构建日志
3. 确认所有依赖都已正确安装

### API Key 配置问题

1. 检查配置文件格式（YAML 语法）
2. 确认 API Key 是否正确
3. 查看应用日志确认错误信息

### 网络连接问题

1. 检查 Zeabur 是否可以访问外部 API
2. 查看应用日志中的网络错误
3. 考虑使用代理或更换 API 服务商

---

**部署完成后，访问 Zeabur 提供的域名即可使用应用！** 🎉
