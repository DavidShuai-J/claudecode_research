"""测试 Coze 国际版 API (api.coze.com)"""
import requests
import json

ACCESS_TOKEN = "pat_iRAbnGWILCaudRctPMkZ8fFGuH9xxoiz4CtHsGBhGwGlVrdgB3nS2o8KvOrOImrL"
BOT_ID = "7563596474257440807"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("测试 Coze 国际版 API (api.coze.com)")
print("=" * 60)

# 测试 1: 获取 Bot 列表
print("\n测试 1: 获取 Bot 列表 (api.coze.com)")
print("-" * 60)

try:
    response = requests.get(
        "https://api.coze.com/v1/bot/list",
        headers=headers,
        params={"page_size": 10, "page_num": 1},
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text[:500]}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 成功！使用 api.coze.com")
        if 'data' in result and 'bots' in result['data']:
            bots = result['data']['bots']
            print(f"\n找到 {len(bots)} 个 Bot:")
            for bot in bots:
                print(f"  Bot ID: {bot.get('bot_id', 'N/A')}")
                print(f"  Bot Name: {bot.get('name', 'N/A')}")
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

# 测试 2: Chat API (api.coze.com)
print("\n" + "=" * 60)
print("测试 2: Chat API (api.coze.com)")
print("-" * 60)

payload = {
    "bot_id": BOT_ID,
    "user_id": "123456789",
    "stream": False,
    "additional_messages": [
        {
            "content_type": "text",
            "role": "user",
            "type": "question",
            "content": "你好"
        }
    ]
}

try:
    response = requests.post(
        "https://api.coze.com/v3/chat",
        headers=headers,
        json=payload,
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text[:500]}")

    if response.status_code == 200:
        print("\n✅ Chat API 成功！")
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

# 测试 3: 尝试不带 bot_id 获取信息
print("\n" + "=" * 60)
print("测试 3: 获取空间信息")
print("-" * 60)

try:
    response = requests.get(
        "https://api.coze.com/v1/workspaces",
        headers=headers,
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text[:500]}")

    if response.status_code == 200:
        print("\n✅ 获取空间信息成功！")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"❌ 异常: {str(e)}")

print("\n" + "=" * 60)
print("结论")
print("=" * 60)
print("""
如果 api.coze.com 能正常工作，说明需要：
1. 修改 CozeClient 使用 api.coze.com 而不是 api.coze.cn
2. 获取正确的 bot_id 和 workflow_id

如果都失败，可能是：
1. Personal Access Token 权限不足
2. 需要在扣子平台重新配置 Token 权限
""")
