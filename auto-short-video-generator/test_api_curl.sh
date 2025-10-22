#!/bin/bash

# 从 .env 文件加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 检查环境变量是否设置
if [ -z "$COZE_ACCESS_TOKEN" ]; then
    echo "❌ 错误: COZE_ACCESS_TOKEN 未设置"
    echo "请在 .env 文件中配置 COZE_ACCESS_TOKEN"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 错误: OPENAI_API_KEY 未设置"
    echo "请在 .env 文件中配置 OPENAI_API_KEY"
    exit 1
fi

echo "=========================================="
echo "测试 1: Coze API"
echo "=========================================="
echo ""

curl -X POST 'https://api.coze.cn/v3/chat' \
  -H "Authorization: Bearer $COZE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "7563596474257440807",
    "user_id": "test_user",
    "stream": false,
    "additional_messages": [{
      "content_type": "text",
      "role": "user",
      "type": "question",
      "content": "你好"
    }]
  }'

echo -e "\n\n=========================================="
echo "测试 2: OpenAI API"
echo "=========================================="
echo ""

curl -X POST 'https://api.openai.com/v1/chat/completions' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }'

echo -e "\n\n=========================================="
echo "测试完成"
echo "=========================================="
