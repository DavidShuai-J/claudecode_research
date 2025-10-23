#!/usr/bin/env node

/**
 * 使用 Axios 和代理测试 Coze API
 */

const axios = require('axios');
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
const WORKFLOW_ID = process.env.COZE_WORKFLOW_ID;
const PLUGIN_VOICE_ID = process.env.PLUGIN_VOICE_SYNTHESIS_ID;

// 创建 axios 实例，配置代理
const proxyUrl = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;
let axiosConfig = {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
  },
  timeout: 30000,
};

if (proxyUrl) {
  console.log(`📡 使用代理: ${proxyUrl.substring(0, 50)}...`);
  // Axios 会自动使用环境变量中的代理
}

const apiClient = axios.create(axiosConfig);

/**
 * 测试 1: Workflow API
 */
async function test1_WorkflowAPI() {
  console.log('\n' + '='.repeat(60));
  console.log('测试 1: Coze Workflow API (文案生成)');
  console.log('='.repeat(60));

  try {
    const response = await apiClient.post(
      'https://api.coze.cn/v1/workflow/run',
      {
        workflow_id: WORKFLOW_ID,
        parameters: {
          input: '请为《活着》这本书写一段超戳心的文案，100字以内',
        },
      }
    );

    console.log('\n✅ 成功调用 Workflow API');
    console.log(`状态码: ${response.status}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(response.data, null, 2));

    return response.data;
  } catch (error) {
    console.error('\n❌ 失败:');
    if (error.response) {
      console.error(`   状态码: ${error.response.status}`);
      console.error(`   响应: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      console.error(`   错误: ${error.message}`);
    }
    return null;
  }
}

/**
 * 测试 2: MCP 插件 - 列出工具
 */
async function test2_ListTools() {
  console.log('\n' + '='.repeat(60));
  console.log('测试 2: MCP 插件 - 列出语音合成工具');
  console.log('='.repeat(60));

  try {
    const response = await apiClient.post(
      `https://mcp.coze.cn/v1/plugins/${PLUGIN_VOICE_ID}`,
      {
        jsonrpc: '2.0',
        method: 'tools/list',
        params: {},
        id: Date.now(),
      }
    );

    console.log('\n✅ 成功调用 MCP API');
    console.log(`状态码: ${response.status}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(response.data, null, 2));

    return response.data;
  } catch (error) {
    console.error('\n❌ 失败:');
    if (error.response) {
      console.error(`   状态码: ${error.response.status}`);
      console.error(`   响应: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      console.error(`   错误: ${error.message}`);
    }
    return null;
  }
}

/**
 * 测试 3: MCP 插件 - 调用工具
 */
async function test3_CallTool() {
  console.log('\n' + '='.repeat(60));
  console.log('测试 3: MCP 插件 - 调用语音合成工具');
  console.log('='.repeat(60));

  try {
    const response = await apiClient.post(
      `https://mcp.coze.cn/v1/plugins/${PLUGIN_VOICE_ID}`,
      {
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: 'synthesize_voice',
          arguments: {
            text: '你好，这是一个测试',
            voice: 'gentle_female',
            speed: 0.9,
          },
        },
        id: Date.now(),
      }
    );

    console.log('\n✅ 成功调用 MCP 工具');
    console.log(`状态码: ${response.status}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(response.data, null, 2));

    return response.data;
  } catch (error) {
    console.error('\n❌ 失败:');
    if (error.response) {
      console.error(`   状态码: ${error.response.status}`);
      console.error(`   响应: ${JSON.stringify(error.response.data, null, 2)}`);
    } else {
      console.error(`   错误: ${error.message}`);
    }
    return null;
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     Coze API Axios 测试工具                              █');
  console.log('█                                                          █');
  console.log('█'.repeat(60));

  console.log(`\n✅ API Token: ${API_TOKEN ? API_TOKEN.substring(0, 20) + '...' : '未设置'}`);

  const results = {};

  results.workflow = await test1_WorkflowAPI();
  results.listTools = await test2_ListTools();
  results.callTool = await test3_CallTool();

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     测试完成                                             █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');

  // 总结
  console.log('\n📊 测试总结:');
  console.log(`   Workflow API: ${results.workflow ? '✅ 成功' : '❌ 失败'}`);
  console.log(`   List Tools:   ${results.listTools ? '✅ 成功' : '❌ 失败'}`);
  console.log(`   Call Tool:    ${results.callTool ? '✅ 成功' : '❌ 失败'}`);
  console.log('');
}

main().catch(console.error);
