"""视频合成器 - 将音频、图片、字幕合成为视频"""
import logging
from pathlib import Path
from typing import List, Optional
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips,
    CompositeVideoClip, TextClip
)
from moviepy.video.fx import resize

from ..models import AudioSegment, VisualSegment, SubtitleSegment
from ..utils import ConfigLoader, print_step, ensure_dir

logger = logging.getLogger(__name__)


class VideoCompositor:
    """视频合成器"""

    def __init__(self, config: ConfigLoader):
        """初始化视频合成器

        Args:
            config: 配置加载器
        """
        self.config = config
        self.output_dir = ensure_dir(config.get('output.base_dir', './output') + '/videos')

        # 视频配置
        self.resolution = tuple(config.get('video.resolution', [1080, 1920]))
        self.fps = config.get('video.fps', 30)
        self.video_codec = config.get('output.video_codec', 'libx264')
        self.audio_codec = config.get('output.audio_codec', 'aac')

        # 字幕配置
        self.subtitle_font = config.get('subtitle.font', 'SimHei')
        self.subtitle_fontsize = config.get('subtitle.font_size', 48)
        self.subtitle_color = config.get('subtitle.font_color', 'white')
        self.subtitle_stroke_color = config.get('subtitle.stroke_color', 'black')
        self.subtitle_stroke_width = config.get('subtitle.stroke_width', 2)

        logger.info(f"视频合成器初始化成功 - 分辨率: {self.resolution}, FPS: {self.fps}")

    def compose_video(
        self,
        audio_segments: List[AudioSegment],
        visual_segments: List[VisualSegment],
        subtitle_segments: List[SubtitleSegment],
        output_name: str = "final_video"
    ) -> str:
        """合成最终视频

        Args:
            audio_segments: 音频片段列表
            visual_segments: 视觉片段列表
            subtitle_segments: 字幕片段列表
            output_name: 输出文件名

        Returns:
            输出视频路径
        """
        print_step("合成最终视频")

        try:
            # 1. 创建视频片段
            video_clips = self._create_video_clips(visual_segments)

            # 2. 拼接视频
            final_video = concatenate_videoclips(video_clips, method="compose")

            # 3. 添加字幕
            final_video = self._add_subtitles(final_video, subtitle_segments)

            # 4. 添加音频
            # 使用完整音频文件
            audio_path = Path(audio_segments[0].audio_path).parent / f"{Path(audio_segments[0].audio_path).stem.rsplit('_', 2)[0]}_full.mp3"
            if audio_path.exists():
                audio_clip = AudioFileClip(str(audio_path))
                final_video = final_video.set_audio(audio_clip)
            else:
                logger.warning("未找到完整音频文件，使用分段音频")
                # 使用分段音频
                from moviepy.editor import concatenate_audioclips
                audio_clips = [AudioFileClip(seg.audio_path) for seg in audio_segments]
                full_audio = concatenate_audioclips(audio_clips)
                final_video = final_video.set_audio(full_audio)

            # 5. 导出视频
            output_path = self.output_dir / f"{output_name}.mp4"

            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec=self.video_codec,
                audio_codec=self.audio_codec,
                preset='medium',
                threads=4,
                logger=None  # 禁用moviepy的进度条（避免干扰）
            )

            # 关闭所有clips释放资源
            final_video.close()
            for clip in video_clips:
                clip.close()

            logger.info(f"视频合成完成: {output_path}")
            print_step(f"视频合成完成", "完成")

            return str(output_path)

        except Exception as e:
            logger.error(f"视频合成失败: {str(e)}")
            print_step("视频合成失败", "失败")
            raise

    def _create_video_clips(self, visual_segments: List[VisualSegment]) -> List[ImageClip]:
        """创建视频片段

        Args:
            visual_segments: 视觉片段列表

        Returns:
            视频片段列表
        """
        clips = []

        for seg in visual_segments:
            if seg.image_path:
                # 使用图片创建视频片段
                clip = ImageClip(seg.image_path, duration=seg.duration)

                # 调整大小以适应分辨率
                clip = clip.resize(height=self.resolution[0], width=self.resolution[1])

                # 设置开始时间
                clip = clip.set_start(seg.start_time)

                clips.append(clip)

            elif seg.video_path:
                # TODO: 支持视频片段
                logger.warning("暂不支持视频片段，跳过")

        return clips

    def _add_subtitles(self, video_clip, subtitle_segments: List[SubtitleSegment]):
        """添加字幕

        Args:
            video_clip: 视频片段
            subtitle_segments: 字幕片段列表

        Returns:
            带字幕的视频片段
        """
        # 创建字幕clips
        subtitle_clips = []

        for seg in subtitle_segments:
            try:
                # 创建文本clip
                txt_clip = TextClip(
                    seg.text,
                    fontsize=self.subtitle_fontsize,
                    color=self.subtitle_color,
                    font=self.subtitle_font,
                    stroke_color=self.subtitle_stroke_color,
                    stroke_width=self.subtitle_stroke_width,
                    method='caption',
                    size=(self.resolution[1] - 100, None),  # 留出边距
                )

                # 设置时间和位置
                txt_clip = txt_clip.set_start(seg.start_time)
                txt_clip = txt_clip.set_duration(seg.end_time - seg.start_time)

                # 位置设置
                if seg.position == 'bottom':
                    txt_clip = txt_clip.set_position(('center', self.resolution[0] - 200))
                elif seg.position == 'top':
                    txt_clip = txt_clip.set_position(('center', 100))
                else:  # center
                    txt_clip = txt_clip.set_position('center')

                subtitle_clips.append(txt_clip)

            except Exception as e:
                logger.warning(f"字幕 '{seg.text}' 添加失败: {str(e)}")

        # 合成视频和字幕
        if subtitle_clips:
            final_clip = CompositeVideoClip([video_clip] + subtitle_clips)
            return final_clip
        else:
            return video_clip

    def create_preview(
        self,
        visual_segments: List[VisualSegment],
        output_name: str = "preview"
    ) -> str:
        """创建预览视频（无音频、无字幕）

        Args:
            visual_segments: 视觉片段列表
            output_name: 输出文件名

        Returns:
            预览视频路径
        """
        print_step("创建预览视频")

        clips = self._create_video_clips(visual_segments)
        preview = concatenate_videoclips(clips, method="compose")

        output_path = self.output_dir / f"{output_name}_preview.mp4"
        preview.write_videofile(
            str(output_path),
            fps=self.fps,
            codec=self.video_codec,
            logger=None
        )

        preview.close()
        for clip in clips:
            clip.close()

        logger.info(f"预览视频创建完成: {output_path}")
        print_step("预览视频创建完成", "完成")

        return str(output_path)
