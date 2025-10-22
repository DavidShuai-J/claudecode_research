"""标题生成器 - 生成爆款标题"""
import logging
from pathlib import Path
from typing import List

from ..models import Script, TitleCandidate
from ..llm_client import LLMClient
from ..utils import ConfigLoader, print_step

logger = logging.getLogger(__name__)


class TitleGenerator:
    """标题生成器"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        """初始化标题生成器

        Args:
            config: 配置加载器
            llm_client: LLM客户端
        """
        self.config = config
        self.llm = llm_client

        # 加载提示词模板
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "title_generator_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

        logger.info("标题生成器初始化成功")

    def generate_titles(self, script: Script, count: int = 5) -> List[TitleCandidate]:
        """生成标题候选

        Args:
            script: 脚本内容
            count: 生成数量

        Returns:
            标题候选列表
        """
        print_step(f"生成{count}个爆款标题候选")

        # 构建提示词
        prompt = self.prompt_template.format(
            script_content=script.content[:1500],  # 只传入前1500字，避免太长
        )

        # 调用LLM
        try:
            result = self.llm.generate_json(
                prompt=prompt,
                temperature=0.9,
                max_tokens=2000
            )

            # 解析结果
            if isinstance(result, dict):
                # 如果返回的是字典，尝试获取标题列表
                titles_data = result.get('titles', [])
            elif isinstance(result, list):
                titles_data = result
            else:
                raise ValueError(f"意外的返回格式: {type(result)}")

            titles = [TitleCandidate(**item) for item in titles_data[:count]]

            # 按分数排序
            titles.sort(key=lambda x: x.score, reverse=True)

            logger.info(f"生成了{len(titles)}个标题候选")
            print_step(f"标题生成完成 - 最高分{titles[0].score}", "完成")

            # 将最佳标题设置到脚本
            if titles:
                script.title = titles[0].title

            return titles

        except Exception as e:
            logger.error(f"标题生成失败: {str(e)}")
            print_step("标题生成失败", "失败")
            raise

    def select_best_title(self, titles: List[TitleCandidate]) -> TitleCandidate:
        """选择最佳标题

        Args:
            titles: 标题候选列表

        Returns:
            最佳标题
        """
        if not titles:
            raise ValueError("标题列表为空")

        # 简单按分数排序取第一
        return sorted(titles, key=lambda x: x.score, reverse=True)[0]
