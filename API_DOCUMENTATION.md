# API 文档

## 翻页书单号视频生成工作流 API

本文档描述了翻页书单号视频生成工作流的 API 接口。

---

## 基础信息

- **基础 URL**: `http://localhost:3000`
- **Content-Type**: `application/json`
- **认证**: 目前无需认证（内部使用）

---

## 端点列表

### 1. 健康检查

检查服务是否正常运行。

**请求**:
```http
GET /health
```

**响应示例**:
```json
{
  "status": "ok",
  "message": "翻页书单号视频生成服务运行中"
}
```

**状态码**:
- `200 OK`: 服务正常运行

---

### 2. 获取工作流信息

获取工作流的详细信息，包括输入输出 Schema。

**请求**:
```http
GET /api/workflow/info
```

**响应示例**:
```json
{
  "id": "book-video-generation",
  "name": "翻页书单号视频生成",
  "description": "自动生成抖音翻页书单号视频，包含文案生成、配音、背景图、字幕和特效",
  "inputSchema": {
    "bookName": "书名（必填）",
    "authorName": "作者名（可选）",
    "referenceImage": "参考图片 URL（可选）",
    "douyinUsername": "抖音用户名（必填）"
  },
  "outputSchema": {
    "success": "是否成功",
    "videoUrl": "生成的视频 URL",
    "jianYingDraftUrl": "剪映草稿链接",
    "totalDuration": "视频总时长（秒）",
    "message": "消息"
  }
}
```

**状态码**:
- `200 OK`: 成功获取信息

---

### 3. 执行工作流

执行翻页书单号视频生成工作流。

**请求**:
```http
POST /api/workflow/execute
Content-Type: application/json
```

**请求体 Schema**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `bookName` | string | 是 | 书名 |
| `authorName` | string | 否 | 作者名 |
| `referenceImage` | string | 否 | 参考图片 URL（用于背景图生成） |
| `douyinUsername` | string | 是 | 抖音用户名（显示在视频末尾） |

**请求示例**:
```json
{
  "bookName": "自卑与超越",
  "authorName": "阿德勒",
  "referenceImage": "https://example.com/book-cover.jpg",
  "douyinUsername": "读书分享号"
}
```

**响应示例 (成功)**:
```json
{
  "success": true,
  "videoUrl": "https://cdn.example.com/videos/abc123.mp4",
  "jianYingDraftUrl": "jianying://draft/xyz789",
  "totalDuration": 45.5,
  "message": "视频生成成功！"
}
```

**响应示例 (失败)**:
```json
{
  "success": false,
  "videoUrl": "",
  "jianYingDraftUrl": "",
  "totalDuration": 0,
  "message": "视频生成失败: API 调用超时"
}
```

**状态码**:
- `200 OK`: 成功执行（包括成功和失败的情况，通过 `success` 字段判断）
- `400 Bad Request`: 请求参数错误
- `500 Internal Server Error`: 服务器内部错误

**错误响应示例**:
```json
{
  "success": false,
  "error": "缺少必填参数: bookName"
}
```

---

### 4. 获取示例输入

获取一些示例输入，帮助理解 API 使用方式。

**请求**:
```http
GET /api/examples
```

**响应示例**:
```json
{
  "examples": [
    {
      "bookName": "自卑与超越",
      "authorName": "阿德勒",
      "douyinUsername": "书单推荐号"
    },
    {
      "bookName": "活着",
      "authorName": "余华",
      "douyinUsername": "读书分享"
    },
    {
      "bookName": "人间失格",
      "authorName": "太宰治",
      "douyinUsername": "文学青年"
    }
  ]
}
```

**状态码**:
- `200 OK`: 成功获取示例

---

## 工作流步骤详解

工作流包含以下 5 个步骤，按顺序执行：

### Step 1: 生成文案 (`generate-copywriting`)

**输入**:
- `bookName`: 书名
- `authorName`: 作者名（可选）

**输出**:
- `copywriting`: 生成的走心文案
- `bookName`: 书名
- `authorName`: 作者名

**描述**:
调用 Coze LLM 工作流，根据书名生成戳心的文案。文案要求：
- 不要干巴巴的介绍
- 要有情感共鸣
- 长度 100-150 字
- 语言要有画面感和诗意

---

### Step 2: 拆分文案 (`split-copywriting`)

**输入**:
- `copywriting`: 完整文案
- `bookName`: 书名
- `authorName`: 作者名

**输出**:
- `sentences`: 拆分后的句子数组
- `bookName`: 书名
- `authorName`: 作者名

**描述**:
使用标点符号（。！？）将文案拆分成句子数组，每句单独配音。

---

### Step 3: 生成语音 (`generate-voice`)

**输入**:
- `sentences`: 句子数组
- `bookName`: 书名
- `authorName`: 作者名

**输出**:
- `audioTracks`: 音频轨道数组，每个包含：
  - `text`: 句子文本
  - `audioUrl`: 音频 URL
  - `duration`: 音频时长（秒）
- `bookName`: 书名
- `authorName`: 作者名

**描述**:
为每句文案生成配音，使用温柔女声，语速 0.9 倍。

---

### Step 4: 生成背景图 (`generate-background`)

**输入**:
- `audioTracks`: 音频轨道数组
- `bookName`: 书名
- `authorName`: 作者名
- `referenceImage`: 参考图片 URL（可选）

**输出**:
- `backgroundUrl`: 背景图 URL
- `audioTracks`: 音频轨道数组
- `bookName`: 书名
- `authorName`: 作者名

**描述**:
使用 AI 生成低饱和度动漫风格背景图，分辨率 1920×1080。

---

### Step 5: 合成视频 (`compose-video`)

**输入**:
- `backgroundUrl`: 背景图 URL
- `audioTracks`: 音频轨道数组
- `bookName`: 书名
- `authorName`: 作者名
- `douyinUsername`: 抖音用户名

**输出**:
- `videoUrl`: 生成的视频 URL
- `jianYingDraftUrl`: 剪映草稿链接
- `totalDuration`: 视频总时长（秒）

**描述**:
组合所有元素生成最终视频，包括：
- 翻书动画特效
- 双层字幕（正文白字 + 标题红字）
- 字幕动画（发光模糊、波纹扭曲、飘雪）
- 自动计算时长
- 导出剪映草稿

---

## 使用示例

### cURL

```bash
curl -X POST http://localhost:3000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "bookName": "自卑与超越",
    "authorName": "阿德勒",
    "douyinUsername": "读书分享号"
  }'
```

### JavaScript (Fetch)

```javascript
const response = await fetch('http://localhost:3000/api/workflow/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    bookName: '自卑与超越',
    authorName: '阿德勒',
    douyinUsername: '读书分享号',
  }),
});

const result = await response.json();
console.log(result);
```

### Python (requests)

```python
import requests

url = 'http://localhost:3000/api/workflow/execute'
data = {
    'bookName': '自卑与超越',
    'authorName': '阿德勒',
    'douyinUsername': '读书分享号'
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

---

## 视频输出规格

- **分辨率**: 1920×1080 (Full HD)
- **帧率**: 30 FPS
- **格式**: MP4
- **时长**: 根据配音自动计算（通常 30-60 秒）

### 字幕规格

**正文字幕**:
- 颜色: 白色 (#FFFFFF)
- 字体大小: 48px
- 字体加粗: 是
- 位置: 居中
- 动画: 发光模糊

**标题字幕**:
- 颜色: 红色 (#FF0000)
- 字体大小: 72px (书名) / 56px (作者)
- 字体加粗: 是
- 位置: 顶部
- 动画: 波纹扭曲 + 飘雪

---

## 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 缺少必填参数 | 检查请求体是否包含 `bookName` 和 `douyinUsername` |
| 500 | 服务器内部错误 | 检查服务日志，确认 API Token 配置正确 |

### 工作流执行错误

即使 HTTP 状态码是 200，工作流执行也可能失败。请检查响应中的 `success` 字段：

```json
{
  "success": false,
  "message": "视频生成失败: MCP 插件调用失败"
}
```

---

## 性能说明

- **平均执行时间**: 2-5 分钟（取决于文案长度和 API 响应速度）
- **并发限制**: 建议不超过 5 个并发请求
- **超时设置**: 默认 10 分钟

---

## 注意事项

1. 确保环境变量 `COZE_API_TOKEN` 正确配置
2. 所有 MCP 插件 ID 必须正确
3. 生成的视频 URL 和剪映草稿链接有效期可能有限制
4. 建议在测试环境先验证各个步骤是否正常工作

---

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本
- 支持基础的翻页书单号视频生成
- 集成 Coze LLM、Seedream、语音合成、视频剪辑等 MCP 插件
