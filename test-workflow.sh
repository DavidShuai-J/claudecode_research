#!/bin/bash

# 翻页书单号视频生成工作流测试脚本

echo "========================================="
echo "翻页书单号视频生成工作流测试"
echo "========================================="
echo ""

# 服务器地址
BASE_URL="http://localhost:3000"

# 1. 健康检查
echo "1. 健康检查..."
curl -s "${BASE_URL}/health" | jq .
echo ""

# 2. 获取工作流信息
echo "2. 获取工作流信息..."
curl -s "${BASE_URL}/api/workflow/info" | jq .
echo ""

# 3. 获取示例输入
echo "3. 获取示例输入..."
curl -s "${BASE_URL}/api/examples" | jq .
echo ""

# 4. 执行工作流 - 示例 1
echo "4. 执行工作流 - 生成《自卑与超越》视频..."
curl -s -X POST "${BASE_URL}/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "bookName": "自卑与超越",
    "authorName": "阿德勒",
    "douyinUsername": "读书分享号"
  }' | jq .
echo ""

# 5. 执行工作流 - 示例 2
echo "5. 执行工作流 - 生成《活着》视频..."
curl -s -X POST "${BASE_URL}/api/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "bookName": "活着",
    "authorName": "余华",
    "douyinUsername": "文学爱好者"
  }' | jq .
echo ""

echo "========================================="
echo "测试完成！"
echo "========================================="
