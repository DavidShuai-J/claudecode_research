# 快速入门指南 🚀

## 5分钟快速开始

### 第一步：环境准备

```bash
# 1. 确保已安装Python 3.9+和FFmpeg
python3 --version
ffmpeg -version

# 2. 运行自动设置脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 第二步：配置API密钥

编辑 `.env` 文件：

```bash
nano .env
```

填入你的OpenAI API密钥：

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

保存并退出（Ctrl+X，然后Y，然后Enter）

### 第三步：生成第一个视频

```bash
python main.py "明朝锦衣卫"
```

等待2-5分钟，视频将自动生成在 `output/videos/` 目录！

## 常用命令

```bash
# 生成视频
python main.py "你的主题"

# 查看帮助
python main.py --help

# 开启调试模式
python main.py "主题" --debug

# 批量生成
chmod +x scripts/batch_generate.sh
./scripts/batch_generate.sh
```

## 查看结果

生成的文件位置：

- **最终视频**: `output/videos/video_YYYYMMDD_HHMMSS_xxx.mp4`
- **文案文本**: `output/scripts/video_YYYYMMDD_HHMMSS_xxx.txt`
- **音频文件**: `output/audio/`
- **图片素材**: `output/images/`
- **字幕文件**: `output/subtitles/`

## 推荐主题

适合爆款的主题示例：

### 历史权力类
- "明朝锦衣卫的秘密任务"
- "清朝粘杆处的恐怖"
- "东厂西厂的权力之争"

### 古代职业类
- "古代试毒官的一天"
- "仵作：最接近真相的人"
- "大内侍卫的残酷训练"

### 历史奇案类
- "大明空印案"
- "清朝文字狱"
- "最离奇的科举舞弊案"

### 极端人性类
- "如果你是明朝锦衣卫，抓到的是你亲爹"
- "生死抉择：救皇帝还是救儿子"
- "卧底十年，身份暴露那一刻"

## 常见问题

### Q: 生成失败，显示API错误？
A: 检查 `.env` 文件中的API密钥是否正确。

### Q: 图片生成很慢？
A: DALL-E生成图片较慢，单张需要10-30秒，请耐心等待。

### Q: 想用其他语言模型？
A: 修改 `config/config.yaml`：
```yaml
api:
  llm_provider: openai  # 或 anthropic
  openai_model: gpt-4-turbo-preview
```

### Q: 可以只生成文案吗？
A: 可以！运行：
```bash
python example.py text
```

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 查看 [example.py](example.py) 学习API用法
- 修改 `config/config.yaml` 自定义参数
- 编辑 `prompts/` 中的提示词模板

## 技术支持

遇到问题？

1. 查看日志文件 `video_generator.log`
2. 运行 `python main.py --debug` 查看详细信息
3. 提交Issue到GitHub仓库

---

**开始创作爆款视频吧！** 🎬
