#!/usr/bin/env node

/**
 * 翻页书单号视频生成工作流 - 演示程序
 *
 * 此脚本展示了基于 Mastra 框架的完整工作流结构和数据流
 * 不需要实际调用 API，而是模拟整个工作流的执行过程
 */

// ============================================
// 辅助函数
// ============================================

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// 工作流步骤定义
// ============================================

/**
 * 步骤 1: 生成文案
 */
async function generateCopywriting(context) {
  console.log(`\n📝 [Step 1] 生成文案 - 书名: ${context.bookName}`);

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
}

/**
 * 步骤 2: 拆分文案
 */
async function splitCopywriting(context) {
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
}

/**
 * 步骤 3: 生成语音
 */
async function generateVoice(context) {
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
}

/**
 * 步骤 4: 生成背景图
 */
async function generateBackground(context) {
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
}

/**
 * 步骤 5: 合成视频
 */
async function composeVideo(context) {
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
}

// ============================================
// 完整工作流
// ============================================

async function executeWorkflow(input) {
  console.log('\n' + '='.repeat(60));
  console.log('🎬 翻页书单号视频生成工作流');
  console.log('='.repeat(60));
  console.log(`\n📚 输入参数:`);
  console.log(`   书名: ${input.bookName}`);
  console.log(`   作者: ${input.authorName || '(未指定)'}`);
  console.log(`   抖音号: @${input.douyinUsername}`);

  try {
    // Step 1: 生成文案
    const step1Result = await generateCopywriting(input);

    // Step 2: 拆分文案
    const step2Result = await splitCopywriting(step1Result);

    // Step 3: 生成语音
    const step3Result = await generateVoice(step2Result);

    // Step 4: 生成背景图
    const step4Result = await generateBackground({
      ...step3Result,
      referenceImage: input.referenceImage,
    });

    // Step 5: 合成视频
    const step5Result = await composeVideo({
      ...step4Result,
      douyinUsername: input.douyinUsername,
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
  } catch (error) {
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
  const result1 = await executeWorkflow({
    bookName: '自卑与超越',
    authorName: '阿德勒',
    douyinUsername: '读书分享号',
  });

  console.log('\n📊 最终输出:');
  console.log(JSON.stringify(result1, null, 2));

  // 示例 2: 《活着》
  console.log('\n\n' + '─'.repeat(60));
  console.log('\n📖 示例 2: 生成《活着》视频\n');
  const result2 = await executeWorkflow({
    bookName: '活着',
    authorName: '余华',
    douyinUsername: '文学爱好者',
  });

  console.log('\n📊 最终输出:');
  console.log(JSON.stringify(result2, null, 2));

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     演示完成！                                           █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');

  console.log('\n💡 提示: 这只是演示程序，实际使用需要:');
  console.log('   1. 安装依赖: npm install');
  console.log('   2. 配置 .env 文件中的 API Token');
  console.log('   3. 启动 API 服务器: npm run dev');
  console.log('   4. 调用 POST /api/workflow/execute 接口\n');
}

// 运行主程序
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { executeWorkflow };
