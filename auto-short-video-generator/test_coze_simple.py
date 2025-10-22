"""简单测试 Coze API - 使用原始 curl 格式"""
import requests
import json

# 配置
ACCESS_TOKEN = "cztei_lvae6PbLhkIHRcHkT4xiQ4X8gPfEwXClxFqwZpP7dhfOYuoBeS2khIwDTZJllefQg"
BOT_ID = "7563596474257440807"
IMAGE_WORKFLOW_ID = "7563924661450457088"

print("=" * 60)
print("测试 1: Coze Chat API (原始格式)")
print("=" * 60)

# 测试 Chat API
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "bot_id": BOT_ID,
    "user_id": "123456789",
    "stream": False,
    "additional_messages": [
        {
            "content_type": "text",
            "role": "user",
            "type": "question",
            "content": "你好啊"
        }
    ],
    "parameters": {}
}

print(f"\nAPI URL: https://api.coze.cn/v3/chat")
print(f"Headers: {json.dumps(headers, indent=2)}")
print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(
        "https://api.coze.cn/v3/chat",
        headers=headers,
        json=payload,
        timeout=30
    )

    print(f"\n状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应内容: {response.text}")

    if response.status_code == 200:
        print("\n✅ Chat API 调用成功！")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Chat API 调用失败: {response.status_code}")

except Exception as e:
    print(f"\n❌ 异常: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试 2: Coze Workflow API (图像生成)")
print("=" * 60)

# 测试 Workflow API
workflow_payload = {
    "workflow_id": IMAGE_WORKFLOW_ID,
    "parameters": {
        "input": "生成一朵花"
    }
}

print(f"\nAPI URL: https://api.coze.cn/v1/workflow/run")
print(f"Payload: {json.dumps(workflow_payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(
        "https://api.coze.cn/v1/workflow/run",
        headers=headers,
        json=workflow_payload,
        timeout=30
    )

    print(f"\n状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

    if response.status_code == 200:
        print("\n✅ Workflow API 调用成功！")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ Workflow API 调用失败: {response.status_code}")

except Exception as e:
    print(f"\n❌ 异常: {str(e)}")
    import traceback
    traceback.print_exc()
