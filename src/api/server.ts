import express, { Request, Response } from 'express';
import { bookVideoWorkflow } from '../workflows/bookVideoWorkflow';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(express.json());

/**
 * 健康检查端点
 */
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'ok', message: '翻页书单号视频生成服务运行中' });
});

/**
 * 工作流信息端点
 */
app.get('/api/workflow/info', (req: Request, res: Response) => {
  res.json({
    id: 'book-video-generation',
    name: '翻页书单号视频生成',
    description: '自动生成抖音翻页书单号视频，包含文案生成、配音、背景图、字幕和特效',
    inputSchema: {
      bookName: '书名（必填）',
      authorName: '作者名（可选）',
      referenceImage: '参考图片 URL（可选）',
      douyinUsername: '抖音用户名（必填）',
    },
    outputSchema: {
      success: '是否成功',
      videoUrl: '生成的视频 URL',
      jianYingDraftUrl: '剪映草稿链接',
      totalDuration: '视频总时长（秒）',
      message: '消息',
    },
  });
});

/**
 * 执行工作流端点
 * POST /api/workflow/execute
 *
 * 请求体示例:
 * {
 *   "bookName": "自卑与超越",
 *   "authorName": "阿德勒",
 *   "referenceImage": "https://example.com/image.jpg",
 *   "douyinUsername": "我的抖音号"
 * }
 */
app.post('/api/workflow/execute', async (req: Request, res: Response) => {
  try {
    // 验证必填字段
    const { bookName, douyinUsername } = req.body;

    if (!bookName) {
      return res.status(400).json({
        success: false,
        error: '缺少必填参数: bookName',
      });
    }

    if (!douyinUsername) {
      return res.status(400).json({
        success: false,
        error: '缺少必填参数: douyinUsername',
      });
    }

    console.log('📚 开始生成视频，输入参数:', req.body);

    // 执行工作流
    const result = await bookVideoWorkflow.execute({ input: req.body });

    console.log('✅ 视频生成完成:', result);

    // 返回结果
    res.json(result);
  } catch (error: any) {
    console.error('❌ 工作流执行失败:', error);
    res.status(500).json({
      success: false,
      error: error.message || '工作流执行失败',
    });
  }
});

/**
 * 示例请求端点
 * 提供一些示例输入
 */
app.get('/api/examples', (req: Request, res: Response) => {
  res.json({
    examples: [
      {
        bookName: '自卑与超越',
        authorName: '阿德勒',
        douyinUsername: '书单推荐号',
      },
      {
        bookName: '活着',
        authorName: '余华',
        douyinUsername: '读书分享',
      },
      {
        bookName: '人间失格',
        authorName: '太宰治',
        douyinUsername: '文学青年',
      },
    ],
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  🎬 翻页书单号视频生成服务                                       ║
║                                                               ║
║  服务地址: http://localhost:${PORT}                            ║
║                                                               ║
║  可用端点:                                                     ║
║  - GET  /health                 健康检查                       ║
║  - GET  /api/workflow/info      工作流信息                     ║
║  - POST /api/workflow/execute   执行工作流                     ║
║  - GET  /api/examples           获取示例输入                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
  `);
});

export default app;
