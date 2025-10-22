"""工具函数"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化配置加载器"""
        # 加载环境变量
        load_dotenv()

        # 加载配置文件
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        logger.info(f"{Fore.GREEN}配置文件加载成功: {config_path}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key_path: 配置路径，如 'api.llm_provider'
            default: 默认值
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取环境变量"""
        return os.getenv(key, default)

    @property
    def api_config(self) -> Dict[str, Any]:
        """API配置"""
        return self.config.get('api', {})

    @property
    def video_config(self) -> Dict[str, Any]:
        """视频配置"""
        return self.config.get('video', {})

    @property
    def subtitle_config(self) -> Dict[str, Any]:
        """字幕配置"""
        return self.config.get('subtitle', {})

    @property
    def script_config(self) -> Dict[str, Any]:
        """文案配置"""
        return self.config.get('script', {})

    @property
    def title_config(self) -> Dict[str, Any]:
        """标题配置"""
        return self.config.get('title', {})

    @property
    def output_config(self) -> Dict[str, Any]:
        """输出配置"""
        return self.config.get('output', {})


def ensure_dir(path: str) -> Path:
    """确保目录存在"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{title:^60}")
    print(f"{Fore.CYAN}{'='*60}\n")


def print_step(step: str, status: str = "进行中"):
    """打印步骤"""
    if status == "完成":
        print(f"{Fore.GREEN}✓ {step}")
    elif status == "失败":
        print(f"{Fore.RED}✗ {step}")
    else:
        print(f"{Fore.YELLOW}⊙ {step}...")


def format_time(seconds: float) -> str:
    """格式化时间"""
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def split_text_by_punctuation(text: str, max_length: int = 20) -> list[str]:
    """按标点符号分割文本，每段不超过max_length字符

    Args:
        text: 要分割的文本
        max_length: 每段最大长度

    Returns:
        分割后的文本列表
    """
    # 标点符号
    punctuations = ['。', '！', '？', '；', '…', '，', '、']

    segments = []
    current = ""

    for char in text:
        current += char

        if char in punctuations:
            # 如果当前段落已经足够长，或者遇到了强标点
            if len(current) >= max_length or char in ['。', '！', '？']:
                segments.append(current.strip())
                current = ""

    # 添加剩余部分
    if current.strip():
        segments.append(current.strip())

    return segments


def clean_text_for_speech(text: str) -> str:
    """清理文本用于语音合成

    Args:
        text: 原始文本

    Returns:
        清理后的文本
    """
    # 移除特殊符号
    replacements = {
        '「': '"',
        '」': '"',
        '『': '"',
        '』': '"',
        '【': '[',
        '】': ']',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()
