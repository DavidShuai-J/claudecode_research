"""视觉素材生成器 - 生成图片和视频素材"""
import logging
import requests
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
import io

from ..models import Script, AudioSegment, VisualSegment
from ..llm_client import LLMClient
from ..utils import ConfigLoader, print_step, ensure_dir

logger = logging.getLogger(__name__)


class VisualGenerator:
    """视觉素材生成器"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        """初始化视觉生成器

        Args:
            config: 配置加载器
            llm_client: LLM客户端（用于生成图片描述）
        """
        self.config = config
        self.llm = llm_client
        self.provider = config.get('api.image_provider', 'dalle')
        self.output_dir = ensure_dir(config.get('output.base_dir', './output') + '/images')

        # 视频配置
        self.resolution = config.get('video.resolution', [1080, 1920])
        self.duration_per_image = config.get('video.duration_per_image', 3)

        logger.info(f"视觉生成器初始化成功 - Provider: {self.provider}")

    def generate_visuals(
        self,
        script: Script,
        audio_segments: List[AudioSegment],
        output_name: Optional[str] = None
    ) -> List[VisualSegment]:
        """生成视觉素材

        Args:
            script: 脚本内容
            audio_segments: 音频片段（用于时间对齐）
            output_name: 输出文件名前缀

        Returns:
            视觉片段列表
        """
        print_step("生成视觉素材")

        if output_name is None:
            output_name = "visual"

        try:
            # 1. 生成场景描述
            scene_descriptions = self._generate_scene_descriptions(script, len(audio_segments))

            # 2. 为每个场景生成图片
            visual_segments = []

            for i, (audio_seg, description) in enumerate(zip(audio_segments, scene_descriptions)):
                # 生成图片
                image_path = self.output_dir / f"{output_name}_scene_{i:03d}.png"

                try:
                    self._generate_image(description, str(image_path))
                except Exception as e:
                    # 如果图片生成失败，创建占位图
                    logger.warning(f"图片生成失败，使用占位图: {str(e)}")
                    self._create_placeholder_image(description, str(image_path))

                # 创建视觉片段
                visual_seg = VisualSegment(
                    description=description,
                    image_path=str(image_path),
                    duration=audio_seg.duration,
                    start_time=audio_seg.start_time
                )

                visual_segments.append(visual_seg)

                logger.debug(f"场景 {i+1}/{len(audio_segments)} 生成完成")

            logger.info(f"视觉素材生成完成 - {len(visual_segments)}个场景")
            print_step(f"视觉素材生成完成 - {len(visual_segments)}个场景", "完成")

            return visual_segments

        except Exception as e:
            logger.error(f"视觉素材生成失败: {str(e)}")
            print_step("视觉素材生成失败", "失败")
            raise

    def _generate_scene_descriptions(self, script: Script, num_scenes: int) -> List[str]:
        """生成场景描述

        Args:
            script: 脚本内容
            num_scenes: 场景数量

        Returns:
            场景描述列表
        """
        # 构建提示词
        prompt = f"""
请根据以下短视频脚本，生成{num_scenes}个场景的视觉描述。

脚本内容：
{script.content}

要求：
1. 每个场景描述要具体、有画面感
2. 描述要符合{script.style_type}的风格
3. 描述要适合AI图片生成（DALL-E或Stable Diffusion）
4. 描述要体现历史感、氛围感
5. 使用英文描述（更适合图片生成模型）

请以JSON格式返回场景描述列表：
{{"scenes": ["scene 1 description", "scene 2 description", ...]}}

每个描述30-50词，包含：场景、人物、动作、氛围、光线、色调等。
"""

        result = self.llm.generate_json(prompt, temperature=0.8, max_tokens=2000)
        scenes = result.get('scenes', [])

        # 如果生成的场景数量不够，复制最后一个
        while len(scenes) < num_scenes:
            scenes.append(scenes[-1] if scenes else "A dramatic historical scene")

        return scenes[:num_scenes]

    def _generate_image(self, description: str, output_path: str):
        """生成单张图片

        Args:
            description: 场景描述
            output_path: 输出路径
        """
        if self.provider == 'dalle':
            self._generate_with_dalle(description, output_path)
        else:
            # 其他提供商可以在这里扩展
            logger.warning(f"暂不支持 {self.provider}，使用占位图")
            self._create_placeholder_image(description, output_path)

    def _generate_with_dalle(self, description: str, output_path: str):
        """使用DALL-E生成图片

        Args:
            description: 场景描述
            output_path: 输出路径
        """
        from openai import OpenAI
        import os

        api_key = self.config.get_env('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("未设置 OPENAI_API_KEY")

        client = OpenAI(api_key=api_key)

        # 调用DALL-E API
        response = client.images.generate(
            model=self.config.get('api.dalle_model', 'dall-e-3'),
            prompt=description,
            size="1792x1024",  # 横屏
            quality="standard",
            n=1,
        )

        # 下载图片
        image_url = response.data[0].url
        img_data = requests.get(image_url).content

        # 保存图片
        with open(output_path, 'wb') as f:
            f.write(img_data)

        logger.debug(f"DALL-E图片生成成功: {output_path}")

    def _create_placeholder_image(self, description: str, output_path: str):
        """创建占位图片

        Args:
            description: 场景描述
            output_path: 输出路径
        """
        # 创建纯色背景图
        width, height = self.resolution[1], self.resolution[0]  # 横屏
        img = Image.new('RGB', (width, height), color=(30, 30, 50))

        draw = ImageDraw.Draw(img)

        # 添加文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            font = ImageFont.load_default()

        # 文字换行处理
        words = description.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # 绘制文字
        y = height // 2 - len(lines) * 25
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y), line, fill=(200, 200, 200), font=font)
            y += 50

        # 保存图片
        img.save(output_path)
        logger.debug(f"占位图片创建成功: {output_path}")
