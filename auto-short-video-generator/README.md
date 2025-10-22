# 短视频自动生成工具 🎬

一个完全自动化的短视频生成系统，专门用于生成民间故事/历史剧情类短视频。只需输入一个主题，即可自动生成包含文案、配音、图片、字幕的完整视频。

## ✨ 核心功能

### 🎯 全自动化工作流

```mermaid
flowchart TD
    Start([📥 用户输入]) -->|主题文本| A[🎯 主题分析]

    A -->|主题+上下文| A1[📊 风格匹配]
    A1 -->|风格类型| A2[📝 结构设计]
    A2 -->|StyleAnalysis| B[✍️ 文案创作]

    B -->|风格+主题| B1[🎭 叙事生成]
    B1 -->|原始文案| B2[🔧 文案优化]
    B2 -->|Script对象| C[🏆 标题生成]

    B2 -->|完整文案| D[🎙️ 语音合成]
    B2 -->|文案内容| E[🎨 图片生成]

    C -->|文案内容| C1[🎣 提取钩子]
    C1 -->|情绪点| C2[📋 生成候选]
    C2 -->|5个标题| C3[⭐ 智能评分]
    C3 -->|最佳标题| End

    D -->|文案分段| D1[🔪 文本分割]
    D1 -->|文本片段| D2[🗣️ 语音转换]
    D2 -->|音频片段| D3[⏱️ 时间对齐]
    D3 -->|音频列表| F[📝 字幕生成]

    E -->|文案+风格| E1[🖼️ 场景描述]
    E1 -->|英文提示词| E2[🎨 AI绘图]
    E2 -->|图片URL| E3[💾 图片下载]
    E3 -->|图片列表| G

    D3 -->|音频+时间| F
    F -->|时间轴| F1[✂️ 字幕分段]
    F1 -->|时间+文本| F2[📄 格式生成]
    F2 -->|字幕列表| G

    G[🎬 视频合成] -->|图片+时长| G1[📹 创建片段]
    G1 -->|视频片段| G2[📝 添加字幕]
    G2 -->|视频+字幕| G3[🔊 音频合并]
    G3 -->|完整视频| G4[📦 编码输出]
    G4 -->|MP4文件| End([✅ 成品视频])

    style Start fill:#e1f5e1,stroke:#4caf50,stroke-width:3px
    style End fill:#e3f2fd,stroke:#2196f3,stroke-width:3px

    style A fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style A1 fill:#ffe0b2,stroke:#ff9800,stroke-width:2px
    style A2 fill:#ffe0b2,stroke:#ff9800,stroke-width:2px

    style B fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    style B1 fill:#f8bbd0,stroke:#e91e63,stroke-width:2px
    style B2 fill:#f8bbd0,stroke:#e91e63,stroke-width:2px

    style C fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style C1 fill:#e1bee7,stroke:#9c27b0,stroke-width:2px
    style C2 fill:#e1bee7,stroke:#9c27b0,stroke-width:2px
    style C3 fill:#e1bee7,stroke:#9c27b0,stroke-width:2px

    style D fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style D1 fill:#c8e6c9,stroke:#4caf50,stroke-width:2px
    style D2 fill:#c8e6c9,stroke:#4caf50,stroke-width:2px
    style D3 fill:#c8e6c9,stroke:#4caf50,stroke-width:2px

    style E fill:#e0f2f1,stroke:#009688,stroke-width:2px
    style E1 fill:#b2dfdb,stroke:#009688,stroke-width:2px
    style E2 fill:#b2dfdb,stroke:#009688,stroke-width:2px
    style E3 fill:#b2dfdb,stroke:#009688,stroke-width:2px

    style F fill:#fff9c4,stroke:#ffc107,stroke-width:2px
    style F1 fill:#fff59d,stroke:#ffc107,stroke-width:2px
    style F2 fill:#fff59d,stroke:#ffc107,stroke-width:2px

    style G fill:#e1bee7,stroke:#9c27b0,stroke-width:2px
    style G1 fill:#ce93d8,stroke:#9c27b0,stroke-width:2px
    style G2 fill:#ce93d8,stroke:#9c27b0,stroke-width:2px
    style G3 fill:#ce93d8,stroke:#9c27b0,stroke-width:2px
    style G4 fill:#ce93d8,stroke:#9c27b0,stroke-width:2px
```

**流程说明**：

🎨 **节点设计**：图标 + 任务名称（≤10字）
📊 **连线标注**：输入/输出数据类型
🎯 **颜色分组**：按功能模块区分

**执行工具映射**：

| 模块 | 节点 | 执行工具 |
|------|------|----------|
| 🟠 策划 | 主题分析/风格匹配/结构设计 | Coze Chat / GPT-4 + 提示词工程 |
| 🔴 文案 | 文案创作/叙事生成/文案优化 | Coze Chat / GPT-4 + 格式处理 |
| 🟣 标题 | 提取钩子/生成候选/智能评分 | Coze Chat / GPT-4 LLM |
| 🟢 语音 | 文本分割/语音转换/时间对齐 | Edge TTS + Pydub（免费） |
| 🔵 图片 | 场景描述/AI绘图/图片下载 | Coze Workflow / DALL-E 3 |
| 🟡 字幕 | 字幕生成/字幕分段/格式生成 | Python + SRT/ASS |
| 🟣 视频 | 创建片段/添加字幕/音频合并/编码输出 | MoviePy + FFmpeg |

**数据流示例**：
- `主题文本` → 主题分析 → `StyleAnalysis` → 文案创作 → `Script对象`
- `完整文案` → 语音合成 → `音频列表` → 字幕生成 → `字幕列表`
- `文案内容` → 图片生成 → `图片列表` → 视频合成 → `成品视频`

### 📋 功能模块

1. **智能策划** - 分析主题，自动生成适合的风格和叙事结构
   - 权力结构型
   - 市井羞辱型
   - 极端人性抉择
   - 社会机制型
   - 命运反转型
   - 悬疑揭秘型

2. **文案创作** - 生成1000+字的专业口播稿
   - 第二人称视角（"你是..."）
   - 强情绪 + 高反转
   - 7段式叙事结构
   - 每行15-22字，适配字幕

3. **爆款标题** - 自动提取情绪钩子
   - 强设问/强视觉/强悬念
   - 12-22字黄金长度
   - 多个候选方案

4. **语音合成** - 高质量中文配音
   - 支持Edge TTS（免费）
   - 支持Azure TTS（可选）
   - 自动分段和时间对齐

5. **图片生成** - AI生成历史场景图
   - 支持扣子(Coze) Workflow（推荐）
   - 支持DALL-E 3
   - 支持Stable Diffusion
   - 智能场景描述

6. **字幕生成** - 专业字幕效果
   - SRT/ASS格式
   - 可自定义样式
   - 自动时间对齐

7. **视频合成** - 一键合成成片
   - 9:16竖屏（抖音/快手）
   - 1080x1920高清
   - 音视频完美同步

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- FFmpeg（必须）
- ImageMagick（可选，用于字幕渲染）

### 2. 安装

```bash
# 克隆项目
git clone <repository-url>
cd auto-short-video-generator

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 3. 配置API密钥

编辑 `.env` 文件：

#### 方案一：使用扣子(Coze) API（推荐）

```bash
# 扣子 API（推荐，用于文案生成和图片生成）
COZE_ACCESS_TOKEN=cztei_your-access-token-here
```

**优势**：
- ✅ 一个Token同时支持文本和图像生成
- ✅ 配置简单，只需一个密钥
- ✅ 支持自定义Bot和Workflow

在 `config/config.yaml` 中配置：
```yaml
api:
  llm_provider: "coze"
  coze_bot_id: "your_bot_id"  # Chat机器人ID
  coze_image_workflow_id: "your_workflow_id"  # 图像生成工作流ID
  image_provider: "coze"
```

#### 方案二：使用OpenAI API

```bash
# OpenAI API（用于文案生成和图片生成）
OPENAI_API_KEY=sk-your-api-key-here

# 可选：使用自定义OpenAI兼容接口
OPENAI_BASE_URL=https://api.openai.com/v1
```

#### 方案三：使用Claude API

```bash
# Anthropic Claude API
ANTHROPIC_API_KEY=your-anthropic-key-here
```

**注意**：音视频处理使用免费的Edge TTS和本地FFmpeg，无需额外API

### 4. 运行

```bash
# 基础用法
python main.py "明朝锦衣卫"

# 指定配置文件
python main.py "古代特殊职业" --config config/config.yaml

# 开启调试模式
python main.py "历史奇案" --debug
```

## 📖 使用示例

### 示例1：生成锦衣卫主题视频

```bash
python main.py "明朝锦衣卫的秘密任务"
```

**输出：**
- 标题：《锦衣卫抓到自己亲爹，皇帝却下令必须杀》
- 视频时长：2分30秒
- 文案字数：1200字
- 场景数：12个

### 示例2：生成古代职业视频

```bash
python main.py "古代最危险的职业"
```

**输出：**
- 标题：《这个职业干一天就得死，却有人抢着做》
- 视频时长：3分钟
- 文案字数：1500字
- 场景数：15个

## 🎨 自定义配置

编辑 `config/config.yaml` 可以自定义各种参数：

```yaml
# 视频分辨率
video:
  resolution: [1080, 1920]  # 竖屏 9:16
  fps: 30

# 字幕样式
subtitle:
  font: "SimHei"
  font_size: 48
  font_color: "white"
  stroke_color: "black"

# 文案要求
script:
  min_words: 1000
  max_words: 1500
```

## 📁 项目结构

```
auto-short-video-generator/
├── src/
│   ├── planner/          # 智能策划
│   ├── writer/           # 文案创作
│   ├── title_generator/  # 标题生成
│   ├── tts/              # 语音合成
│   ├── visual/           # 图片生成
│   ├── subtitle/         # 字幕生成
│   ├── compositor/       # 视频合成
│   └── workflow/         # 工作流引擎
├── prompts/              # AI提示词模板
├── config/               # 配置文件
├── output/               # 输出目录
│   ├── videos/          # 最终视频
│   ├── audio/           # 音频文件
│   ├── images/          # 图片素材
│   ├── subtitles/       # 字幕文件
│   └── scripts/         # 文案文本
├── main.py              # 主入口
└── requirements.txt     # 依赖列表
```

## 🔧 高级功能

### 只生成文案（不生成视频）

修改代码可以只运行部分流程：

```python
from src.workflow import VideoPipeline

pipeline = VideoPipeline()
theme = VideoTheme(topic="明朝锦衣卫")

# 只执行策划和文案
style = pipeline.planner.analyze_theme(theme)
script = pipeline.writer.write_script(theme, style)
print(script.content)
```

### 批量生成

```bash
# 创建主题列表
cat topics.txt
明朝锦衣卫
古代特殊职业
历史奇案
...

# 批量生成
while read topic; do
  python main.py "$topic"
done < topics.txt
```

## 🎯 爆款公式

本工具内置的爆款公式：

### 文案结构（7段式）

1. **震撼开头** - 第二人称强代入
2. **角色设定** - 身份地位处境
3. **危机突发** - 矛盾激化
4. **希望破灭** - 情绪跌落
5. **极端选择** - 道德困境
6. **真相反转** - 颠覆认知
7. **宿命结尾** - 引人思考

### 标题钩子

- **强设问**："你知道XXX吗？"
- **强视觉**：具体冲击场景
- **强悬念**："真相竟然是..."
- **强对比**："明明XXX，却XXX"
- **强冲突**："必须XXX，否则XXX"

## 💡 常见问题

### Q: 生成一个视频需要多久？
A: 通常2-5分钟，取决于：
- LLM响应速度（文案生成）
- 图片生成速度（DALL-E较慢）
- 视频时长

### Q: 生成成本多少？
A: 估算单个视频成本：
- OpenAI GPT-4: ~$0.5-1.0（文案+场景描述）
- DALL-E 3: ~$0.4-0.8（10-15张图）
- Edge TTS: 免费
- **总计**: ~$1-2/视频

### Q: 可以用国产大模型吗？
A: 可以！修改配置使用OpenAI兼容接口：
```yaml
api:
  llm_provider: openai
  openai_model: your-model
# .env中设置
OPENAI_BASE_URL=https://your-api-endpoint
```

### Q: 图片生成失败怎么办？
A: 工具会自动创建占位图，确保流程不中断。可以后期替换。

### Q: 可以添加背景音乐吗？
A: 目前版本暂不支持，可以用剪映等工具后期添加。

## 🛠️ 开发指南

### 添加新的风格类型

1. 编辑 `config/config.yaml`：
```yaml
script:
  style_types:
    - "你的新风格"
```

2. 修改 `prompts/planner_prompt.txt` 添加风格描述

### 支持新的TTS引擎

在 `src/tts/tts_engine.py` 中添加：

```python
def _generate_with_custom_tts(self, script, output_name):
    # 你的TTS实现
    pass
```

### 支持新的图片生成器

在 `src/visual/visual_generator.py` 中添加：

```python
def _generate_with_stable_diffusion(self, description, output_path):
    # Stable Diffusion实现
    pass
```

## 📊 性能优化

### 加速生成

1. **使用本地模型**
   - 文案生成：本地部署Qwen/GLM等
   - 图片生成：本地Stable Diffusion

2. **并行处理**
   - 图片生成可并行
   - 音频分段可并行

3. **缓存机制**
   - 相似主题复用场景描述
   - 图片素材库

## 🤝 贡献

欢迎提交Issue和PR！

## 📄 许可证

MIT License

## 🙏 致谢

- OpenAI GPT-4 - 文案生成
- DALL-E 3 - 图片生成
- Edge TTS - 语音合成
- MoviePy - 视频处理
- FFmpeg - 音视频编码

---

**打造爆款短视频，从这里开始！** 🎬✨
