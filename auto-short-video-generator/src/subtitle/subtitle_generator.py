"""字幕生成器 - 生成SRT/ASS字幕文件"""
import logging
from pathlib import Path
from typing import List
import pysrt

from ..models import AudioSegment, SubtitleSegment
from ..utils import ConfigLoader, print_step, ensure_dir

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """字幕生成器"""

    def __init__(self, config: ConfigLoader):
        """初始化字幕生成器

        Args:
            config: 配置加载器
        """
        self.config = config
        self.output_dir = ensure_dir(config.get('output.base_dir', './output') + '/subtitles')

        # 字幕配置
        self.font = config.get('subtitle.font', 'SimHei')
        self.font_size = config.get('subtitle.font_size', 48)
        self.font_color = config.get('subtitle.font_color', 'white')
        self.stroke_color = config.get('subtitle.stroke_color', 'black')
        self.stroke_width = config.get('subtitle.stroke_width', 2)
        self.position = config.get('subtitle.position', 'bottom')

        logger.info("字幕生成器初始化成功")

    def generate_subtitles(
        self,
        audio_segments: List[AudioSegment],
        output_name: str = "subtitles"
    ) -> List[SubtitleSegment]:
        """生成字幕

        Args:
            audio_segments: 音频片段列表
            output_name: 输出文件名

        Returns:
            字幕片段列表
        """
        print_step("生成字幕文件")

        try:
            subtitle_segments = []

            for seg in audio_segments:
                subtitle_seg = SubtitleSegment(
                    text=seg.text,
                    start_time=seg.start_time,
                    end_time=seg.start_time + seg.duration,
                    position=self.position
                )
                subtitle_segments.append(subtitle_seg)

            # 生成SRT文件
            srt_path = self.output_dir / f"{output_name}.srt"
            self._generate_srt(subtitle_segments, str(srt_path))

            # 生成ASS文件（更丰富的样式）
            ass_path = self.output_dir / f"{output_name}.ass"
            self._generate_ass(subtitle_segments, str(ass_path))

            logger.info(f"字幕生成完成 - {len(subtitle_segments)}条字幕")
            print_step(f"字幕生成完成 - {len(subtitle_segments)}条", "完成")

            return subtitle_segments

        except Exception as e:
            logger.error(f"字幕生成失败: {str(e)}")
            print_step("字幕生成失败", "失败")
            raise

    def _generate_srt(self, segments: List[SubtitleSegment], output_path: str):
        """生成SRT格式字幕

        Args:
            segments: 字幕片段列表
            output_path: 输出路径
        """
        subs = pysrt.SubRipFile()

        for i, seg in enumerate(segments, 1):
            # 转换时间为SRT格式
            start = self._seconds_to_srt_time(seg.start_time)
            end = self._seconds_to_srt_time(seg.end_time)

            sub = pysrt.SubRipItem(
                index=i,
                start=start,
                end=end,
                text=seg.text
            )
            subs.append(sub)

        subs.save(output_path, encoding='utf-8')
        logger.debug(f"SRT字幕保存成功: {output_path}")

    def _generate_ass(self, segments: List[SubtitleSegment], output_path: str):
        """生成ASS格式字幕（支持更丰富的样式）

        Args:
            segments: 字幕片段列表
            output_path: 输出路径
        """
        # ASS文件头
        ass_header = f"""[Script Info]
Title: Auto Generated Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.font},{self.font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{self.stroke_width},0,2,10,10,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # 生成字幕行
        lines = []
        for seg in segments:
            start = self._seconds_to_ass_time(seg.start_time)
            end = self._seconds_to_ass_time(seg.end_time)

            # ASS对话行格式
            line = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{seg.text}"
            lines.append(line)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_header)
            f.write('\n'.join(lines))

        logger.debug(f"ASS字幕保存成功: {output_path}")

    def _seconds_to_srt_time(self, seconds: float) -> pysrt.SubRipTime:
        """将秒转换为SRT时间格式

        Args:
            seconds: 秒数

        Returns:
            SRT时间对象
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return pysrt.SubRipTime(hours, minutes, secs, millis)

    def _seconds_to_ass_time(self, seconds: float) -> str:
        """将秒转换为ASS时间格式 (H:MM:SS.CC)

        Args:
            seconds: 秒数

        Returns:
            ASS时间字符串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)

        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def get_subtitle_file(self, output_name: str, format: str = "ass") -> str:
        """获取字幕文件路径

        Args:
            output_name: 输出文件名
            format: 格式 ('srt' 或 'ass')

        Returns:
            字幕文件路径
        """
        return str(self.output_dir / f"{output_name}.{format}")
