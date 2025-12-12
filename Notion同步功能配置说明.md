# Notion 同步功能配置说明

## 📋 功能概述

本功能实现了将生成的笔记和图片自动同步到 Notion 数据库的功能：

1. **图片上传到 COS**：使用现有的 COS 图床服务上传图片
2. **内容同步到 Notion**：将笔记标题、大纲内容和图片链接同步到 Notion 数据库

## ⚙️ 配置方法

### 方式一：环境变量配置（推荐）

在项目根目录创建 `.env` 文件，或设置系统环境变量：

```bash
# COS 服务配置
COS_SERVICE_URL=http://212.64.57.87:10009/upload-to-cos

# Notion 配置
NOTION_INTEGRATION_TOKEN=你的Notion Token
NOTION_DATABASE_ID=2c771735fbc5802e8474d17cda149056

# 同步功能开关
SYNC_ENABLED=true
```

### 方式二：直接修改代码配置

编辑 `backend/config.py`，修改默认值：

```python
# 同步服务配置
COS_SERVICE_URL = os.getenv('COS_SERVICE_URL', 'http://212.64.57.87:10009/upload-to-cos')
NOTION_INTEGRATION_TOKEN = os.getenv('NOTION_INTEGRATION_TOKEN', '你的Token')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID', '你的DatabaseID')
SYNC_ENABLED = os.getenv('SYNC_ENABLED', 'true').lower() == 'true'
```

## 🔧 Notion 数据库配置

### 数据库字段要求

Notion 数据库需要包含以下字段：

1. **标题**（Title 类型）
   - 字段名：`标题`
   - 类型：Title

2. **笔记**（Rich text 类型）
   - 字段名：`笔记`
   - 类型：Rich text 或 Text

3. **图片**（Files & media 类型）
   - 字段名：`图片`
   - 类型：Files & media

4. **上传时间**（Date 类型）
   - 字段名：`上传时间`
   - 类型：Date（包含时间）

### 数据库链接

当前配置的数据库：
- **链接**：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056
- **Database ID**：`2c771735fbc5802e8474d17cda149056`

## 🚀 使用方式

### 自动同步（默认）

当图片生成完成且历史记录状态更新为 `completed` 时，系统会自动触发同步：

1. 上传所有图片到 COS
2. 获取 COS URL
3. 创建 Notion 页面
4. 将标题、笔记内容和图片链接写入 Notion

**注意**：同步是异步进行的，不会阻塞用户操作。

### 手动同步

如果自动同步失败，可以通过 API 手动触发同步：

**API 接口**：
```
POST /api/sync/<record_id>
```

**前端调用示例**：
```typescript
import { syncToNotion } from '../api'

// 同步记录到 Notion
const result = await syncToNotion(recordId)
if (result.success) {
  console.log('同步成功:', result.notion_page_url)
} else {
  console.error('同步失败:', result.error)
}
```

## 📊 同步流程

```
图片生成完成
  ↓
更新历史记录状态为 completed
  ↓
触发自动同步（后台异步）
  ↓
读取历史记录数据
  ↓
上传图片到 COS
  ├─→ 成功：获取 COS URL
  └─→ 失败：记录错误，继续 Notion 同步
  ↓
创建 Notion 页面
  ├─→ 标题：用户输入的主题
  ├─→ 笔记：完整大纲文本 + 分页内容
  ├─→ 图片：COS URL 列表
  └─→ 上传时间：记录创建时间
  ↓
同步完成
```

## 🔍 日志查看

同步过程的日志会输出到后端日志中：

- **成功**：`✅ 记录 {record_id} 同步成功`
- **失败**：`❌ 同步失败: {错误信息}`
- **COS 上传**：`✅ 图片 {filename} 上传成功`
- **Notion 创建**：`✅ Notion 页面创建成功`

## ⚠️ 注意事项

### 1. COS 服务

- 确保 COS 服务正常运行：`http://212.64.57.87:10009/upload-to-cos`
- 如果 COS 服务不可用，同步会失败
- 图片上传失败不会影响 Notion 同步（会创建无图片的页面）

### 2. Notion 配置

- 确保 Notion Integration Token 有效
- 确保 Database ID 正确
- 确保 Integration 有权限访问目标数据库
- 确保数据库字段名称与配置一致

### 3. 性能考虑

- 同步是异步进行的，不会阻塞用户操作
- 大量图片上传可能需要较长时间
- 建议在网络良好的环境下使用

### 4. 错误处理

- 如果同步失败，不会影响历史记录的保存
- 可以通过手动同步 API 重试
- 错误信息会记录在日志中

## 🛠️ 故障排查

### 问题 1：同步未触发

**检查**：
1. 确认 `SYNC_ENABLED=true`
2. 确认历史记录状态已更新为 `completed`
3. 查看后端日志是否有错误

### 问题 2：COS 上传失败

**检查**：
1. 测试 COS 服务是否可访问：`curl http://212.64.57.87:10009/upload-to-cos`
2. 检查图片文件是否存在
3. 查看后端日志中的错误信息

### 问题 3：Notion 同步失败

**检查**：
1. 确认 Notion Token 和 Database ID 正确
2. 确认 Integration 有权限访问数据库
3. 确认数据库字段名称正确
4. 查看后端日志中的详细错误信息

### 问题 4：字段不匹配

**检查**：
1. 确认数据库字段名称：
   - `标题`（Title）
   - `笔记`（Rich text）
   - `图片`（Files & media）
   - `上传时间`（Date）
2. 如果字段名称不同，需要修改 `backend/services/notion_sync.py` 中的字段映射

## 📝 配置验证

启动服务后，检查日志中是否有以下信息：

```
COS 上传服务初始化: http://212.64.57.87:10009/upload-to-cos
Notion 同步服务初始化: database_id=2c771735...
同步服务初始化完成
```

如果看到 "Notion 同步服务未初始化" 或 "同步服务已禁用"，说明配置有问题。

## 🔄 更新配置

修改配置后，需要重启服务才能生效：

```bash
# 如果使用 uv
uv run python -m backend.app

# 如果使用 Docker
docker-compose restart
```

## 📚 相关文档

- [COS 图床服务完整文档](../N8N/maoyu/COS图床服务完整文档.md)
- [Notion API 文档](https://developers.notion.com/reference/intro)
- [Notion 同步功能可行性报告](./Notion同步功能可行性报告.md)

