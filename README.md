# 翻页书单号视频生成工作流

基于 Mastra 框架的自动化视频生成工作流，可以一键生成抖音"翻页书单号"风格的视频。

## 功能特点

- **智能文案生成**：输入书名，自动生成戳心的文案
- **自动配音**：文案自动拆句，每句独立配音（温柔女声，0.9倍速）
- **AI 背景图**：自动生成低饱和度动漫风格背景图（1920×1080）
- **翻书动画**：视频开头添加翻书动画特效
- **双层字幕**：
  - 第一层：正文白字 + 发光模糊动画
  - 第二层：书名/作者红字大标题 + 波纹扭曲 + 飘雪特效
- **自动时长计算**：根据配音时长自动调整动画和字幕时长
- **剪映草稿导出**：一键生成剪映草稿链接，直接导入剪映发布

## 技术栈

- **框架**: Mastra (工作流编排)
- **语言**: TypeScript
- **API 服务**: Express
- **AI 服务**:
  - Coze LLM API (文案生成)
  - Doubao-Seedream-4.0 MCP (背景图生成)
  - 语音合成 MCP (配音生成)
  - 视频剪辑工具 MCP (视频编辑)
  - 添加文字 MCP (字幕添加)

## 项目结构

```
.
├── src/
│   ├── workflows/
│   │   └── bookVideoWorkflow.ts    # 主工作流定义
│   ├── utils/
│   │   └── cozeClient.ts           # Coze API 客户端
│   └── api/
│       └── server.ts                # Express API 服务器
├── .env                             # 环境变量配置
├── package.json                     # 项目依赖
├── tsconfig.json                    # TypeScript 配置
└── README.md                        # 项目文档
```

## 安装

```bash
# 安装依赖
npm install
```

## 配置

在 `.env` 文件中配置必要的 API 凭证：

```env
# Coze API 配置
COZE_API_TOKEN=your_coze_api_token_here
COZE_WORKFLOW_ID=7564000473180553225

# API 服务器配置
PORT=3000
```

## 运行

```bash
# 开发模式
npm run dev

# 构建
npm run build

# 生产模式
npm start
```

## API 使用

### 1. 健康检查

```bash
GET http://localhost:3000/health
```

### 2. 获取工作流信息

```bash
GET http://localhost:3000/api/workflow/info
```

### 3. 执行工作流

```bash
POST http://localhost:3000/api/workflow/execute
Content-Type: application/json

{
  "bookName": "自卑与超越",
  "authorName": "阿德勒",
  "referenceImage": "https://example.com/image.jpg",
  "douyinUsername": "我的抖音号"
}
```

**请求参数说明**:
- `bookName` (必填): 书名
- `authorName` (可选): 作者名
- `referenceImage` (可选): 参考图片 URL
- `douyinUsername` (必填): 抖音用户名（显示在视频末尾）

**响应示例**:
```json
{
  "success": true,
  "videoUrl": "https://example.com/video.mp4",
  "jianYingDraftUrl": "jianying://draft/xxxx",
  "totalDuration": 45.5,
  "message": "视频生成成功！"
}
```

### 4. 获取示例输入

```bash
GET http://localhost:3000/api/examples
```

## 工作流步骤

工作流包含以下 5 个步骤：

1. **生成文案** (`generate-copywriting`)
   - 输入: 书名、作者名
   - 输出: 走心的文案内容

2. **拆分文案** (`split-copywriting`)
   - 输入: 完整文案
   - 输出: 拆分后的句子数组

3. **生成语音** (`generate-voice`)
   - 输入: 句子数组
   - 输出: 每句的配音 URL 和时长

4. **生成背景图** (`generate-background`)
   - 输入: 书名、参考图（可选）
   - 输出: AI 生成的背景图 URL

5. **合成视频** (`compose-video`)
   - 输入: 所有素材（背景图、配音、文案等）
   - 输出: 最终视频 URL 和剪映草稿链接

## 使用示例

### 示例 1: 基本使用

```bash
curl -X POST http://localhost:3000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "bookName": "活着",
    "authorName": "余华",
    "douyinUsername": "读书分享"
  }'
```

### 示例 2: 带参考图

```bash
curl -X POST http://localhost:3000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "bookName": "人间失格",
    "authorName": "太宰治",
    "referenceImage": "https://example.com/book-cover.jpg",
    "douyinUsername": "文学青年"
  }'
```

## 视频特效说明

### 字幕效果

1. **正文字幕**（白色）
   - 颜色: #FFFFFF
   - 字体大小: 48px
   - 动画: 发光模糊 (`glow-blur`)
   - 位置: 居中

2. **标题字幕**（红色）
   - 颜色: #FF0000
   - 字体大小: 72px (书名) / 56px (作者)
   - 动画: 波纹扭曲 + 飘雪 (`ripple-distort` + `snow`)
   - 位置: 顶部

### 动画效果

- **翻书动画**: 贯穿全视频，营造翻页感
- **飘雪特效**: 贯穿全视频，增加氛围感
- **发光模糊**: 字幕逐句出现，带发光效果
- **波纹扭曲**: 标题字幕动态效果

## Mastra 工作流结构

本项目遵循 Mastra 框架的标准结构：

```typescript
// 定义步骤
const step = createStep({
  id: 'step-id',
  description: '步骤描述',
  inputSchema: z.object({ /* Zod schema */ }),
  outputSchema: z.object({ /* Zod schema */ }),
  execute: async ({ context }) => { /* 执行逻辑 */ }
});

// 创建工作流
const workflow = createWorkflow({
  id: 'workflow-id',
  name: '工作流名称',
  inputSchema: z.object({ /* 输入 schema */ }),
  outputSchema: z.object({ /* 输出 schema */ }),
  steps: [step1, step2, ...],
  execute: async ({ input }) => { /* 工作流逻辑 */ }
});
```

## 注意事项

1. 确保所有环境变量正确配置
2. Coze API Token 需要有相应插件的访问权限
3. 生成的视频时长取决于文案长度和配音速度
4. 建议在测试环境先验证各个 MCP 插件是否正常工作

## License

MIT
