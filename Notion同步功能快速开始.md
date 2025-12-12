# Notion 同步功能快速开始

## 🚀 5 分钟快速配置

### 步骤 1：设置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入以下配置
```

```bash
COS_SERVICE_URL=http://212.64.57.87:10009/upload-to-cos
NOTION_INTEGRATION_TOKEN=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
NOTION_DATABASE_ID=2c771735fbc5802e8474d17cda149056
SYNC_ENABLED=true
```

### 步骤 2：验证 Notion 数据库

访问 Notion 数据库：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056

确认数据库包含以下字段：
- ✅ **标题**（Title 类型）
- ✅ **笔记**（Rich text 类型）
- ✅ **图片**（Files & media 类型）
- ✅ **上传时间**（Date 类型，包含时间）

### 步骤 3：重启服务

```bash
# 如果使用 uv
uv run python -m backend.app

# 如果使用 Docker
docker-compose restart
```

### 步骤 4：测试

1. 生成一篇笔记和图片
2. 等待生成完成
3. 检查 Notion 数据库，应该能看到新创建的页面

## ✅ 验证配置

启动服务后，查看日志，应该看到：

```
COS 上传服务初始化: http://212.64.57.87:10009/upload-to-cos
Notion 同步服务初始化: database_id=2c771735...
同步服务初始化完成
```

如果看到 "Notion 同步服务未初始化" 或 "同步服务已禁用"，说明配置有问题。

## 🔧 故障排查

### 问题：同步未触发

**检查**：
1. 确认 `SYNC_ENABLED=true`
2. 确认历史记录状态已更新为 `completed`
3. 查看后端日志

### 问题：COS 上传失败

**检查**：
1. 测试 COS 服务：`curl http://212.64.57.87:10009/upload-to-cos`
2. 检查图片文件是否存在

### 问题：Notion 同步失败

**检查**：
1. 确认 Token 和 Database ID 正确
2. 确认 Integration 有权限访问数据库
3. 查看后端日志中的详细错误

## 📚 更多信息

- 详细配置说明：[Notion同步功能配置说明.md](./Notion同步功能配置说明.md)
- 实现总结：[Notion同步功能实现总结.md](./Notion同步功能实现总结.md)
- 可行性报告：[Notion同步功能可行性报告.md](./Notion同步功能可行性报告.md)

