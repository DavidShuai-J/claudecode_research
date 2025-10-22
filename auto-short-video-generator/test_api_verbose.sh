#!/bin/bash

# 从 .env 文件加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "=========================================="
echo "详细测试 1: Coze API"
echo "=========================================="
echo ""
echo "Token (前20字符): ${COZE_ACCESS_TOKEN:0:20}..."
echo "API URL: https://api.coze.cn/v3/chat"
echo ""
echo "发送请求..."
echo ""

curl -v -X POST 'https://api.coze.cn/v3/chat' \
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
  }' 2>&1 | head -50

echo -e "\n\n=========================================="
echo "详细测试 2: OpenAI API"
echo "=========================================="
echo ""
echo "API Key (前20字符): ${OPENAI_API_KEY:0:20}..."
echo "API URL: https://api.openai.com/v1/chat/completions"
echo ""
echo "发送请求..."
echo ""

curl -v -X POST 'https://api.openai.com/v1/chat/completions' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }' 2>&1 | head -50

echo -e "\n\n=========================================="
echo "测试 3: 检查 .env 文件配置"
echo "=========================================="
if [ -f .env ]; then
    echo "✅ .env 文件存在"
    echo ""
    echo "配置的变量（隐藏完整值）："
    echo "COZE_ACCESS_TOKEN: ${COZE_ACCESS_TOKEN:+已设置 (长度: ${#COZE_ACCESS_TOKEN})}"
    echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+已设置 (长度: ${#OPENAI_API_KEY})}"
else
    echo "❌ .env 文件不存在"
fi

echo -e "\n=========================================="
echo "测试完成"
echo "=========================================="
