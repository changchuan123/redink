# Notion Token 重新生成步骤

## 测试结果
本地测试显示：**Token 无效（401 错误）**

虽然 `n8n-bot` 已经在数据库的连接列表中，但 Token 可能已过期或被撤销。

## 解决方案：重新生成 Token

### 步骤 1：访问 Notion Integration 设置

1. 打开：https://www.notion.so/my-integrations
2. 或：Notion → Settings & Members → Connections → Develop or manage integrations

### 步骤 2：找到 n8n-bot Integration

在 Integration 列表中找到 `n8n-bot`

### 步骤 3：查看/重置 Token

1. 点击 `n8n-bot` Integration
2. 在 **"Internal Integration Token"** 部分
3. 点击 **"Show"** 或 **"显示"** 查看当前 Token
4. 如果 Token 已过期，点击 **"Reset"** 或 **"重置"** 生成新 Token

### 步骤 4：复制新 Token

**重要：**
- 完整复制整个 Token（从 `ntn_` 开始到结尾）
- 不要有任何空格
- 不要遗漏任何字符

### 步骤 5：更新 Zeabur 环境变量

1. 登录 Zeabur 控制台
2. 进入你的项目
3. 找到 **Environment Variables**
4. 找到 `NOTION_INTEGRATION_TOKEN`
5. 点击编辑，粘贴新 Token
6. **确保没有前后空格**
7. 保存

### 步骤 6：重启服务

Zeabur 会自动重启，或手动重启服务

### 步骤 7：验证

重新生成一篇笔记，查看日志应该显示：
```
✅ Notion 同步服务初始化: database_id=2c771735..., token=ntn_3045...
📝 写入 Notion 数据库: title=...
✅ 已写入 Notion 数据库: 页面ID=..., URL=...
```

## 如果重新生成后仍然 401

### 检查 Integration 权限

1. 在 Integration 设置页面
2. 确保有以下权限：
   - ✅ **Read content**
   - ✅ **Update content**  
   - ✅ **Insert content**

### 检查数据库连接

1. 打开数据库：https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056
2. 点击右上角 **"..."** → **"Connections"**
3. 确认 `n8n-bot` 在列表中
4. 如果不在，点击 **"Add connections"** → 选择 `n8n-bot`

### 检查数据库 ID

确保 `NOTION_DATABASE_ID` 正确：
- 从数据库 URL 获取：`https://www.notion.so/Redink-2c771735fbc5802e8474d17cda149056`
- 数据库 ID 是最后一部分：`2c771735fbc5802e8474d17cda149056`

## 快速测试脚本

运行以下命令测试新 Token：

```bash
python3 test_notion_api.py
```

如果测试通过，会显示：
```
✅ 数据库查询成功！
✅ 页面创建成功！
```

