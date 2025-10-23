#!/usr/bin/env node

/**
 * Coze 插件调用完整示例
 *
 * 本示例展示如何正确使用 MCP 协议调用 Coze 插件
 * 基于 JSON-RPC 2.0 标准
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 加载环境变量
function loadEnv() {
  const envPath = path.join(__dirname, '..', '.env');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    envContent.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split('=');
        const value = valueParts.join('=');
        process.env[key] = value;
      }
    });
  }
}

loadEnv();

const API_TOKEN = process.env.COZE_API_TOKEN;
const PLUGIN_VOICE_SYNTHESIS_ID = process.env.PLUGIN_VOICE_SYNTHESIS_ID;
const PLUGIN_IMAGE_GENERATION_ID = process.env.PLUGIN_IMAGE_GENERATION_ID;

/**
 * 发送 MCP 请求（JSON-RPC 2.0）
 */
function sendMCPRequest(pluginId, method, params) {
  return new Promise((resolve, reject) => {
    const requestBody = JSON.stringify({
      jsonrpc: '2.0',
      method: method,
      params: params,
      id: Date.now(),
    });

    const options = {
      hostname: 'mcp.coze.cn',
      path: `/v1/plugins/${pluginId}`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(requestBody),
      },
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);

          // 检查 JSON-RPC 错误
          if (jsonData.error) {
            reject(new Error(`MCP 错误 [${jsonData.error.code}]: ${jsonData.error.message}`));
            return;
          }

          resolve({
            statusCode: res.statusCode,
            data: jsonData,
            result: jsonData.result,
          });
        } catch (e) {
          reject(new Error(`解析响应失败: ${e.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(requestBody);
    req.end();
  });
}

/**
 * 示例 1: 列出插件提供的所有工具
 */
async function example1_ListPluginTools() {
  console.log('\n' + '='.repeat(60));
  console.log('示例 1: 列出插件工具');
  console.log('='.repeat(60));

  try {
    const response = await sendMCPRequest(
      PLUGIN_VOICE_SYNTHESIS_ID,
      'tools/list',
      {}
    );

    console.log('\n✅ 成功获取插件工具列表');
    console.log(`状态码: ${response.statusCode}`);
    console.log('\n工具列表:');
    console.log(JSON.stringify(response.result, null, 2));
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
  }
}

/**
 * 示例 2: 调用语音合成工具
 */
async function example2_CallVoiceSynthesis() {
  console.log('\n' + '='.repeat(60));
  console.log('示例 2: 调用语音合成工具');
  console.log('='.repeat(60));

  try {
    const response = await sendMCPRequest(
      PLUGIN_VOICE_SYNTHESIS_ID,
      'tools/call',
      {
        name: 'synthesize_voice',
        arguments: {
          text: '你好，这是一个测试语音合成的示例',
          voice: 'gentle_female',
          speed: 0.9,
        },
      }
    );

    console.log('\n✅ 成功调用语音合成工具');
    console.log(`状态码: ${response.statusCode}`);
    console.log('\n调用结果:');
    console.log(JSON.stringify(response.result, null, 2));

    // 提取音频 URL
    if (response.result && response.result.content) {
      const textContent = response.result.content.find(item => item.type === 'text');
      if (textContent) {
        console.log('\n📄 音频 URL:', textContent.text);
      }
    }
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
  }
}

/**
 * 示例 3: 调用图像生成工具
 */
async function example3_CallImageGeneration() {
  console.log('\n' + '='.repeat(60));
  console.log('示例 3: 调用图像生成工具');
  console.log('='.repeat(60));

  try {
    const response = await sendMCPRequest(
      PLUGIN_IMAGE_GENERATION_ID,
      'tools/call',
      {
        name: 'generate_image',
        arguments: {
          prompt: '低饱和度动漫风格的书籍背景图，温馨唯美',
          width: 1920,
          height: 1080,
          style: 'anime',
          quality: 'high',
        },
      }
    );

    console.log('\n✅ 成功调用图像生成工具');
    console.log(`状态码: ${response.statusCode}`);
    console.log('\n调用结果:');
    console.log(JSON.stringify(response.result, null, 2));

    // 提取图片 URL
    if (response.result && response.result.content) {
      const textContent = response.result.content.find(item => item.type === 'text');
      if (textContent) {
        console.log('\n🖼️  图片 URL:', textContent.text);
      }
    }
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
  }
}

/**
 * 示例 4: 完整的工作流示例
 */
async function example4_CompleteWorkflow() {
  console.log('\n' + '='.repeat(60));
  console.log('示例 4: 完整的翻页书单号视频生成工作流');
  console.log('='.repeat(60));

  console.log('\n📚 输入: 《自卑与超越》');

  try {
    // Step 1: 生成文案（使用 Workflow API）
    console.log('\n📝 Step 1: 生成文案...');
    console.log('   (此步骤需要调用 Workflow API，略过演示)');

    const mockCopywriting = '你以为的自卑是缺点，其实是上天给你的礼物。';

    // Step 2: 语音合成
    console.log('\n🎙️  Step 2: 生成语音...');
    const voiceResult = await sendMCPRequest(
      PLUGIN_VOICE_SYNTHESIS_ID,
      'tools/call',
      {
        name: 'synthesize_voice',
        arguments: {
          text: mockCopywriting,
          voice: 'gentle_female',
          speed: 0.9,
        },
      }
    );

    console.log('   ✅ 语音生成成功');
    if (voiceResult.result && voiceResult.result.content) {
      const textContent = voiceResult.result.content.find(item => item.type === 'text');
      if (textContent) {
        console.log(`   音频 URL: ${textContent.text}`);
      }
    }

    // Step 3: 生成背景图
    console.log('\n🎨 Step 3: 生成背景图...');
    const imageResult = await sendMCPRequest(
      PLUGIN_IMAGE_GENERATION_ID,
      'tools/call',
      {
        name: 'generate_image',
        arguments: {
          prompt: '自卑与超越主题背景图，低饱和度动漫风格',
          width: 1920,
          height: 1080,
          style: 'anime',
        },
      }
    );

    console.log('   ✅ 背景图生成成功');
    if (imageResult.result && imageResult.result.content) {
      const textContent = imageResult.result.content.find(item => item.type === 'text');
      if (textContent) {
        console.log(`   图片 URL: ${textContent.text}`);
      }
    }

    console.log('\n✅ 工作流执行成功！');
  } catch (error) {
    console.error('\n❌ 工作流执行失败:', error.message);
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     Coze 插件调用完整示例                                 █');
  console.log('█     基于 MCP (JSON-RPC 2.0) 协议                         █');
  console.log('█                                                          █');
  console.log('█'.repeat(60));

  if (!API_TOKEN) {
    console.error('\n❌ 错误: 未设置 COZE_API_TOKEN 环境变量');
    process.exit(1);
  }

  console.log(`\n✅ API Token: ${API_TOKEN.substring(0, 20)}...`);

  // 运行所有示例
  await example1_ListPluginTools();
  await example2_CallVoiceSynthesis();
  await example3_CallImageGeneration();
  await example4_CompleteWorkflow();

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     所有示例执行完成                                      █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');

  console.log('\n💡 重要说明:');
  console.log('   1. 所有 MCP 插件调用使用 JSON-RPC 2.0 协议');
  console.log('   2. 请求格式: { jsonrpc: "2.0", method, params, id }');
  console.log('   3. 响应格式: { jsonrpc: "2.0", result, id }');
  console.log('   4. 错误格式: { jsonrpc: "2.0", error: { code, message }, id }');
  console.log('\n📚 参考文档:');
  console.log('   - 获取插件详情: https://www.coze.cn/open/docs/developer_guides/get_plugin');
  console.log('   - 调用插件工具: https://www.coze.cn/open/docs/developer_guides/call_plugin_tool');
  console.log('   - JSON-RPC 2.0: https://www.jsonrpc.org/specification\n');
}

// 运行主函数
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  sendMCPRequest,
};
