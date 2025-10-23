#!/usr/bin/env node

/**
 * Coze 插件详情查询脚本
 * 用于获取插件的详细信息，包括可用的工具、参数等
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 手动读取 .env 文件
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
const BASE_URL = 'api.coze.cn';

// 插件 ID 列表
const PLUGINS = {
  '图像生成': process.env.PLUGIN_IMAGE_GENERATION_ID,
  '图像编辑': process.env.PLUGIN_IMAGE_EDIT_ID,
  '视频剪辑': process.env.PLUGIN_VIDEO_EDIT_ID,
  '音乐生成': process.env.PLUGIN_MUSIC_GENERATION_ID,
  '联网问答': process.env.PLUGIN_WEB_QA_ID,
  '语音合成': process.env.PLUGIN_VOICE_SYNTHESIS_ID,
  '视频生成': process.env.PLUGIN_VIDEO_GENERATION_ID,
  '添加文字': process.env.PLUGIN_ADD_TEXT_ID,
};

/**
 * 发送 HTTPS GET 请求
 */
function httpsGet(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: BASE_URL,
      path: path,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json',
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
          resolve({ statusCode: res.statusCode, headers: res.headers, data: jsonData });
        } catch (e) {
          resolve({ statusCode: res.statusCode, headers: res.headers, data: data });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.end();
  });
}

/**
 * 尝试不同的 API 端点获取插件详情
 */
async function getPluginDetails(pluginId, pluginName) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🔍 查询插件: ${pluginName} (ID: ${pluginId})`);
  console.log('='.repeat(60));

  // 尝试的 API 路径列表
  const apiPaths = [
    `/v1/plugins/${pluginId}`,
    `/v1/plugin/${pluginId}`,
    `/open_api/v1/plugins/${pluginId}`,
    `/open_api/v1/plugin/${pluginId}`,
    `/api/v1/plugins/${pluginId}`,
    `/v1/plugins/${pluginId}/info`,
    `/v1/plugins/${pluginId}/detail`,
  ];

  for (const path of apiPaths) {
    try {
      console.log(`\n📡 尝试端点: ${path}`);
      const result = await httpsGet(path);

      console.log(`   状态码: ${result.statusCode}`);

      if (result.statusCode === 200) {
        console.log(`   ✅ 成功获取插件详情！`);
        console.log('\n📋 插件详情:');
        console.log(JSON.stringify(result.data, null, 2));
        return result.data;
      } else if (result.statusCode === 401) {
        console.log(`   ❌ 认证失败 (401) - 请检查 API Token`);
        return null;
      } else if (result.statusCode === 403) {
        console.log(`   ❌ 权限不足 (403)`);
      } else if (result.statusCode === 404) {
        console.log(`   ⚠️  未找到 (404)`);
      } else {
        console.log(`   ⚠️  响应: ${JSON.stringify(result.data).substring(0, 200)}`);
      }
    } catch (error) {
      console.log(`   ❌ 错误: ${error.message}`);
    }

    // 添加延迟避免频繁请求
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log(`\n❌ 所有端点都无法获取插件详情`);
  return null;
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     Coze 插件详情查询工具                                █');
  console.log('█                                                          █');
  console.log('█'.repeat(60));

  if (!API_TOKEN) {
    console.error('\n❌ 错误: 未设置 COZE_API_TOKEN 环境变量');
    console.log('请在 .env 文件中设置 COZE_API_TOKEN');
    process.exit(1);
  }

  console.log(`\n✅ API Token: ${API_TOKEN.substring(0, 20)}...`);
  console.log(`📦 待查询插件数量: ${Object.keys(PLUGINS).length}`);

  // 只查询第一个插件作为示例
  const firstPlugin = Object.entries(PLUGINS)[0];
  if (firstPlugin) {
    const [name, id] = firstPlugin;
    await getPluginDetails(id, name);
  }

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     查询完成                                             █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');

  console.log('\n💡 提示:');
  console.log('   如需查询所有插件，请修改代码中的循环部分');
  console.log('   如果所有端点都失败，请查阅官方文档:');
  console.log('   https://www.coze.cn/open/docs/developer_guides/get_plugin\n');
}

// 执行主函数
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { getPluginDetails };
