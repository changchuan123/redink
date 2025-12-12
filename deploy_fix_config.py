#!/usr/bin/env python3

print("🔧 准备部署配置修复...")

# 确认配置文件内容
with open('text_providers.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

if 'api_key' in content and content.strip():
    print("✅ 本地配置文件包含 DeepSeek API Key")
else:
    print("❌ 本地配置文件缺少 API Key")
    exit(1)

# 验证 Dockerfile 路径
with open('Dockerfile', 'r', encoding='utf-8') as f:
    dockerfile = f.read()

if 'COPY text_providers.yaml ./text_providers.yaml' in dockerfile:
    print("✅ Dockerfile 配置正确")
else:
    print("❌ Dockerfile 配置错误")
    exit(1)

print("🚀 准备重新部署...")
print("请在 Zeabur 控制台中执行强制重新部署！")