import { createWorkflow, createStep } from '@mastra/core';
import { z } from 'zod';
import { CozeClient } from '../utils/cozeClient';
import dotenv from 'dotenv';

dotenv.config();

const cozeClient = new CozeClient(process.env.COZE_API_TOKEN!);

/**
 * 步骤 1: 生成文案
 * 使用 Coze LLM 工作流生成走心的书单文案
 */
const generateCopywritingStep = createStep({
  id: 'generate-copywriting',
  description: '生成走心的书单文案',
  inputSchema: z.object({
    bookName: z.string().describe('书名'),
    authorName: z.string().optional().describe('作者名（可选）'),
  }),
  outputSchema: z.object({
    copywriting: z.string().describe('生成的文案'),
    bookName: z.string().describe('书名'),
    authorName: z.string().optional().describe('作者名'),
  }),
  execute: async ({ context }) => {
    const { bookName, authorName } = context;

    // 构造提示词
    const prompt = `请为《${bookName}》这本书写一段超戳心的文案，要求：
1. 不要干巴巴的介绍，要像"枕头里发霉的梦"这种能把人看沉默的句子
2. 文案要有情感共鸣，引发思考
3. 长度控制在 100-150 字
4. 语言要有画面感和诗意
${authorName ? `5. 作者是 ${authorName}` : ''}`;

    // 调用 Coze 工作流生成文案
    const response = await cozeClient.runWorkflow(
      process.env.COZE_WORKFLOW_ID!,
      { input: prompt }
    );

    return {
      copywriting: response.data.output || response.output,
      bookName,
      authorName,
    };
  },
});

/**
 * 步骤 2: 拆分文案
 * 将文案拆分成句子数组
 */
const splitCopywritingStep = createStep({
  id: 'split-copywriting',
  description: '将文案拆分成句子',
  inputSchema: z.object({
    copywriting: z.string().describe('完整文案'),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  outputSchema: z.object({
    sentences: z.array(z.string()).describe('拆分后的句子数组'),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    const { copywriting, bookName, authorName } = context;

    // 使用标点符号拆分句子
    const sentences = copywriting
      .split(/[。！？\n]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);

    return {
      sentences,
      bookName,
      authorName,
    };
  },
});

/**
 * 步骤 3: 生成语音
 * 为每句文案生成配音
 */
const generateVoiceStep = createStep({
  id: 'generate-voice',
  description: '为每句文案生成配音',
  inputSchema: z.object({
    sentences: z.array(z.string()),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  outputSchema: z.object({
    audioTracks: z.array(z.object({
      text: z.string(),
      audioUrl: z.string(),
      duration: z.number().describe('音频时长（秒）'),
    })),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    const { sentences, bookName, authorName } = context;

    const audioTracks = [];

    // 为每句话生成配音
    for (const sentence of sentences) {
      const audioUrl = await cozeClient.synthesizeVoice(sentence, 0.9);

      // 估算音频时长（假设每个字 0.5 秒，0.9 倍速后约 0.55 秒/字）
      const estimatedDuration = sentence.length * 0.55;

      audioTracks.push({
        text: sentence,
        audioUrl,
        duration: estimatedDuration,
      });
    }

    return {
      audioTracks,
      bookName,
      authorName,
    };
  },
});

/**
 * 步骤 4: 生成背景图
 * 使用 AI 生成低饱和度动漫风格背景图
 */
const generateBackgroundStep = createStep({
  id: 'generate-background',
  description: '生成背景图',
  inputSchema: z.object({
    audioTracks: z.array(z.any()),
    bookName: z.string(),
    authorName: z.string().optional(),
    referenceImage: z.string().optional().describe('参考图片 URL'),
  }),
  outputSchema: z.object({
    backgroundUrl: z.string().describe('背景图 URL'),
    audioTracks: z.array(z.any()),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    const { audioTracks, bookName, authorName, referenceImage } = context;

    // 构造背景图提示词
    const prompt = `${bookName}主题背景图，低饱和度，动漫风格，唯美，温馨，不要血腥元素，适合作为读书分享视频背景`;

    // 生成背景图
    const backgroundUrl = await cozeClient.generateImage(prompt, 1920, 1080);

    return {
      backgroundUrl,
      audioTracks,
      bookName,
      authorName,
    };
  },
});

/**
 * 步骤 5: 合成视频
 * 组合所有元素生成最终视频
 */
const composeVideoStep = createStep({
  id: 'compose-video',
  description: '合成视频并添加字幕、特效',
  inputSchema: z.object({
    backgroundUrl: z.string(),
    audioTracks: z.array(z.object({
      text: z.string(),
      audioUrl: z.string(),
      duration: z.number(),
    })),
    bookName: z.string(),
    authorName: z.string().optional(),
    douyinUsername: z.string().describe('抖音用户名'),
  }),
  outputSchema: z.object({
    videoUrl: z.string().describe('生成的视频 URL'),
    jianYingDraftUrl: z.string().describe('剪映草稿链接'),
    totalDuration: z.number().describe('视频总时长（秒）'),
  }),
  execute: async ({ context }) => {
    const { backgroundUrl, audioTracks, bookName, authorName, douyinUsername } = context;

    // 计算总时长
    const totalDuration = audioTracks.reduce((sum, track) => sum + track.duration, 0);

    // 构建视频编辑配置
    const videoConfig = {
      background: {
        type: 'image',
        url: backgroundUrl,
        duration: totalDuration,
      },
      animations: [
        {
          type: 'page-flip', // 翻书动画
          startTime: 0,
          duration: totalDuration,
        },
      ],
      audioTracks: audioTracks.map((track, index) => ({
        url: track.audioUrl,
        startTime: audioTracks.slice(0, index).reduce((sum, t) => sum + t.duration, 0),
        duration: track.duration,
      })),
      textLayers: [
        // 第一层：正文白字
        ...audioTracks.map((track, index) => ({
          text: track.text,
          startTime: audioTracks.slice(0, index).reduce((sum, t) => sum + t.duration, 0),
          duration: track.duration,
          style: {
            color: '#FFFFFF',
            fontSize: 48,
            fontWeight: 'bold',
            position: 'center',
            animation: 'glow-blur', // 发光模糊动画
          },
        })),
        // 第二层：书名和作者红字大标题
        {
          text: `《${bookName}》`,
          startTime: 0,
          duration: 3,
          style: {
            color: '#FF0000',
            fontSize: 72,
            fontWeight: 'bold',
            position: 'top',
            animation: ['ripple-distort', 'snow'], // 波纹扭曲 + 飘雪
          },
        },
        ...(authorName ? [{
          text: authorName,
          startTime: 0,
          duration: 3,
          style: {
            color: '#FF0000',
            fontSize: 56,
            fontWeight: 'bold',
            position: 'top-subtitle',
            animation: ['ripple-distort', 'snow'],
          },
        }] : []),
        // 结尾：抖音用户名
        {
          text: `@${douyinUsername}`,
          startTime: totalDuration - 2,
          duration: 2,
          style: {
            color: '#FFFFFF',
            fontSize: 40,
            position: 'bottom-right',
          },
        },
      ],
      effects: [
        {
          type: 'snow', // 飘雪特效
          startTime: 0,
          duration: totalDuration,
        },
      ],
      output: {
        format: 'mp4',
        resolution: '1920x1080',
        fps: 30,
        exportToDraft: true, // 导出为剪映草稿
      },
    };

    // 调用视频编辑服务
    const result = await cozeClient.editVideo(videoConfig);

    return {
      videoUrl: result.videoUrl || result.url,
      jianYingDraftUrl: result.draftUrl || result.jianYingDraftUrl,
      totalDuration,
    };
  },
});

/**
 * 完整工作流定义
 * 翻页书单号视频生成工作流
 */
export const bookVideoWorkflow = createWorkflow({
  id: 'book-video-generation',
  name: '翻页书单号视频生成',
  description: '自动生成抖音翻页书单号视频，包含文案生成、配音、背景图、字幕和特效',

  // 工作流输入 Schema
  inputSchema: z.object({
    bookName: z.string().describe('书名（必填）'),
    authorName: z.string().optional().describe('作者名（可选）'),
    referenceImage: z.string().optional().describe('参考图片 URL（可选）'),
    douyinUsername: z.string().describe('抖音用户名（必填）'),
  }),

  // 工作流输出 Schema
  outputSchema: z.object({
    success: z.boolean(),
    videoUrl: z.string().describe('生成的视频 URL'),
    jianYingDraftUrl: z.string().describe('剪映草稿链接'),
    totalDuration: z.number().describe('视频总时长（秒）'),
    message: z.string().optional(),
  }),

  // 定义步骤执行顺序
  steps: [
    generateCopywritingStep,
    splitCopywritingStep,
    generateVoiceStep,
    generateBackgroundStep,
    composeVideoStep,
  ],

  // 执行工作流
  execute: async ({ input }) => {
    try {
      // Step 1: 生成文案
      const step1Result = await generateCopywritingStep.execute({ context: input });

      // Step 2: 拆分文案
      const step2Result = await splitCopywritingStep.execute({ context: step1Result });

      // Step 3: 生成语音
      const step3Result = await generateVoiceStep.execute({ context: step2Result });

      // Step 4: 生成背景图
      const step4Result = await generateBackgroundStep.execute({
        context: { ...step3Result, referenceImage: input.referenceImage },
      });

      // Step 5: 合成视频
      const step5Result = await composeVideoStep.execute({
        context: { ...step4Result, douyinUsername: input.douyinUsername },
      });

      return {
        success: true,
        videoUrl: step5Result.videoUrl,
        jianYingDraftUrl: step5Result.jianYingDraftUrl,
        totalDuration: step5Result.totalDuration,
        message: '视频生成成功！',
      };
    } catch (error: any) {
      return {
        success: false,
        videoUrl: '',
        jianYingDraftUrl: '',
        totalDuration: 0,
        message: `视频生成失败: ${error.message}`,
      };
    }
  },
});
