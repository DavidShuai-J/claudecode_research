"""TTS引擎 - 文字转语音"""
import logging
import asyncio
from pathlib import Path
from typing import List, Optional
import edge_tts
from pydub import AudioSegment

from ..models import Script, AudioSegment as AudioSeg
from ..utils import ConfigLoader, print_step, ensure_dir, clean_text_for_speech

logger = logging.getLogger(__name__)


class TTSEngine:
    """TTS引擎"""

    def __init__(self, config: ConfigLoader):
        """初始化TTS引擎

        Args:
            config: 配置加载器
        """
        self.config = config
        self.provider = config.get('api.tts_provider', 'edge')
        self.voice = config.get('api.edge_voice', 'zh-CN-YunxiNeural')
        self.output_dir = ensure_dir(config.get('output.base_dir', './output') + '/audio')

        logger.info(f"TTS引擎初始化成功 - Provider: {self.provider}, Voice: {self.voice}")

    def generate_audio(
        self,
        script: Script,
        output_name: Optional[str] = None
    ) -> List[AudioSeg]:
        """生成音频

        Args:
            script: 脚本内容
            output_name: 输出文件名前缀

        Returns:
            音频片段列表
        """
        print_step("生成语音音频")

        if output_name is None:
            output_name = "audio"

        try:
            if self.provider == 'edge':
                audio_segments = self._generate_with_edge(script, output_name)
            else:
                raise ValueError(f"不支持的TTS提供商: {self.provider}")

            logger.info(f"音频生成完成 - {len(audio_segments)}个片段")
            print_step(f"音频生成完成 - {len(audio_segments)}个片段", "完成")

            return audio_segments

        except Exception as e:
            logger.error(f"音频生成失败: {str(e)}")
            print_step("音频生成失败", "失败")
            raise

    def _generate_with_edge(self, script: Script, output_name: str) -> List[AudioSeg]:
        """使用Edge TTS生成音频

        Args:
            script: 脚本内容
            output_name: 输出文件名前缀

        Returns:
            音频片段列表
        """
        audio_segments = []
        current_time = 0.0

        # 为每个片段生成音频
        for i, segment_text in enumerate(script.segments):
            # 清理文本
            clean_text = clean_text_for_speech(segment_text)

            # 生成音频文件路径
            audio_path = self.output_dir / f"{output_name}_segment_{i:03d}.mp3"

            # 使用asyncio运行edge-tts
            asyncio.run(self._edge_tts_generate(clean_text, str(audio_path)))

            # 获取音频时长
            audio = AudioSegment.from_mp3(str(audio_path))
            duration = len(audio) / 1000.0  # 转换为秒

            # 创建音频片段对象
            audio_seg = AudioSeg(
                text=segment_text,
                audio_path=str(audio_path),
                duration=duration,
                start_time=current_time
            )

            audio_segments.append(audio_seg)
            current_time += duration

            logger.debug(f"片段 {i+1}/{len(script.segments)} 生成完成: {duration:.2f}秒")

        # 合并所有音频片段为一个完整文件
        full_audio_path = self.output_dir / f"{output_name}_full.mp3"
        self._merge_audio_segments(audio_segments, str(full_audio_path))

        return audio_segments

    async def _edge_tts_generate(self, text: str, output_path: str):
        """使用Edge TTS生成单个音频

        Args:
            text: 文本内容
            output_path: 输出文件路径
        """
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def _merge_audio_segments(self, segments: List[AudioSeg], output_path: str):
        """合并音频片段

        Args:
            segments: 音频片段列表
            output_path: 输出文件路径
        """
        if not segments:
            return

        # 加载所有音频片段
        combined = AudioSegment.empty()

        for seg in segments:
            audio = AudioSegment.from_mp3(seg.audio_path)
            combined += audio

        # 导出合并后的音频
        combined.export(output_path, format="mp3")
        logger.info(f"音频合并完成: {output_path}")

    def get_total_duration(self, audio_segments: List[AudioSeg]) -> float:
        """获取总时长

        Args:
            audio_segments: 音频片段列表

        Returns:
            总时长（秒）
        """
        return sum(seg.duration for seg in audio_segments)
