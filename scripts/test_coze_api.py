#!/usr/bin/env python3
"""
Coze API 测试脚本
测试 Workflow API 和 MCP 插件调用
"""

import os
import json
import requests
from pathlib import Path

# 加载环境变量
def load_env():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value

load_env()

API_TOKEN = os.getenv('COZE_API_TOKEN')
WORKFLOW_ID = os.getenv('COZE_WORKFLOW_ID')
PLUGIN_VOICE_ID = os.getenv('PLUGIN_VOICE_SYNTHESIS_ID')
PLUGIN_IMAGE_ID = os.getenv('PLUGIN_IMAGE_GENERATION_ID')

# 代理配置（自动从环境变量读取）
proxies = {
    'http': os.getenv('HTTP_PROXY'),
    'https': os.getenv('HTTPS_PROXY'),
} if os.getenv('HTTPS_PROXY') else None

# 请求头
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json',
}

def test1_workflow_api():
    """测试 1: Workflow API"""
    print('\n' + '=' * 60)
    print('测试 1: Coze Workflow API (文案生成)')
    print('=' * 60)

    try:
        url = 'https://api.coze.cn/v1/workflow/run'
        payload = {
            'workflow_id': WORKFLOW_ID,
            'parameters': {
                'input': '请为《活着》这本书写一段超戳心的文案，100字以内'
            }
        }

        print(f'\n📡 请求 URL: {url}')
        print(f'📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}')

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=30
        )

        print(f'\n✅ 成功调用 Workflow API')
        print(f'状态码: {response.status_code}')
        print('\n响应数据:')
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))

        return response.json()

    except Exception as e:
        print(f'\n❌ 失败: {str(e)}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'状态码: {e.response.status_code}')
            print(f'响应: {e.response.text}')
        return None

def test2_list_tools():
    """测试 2: MCP 插件 - 列出工具"""
    print('\n' + '=' * 60)
    print('测试 2: MCP 插件 - 列出语音合成工具')
    print('=' * 60)

    try:
        url = f'https://mcp.coze.cn/v1/plugins/{PLUGIN_VOICE_ID}'
        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/list',
            'params': {},
            'id': 1
        }

        print(f'\n📡 请求 URL: {url}')
        print(f'📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}')

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=30
        )

        print(f'\n✅ 成功调用 MCP API')
        print(f'状态码: {response.status_code}')
        print('\n响应数据:')
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))

        return response.json()

    except Exception as e:
        print(f'\n❌ 失败: {str(e)}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'状态码: {e.response.status_code}')
            try:
                print(f'响应: {json.dumps(e.response.json(), ensure_ascii=False, indent=2)}')
            except:
                print(f'响应: {e.response.text}')
        return None

def test3_call_tool():
    """测试 3: MCP 插件 - 调用工具"""
    print('\n' + '=' * 60)
    print('测试 3: MCP 插件 - 调用语音合成工具')
    print('=' * 60)

    try:
        url = f'https://mcp.coze.cn/v1/plugins/{PLUGIN_VOICE_ID}'
        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'synthesize_voice',
                'arguments': {
                    'text': '你好，这是一个测试',
                    'voice': 'gentle_female',
                    'speed': 0.9
                }
            },
            'id': 2
        }

        print(f'\n📡 请求 URL: {url}')
        print(f'📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}')

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=30
        )

        print(f'\n✅ 成功调用 MCP 工具')
        print(f'状态码: {response.status_code}')
        print('\n响应数据:')
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))

        return response.json()

    except Exception as e:
        print(f'\n❌ 失败: {str(e)}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'状态码: {e.response.status_code}')
            try:
                print(f'响应: {json.dumps(e.response.json(), ensure_ascii=False, indent=2)}')
            except:
                print(f'响应: {e.response.text}')
        return None

def test4_call_image_generation():
    """测试 4: 图像生成工具"""
    print('\n' + '=' * 60)
    print('测试 4: MCP 插件 - 调用图像生成工具')
    print('=' * 60)

    try:
        url = f'https://mcp.coze.cn/v1/plugins/{PLUGIN_IMAGE_ID}'
        payload = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'generate_image',
                'arguments': {
                    'prompt': '低饱和度动漫风格的书籍背景图，温馨唯美',
                    'width': 1920,
                    'height': 1080
                }
            },
            'id': 3
        }

        print(f'\n📡 请求 URL: {url}')
        print(f'📦 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}')

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=60  # 图像生成可能需要更长时间
        )

        print(f'\n✅ 成功调用图像生成工具')
        print(f'状态码: {response.status_code}')
        print('\n响应数据:')
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))

        return response.json()

    except Exception as e:
        print(f'\n❌ 失败: {str(e)}')
        if hasattr(e, 'response') and e.response is not None:
            print(f'状态码: {e.response.status_code}')
            try:
                print(f'响应: {json.dumps(e.response.json(), ensure_ascii=False, indent=2)}')
            except:
                print(f'响应: {e.response.text}')
        return None

def main():
    print('\n' + '█' * 60)
    print('█' + ' ' * 58 + '█')
    print('█     Coze API 测试工具 (Python)                         █')
    print('█' + ' ' * 58 + '█')
    print('█' * 60)

    print(f'\n✅ API Token: {API_TOKEN[:20] if API_TOKEN else "未设置"}...')
    print(f'✅ 代理: {"已配置" if proxies else "未配置"}')
    if proxies and proxies.get('https'):
        print(f'   HTTPS_PROXY: {proxies["https"][:60]}...')

    results = {}

    # 运行所有测试
    results['workflow'] = test1_workflow_api()
    results['list_tools'] = test2_list_tools()
    results['call_tool'] = test3_call_tool()
    results['image_gen'] = test4_call_image_generation()

    # 总结
    print('\n' + '█' * 60)
    print('█' + ' ' * 58 + '█')
    print('█     测试完成                                           █')
    print('█' + ' ' * 58 + '█')
    print('█' * 60)

    print('\n📊 测试总结:')
    print(f'   Workflow API:     {"✅ 成功" if results["workflow"] else "❌ 失败"}')
    print(f'   List Tools:       {"✅ 成功" if results["list_tools"] else "❌ 失败"}')
    print(f'   Call Tool:        {"✅ 成功" if results["call_tool"] else "❌ 失败"}')
    print(f'   Image Generation: {"✅ 成功" if results["image_gen"] else "❌ 失败"}')
    print('')

if __name__ == '__main__':
    main()
