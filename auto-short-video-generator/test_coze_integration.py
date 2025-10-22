"""测试扣子(Coze) API集成"""
import sys
import logging
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.coze_client import CozeClient
from src.llm_client import LLMClient
from src.utils import ConfigLoader

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_coze_chat():
    """测试Coze Chat API"""
    print("\n" + "="*60)
    print("测试 1: Coze Chat API (文本生成)")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        access_token = config.get_env('COZE_ACCESS_TOKEN')
        bot_id = config.get('api.coze_bot_id')

        if not access_token:
            print("❌ 未设置 COZE_ACCESS_TOKEN")
            return False

        if not bot_id:
            print("❌ 未设置 api.coze_bot_id")
            return False

        # 创建客户端
        client = CozeClient(access_token=access_token, bot_id=bot_id)

        # 测试简单对话
        print("\n发送测试消息: '你好，请介绍一下明朝锦衣卫'")
        response = client.chat("你好，请介绍一下明朝锦衣卫", stream=False)

        print(f"\n✅ Coze Chat 响应:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_coze_llm_client():
    """测试通过LLMClient使用Coze"""
    print("\n" + "="*60)
    print("测试 2: LLMClient + Coze")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        access_token = config.get_env('COZE_ACCESS_TOKEN')
        bot_id = config.get('api.coze_bot_id')

        if not access_token or not bot_id:
            print("❌ 配置不完整，跳过测试")
            return False

        # 创建LLM客户端
        llm = LLMClient(
            provider='coze',
            api_key=access_token,
            bot_id=bot_id
        )

        # 测试文本生成
        prompt = "用一句话描述明朝锦衣卫的职责"
        print(f"\n发送提示词: '{prompt}'")

        response = llm.generate(prompt)

        print(f"\n✅ LLMClient 响应:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_coze_json_generation():
    """测试Coze JSON生成"""
    print("\n" + "="*60)
    print("测试 3: Coze JSON 生成")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        access_token = config.get_env('COZE_ACCESS_TOKEN')
        bot_id = config.get('api.coze_bot_id')

        if not access_token or not bot_id:
            print("❌ 配置不完整，跳过测试")
            return False

        # 创建LLM客户端
        llm = LLMClient(
            provider='coze',
            api_key=access_token,
            bot_id=bot_id
        )

        # 测试JSON生成
        prompt = """
请分析"明朝锦衣卫"这个主题，返回以下JSON格式：
{
    "theme": "主题名称",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "style_type": "适合的风格类型"
}
"""
        print(f"\n发送JSON请求...")

        response = llm.generate_json(prompt)

        print(f"\n✅ JSON 响应:")
        print("-" * 60)
        import json
        print(json.dumps(response, ensure_ascii=False, indent=2))
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_coze_image_generation():
    """测试Coze图像生成"""
    print("\n" + "="*60)
    print("测试 4: Coze Image Workflow")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        access_token = config.get_env('COZE_ACCESS_TOKEN')
        image_workflow_id = config.get('api.coze_image_workflow_id')

        if not access_token:
            print("❌ 未设置 COZE_ACCESS_TOKEN")
            return False

        if not image_workflow_id:
            print("❌ 未设置 api.coze_image_workflow_id")
            return False

        # 创建客户端
        client = CozeClient(
            access_token=access_token,
            image_workflow_id=image_workflow_id
        )

        # 测试图像生成
        prompt = "生成一朵红色的玫瑰花"
        print(f"\n发送图像生成请求: '{prompt}'")

        result = client.generate_image(prompt)

        print(f"\n✅ 图像生成结果:")
        print("-" * 60)
        print(result)
        print("-" * 60)

        if result.startswith('http'):
            print(f"\n✅ 获得图片URL: {result}")
        else:
            print(f"\n⚠️  返回的不是URL，可能需要进一步处理")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("扣子(Coze) API 集成测试")
    print("🚀" * 30)

    results = []

    # 测试1: Chat API
    results.append(("Coze Chat API", test_coze_chat()))

    # 测试2: LLMClient集成
    results.append(("LLMClient + Coze", test_coze_llm_client()))

    # 测试3: JSON生成
    results.append(("Coze JSON生成", test_coze_json_generation()))

    # 测试4: 图像生成
    results.append(("Coze图像生成", test_coze_image_generation()))

    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！Coze API集成成功！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置")


if __name__ == "__main__":
    main()
