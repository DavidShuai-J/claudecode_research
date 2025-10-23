#!/usr/bin/env node

/**
 * 使用代理测试 Coze API
 * 通过 HTTP/HTTPS 代理连接到 Coze API
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');
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

/**
 * 通过代理发送 HTTPS 请求
 */
function httpsRequestViaProxy(targetUrl, options = {}, postData = null) {
  return new Promise((resolve, reject) => {
    const proxyUrl = process.env.HTTPS_PROXY || process.env.HTTP_PROXY;
    if (!proxyUrl) {
      reject(new Error('未设置代理'));
      return;
    }

    const proxy = new URL(proxyUrl);
    const target = new URL(targetUrl);

    const connectOptions = {
      host: proxy.hostname,
      port: proxy.port || 80,
      method: 'CONNECT',
      path: `${target.hostname}:${target.port || 443}`,
      headers: {
        'Host': target.hostname,
      },
    };

    // 如果代理需要认证
    if (proxy.username && proxy.password) {
      const auth = Buffer.from(`${proxy.username}:${proxy.password}`).toString('base64');
      connectOptions.headers['Proxy-Authorization'] = `Basic ${auth}`;
    }

    const connectReq = http.request(connectOptions);

    connectReq.on('connect', (res, socket, head) => {
      if (res.statusCode !== 200) {
        reject(new Error(`代理连接失败: ${res.statusCode} ${res.statusMessage}`));
        return;
      }

      const requestOptions = {
        socket: socket,
        path: target.pathname + target.search,
        method: options.method || 'GET',
        headers: options.headers || {},
      };

      const httpsReq = https.request(requestOptions, (httpsRes) => {
        let data = '';

        httpsRes.on('data', (chunk) => {
          data += chunk;
        });

        httpsRes.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            resolve({
              statusCode: httpsRes.statusCode,
              headers: httpsRes.headers,
              data: jsonData,
            });
          } catch (e) {
            resolve({
              statusCode: httpsRes.statusCode,
              headers: httpsRes.headers,
              data: data,
            });
          }
        });
      });

      httpsReq.on('error', (error) => {
        reject(error);
      });

      if (postData) {
        httpsReq.write(postData);
      }

      httpsReq.end();
    });

    connectReq.on('error', (error) => {
      reject(error);
    });

    connectReq.end();
  });
}

/**
 * 测试 1: Workflow API
 */
async function test1_WorkflowAPI() {
  console.log('\n' + '='.repeat(60));
  console.log('测试 1: Coze Workflow API (文案生成)');
  console.log('='.repeat(60));

  try {
    const postData = JSON.stringify({
      workflow_id: WORKFLOW_ID,
      parameters: {
        input: '请为《活着》这本书写一段超戳心的文案，100字以内',
      },
    });

    const result = await httpsRequestViaProxy(
      'https://api.coze.cn/v1/workflow/run',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
        },
      },
      postData
    );

    console.log('\n✅ 成功调用 Workflow API');
    console.log(`状态码: ${result.statusCode}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
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
    const postData = JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/list',
      params: {},
      id: Date.now(),
    });

    const result = await httpsRequestViaProxy(
      `https://mcp.coze.cn/v1/plugins/${PLUGIN_VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
        },
      },
      postData
    );

    console.log('\n✅ 成功调用 MCP API');
    console.log(`状态码: ${result.statusCode}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
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
    const postData = JSON.stringify({
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
    });

    const result = await httpsRequestViaProxy(
      `https://mcp.coze.cn/v1/plugins/${PLUGIN_VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_TOKEN}`,
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
        },
      },
      postData
    );

    console.log('\n✅ 成功调用 MCP 工具');
    console.log(`状态码: ${result.statusCode}`);
    console.log('\n响应数据:');
    console.log(JSON.stringify(result.data, null, 2));
  } catch (error) {
    console.error('\n❌ 失败:', error.message);
  }
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     Coze API 代理测试工具                                █');
  console.log('█                                                          █');
  console.log('█'.repeat(60));

  console.log(`\n✅ 代理: ${process.env.HTTPS_PROXY ? '已配置' : '未配置'}`);
  console.log(`✅ API Token: ${API_TOKEN ? API_TOKEN.substring(0, 20) + '...' : '未设置'}`);

  await test1_WorkflowAPI();
  await test2_ListTools();
  await test3_CallTool();

  console.log('\n' + '█'.repeat(60));
  console.log('█                                                          █');
  console.log('█     测试完成                                             █');
  console.log('█                                                          █');
  console.log('█'.repeat(60) + '\n');
}

main().catch(console.error);
