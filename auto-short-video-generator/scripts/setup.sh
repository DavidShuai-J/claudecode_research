#!/bin/bash
# 环境设置脚本

echo "========================================="
echo "短视频自动生成工具 - 环境设置"
echo "========================================="

# 检查Python版本
echo -n "检查Python版本... "
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version"
else
    echo "✗ 需要Python 3.9+，当前版本: $python_version"
    exit 1
fi

# 检查FFmpeg
echo -n "检查FFmpeg... "
if command -v ffmpeg &> /dev/null; then
    echo "✓ 已安装"
else
    echo "✗ 未安装"
    echo "请安装FFmpeg: sudo apt-get install ffmpeg (Ubuntu/Debian)"
    exit 1
fi

# 创建虚拟环境
echo -n "创建虚拟环境... "
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 完成"
else
    echo "⊙ 已存在"
fi

# 激活虚拟环境
echo -n "激活虚拟环境... "
source venv/bin/activate
echo "✓ 完成"

# 安装依赖
echo "安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建.env文件
if [ ! -f ".env" ]; then
    echo -n "创建.env配置文件... "
    cp .env.example .env
    echo "✓ 完成"
    echo ""
    echo "⚠️  请编辑.env文件，填入你的API密钥！"
    echo ""
fi

# 创建输出目录
echo -n "创建输出目录... "
mkdir -p output/{videos,audio,images,subtitles,scripts}
echo "✓ 完成"

echo ""
echo "========================================="
echo "✓ 环境设置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，填入API密钥"
echo "2. 运行: python main.py \"你的主题\""
echo ""
