# Notion Token 401 错误排查指南

## 错误信息
```
Notion API 返回错误: 401 - {"object":"error","status":401,"code":"unauthorized","message":"API token is invalid."}
```

## 问题原因
401 错误表示 Notion API Token 无效。可能的原因：

1. **Token 未正确设置**：Zeabur 环境变量中未设置或设置错误
2. **Token 格式错误**：有多余的空格、换行符或特殊字符
3. **Token 已过期或被撤销**：在 Notion 中重新生成了 Token
4. **Integration 没有权限**：Notion Integration 没有访问数据库的权限

## 排查步骤

### 第一步：检查 Zeabur 环境变量

1. 登录 Zeabur 控制台
2. 进入你的项目
3. 找到 **Environment Variables**（环境变量）设置
4. 检查以下变量：

```
NOTION_INTEGRATION_TOKEN=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
NOTION_DATABASE_ID=2c771735fbc5802e8474d17cda149056
```

**重要检查点：**
- ✅ Token 值是否正确（完整复制，没有遗漏）
- ✅ 没有多余的空格（前后都不能有空格）
- ✅ 没有换行符
- ✅ 变量名完全正确（大小写敏感）

### 第二步：验证 Token 格式

正确的 Notion Token 格式：
- 应该以 `secret_` 或 `ntn_` 开头
- 你提供的 Token：`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` ✅ 格式正确

### 第三步：检查 Notion Integration 权限

1. 访问 Notion Integration 设置：
   - https://www.notion.so/my-integrations
   - 或：Notion → Settings & Members → Connections → Develop or manage integrations

2. 找到你的 Integration：`n8n-bot`

3. 检查 Integration 是否有以下权限：
   - ✅ **Read content**（读取内容）
   - ✅ **Update content**（更新内容）
   - ✅ **Insert content**（插入内容）

4. **重要**：确保 Integration 已连接到你的数据库
   - 打开你的 Notion 数据库：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056
   - 点击右上角的 **"..."** 菜单
   - 选择 **"Connections"** 或 **"连接"**
   - 确保 `n8n-bot` 已连接（如果没有，点击添加）

### 第四步：重新生成 Token（如果需要）

如果 Token 可能已过期或被撤销：

1. 访问：https://www.notion.so/my-integrations
2. 找到 `n8n-bot` Integration
3. 点击 **"Show"** 或 **"显示"** 查看 Token
4. 如果 Token 已过期，点击 **"Reset"** 或 **"重置"** 生成新 Token
5. **复制新 Token**（完整复制，不要遗漏）
6. 在 Zeabur 中更新 `NOTION_INTEGRATION_TOKEN` 环境变量
7. **重启服务**（Zeabur 会自动重启）

### 第五步：验证数据库 ID

确保 `NOTION_DATABASE_ID` 正确：

1. 打开数据库：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056
2. 数据库 ID 是 URL 中的最后一部分：`2c771735fbc5802e8474d17cda149056`
3. 确保 Zeabur 中的 `NOTION_DATABASE_ID` 值完全匹配（没有多余字符）

## 快速修复步骤

### 方法 1：重新设置环境变量

1. 在 Zeabur 中删除 `NOTION_INTEGRATION_TOKEN` 环境变量
2. 重新添加，确保：
   - 变量名：`NOTION_INTEGRATION_TOKEN`
   - 变量值：从 Notion 完整复制 Token（`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`）
   - **不要有任何空格或换行**
3. 保存并等待服务重启

### 方法 2：检查 Integration 连接

1. 打开数据库：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056
2. 点击右上角 **"..."** → **"Connections"**
3. 如果 `n8n-bot` 未连接，点击添加
4. 确保有 **Read**、**Update**、**Insert** 权限

## 验证修复

修复后，重新生成一篇笔记，查看 Zeabur 日志：

**成功日志应该显示：**
```
✅ Notion 同步服务初始化: database_id=2c771735..., token=ntn_3045...
📝 写入 Notion 数据库: title=...
✅ 已写入 Notion 数据库: 页面ID=..., URL=...
```

**如果还有 401 错误，日志会显示：**
```
❌ Notion API Token 无效！
   请检查：
   1. Zeabur 环境变量 NOTION_INTEGRATION_TOKEN 是否正确设置
   2. Token 是否有多余的空格或换行符
   3. Token 是否已过期或被撤销
   4. Notion Integration 是否有访问数据库的权限
   Token 前缀: ntn_3045...
```

## 常见问题

### Q: Token 格式看起来正确，为什么还是 401？
A: 最常见的原因是：
1. **Integration 未连接到数据库**（最重要！）
2. Token 在 Zeabur 中有多余空格
3. Token 已过期，需要重新生成

### Q: 如何确认 Integration 已连接？
A: 
1. 打开数据库页面
2. 点击右上角 **"..."** → **"Connections"**
3. 应该能看到 `n8n-bot` 在连接列表中

### Q: 可以重新生成 Token 吗？
A: 可以，但需要：
1. 在 Notion 中重置 Token
2. 在 Zeabur 中更新环境变量
3. 重启服务

## 联系支持

如果以上步骤都无法解决，请提供：
1. Zeabur 日志中的完整错误信息
2. Token 前缀（前 10 个字符，如：`ntn_3045...`）
3. 确认 Integration 是否已连接到数据库

