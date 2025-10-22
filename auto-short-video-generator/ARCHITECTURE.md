# 系统架构文档 🏗️

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户输入层                           │
│                   (main.py / API)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  工作流编排层                            │
│              (workflow.VideoPipeline)                   │
└─┬───────┬────────┬─────────┬─────────┬────────┬────────┘
  │       │        │         │         │        │
  ▼       ▼        ▼         ▼         ▼        ▼
┌───┐  ┌───┐   ┌────┐   ┌─────┐   ┌─────┐  ┌──────┐
│策 │  │文 │   │标  │   │语音 │   │图片 │  │视频  │
│划 │→ │案 │→ │题  │→ │合成 │→ │生成 │→ │合成  │
└───┘  └───┘   └────┘   └─────┘   └─────┘  └──────┘
                           │         │         │
                           ▼         ▼         ▼
                      ┌────────────────────────────┐
                      │      输出文件系统          │
                      │  (videos/audio/images)    │
                      └────────────────────────────┘
```

## 核心模块

### 1. 智能策划 (Planner)

**职责**: 分析主题，生成视频风格和叙事结构

**输入**:
- `VideoTheme`: 主题关键词

**输出**:
- `StyleAnalysis`: 风格类型、叙事结构、情绪曲线

**关键技术**:
- LLM推理（GPT-4/Claude）
- 提示词工程
- JSON结构化输出

**代码位置**: `src/planner/`

---

### 2. 文案创作 (Writer)

**职责**: 生成1000+字的专业口播稿

**输入**:
- `VideoTheme`: 主题
- `StyleAnalysis`: 风格分析结果

**输出**:
- `Script`: 完整文案、分段文案、关键词

**核心算法**:
```python
# 7段式叙事结构
1. 震撼开头 (强代入)
2. 角色设定 (建立认同)
3. 危机突发 (制造冲突)
4. 希望破灭 (情绪低谷)
5. 极端选择 (道德困境)
6. 真相反转 (认知颠覆)
7. 宿命结尾 (升华主题)
```

**代码位置**: `src/writer/`

---

### 3. 标题生成 (TitleGenerator)

**职责**: 从文案提取钩子，生成爆款标题

**输入**:
- `Script`: 完整文案

**输出**:
- `List[TitleCandidate]`: 5个标题候选，带评分

**评分维度**:
- 钩子强度 (40%)
- 信息密度 (30%)
- 画面感 (20%)
- 字数适配 (10%)

**代码位置**: `src/title_generator/`

---

### 4. 语音合成 (TTS Engine)

**职责**: 将文案转换为语音

**支持引擎**:
- Edge TTS (免费，推荐)
- Azure TTS (付费，高质量)

**技术细节**:
```python
# 分段处理
for segment in script.segments:
    audio = tts.generate(segment)
    audio_segments.append(audio)

# 时间对齐
for i, seg in enumerate(audio_segments):
    seg.start_time = sum(prev.duration for prev in audio_segments[:i])
```

**代码位置**: `src/tts/`

---

### 5. 图片生成 (Visual Generator)

**职责**: 生成历史场景图片

**支持引擎**:
- DALL-E 3 (OpenAI)
- Stable Diffusion (Replicate/本地)

**工作流程**:
```
文案 → LLM生成场景描述(英文) → 图片生成API → 下载保存
```

**场景描述示例**:
```
"A Ming Dynasty secret agent in black uniform,
standing in a dark palace hall, dramatic lighting,
historical Chinese painting style, cinematic"
```

**代码位置**: `src/visual/`

---

### 6. 字幕生成 (Subtitle Generator)

**职责**: 生成SRT/ASS字幕文件

**时间对齐**:
```python
for audio_seg in audio_segments:
    subtitle = SubtitleSegment(
        text=audio_seg.text,
        start_time=audio_seg.start_time,
        end_time=audio_seg.start_time + audio_seg.duration
    )
```

**样式配置**:
- 字体、大小、颜色
- 描边、阴影
- 位置（顶部/底部/居中）

**代码位置**: `src/subtitle/`

---

### 7. 视频合成 (Video Compositor)

**职责**: 将所有素材合成为最终视频

**技术栈**:
- MoviePy (Python视频编辑)
- FFmpeg (底层编码)

**合成流程**:
```python
# 1. 创建图片序列
image_clips = [ImageClip(img, duration=d) for img, d in visuals]

# 2. 拼接视频
video = concatenate_videoclips(image_clips)

# 3. 添加字幕
video = add_subtitles(video, subtitles)

# 4. 添加音频
video = video.set_audio(audio)

# 5. 导出
video.write_videofile(output_path)
```

**代码位置**: `src/compositor/`

---

## 数据流

### 核心数据模型

```python
class VideoProject:
    project_id: str              # 项目ID
    theme: VideoTheme            # 主题
    style: StyleAnalysis         # 风格分析
    script: Script               # 文案
    titles: List[TitleCandidate] # 标题候选
    audio_segments: List[AudioSegment]    # 音频片段
    visual_segments: List[VisualSegment]  # 视觉片段
    subtitles: List[SubtitleSegment]      # 字幕
    output_path: str             # 输出路径
```

### 状态转换

```
VideoTheme
    → StyleAnalysis
    → Script
    → TitleCandidate[]
    → AudioSegment[]
    → VisualSegment[]
    → SubtitleSegment[]
    → VideoFile
```

---

## 配置系统

### 配置文件层次

```
1. config/config.yaml    # 默认配置
2. .env                  # 环境变量（API密钥）
3. 命令行参数            # 运行时覆盖
```

### 配置加载优先级

```
命令行参数 > 环境变量 > config.yaml > 默认值
```

---

## 扩展点

### 1. 添加新的LLM提供商

```python
# src/llm_client.py
def _generate_custom_llm(self, prompt, ...):
    # 实现你的LLM调用逻辑
    pass
```

### 2. 添加新的TTS引擎

```python
# src/tts/tts_engine.py
def _generate_with_custom_tts(self, script, ...):
    # 实现你的TTS逻辑
    pass
```

### 3. 添加新的图片生成器

```python
# src/visual/visual_generator.py
def _generate_with_custom_image(self, description, ...):
    # 实现你的图片生成逻辑
    pass
```

### 4. 自定义视频效果

```python
# src/compositor/video_compositor.py
def add_custom_effect(self, video_clip):
    # 添加转场、滤镜等效果
    pass
```

---

## 性能优化

### 并行处理

```python
# 图片生成可并行
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(generate_image, desc)
        for desc in descriptions
    ]
    images = [f.result() for f in futures]
```

### 缓存机制

```python
# 缓存LLM结果
@lru_cache(maxsize=100)
def generate_scene_description(script_hash):
    return llm.generate(...)
```

### 内存管理

```python
# 及时释放MoviePy资源
try:
    video.write_videofile(...)
finally:
    video.close()
    for clip in clips:
        clip.close()
```

---

## 错误处理

### 重试机制

```python
@retry(tries=3, delay=2, backoff=2)
def call_api():
    return api.generate(...)
```

### 降级策略

```
图片生成失败 → 使用占位图
TTS失败 → 使用备用引擎
字幕渲染失败 → 仅使用SRT文件
```

---

## 监控与日志

### 日志级别

- DEBUG: 详细调试信息
- INFO: 关键步骤
- WARNING: 降级处理
- ERROR: 错误信息

### 性能指标

```python
logger.info(f"文案生成耗时: {elapsed:.2f}秒")
logger.info(f"图片生成耗时: {elapsed:.2f}秒")
logger.info(f"视频合成耗时: {elapsed:.2f}秒")
```

---

## 安全考虑

### API密钥管理

- 使用 `.env` 文件
- 不提交到Git
- 支持环境变量注入

### 内容审核

```python
# TODO: 添加内容审核
def check_content_safety(text):
    # 检查敏感词
    # 检查政治内容
    pass
```

---

## 测试策略

### 单元测试

```bash
pytest tests/test_planner.py
pytest tests/test_writer.py
```

### 集成测试

```bash
pytest tests/test_pipeline.py
```

### 端到端测试

```bash
python main.py "测试主题" --debug
```

---

**更新时间**: 2024
**文档版本**: v1.0
