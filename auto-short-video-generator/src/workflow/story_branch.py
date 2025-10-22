"""短剧完整工作流分支"""
import logging
import uuid
from typing import List, Optional
from urllib.parse import quote

from ..models import (
    DramaScript,
    DramaScene,
    RoleProfile,
    StoryboardFrame,
    StoryWorkflowResult,
    VideoSlice,
)
from ..llm_client import LLMClient
from ..utils import ConfigLoader, print_section, print_step

logger = logging.getLogger(__name__)


class StoryCreator:
    """根据故事概念生成短剧剧本"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        prompt_path = (
            config.base_dir / "prompts" / "drama_story_creator_prompt.txt"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def create(self, concept: str) -> DramaScript:
        print_step("生成短剧剧本")
        prompt = self.prompt_template.format(concept=concept)
        result = self.llm.generate_json(prompt, temperature=0.85, max_tokens=4000)

        scenes: List[DramaScene] = []
        raw_scenes = result.get("scenes", []) or []
        for index, scene in enumerate(raw_scenes, start=1):
            scenes.append(
                DramaScene(
                    index=scene.get("index", index),
                    heading=scene.get("heading", f"Scene {index}"),
                    description=scene.get("description", scene.get("summary", "")),
                    dialogue=scene.get("dialogue", []),
                )
            )

        story = DramaScript(
            concept=concept,
            title=result.get("title", concept),
            genre=result.get("genre", "剧情"),
            summary=result.get("summary", ""),
            script_text=result.get("script", result.get("script_text", "")),
            scenes=scenes,
        )

        logger.info("短剧剧本生成完成: %s", story.title)
        return story


class RoleGenerator:
    """根据剧本生成角色设定"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        prompt_path = config.base_dir / "prompts" / "drama_role_generator_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def generate(self, story: DramaScript) -> List[RoleProfile]:
        print_step("生成角色画像")
        prompt = self.prompt_template.format(
            title=story.title,
            summary=story.summary,
            script=story.script_text,
        )
        result = self.llm.generate_json(prompt, temperature=0.7, max_tokens=2000)

        roles: List[RoleProfile] = []
        for role in result.get("roles", []) or []:
            name = role.get("name", "角色")
            image_prompt = role.get("image_prompt") or f"Portrait of {name}"
            image_url = self._build_placeholder_image(image_prompt)
            roles.append(
                RoleProfile(
                    name=name,
                    archetype=role.get("archetype", role.get("role", "")),
                    description=role.get("description", ""),
                    motivations=role.get("motivations", role.get("goals", [])),
                    conflicts=role.get("conflicts", []),
                    image_prompt=image_prompt,
                    image_url=image_url,
                )
            )

        logger.info("角色生成完成，共 %d 个角色", len(roles))
        return roles

    def _build_placeholder_image(self, image_prompt: str) -> str:
        base_url = self.config.get(
            "output.placeholder_image_base",
            "https://dummyimage.com/512x768/191919/ffffff.png&text=",
        )
        return f"{base_url}{quote(image_prompt[:40])}"


class StoryboardDesigner:
    """根据剧本和角色生成分镜"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        self.config = config
        self.llm = llm_client
        prompt_path = config.base_dir / "prompts" / "drama_storyboard_prompt.txt"
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def design(self, story: DramaScript, roles: List[RoleProfile]) -> List[StoryboardFrame]:
        print_step("设计分镜")
        role_descriptions = "\n".join(
            f"- {role.name}: {role.description}" for role in roles
        )
        prompt = self.prompt_template.format(
            title=story.title,
            summary=story.summary,
            roles=role_descriptions,
            script=story.script_text,
        )
        result = self.llm.generate_json(prompt, temperature=0.75, max_tokens=2500)

        frames: List[StoryboardFrame] = []
        for index, frame in enumerate(result.get("frames", []) or [], start=1):
            frames.append(
                StoryboardFrame(
                    frame_id=frame.get("id", f"frame_{index:02d}"),
                    scene_index=frame.get("scene_index", index),
                    shot_type=frame.get("shot_type", frame.get("camera", "medium")),
                    visual_description=frame.get(
                        "visual_description", frame.get("visual", "")
                    ),
                    dialogue=frame.get("dialogue", frame.get("line", "")),
                    style_reference=frame.get("style", frame.get("style_reference", "")),
                )
            )

        logger.info("分镜生成完成，共 %d 个镜头", len(frames))
        return frames


class VideoSlicePlanner:
    """根据分镜规划视频切片"""

    def __init__(self, config: ConfigLoader):
        self.config = config
        self.default_duration = float(self.config.get("video.slice_duration", 5))
        self.base_url = self.config.get(
            "output.slice_base_url", "https://cdn.example.com/slices"
        )

    def create_slices(
        self, project_id: str, frames: List[StoryboardFrame]
    ) -> List[VideoSlice]:
        print_step("规划视频切片")
        slices: List[VideoSlice] = []
        for index, frame in enumerate(frames, start=1):
            slice_id = f"slice_{index:02d}"
            asset_url = f"{self.base_url}/{project_id}/{slice_id}.mp4"
            slices.append(
                VideoSlice(
                    slice_id=slice_id,
                    frame_id=frame.frame_id,
                    description=frame.visual_description,
                    duration=self.default_duration,
                    asset_url=asset_url,
                )
            )

        logger.info("切片规划完成，共 %d 段", len(slices))
        return slices


class FinalAssembler:
    """生成最终视频的占位URL"""

    def __init__(self, config: ConfigLoader):
        self.config = config
        self.base_url = self.config.get(
            "output.final_video_base_url", "https://cdn.example.com/final"
        )

    def assemble(self, project_id: str, slices: List[VideoSlice]) -> str:
        print_step("合成最终视频")
        if not slices:
            raise ValueError("切片列表为空，无法生成最终视频")

        final_url = f"{self.base_url}/{project_id}.mp4"
        logger.info("最终视频占位URL: %s", final_url)
        return final_url


class StoryWorkflowBranch:
    """围绕短剧生产的完整工作流分支"""

    def __init__(self, config: ConfigLoader, llm_client: LLMClient):
        self.config = config
        self.story_creator = StoryCreator(config, llm_client)
        self.role_generator = RoleGenerator(config, llm_client)
        self.storyboard_designer = StoryboardDesigner(config, llm_client)
        self.slice_planner = VideoSlicePlanner(config)
        self.final_assembler = FinalAssembler(config)

    def run(
        self, concept: str, project_id: Optional[str] = None
    ) -> StoryWorkflowResult:
        if project_id is None:
            project_id = f"story_{uuid.uuid4().hex[:8]}"

        print_section("【分支】短剧完整流程")
        story = self.story_creator.create(concept)
        roles = self.role_generator.generate(story)
        storyboard = self.storyboard_designer.design(story, roles)
        slices = self.slice_planner.create_slices(project_id, storyboard)
        final_url = self.final_assembler.assemble(project_id, slices)

        return StoryWorkflowResult(
            project_id=project_id,
            concept=concept,
            story=story,
            roles=roles,
            storyboard=storyboard,
            video_slices=slices,
            final_video_url=final_url,
        )
