/**
 * 工作流演示脚本
 * 展示翻页书单号视频生成工作流的完整结构和数据流
 *
 * 此脚本不需要实际调用 API，而是模拟整个工作流的执行过程
 */

import { z } from 'zod';

// ============================================
// Mastra 框架核心（简化实现）
// ============================================

interface StepContext<T = any> {
  context: T;
}

interface Step<TInput = any, TOutput = any> {
  id: string;
  description: string;
  inputSchema: z.ZodType<TInput>;
  outputSchema: z.ZodType<TOutput>;
  execute: (params: StepContext<TInput>) => Promise<TOutput>;
}

function createStep<TInput = any, TOutput = any>(config: {
  id: string;
  description: string;
  inputSchema: z.ZodType<TInput>;
  outputSchema: z.ZodType<TOutput>;
  execute: (params: StepContext<TInput>) => Promise<TOutput>;
}): Step<TInput, TOutput> {
  return config;
}

interface Workflow<TInput = any, TOutput = any> {
  id: string;
  name: string;
  description: string;
  inputSchema: z.ZodType<TInput>;
  outputSchema: z.ZodType<TOutput>;
  execute: (params: { input: TInput }) => Promise<TOutput>;
}

function createWorkflow<TInput = any, TOutput = any>(config: {
  id: string;
  name: string;
  description: string;
  inputSchema: z.ZodType<TInput>;
  outputSchema: z.ZodType<TOutput>;
  execute: (params: { input: TInput }) => Promise<TOutput>;
}): Workflow<TInput, TOutput> {
  return config;
}

// ============================================
// 工作流步骤定义
// ============================================

/**
 * 步骤 1: 生成文案
 */
const generateCopywritingStep = createStep({
  id: 'generate-copywriting',
  description: '生成走心的书单文案',
  inputSchema: z.object({
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  outputSchema: z.object({
    copywriting: z.string(),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    console.log(`\n📝 [Step 1] 生成文案 - 书名: ${context.bookName}`);

    // 模拟 API 调用
    await delay(1000);

    const copywriting = `你以为的自卑是缺点，其实是上天给你的礼物。
那些藏在枕头里发霉的梦，原来都是通往超越的阶梯。
阿德勒说，每个人都在用一生的时间，治愈童年的伤痕。
但真正的勇气，不是假装坚强，而是接纳自己的不完美。`;

    console.log(`✅ 文案生成成功:\n${copywriting.substring(0, 50)}...`);

    return {
      copywriting,
      bookName: context.bookName,
      authorName: context.authorName,
    };
  },
});

/**
 * 步骤 2: 拆分文案
 */
const splitCopywritingStep = createStep({
  id: 'split-copywriting',
  description: '将文案拆分成句子',
  inputSchema: z.object({
    copywriting: z.string(),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  outputSchema: z.object({
    sentences: z.array(z.string()),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    console.log(`\n✂️  [Step 2] 拆分文案`);

    const sentences = context.copywriting
      .split(/[。！？\n]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);

    console.log(`✅ 文案已拆分为 ${sentences.length} 句`);
    sentences.forEach((s, i) => console.log(`   ${i + 1}. ${s}`));

    return {
      sentences,
      bookName: context.bookName,
      authorName: context.authorName,
    };
  },
});

/**
 * 步骤 3: 生成语音
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
      duration: z.number(),
    })),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    console.log(`\n🎙️  [Step 3] 生成语音 (温柔女声, 0.9x 速度)`);

    const audioTracks = [];

    for (let i = 0; i < context.sentences.length; i++) {
      const sentence = context.sentences[i];
      await delay(300);

      const duration = sentence.length * 0.55; // 估算时长
      const audioUrl = `https://cdn.example.com/audio/track_${i + 1}.mp3`;

      audioTracks.push({
        text: sentence,
        audioUrl,
        duration,
      });

      console.log(`   ✅ 第 ${i + 1} 句配音完成 (${duration.toFixed(1)}秒)`);
    }

    const totalDuration = audioTracks.reduce((sum, t) => sum + t.duration, 0);
    console.log(`✅ 全部配音完成，总时长: ${totalDuration.toFixed(1)}秒`);

    return {
      audioTracks,
      bookName: context.bookName,
      authorName: context.authorName,
    };
  },
});

/**
 * 步骤 4: 生成背景图
 */
const generateBackgroundStep = createStep({
  id: 'generate-background',
  description: '生成背景图',
  inputSchema: z.object({
    audioTracks: z.array(z.any()),
    bookName: z.string(),
    authorName: z.string().optional(),
    referenceImage: z.string().optional(),
  }),
  outputSchema: z.object({
    backgroundUrl: z.string(),
    audioTracks: z.array(z.any()),
    bookName: z.string(),
    authorName: z.string().optional(),
  }),
  execute: async ({ context }) => {
    console.log(`\n🎨 [Step 4] 生成背景图 (低饱和度动漫风格, 1920x1080)`);
    console.log(`   主题: ${context.bookName}`);

    await delay(1500);

    const backgroundUrl = 'https://cdn.example.com/backgrounds/book_bg_anime.jpg';
    console.log(`✅ 背景图生成成功: ${backgroundUrl}`);

    return {
      backgroundUrl,
      audioTracks: context.audioTracks,
      bookName: context.bookName,
      authorName: context.authorName,
    };
  },
});

/**
 * 步骤 5: 合成视频
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
    douyinUsername: z.string(),
  }),
  outputSchema: z.object({
    videoUrl: z.string(),
    jianYingDraftUrl: z.string(),
    totalDuration: z.number(),
  }),
  execute: async ({ context }) => {
    console.log(`\n🎬 [Step 5] 合成视频`);
    console.log(`   - 背景图: ${context.backgroundUrl}`);
    console.log(`   - 音频轨道: ${context.audioTracks.length} 个`);
    console.log(`   - 特效: 翻书动画 + 双层字幕 + 飘雪`);

    const totalDuration = context.audioTracks.reduce((sum, t) => sum + t.duration, 0);

    // 模拟视频合成过程
    console.log(`\n   [处理中]`);
    console.log(`   ⏳ 添加翻书动画...`);
    await delay(500);

    console.log(`   ⏳ 添加正文字幕 (白色, 发光模糊)...`);
    await delay(500);

    console.log(`   ⏳ 添加标题字幕 (红色, 波纹扭曲)...`);
    await delay(500);

    console.log(`   ⏳ 添加飘雪特效...`);
    await delay(500);

    console.log(`   ⏳ 渲染视频 (1920x1080, 30fps)...`);
    await delay(1000);

    console.log(`   ⏳ 生成剪映草稿...`);
    await delay(500);

    const videoUrl = 'https://cdn.example.com/videos/book_video_final.mp4';
    const jianYingDraftUrl = 'jianying://draft/abc123xyz789';

    console.log(`\n✅ 视频合成完成!`);
    console.log(`   📹 视频链接: ${videoUrl}`);
    console.log(`   📋 剪映草稿: ${jianYingDraftUrl}`);
    console.log(`   ⏱️  时长: ${totalDuration.toFixed(1)}秒`);
    console.log(`   👤 创作者: @${context.douyinUsername}`);

    return {
      videoUrl,
      jianYingDraftUrl,
      totalDuration,
    };
  },
});

// ============================================
// 完整工作流
// ============================================

const bookVideoWorkflow = createWorkflow({
  id: 'book-video-generation',
  name: '翻页书单号视频生成',
  description: '自动生成抖音翻页书单号视频',

  inputSchema: z.object({
    bookName: z.string(),
    authorName: z.string().optional(),
    referenceImage: z.string().optional(),
    douyinUsername: z.string(),
  }),

  outputSchema: z.object({
    success: z.boolean(),
    videoUrl: z.string(),
    jianYingDraftUrl: z.string(),
    totalDuration: z.number(),
    message: z.string().optional(),
  }),

  execute: async ({ input }) => {
    console.log('\n' + '='.repeat(60));
    console.log('🎬 翻页书单号视频生成工作流');
    console.log('='.repeat(60));
    console.log(`\n📚 输入参数:`);
    console.log(`   书名: ${input.bookName}`);
    console.log(`   作者: ${input.authorName || '(未指定)'}`);
    console.log(`   抖音号: @${input.douyinUsername}`);

    try {
      // Step 1
      const step1Result = await generateCopywritingStep.execute({ context: input });

      // Step 2
      const step2Result = await splitCopywritingStep.execute({ context: step1Result });

      // Step 3
      const step3Result = await generateVoiceStep.execute({ context: step2Result });

      // Step 4
      const step4Result = await generateBackgroundStep.execute({
        context: { ...step3Result, referenceImage: input.referenceImage },
      });

      // Step 5
      const step5Result = await composeVideoStep.execute({
        context: { ...step4Result, douyinUsername: input.douyinUsername },
      });

      console.log('\n' + '='.repeat(60));
      console.log('✅ 工作流执行成功！');
      console.log('='.repeat(60));

      return {
        success: true,
        videoUrl: step5Result.videoUrl,
        jianYingDraftUrl: step5Result.jianYingDraftUrl,
        totalDuration: step5Result.totalDuration,
        message: '视频生成成功！',
      };
    } catch (error: any) {
      console.log('\n' + '='.repeat(60));
      console.log('❌ 工作流执行失败');
      console.log('='.repeat(60));
      console.error(`错误: ${error.message}`);

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

// ============================================
// 辅助函数
// ============================================

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// 主程序
// ============================================

async function main() {
  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     翻页书单号视频生成工作流 - 演示程序                  █');
  console.log('█     基于 Mastra 框架                                     █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');

  // 示例 1: 《自卑与超越》
  console.log('\n📖 示例 1: 生成《自卑与超越》视频\n');
  const result1 = await bookVideoWorkflow.execute({
    input: {
      bookName: '自卑与超越',
      authorName: '阿德勒',
      douyinUsername: '读书分享号',
    },
  });

  console.log('\n📊 最终输出:');
  console.log(JSON.stringify(result1, null, 2));

  // 示例 2: 《活着》
  console.log('\n\n' + '─'.repeat(60));
  console.log('\n📖 示例 2: 生成《活着》视频\n');
  const result2 = await bookVideoWorkflow.execute({
    input: {
      bookName: '活着',
      authorName: '余华',
      douyinUsername: '文学爱好者',
    },
  });

  console.log('\n📊 最终输出:');
  console.log(JSON.stringify(result2, null, 2));

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     演示完成！                                           █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');
}

// 运行主程序
if (require.main === module) {
  main().catch(console.error);
}

export { bookVideoWorkflow };
