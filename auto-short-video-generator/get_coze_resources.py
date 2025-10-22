"""获取用户的 Bot 和 Workspace 信息"""
import requests
import json

ACCESS_TOKEN = "pat_iRAbnGWILCaudRctPMkZ8fFGuH9xxoiz4CtHsGBhGwGlVrdgB3nS2o8KvOrOImrL"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("获取 Coze API 资源列表")
print("=" * 60)

# 测试 1: 获取 Bot 列表
print("\n测试 1: 获取 Bot 列表")
print("-" * 60)

try:
    # Coze API v3 获取 Bot 列表
    response = requests.get(
        "https://api.coze.cn/v1/bot/list",
        headers=headers,
        params={"page_size": 10, "page_num": 1},
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 获取 Bot 列表成功！")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if 'data' in result and 'bots' in result['data']:
            bots = result['data']['bots']
            print(f"\n找到 {len(bots)} 个 Bot:")
            for bot in bots:
                print(f"  - Bot Name: {bot.get('name', 'N/A')}")
                print(f"    Bot ID: {bot.get('bot_id', 'N/A')}")
                print(f"    Description: {bot.get('description', 'N/A')[:50]}...")
                print()
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

# 测试 2: 获取 Workspace 列表
print("\n" + "=" * 60)
print("测试 2: 获取 Workspace 信息")
print("-" * 60)

try:
    response = requests.get(
        "https://api.coze.cn/v1/workspaces",
        headers=headers,
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 获取 Workspace 成功！")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

# 测试 3: 获取 Workflow 列表（如果有 space_id）
print("\n" + "=" * 60)
print("测试 3: 测试简单的 API 调用")
print("-" * 60)

# 测试一个简单的 endpoint
try:
    response = requests.get(
        "https://api.coze.cn/v1/audio/voices",
        headers=headers,
        timeout=30
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容:\n{response.text[:500]}")

    if response.status_code == 200:
        print("\n✅ Token 有效！")
    else:
        print(f"❌ 失败: {response.status_code}")

except Exception as e:
    print(f"❌ 异常: {str(e)}")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
如果上述测试成功，你应该能看到：
1. 你的 Bot 列表和对应的 bot_id
2. 你的 Workspace 信息和 space_id
3. Token 有效性确认

请将正确的 bot_id 更新到 config/config.yaml 中的 api.coze_bot_id
如果需要使用 Workflow，还需要获取 workflow_id
""")
