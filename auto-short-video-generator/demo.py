#!/usr/bin/env python3
"""简化演示 - 不需要API密钥"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import VideoTheme, StyleAnalysis, Script
from src.utils import print_section, print_step
from colorama import Fore, Style, init

init(autoreset=True)

def demo_workflow():
    """演示完整工作流（模拟数据）"""
    
    print_section("短视频自动生成工具 - 演示模式")
    
    # 1. 主题输入
    print_section("【步骤1/7】主题输入")
    theme = VideoTheme(topic="明朝锦衣卫")
    print(f"主题: {Fore.CYAN}{theme.topic}{Style.RESET_ALL}")
    print_step("主题接收完成", "完成")
    
    # 2. 智能策划（模拟）
    print_section("【步骤2/7】智能策划")
    print_step("分析主题，生成风格策略")
    
    style = StyleAnalysis(
        style_type="极端人性抉择",
        narrative_structure="第二人称强代入 → 身份设定 → 危机爆发 → 道德困境 → 真相反转 → 宿命结尾",
        emotional_arc=["震撼开场", "紧张升级", "希望破灭", "绝望抉择", "真相震撼", "深刻思考"],
        key_elements=["权力斗争", "忠诚与背叛", "生死抉择", "家国情怀"],
        reasoning="明朝锦衣卫主题最适合'极端人性抉择'风格，能够展现特务身份下的道德困境"
    )
    
    print(f"{Fore.YELLOW}风格类型: {style.style_type}{Style.RESET_ALL}")
    print(f"叙事结构: {style.narrative_structure}")
    print(f"情绪曲线: {' → '.join(style.emotional_arc)}")
    print_step("策划完成", "完成")
    
    # 3. 文案创作（模拟）
    print_section("【步骤3/7】文案创作")
    print_step("创作口播文案")
    
    script_content = """你是大明锦衣卫，
今夜的任务是抓捕一名谋逆重犯。

当你冲进那间破旧的茅屋，
火把照亮了那张熟悉的面孔时，
你的手开始颤抖。

那是你的父亲。

他被控与倭寇勾结，
证据确凿，罪无可恕。
按照大明律，
谋逆者，夷三族。

你想起十年前，
父亲送你进锦衣卫时说的话：
"忠君报国，至死不渝。"

现在，你必须做出选择。
抓他，你就是忠臣。
放他，你就是逆贼。

父亲看着你，眼中没有恐惧，
只有平静。
他说："动手吧，孩子。
你从穿上这身飞鱼服的那天起，
就不再是我的儿子。"

你举起了绣春刀。

三天后，刑场上，
你亲手执行了父亲的死刑。
皇帝嘉奖了你的忠诚，
赐你千户之职。

但从那天起，
你再也没有做过一个完整的梦。

这就是大明锦衣卫的宿命。
忠与孝，
从来都是一道无解的选择题。"""

    script = Script(
        title="",  # 待生成
        content=script_content,
        segments=script_content.split('\n\n'),
        word_count=len(script_content),
        style_type=style.style_type,
        keywords=["锦衣卫", "忠诚", "父亲", "选择", "宿命"]
    )
    
    print(f"{Fore.GREEN}文案预览:{Style.RESET_ALL}\n")
    print(script_content[:200] + "...")
    print(f"\n{Fore.YELLOW}字数: {script.word_count} | 段落: {len(script.segments)}{Style.RESET_ALL}")
    print_step("文案创作完成", "完成")
    
    # 4. 标题生成（模拟）
    print_section("【步骤4/7】标题生成")
    print_step("生成爆款标题候选")
    
    titles = [
        ("锦衣卫抓到自己亲爹，皇帝却下令必须杀", 95, "强冲突"),
        ("你是锦衣卫，要抓的逆贼竟是你父亲", 92, "强设问+强冲突"),
        ("忠与孝的终极选择，他举起了绣春刀", 88, "强悬念"),
        ("这个锦衣卫亲手处决了父亲，却升了官", 85, "强对比"),
        ("大明最残酷的选择题：救父还是忠君", 83, "强设问")
    ]
    
    print(f"{Fore.GREEN}标题候选:{Style.RESET_ALL}\n")
    for i, (title, score, hook_type) in enumerate(titles, 1):
        print(f"{i}. {Fore.CYAN}{title}{Style.RESET_ALL}")
        print(f"   评分: {score} | 钩子: {hook_type}\n")
    
    script.title = titles[0][0]
    print_step("标题生成完成", "完成")
    
    # 5. 语音合成（模拟）
    print_section("【步骤5/7】语音合成")
    print_step("生成语音音频（演示模式：跳过）")
    print(f"{Fore.YELLOW}⚠️  演示模式：TTS需要实际运行时生成{Style.RESET_ALL}")
    print(f"预计生成: {len(script.segments)}个音频片段")
    print(f"预计时长: 约2分30秒")
    print_step("语音合成（已跳过）", "完成")
    
    # 6. 图片生成（模拟）
    print_section("【步骤6/7】图片生成")
    print_step("生成视觉素材（演示模式：跳过）")
    
    scenes = [
        "锦衣卫深夜执行任务，火把照亮破旧茅屋",
        "锦衣卫发现犯人是自己父亲，震惊表情",
        "父子对峙，绣春刀与眼泪",
        "刑场，锦衣卫亲手执刑",
        "孤独的锦衣卫，夜不能寐"
    ]
    
    print(f"{Fore.GREEN}场景描述:{Style.RESET_ALL}\n")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene}")
    
    print(f"\n{Fore.YELLOW}⚠️  演示模式：图片生成需要DALL-E API{Style.RESET_ALL}")
    print(f"预计生成: {len(scenes)}张历史场景图")
    print_step("图片生成（已跳过）", "完成")
    
    # 7. 字幕和视频合成（模拟）
    print_section("【步骤7/7】字幕生成与视频合成")
    print_step("生成字幕文件（演示模式：跳过）")
    print_step("合成最终视频（演示模式：跳过）")
    
    print(f"\n{Fore.YELLOW}⚠️  演示模式：视频合成需要FFmpeg和完整素材{Style.RESET_ALL}")
    print(f"输出格式: MP4 (1080x1920)")
    print(f"包含: 视频 + 音频 + 字幕")
    print_step("视频合成（已跳过）", "完成")
    
    # 最终总结
    print_section("✅ 演示完成！")
    
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"生成摘要")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    print(f"主题: {theme.topic}")
    print(f"风格: {style.style_type}")
    print(f"\n标题: {Fore.CYAN}{script.title}{Style.RESET_ALL}")
    print(f"文案字数: {script.word_count}")
    print(f"预计时长: 2分30秒")
    print(f"场景数: {len(scenes)}")
    
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"💡 完整运行说明")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    print("要生成真实视频，需要：")
    print("1. 配置.env文件，填入OPENAI_API_KEY")
    print("2. 安装FFmpeg: sudo apt-get install ffmpeg")
    print("3. 安装完整依赖: pip install -r requirements.txt")
    print("4. 运行: python main.py \"明朝锦衣卫\"")
    
    print(f"\n{Fore.GREEN}演示的是完整工作流的结构和逻辑！{Style.RESET_ALL}\n")

if __name__ == '__main__':
    demo_workflow()
