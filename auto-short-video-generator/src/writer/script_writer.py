"""脚本编剧 - 生成口播稿"""
import logging
import re
from pathlib import Path
from typing import List

from ..models import VideoTheme, StyleAnalysis, Script
from ..llm_client import LLMClient
from ..utils import ConfigLoader, print_step, split_text_by_punctuation

logger = logging.getLogger(__name__)


class ScriptWriter:
    """脚本编剧"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        """初始化编剧

        Args:
            config: 配置加载器
            llm_client: LLM客户端
        """
        self.config = config
        self.llm = llm_client

        # 加载提示词模板
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "script_writer_prompt.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

        self.max_chars_per_line = config.get('subtitle.max_chars_per_line', 20)

        logger.info("脚本编剧初始化成功")

    def write_script(self, theme: VideoTheme, style: StyleAnalysis) -> Script:
        """创作口播稿

        Args:
            theme: 视频主题
            style: 风格分析

        Returns:
            完整脚本
        """
        print_step("创作口播文案")

        # 构建提示词
        prompt = self.prompt_template.format(
            topic=theme.topic,
            style_type=style.style_type,
            emotional_arc=", ".join(style.emotional_arc),
            key_elements=", ".join(style.key_elements),
        )

        # 调用LLM生成文案
        try:
            content = self.llm.generate(
                prompt=prompt,
                temperature=0.9,
                max_tokens=4000
            )

            # 清理和格式化文案
            content = self._clean_content(content)

            # 分段处理
            segments = self._split_into_segments(content)

            # 提取关键词
            keywords = self._extract_keywords(content, style)

            # 创建脚本对象
            script = Script(
                title="",  # 标题后续生成
                content=content,
                segments=segments,
                word_count=len(content),
                style_type=style.style_type,
                keywords=keywords
            )

            logger.info(f"文案创作完成 - 字数: {script.word_count}, 段落: {len(segments)}")
            print_step(f"文案创作完成 - {script.word_count}字", "完成")

            return script

        except Exception as e:
            logger.error(f"文案创作失败: {str(e)}")
            print_step("文案创作失败", "失败")
            raise

    def _clean_content(self, content: str) -> str:
        """清理文案内容

        Args:
            content: 原始文案

        Returns:
            清理后的文案
        """
        # 移除markdown格式
        content = re.sub(r'[#*`]', '', content)

        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 移除开头的说明性文字
        lines = content.split('\n')
        cleaned_lines = []
        started = False

        for line in lines:
            line = line.strip()

            # 跳过空行和说明性文字
            if not line:
                continue

            # 检查是否是文案开始（以"你"开头）
            if not started and (line.startswith('你') or line.startswith('"你')):
                started = True

            if started:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _split_into_segments(self, content: str) -> List[str]:
        """将文案分段，每段适合字幕显示

        Args:
            content: 完整文案

        Returns:
            分段列表
        """
        # 先按段落分
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        # 再按标点符号细分
        segments = []
        for para in paragraphs:
            # 如果段落太长，进一步分割
            if len(para) > self.max_chars_per_line:
                sub_segments = split_text_by_punctuation(para, self.max_chars_per_line)
                segments.extend(sub_segments)
            else:
                segments.append(para)

        return segments

    def _extract_keywords(self, content: str, style: StyleAnalysis) -> List[str]:
        """提取关键词

        Args:
            content: 文案内容
            style: 风格分析

        Returns:
            关键词列表
        """
        keywords = set()

        # 从风格要素中提取
        keywords.update(style.key_elements)

        # 提取高频名词（简单实现）
        # 这里可以使用jieba等分词工具做更精确的提取
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', content)
        from collections import Counter
        word_freq = Counter(words)

        # 取频率最高的前10个词
        top_words = [word for word, count in word_freq.most_common(10) if count >= 2]
        keywords.update(top_words)

        return list(keywords)[:15]  # 最多返回15个关键词
