#!/bin/bash

##
# Coze 插件 API 测试脚本
# 测试获取插件详情和调用插件工具
##

# 加载环境变量
source .env

echo "█████████████████████████████████████████████████████████████"
echo "█                                                           █"
echo "█     Coze 插件 API 测试工具                                █"
echo "█                                                           █"
echo "█████████████████████████████████████████████████████████████"
echo ""

if [ -z "$COZE_API_TOKEN" ]; then
    echo "❌ 错误: 未设置 COZE_API_TOKEN 环境变量"
    exit 1
fi

echo "✅ API Token: ${COZE_API_TOKEN:0:20}..."
echo ""

# 测试插件列表
declare -A PLUGINS
PLUGINS=(
    ["语音合成"]="$PLUGIN_VOICE_SYNTHESIS_ID"
    ["图像生成"]="$PLUGIN_IMAGE_GENERATION_ID"
    ["视频剪辑"]="$PLUGIN_VIDEO_EDIT_ID"
)

##
# 测试 1: 获取插件详情
##
echo "============================================================"
echo "测试 1: 获取插件详情"
echo "============================================================"
echo ""

PLUGIN_NAME="语音合成"
PLUGIN_ID="${PLUGINS[$PLUGIN_NAME]}"

echo "🔍 查询插件: $PLUGIN_NAME (ID: $PLUGIN_ID)"
echo ""

# 尝试不同的 API 端点
API_ENDPOINTS=(
    "https://api.coze.cn/v1/plugins/$PLUGIN_ID"
    "https://api.coze.cn/open_api/v1/plugins/$PLUGIN_ID"
    "https://api.coze.cn/v1/plugin/$PLUGIN_ID"
    "https://api.coze.com/v1/plugins/$PLUGIN_ID"
    "https://api.coze.com/open_api/v1/plugins/$PLUGIN_ID"
)

for endpoint in "${API_ENDPOINTS[@]}"; do
    echo "📡 尝试端点: $endpoint"

    response=$(curl -s -w "\n%{http_code}" -X GET "$endpoint" \
        -H "Authorization: Bearer $COZE_API_TOKEN" \
        -H "Content-Type: application/json")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "   状态码: $http_code"

    if [ "$http_code" -eq 200 ]; then
        echo "   ✅ 成功获取插件详情！"
        echo ""
        echo "📋 插件详情:"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        echo ""
        break
    elif [ "$http_code" -eq 401 ]; then
        echo "   ❌ 认证失败 (401)"
        echo "   响应: $body"
    elif [ "$http_code" -eq 403 ]; then
        echo "   ❌ 权限不足 (403)"
        echo "   响应: $body"
    elif [ "$http_code" -eq 404 ]; then
        echo "   ⚠️  未找到 (404)"
    else
        echo "   ⚠️  其他错误"
        echo "   响应: ${body:0:200}"
    fi

    echo ""
    sleep 1
done

echo ""
echo "============================================================"
echo "测试 2: 调用插件工具"
echo "============================================================"
echo ""

echo "🎙️  测试: 调用语音合成插件"
echo ""

# 尝试不同的调用端点
CALL_ENDPOINTS=(
    "https://api.coze.cn/v1/plugins/$PLUGIN_ID/tools/call"
    "https://api.coze.cn/v1/plugins/$PLUGIN_ID/call"
    "https://api.coze.cn/open_api/v1/plugins/$PLUGIN_ID/tools/call"
    "https://api.coze.com/v1/plugins/$PLUGIN_ID/tools/call"
)

# 测试参数
TEST_PAYLOAD='{
  "tool_name": "synthesize_voice",
  "tool_parameters": {
    "text": "你好，这是一个测试",
    "voice": "gentle_female",
    "speed": 0.9
  }
}'

for endpoint in "${CALL_ENDPOINTS[@]}"; do
    echo "📡 尝试端点: $endpoint"

    response=$(curl -s -w "\n%{http_code}" -X POST "$endpoint" \
        -H "Authorization: Bearer $COZE_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$TEST_PAYLOAD")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "   状态码: $http_code"

    if [ "$http_code" -eq 200 ]; then
        echo "   ✅ 成功调用插件！"
        echo ""
        echo "📋 调用结果:"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        echo ""
        break
    elif [ "$http_code" -eq 401 ]; then
        echo "   ❌ 认证失败 (401)"
    elif [ "$http_code" -eq 403 ]; then
        echo "   ❌ 权限不足 (403)"
    elif [ "$http_code" -eq 404 ]; then
        echo "   ⚠️  未找到 (404)"
    else
        echo "   ⚠️  其他错误"
        echo "   响应: ${body:0:200}"
    fi

    echo ""
    sleep 1
done

echo ""
echo "============================================================"
echo "测试 3: 测试已知可用的 Workflow API"
echo "============================================================"
echo ""

echo "🔧 调用 Coze Workflow API (文案生成)"
echo ""

curl -X POST 'https://api.coze.cn/v1/workflow/run' \
  -H "Authorization: Bearer $COZE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"workflow_id\": \"$COZE_WORKFLOW_ID\",
    \"parameters\": {
      \"input\": \"请为《活着》这本书写一段戳心的文案\"
    }
  }" | jq . 2>/dev/null

echo ""
echo ""
echo "█████████████████████████████████████████████████████████████"
echo "█                                                           █"
echo "█     测试完成                                              █"
echo "█                                                           █"
echo "█████████████████████████████████████████████████████████████"
echo ""
