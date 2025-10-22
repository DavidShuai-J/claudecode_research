"""数据模型定义"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class VideoTheme(BaseModel):
    """视频主题"""
    topic: str = Field(..., description="主题关键词")
    keywords: Optional[List[str]] = Field(default=None, description="相关关键词")
    target_emotion: Optional[str] = Field(default="震撼", description="目标情绪")


class StyleAnalysis(BaseModel):
    """风格分析结果"""
    style_type: str = Field(..., description="风格类型")
    narrative_structure: str = Field(..., description="叙事结构")
    emotional_arc: List[str] = Field(..., description="情绪曲线")
    key_elements: List[str] = Field(..., description="关键要素")
    reasoning: str = Field(..., description="选择理由")


class Script(BaseModel):
    """口播稿"""
    title: str = Field(..., description="标题")
    content: str = Field(..., description="完整文案")
    segments: List[str] = Field(..., description="分段文案")
    word_count: int = Field(..., description="字数")
    style_type: str = Field(..., description="风格类型")
    keywords: List[str] = Field(default_factory=list, description="关键词")


class TitleCandidate(BaseModel):
    """标题候选"""
    title: str = Field(..., description="标题文案")
    hook_type: str = Field(..., description="钩子类型")
    score: float = Field(..., description="评分 0-100")
    reasoning: str = Field(..., description="评分理由")


class AudioSegment(BaseModel):
    """音频片段"""
    text: str = Field(..., description="文本内容")
    audio_path: str = Field(..., description="音频文件路径")
    duration: float = Field(..., description="时长(秒)")
    start_time: float = Field(default=0.0, description="开始时间")


class VisualSegment(BaseModel):
    """视觉片段"""
    description: str = Field(..., description="画面描述")
    image_path: Optional[str] = Field(default=None, description="图片路径")
    video_path: Optional[str] = Field(default=None, description="视频路径")
    duration: float = Field(..., description="时长(秒)")
    start_time: float = Field(default=0.0, description="开始时间")


class SubtitleSegment(BaseModel):
    """字幕片段"""
    text: str = Field(..., description="字幕文本")
    start_time: float = Field(..., description="开始时间(秒)")
    end_time: float = Field(..., description="结束时间(秒)")
    position: str = Field(default="bottom", description="位置")


class VideoProject(BaseModel):
    """视频项目"""
    project_id: str = Field(..., description="项目ID")
    theme: VideoTheme = Field(..., description="主题")
    style: Optional[StyleAnalysis] = Field(default=None, description="风格分析")
    script: Optional[Script] = Field(default=None, description="脚本")
    titles: List[TitleCandidate] = Field(default_factory=list, description="标题候选")
    audio_segments: List[AudioSegment] = Field(default_factory=list, description="音频片段")
    visual_segments: List[VisualSegment] = Field(default_factory=list, description="视觉片段")
    subtitles: List[SubtitleSegment] = Field(default_factory=list, description="字幕")
    output_path: Optional[str] = Field(default=None, description="输出视频路径")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    class Config:
        arbitrary_types_allowed = True
