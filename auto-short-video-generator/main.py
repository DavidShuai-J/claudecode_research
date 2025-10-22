#!/usr/bin/env python3
"""短视频自动生成工具 - 主入口"""
import argparse
import logging
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.workflow import VideoPipeline
from src.utils import print_section
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)


def setup_logging(debug: bool = False):
    """设置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('video_generator.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='短视频自动生成工具 - 输入主题，自动生成爆款短视频',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s "明朝锦衣卫"
  %(prog)s "古代特殊职业" --config custom_config.yaml
  %(prog)s "历史奇案" --debug

更多信息请查看 README.md
        """
    )

    parser.add_argument(
        'topic',
        type=str,
        help='视频主题（例如：明朝锦衣卫、古代特殊职业、历史奇案）'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        default=None,
        help='配置文件路径（默认: config/config.yaml）'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出目录（默认: ./output）'
    )

    parser.add_argument(
        '--no-save-intermediate',
        action='store_true',
        help='不保存中间文件'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.debug)

    # 打印欢迎信息
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{'短视频自动生成工具 v1.0':^70}")
    print(f"{Fore.CYAN}{'AI驱动的历史故事短视频生成系统':^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    try:
        # 初始化Pipeline
        pipeline = VideoPipeline(config_path=args.config)

        # 生成视频
        project = pipeline.generate(
            topic=args.topic,
            save_intermediate=not args.no_save_intermediate
        )

        # 输出结果
        print(f"\n{Fore.GREEN}✅ 视频生成成功！{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📹 视频路径: {project.output_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 标题: {project.script.title}{Style.RESET_ALL}\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  用户中断操作{Style.RESET_ALL}")
        return 1

    except Exception as e:
        print(f"\n{Fore.RED}❌ 错误: {str(e)}{Style.RESET_ALL}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
