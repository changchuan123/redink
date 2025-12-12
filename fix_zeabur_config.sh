#!/bin/bash

echo "🔧 修复 Zeabur 部署配置..."

# 确保 text_providers.yaml 存在且有正确内容
if [ ! -f "text_providers.yaml" ]; then
    echo "❌ text_providers.yaml 文件不存在"
    exit 1
fi

# 验证配置文件格式
python3 -c "
import yaml
try:
    with open('text_providers.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print('✅ 配置文件格式正确')

    active = config.get('active_provider')
    deepseek = config.get('providers', {}).get('deepseek', {})

    print(f'激活服务商: {active}')
    print(f'DeepSeek API Key: {\"已配置\" if deepseek.get(\"api_key\") else \"❌ 未配置\"}')
    print(f'DeepSeek Base URL: {deepseek.get(\"base_url\")}')

    # 验证 URL 生成
    base_url = deepseek.get('base_url', '').rstrip('/').rstrip('/v1')
    endpoint = deepseek.get('endpoint_type', '/v1/chat/completions')
    final_url = f'{base_url}{endpoint}'
    print(f'最终端点: {final_url}')

    if final_url != 'https://api.deepseek.com/v1/chat/completions':
        print('❌ DeepSeek 端点配置错误')
        exit(1)

    print('✅ 所有配置验证通过')
except Exception as e:
    print(f'❌ 配置验证失败: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ 配置文件验证成功"
    echo "🚀 可以重新部署到 Zeabur"
else
    echo "❌ 配置文件验证失败"
    echo "请检查配置文件"
fi