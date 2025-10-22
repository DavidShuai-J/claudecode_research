"""视频生成Pipeline - 完整工作流"""
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import VideoTheme, VideoProject
from ..utils import ConfigLoader, print_section, print_step
from ..llm_client import LLMClient
from ..planner import VideoPlanner
from ..writer import ScriptWriter
from ..title_generator import TitleGenerator
from ..tts import TTSEngine
from ..visual import VisualGenerator
from ..subtitle import SubtitleGenerator
from ..compositor import VideoCompositor
from .story_branch import StoryWorkflowBranch

logger = logging.getLogger(__name__)


class VideoPipeline:
    """视频生成Pipeline"""

    def __init__(self, config_path: Optional[str] = None):
        """初始化Pipeline

        Args:
            config_path: 配置文件路径（可选）
        """
        print_section("初始化短视频生成工具")

        # 加载配置
        self.config = ConfigLoader(config_path)

        # 初始化LLM客户端
        llm_provider = self.config.get('api.llm_provider', 'openai')

        # 根据provider获取相应的API密钥
        if llm_provider == 'openai':
            api_key = self.config.get_env('OPENAI_API_KEY')
            key_name = 'OPENAI_API_KEY'
        elif llm_provider == 'anthropic':
            api_key = self.config.get_env('ANTHROPIC_API_KEY')
            key_name = 'ANTHROPIC_API_KEY'
        elif llm_provider == 'coze':
            api_key = self.config.get_env('COZE_ACCESS_TOKEN')
            key_name = 'COZE_ACCESS_TOKEN'
        else:
            raise ValueError(f"不支持的LLM提供商: {llm_provider}")

        if not api_key:
            raise ValueError(f"未设置API密钥: {key_name}")

        # 根据provider设置相应参数
        if llm_provider == 'coze':
            bot_id = self.config.get('api.coze_bot_id')
            if not bot_id:
                raise ValueError("未设置Coze Bot ID (api.coze_bot_id)")
            self.llm = LLMClient(llm_provider, api_key, bot_id=bot_id)
        else:
            model = self.config.get(f'api.{llm_provider}_model')
            base_url = self.config.get_env('OPENAI_BASE_URL') if llm_provider == 'openai' else None
            self.llm = LLMClient(llm_provider, api_key, model, base_url)

        # 初始化各个模块
        self.planner = VideoPlanner(self.config, self.llm)
        self.writer = ScriptWriter(self.config, self.llm)
        self.title_generator = TitleGenerator(self.config, self.llm)
        self.tts_engine = TTSEngine(self.config)
        self.visual_generator = VisualGenerator(self.config, self.llm)
        self.subtitle_generator = SubtitleGenerator(self.config)
        self.video_compositor = VideoCompositor(self.config)
        self.story_branch = StoryWorkflowBranch(self.config, self.llm)

        print_step("所有模块初始化完成", "完成")
        logger.info("VideoPipeline初始化成功")

    def generate(
        self,
        topic: str,
        project_id: Optional[str] = None,
        save_intermediate: bool = True
    ) -> VideoProject:
        """生成视频的完整流程

        Args:
            topic: 视频主题
            project_id: 项目ID（可选，自动生成）
            save_intermediate: 是否保存中间文件

        Returns:
            视频项目对象
        """
        print_section(f"开始生成视频: {topic}")

        # 创建项目
        if project_id is None:
            project_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        theme = VideoTheme(topic=topic)
        project = VideoProject(project_id=project_id, theme=theme)

        try:
            # 步骤1: 智能策划
            print_section("【步骤1/7】智能策划")
            project.style = self.planner.analyze_theme(theme)

            # 步骤2: 文案创作
            print_section("【步骤2/7】文案创作")
            project.script = self.writer.write_script(theme, project.style)

            # 保存文案
            if save_intermediate:
                self._save_script(project)

            # 步骤3: 标题生成
            print_section("【步骤3/7】标题生成")
            project.titles = self.title_generator.generate_titles(project.script)

            # 步骤4: 语音合成
            print_section("【步骤4/7】语音合成")
            project.audio_segments = self.tts_engine.generate_audio(
                project.script,
                output_name=project_id
            )

            # 步骤5: 视觉素材生成
            print_section("【步骤5/7】视觉素材生成")
            project.visual_segments = self.visual_generator.generate_visuals(
                project.script,
                project.audio_segments,
                output_name=project_id
            )

            # 步骤6: 字幕生成
            print_section("【步骤6/7】字幕生成")
            project.subtitles = self.subtitle_generator.generate_subtitles(
                project.audio_segments,
                output_name=project_id
            )

            # 步骤7: 视频合成
            print_section("【步骤7/7】视频合成")
            project.output_path = self.video_compositor.compose_video(
                project.audio_segments,
                project.visual_segments,
                project.subtitles,
                output_name=project_id
            )

            # 保存项目元数据
            if save_intermediate:
                self._save_project_metadata(project)

            print_section("✅ 视频生成完成！")
            self._print_summary(project)

            return project

        except Exception as e:
            logger.error(f"视频生成失败: {str(e)}", exc_info=True)
            print_section("❌ 视频生成失败")
            raise

    def generate_story_workflow(
        self, concept: str, project_id: Optional[str] = None
    ):
        """运行短剧完整流程分支"""

        print_section(f"开始短剧工作流: {concept}")
        result = self.story_branch.run(concept, project_id)
        print_section("✅ 短剧工作流完成！")
        return result

    def _save_script(self, project: VideoProject):
        """保存文案到文件

        Args:
            project: 视频项目
        """
        script_dir = Path(self.config.get('output.base_dir', './output')) / 'scripts'
        script_dir.mkdir(parents=True, exist_ok=True)

        script_file = script_dir / f"{project.project_id}.txt"

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(f"标题: {project.script.title}\n")
            f.write(f"风格: {project.script.style_type}\n")
            f.write(f"字数: {project.script.word_count}\n")
            f.write("=" * 60 + "\n\n")
            f.write(project.script.content)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("关键词: " + ", ".join(project.script.keywords))

        logger.info(f"文案已保存: {script_file}")

    def _save_project_metadata(self, project: VideoProject):
        """保存项目元数据

        Args:
            project: 视频项目
        """
        import json

        metadata_dir = Path(self.config.get('output.base_dir', './output'))
        metadata_file = metadata_dir / f"{project.project_id}_metadata.json"

        # 转换为字典
        metadata = {
            "project_id": project.project_id,
            "theme": project.theme.topic,
            "style": project.style.style_type if project.style else None,
            "title": project.script.title if project.script else None,
            "word_count": project.script.word_count if project.script else 0,
            "duration": sum(seg.duration for seg in project.audio_segments),
            "num_scenes": len(project.visual_segments),
            "output_path": project.output_path,
            "created_at": project.created_at.isoformat(),
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"项目元数据已保存: {metadata_file}")

    def _print_summary(self, project: VideoProject):
        """打印生成摘要

        Args:
            project: 视频项目
        """
        from colorama import Fore, Style

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}生成摘要")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")

        print(f"项目ID: {project.project_id}")
        print(f"主题: {project.theme.topic}")
        print(f"风格: {project.style.style_type if project.style else 'N/A'}")
        print(f"\n标题: {Fore.CYAN}{project.script.title if project.script else 'N/A'}{Style.RESET_ALL}")
        print(f"文案字数: {project.script.word_count if project.script else 0}")

        # 时长
        total_duration = sum(seg.duration for seg in project.audio_segments)
        minutes = int(total_duration // 60)
        seconds = int(total_duration % 60)
        print(f"视频时长: {minutes}分{seconds}秒")

        print(f"场景数: {len(project.visual_segments)}")
        print(f"\n输出路径: {Fore.YELLOW}{project.output_path}{Style.RESET_ALL}\n")

        # 备选标题
        if project.titles:
            print(f"{Fore.CYAN}备选标题:{Style.RESET_ALL}")
            for i, title in enumerate(project.titles[:3], 1):
                print(f"  {i}. {title.title} (评分: {title.score})")

        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
