#!/usr/bin/env python3
"""真实API调用测试 - 生成文案和标题"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import VideoTheme
from src.utils import ConfigLoader, print_section, print_step
from src.llm_client import LLMClient
from src.planner import VideoPlanner
from src.writer import ScriptWriter
from src.title_generator import TitleGenerator
from colorama import Fore, Style

print_section("真实API测试 - 生成短视频文案")

# 初始化
config = ConfigLoader()
api_key = config.get_env('OPENAI_API_KEY')
llm = LLMClient('openai', api_key, 'gpt-4-turbo-preview')

# 创建主题
theme = VideoTheme(topic="古代试毒官的一天")
print(f"主题: {Fore.CYAN}{theme.topic}{Style.RESET_ALL}\n")

# 步骤1: 智能策划
print_section("【步骤1】智能策划")
planner = VideoPlanner(config, llm)
style = planner.analyze_theme(theme)

print(f"\n{Fore.YELLOW}策划结果:{Style.RESET_ALL}")
print(f"风格类型: {style.style_type}")
print(f"叙事结构: {style.narrative_structure}")
print(f"情绪曲线: {' → '.join(style.emotional_arc[:3])}...")
print(f"选择理由: {style.reasoning[:100]}...")

# 步骤2: 文案创作
print_section("【步骤2】文案创作")
writer = ScriptWriter(config, llm)
script = writer.write_script(theme, style)

print(f"\n{Fore.GREEN}文案预览:{Style.RESET_ALL}\n")
print(script.content[:500])
print(f"\n... (共{script.word_count}字)\n")

# 步骤3: 标题生成
print_section("【步骤3】标题生成")
title_gen = TitleGenerator(config, llm)
titles = title_gen.generate_titles(script, count=5)

print(f"\n{Fore.GREEN}爆款标题:{Style.RESET_ALL}\n")
for i, title in enumerate(titles, 1):
    print(f"{i}. {Fore.CYAN}{title.title}{Style.RESET_ALL}")
    print(f"   评分: {title.score} | 钩子: {title.hook_type}")
    print(f"   理由: {title.reasoning[:60]}...\n")

# 保存结果
print_section("✅ 测试完成")
output_file = Path('output/scripts') / 'real_test_script.txt'
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"标题: {script.title}\n")
    f.write(f"风格: {style.style_type}\n")
    f.write(f"字数: {script.word_count}\n")
    f.write("=" * 60 + "\n\n")
    f.write(script.content)
    f.write("\n\n" + "=" * 60 + "\n")
    f.write("备选标题:\n")
    for i, t in enumerate(titles, 1):
        f.write(f"{i}. {t.title} ({t.score}分)\n")

print(f"\n{Fore.GREEN}文案已保存: {output_file}{Style.RESET_ALL}\n")
print(f"主题: {theme.topic}")
print(f"风格: {style.style_type}")
print(f"标题: {script.title}")
print(f"字数: {script.word_count}")

