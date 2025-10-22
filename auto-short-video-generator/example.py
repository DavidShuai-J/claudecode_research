#!/usr/bin/env python3
"""使用示例 - 展示如何使用API"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.workflow import VideoPipeline
from src.models import VideoTheme


def example_full_pipeline():
    """完整流程示例"""
    print("=== 完整流程示例 ===\n")

    # 初始化Pipeline
    pipeline = VideoPipeline()

    # 生成视频
    project = pipeline.generate(
        topic="明朝锦衣卫的秘密任务",
        save_intermediate=True
    )

    print(f"\n视频生成完成！")
    print(f"输出路径: {project.output_path}")
    print(f"标题: {project.script.title}")


def example_text_only():
    """仅生成文案示例"""
    print("=== 仅生成文案示例 ===\n")

    pipeline = VideoPipeline()

    # 创建主题
    theme = VideoTheme(topic="古代特殊职业：仵作")

    # 步骤1: 策划
    style = pipeline.planner.analyze_theme(theme)
    print(f"风格类型: {style.style_type}")
    print(f"叙事结构: {style.narrative_structure}")

    # 步骤2: 创作文案
    script = pipeline.writer.write_script(theme, style)
    print(f"\n文案内容:\n{script.content}")

    # 步骤3: 生成标题
    titles = pipeline.title_generator.generate_titles(script)
    print(f"\n候选标题:")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title.title} (评分: {title.score})")


def example_audio_only():
    """仅生成音频示例"""
    print("=== 仅生成音频示例 ===\n")

    pipeline = VideoPipeline()

    # 创建主题
    theme = VideoTheme(topic="历史奇案：大明奇案")

    # 生成文案
    style = pipeline.planner.analyze_theme(theme)
    script = pipeline.writer.write_script(theme, style)

    # 生成音频
    audio_segments = pipeline.tts_engine.generate_audio(script, output_name="test_audio")

    print(f"\n音频生成完成！")
    print(f"片段数: {len(audio_segments)}")
    print(f"总时长: {sum(seg.duration for seg in audio_segments):.2f}秒")


def example_custom_theme():
    """自定义主题示例"""
    print("=== 自定义主题示例 ===\n")

    pipeline = VideoPipeline()

    # 自定义主题（带关键词）
    theme = VideoTheme(
        topic="明朝锦衣卫",
        keywords=["权力", "忠诚", "秘密", "背叛"],
        target_emotion="震撼"
    )

    # 生成视频
    project = pipeline.generate(topic=theme.topic)

    print(f"\n完成！输出: {project.output_path}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='使用示例')
    parser.add_argument(
        'example',
        choices=['full', 'text', 'audio', 'custom'],
        help='选择示例类型'
    )

    args = parser.parse_args()

    if args.example == 'full':
        example_full_pipeline()
    elif args.example == 'text':
        example_text_only()
    elif args.example == 'audio':
        example_audio_only()
    elif args.example == 'custom':
        example_custom_theme()
