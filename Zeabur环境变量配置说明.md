# Zeabur 环境变量配置说明

## 📋 环境变量列表

在 Zeabur 的环境变量设置中，可以添加以下环境变量：

### Notion 同步功能（已配置）

```bash
COS_SERVICE_URL=http://212.64.57.87:10009/upload-to-cos
NOTION_INTEGRATION_TOKEN=你的Notion Token
NOTION_DATABASE_ID=2c771735fbc5802e8474d17cda149056
SYNC_ENABLED=true
```

### API Key 配置（新增支持）

现在支持通过环境变量配置 API Key，优先级高于 YAML 配置文件：

#### DeepSeek API Key

```bash
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

#### Gemini API Key

```bash
GEMINI_API_KEY=你的Gemini API Key
```

#### 其他服务商

环境变量命名规则：`{服务商名称大写}_API_KEY`

例如：
- `OPENAI_COMPATIBLE_API_KEY` - OpenAI 兼容接口
- `GOOGLE_GENAI_API_KEY` - Google GenAI（图片生成）

## 🔧 配置方法

### 在 Zeabur 中配置

1. 进入 Zeabur 项目设置
2. 点击 **"环境变量"** 标签
3. 点击 **"编辑原始环境变量"**
4. 在文本框中添加环境变量，每行一个：

```bash
PORT=${WEB_PORT}
PASSWORD=m7c2yg5T3YL4vaiftnp6xe0Hw8sz19A0
SYNC_ENABLED=true
COS_SERVICE_URL=http://212.64.57.87:10009/upload-to-cos
NOTION_INTEGRATION_TOKEN=你的Notion Token
NOTION_DATABASE_ID=2c771735fbc5802e8474d17cda149056
DEEPSEEK_API_KEY=你的DeepSeek API Key
GEMINI_API_KEY=你的Gemini API Key
```

5. 点击 **"保存"** 或 **"应用"**
6. Zeabur 会自动重新部署服务

## ⚙️ 优先级说明

配置读取优先级（从高到低）：

1. **环境变量** - 如果设置了环境变量，优先使用
2. **YAML 配置文件** - 如果环境变量未设置，使用配置文件
3. **Web 界面配置** - 通过 `/settings` 页面配置的会保存到 YAML 文件

## 📝 注意事项

1. **环境变量名称**：必须使用大写字母，服务商名称与 YAML 配置中的名称一致
2. **服务商名称**：环境变量中的服务商名称必须与 YAML 配置中的 `providers` 键名一致
   - 例如：YAML 中是 `deepseek`，环境变量是 `DEEPSEEK_API_KEY`
   - 例如：YAML 中是 `gemini`，环境变量是 `GEMINI_API_KEY`
3. **重新部署**：修改环境变量后，Zeabur 会自动重新部署服务
4. **安全性**：环境变量中的 API Key 不会显示在 Web 界面，更安全

## 🔍 验证配置

部署完成后，查看服务日志，应该看到：

```
✅ 文本服务商 [deepseek] API Key 已配置
✅ 图片服务商 [gemini] API Key 已配置
```

如果看到 "从环境变量读取 API Key"，说明环境变量配置成功。

## 💡 推荐配置方式

- **生产环境（Zeabur）**：使用环境变量配置，更安全
- **开发环境**：使用 Web 界面配置，更方便

