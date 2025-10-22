"""测试 OpenAI API 集成"""
import sys
import logging
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.llm_client import LLMClient
from src.utils import ConfigLoader

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_openai_text_generation():
    """测试 OpenAI 文本生成"""
    print("\n" + "="*60)
    print("测试 1: OpenAI 文本生成")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        api_key = config.get_env('OPENAI_API_KEY')

        if not api_key:
            print("❌ 未设置 OPENAI_API_KEY")
            return False

        # 创建 LLM 客户端
        llm = LLMClient(
            provider='openai',
            api_key=api_key,
            model='gpt-4-turbo-preview'
        )

        # 测试简单文本生成
        prompt = "用一句话介绍明朝锦衣卫的职责"
        print(f"\n发送提示词: '{prompt}'")

        response = llm.generate(prompt, max_tokens=200)

        print(f"\n✅ OpenAI 响应:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_json_generation():
    """测试 OpenAI JSON 生成"""
    print("\n" + "="*60)
    print("测试 2: OpenAI JSON 生成")
    print("="*60)

    try:
        # 加载配置
        config = ConfigLoader()
        api_key = config.get_env('OPENAI_API_KEY')

        if not api_key:
            print("❌ 未设置 OPENAI_API_KEY")
            return False

        # 创建 LLM 客户端
        llm = LLMClient(
            provider='openai',
            api_key=api_key,
            model='gpt-4-turbo-preview'
        )

        # 测试 JSON 生成
        prompt = """
请分析"明朝锦衣卫"这个主题，返回以下JSON格式：
{
    "theme": "主题名称",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "style_type": "适合的风格类型",
    "target_audience": "目标受众"
}
"""
        print(f"\n发送 JSON 请求...")

        response = llm.generate_json(prompt, max_tokens=500)

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


def test_dalle_image_generation():
    """测试 DALL-E 图像生成"""
    print("\n" + "="*60)
    print("测试 3: DALL-E 3 图像生成")
    print("="*60)

    try:
        from openai import OpenAI
        import os

        # 加载配置
        config = ConfigLoader()
        api_key = config.get_env('OPENAI_API_KEY')

        if not api_key:
            print("❌ 未设置 OPENAI_API_KEY")
            return False

        client = OpenAI(api_key=api_key)

        # 测试图像生成
        prompt = "A historical Chinese scene showing Ming Dynasty Jinyiwei (royal guards) in traditional uniform, cinematic style"
        print(f"\n发送图像生成请求...")
        print(f"提示词: {prompt}")

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        print(f"\n✅ DALL-E 3 图像生成成功!")
        print("-" * 60)
        print(f"图像 URL: {image_url}")
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("OpenAI API 集成测试")
    print("🚀" * 30)

    results = []

    # 测试1: 文本生成
    results.append(("OpenAI 文本生成", test_openai_text_generation()))

    # 测试2: JSON生成
    results.append(("OpenAI JSON生成", test_openai_json_generation()))

    # 测试3: 图像生成
    results.append(("DALL-E 3 图像生成", test_dalle_image_generation()))

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
        print("\n🎉 所有测试通过！OpenAI API 集成成功！")
        print("\n下一步：运行完整的视频生成测试")
        print("命令：python main.py \"明朝锦衣卫\"")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置")


if __name__ == "__main__":
    main()
