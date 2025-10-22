#!/bin/bash
# 批量生成视频脚本

# 主题列表
topics=(
    "明朝锦衣卫的秘密任务"
    "古代特殊职业：仵作"
    "清朝最神秘的机构：粘杆处"
    "大明奇案：空印案"
    "古代最危险的职业：试毒官"
)

# 遍历主题
for topic in "${topics[@]}"; do
    echo "========================================="
    echo "正在生成: $topic"
    echo "========================================="

    python main.py "$topic"

    if [ $? -eq 0 ]; then
        echo "✓ $topic 生成成功"
    else
        echo "✗ $topic 生成失败"
    fi

    echo ""
    sleep 5  # 避免API限流
done

echo "批量生成完成！"
