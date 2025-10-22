"""视频策划器 - 分析主题并生成风格策略"""
import logging
from pathlib import Path
from typing import Optional

from ..models import VideoTheme, StyleAnalysis
from ..llm_client import LLMClient
from ..utils import ConfigLoader, print_step

logger = logging.getLogger(__name__)


class VideoPlanner:
    """视频策划器"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        """初始化策划器

        Args:
            config: 配置加载器
            llm_client: LLM客户端
        """
        self.config = config
        self.llm = llm_client

        # 加载提示词模板
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "planner_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

        logger.info("视频策划器初始化成功")

    def analyze_theme(self, theme: VideoTheme) -> StyleAnalysis:
        """分析主题并生成风格策略

        Args:
            theme: 视频主题

        Returns:
            风格分析结果
        """
        print_step("分析主题，生成视频策略")

        # 构建提示词
        prompt = self.prompt_template.format(
            topic=theme.topic,
        )

        # 调用LLM
        try:
            result = self.llm.generate_json(
                prompt=prompt,
                temperature=0.8,
                max_tokens=2000
            )

            # 解析结果
            style = StyleAnalysis(**result)

            logger.info(f"策划完成 - 风格类型: {style.style_type}")
            print_step(f"策划完成 - {style.style_type}", "完成")

            return style

        except Exception as e:
            logger.error(f"主题分析失败: {str(e)}")
            print_step("主题分析失败", "失败")
            raise

    def get_available_styles(self) -> list[str]:
        """获取可用的风格类型"""
        return self.config.get('script.style_types', [])
