#!/usr/bin/env node

/**
 * 网络连接诊断脚本
 * 测试各个 Coze API 端点的可达性
 */

const https = require('https');
const http = require('http');
const dns = require('dns');

// 要测试的域名列表
const DOMAINS = [
  'api.coze.cn',
  'api.coze.com',
  'mcp.coze.cn',
  'www.coze.cn',
];

// 要测试的 API 端点
const API_ENDPOINTS = [
  { method: 'GET', url: 'https://api.coze.cn/v1/health', desc: 'Coze API 健康检查' },
  { method: 'GET', url: 'https://api.coze.com/v1/health', desc: 'Coze.com API 健康检查' },
  { method: 'GET', url: 'https://www.coze.cn', desc: 'Coze 官网' },
];

/**
 * DNS 解析测试
 */
function testDNS(domain) {
  return new Promise((resolve) => {
    dns.resolve4(domain, (err, addresses) => {
      if (err) {
        resolve({ domain, success: false, error: err.message });
      } else {
        resolve({ domain, success: true, addresses });
      }
    });
  });
}

/**
 * HTTP(S) 连接测试
 */
function testHTTP(endpoint) {
  return new Promise((resolve) => {
    const urlObj = new URL(endpoint.url);
    const protocol = urlObj.protocol === 'https:' ? https : http;

    const req = protocol.request(
      {
        hostname: urlObj.hostname,
        path: urlObj.pathname,
        method: endpoint.method,
        timeout: 5000,
      },
      (res) => {
        resolve({
          url: endpoint.url,
          success: true,
          statusCode: res.statusCode,
          headers: res.headers,
        });
      }
    );

    req.on('error', (error) => {
      resolve({
        url: endpoint.url,
        success: false,
        error: error.message,
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        url: endpoint.url,
        success: false,
        error: 'Request timeout',
      });
    });

    req.end();
  });
}

/**
 * 主函数
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('🔍 Coze API 网络诊断工具');
  console.log('='.repeat(60));

  // 1. DNS 解析测试
  console.log('\n📡 DNS 解析测试\n');

  for (const domain of DOMAINS) {
    const result = await testDNS(domain);
    if (result.success) {
      console.log(`✅ ${domain}`);
      console.log(`   IP: ${result.addresses.join(', ')}`);
    } else {
      console.log(`❌ ${domain}`);
      console.log(`   错误: ${result.error}`);
    }
  }

  // 2. HTTP(S) 连接测试
  console.log('\n\n🌐 HTTP(S) 连接测试\n');

  for (const endpoint of API_ENDPOINTS) {
    console.log(`测试: ${endpoint.desc}`);
    console.log(`URL: ${endpoint.url}`);

    const result = await testHTTP(endpoint);
    if (result.success) {
      console.log(`✅ 连接成功`);
      console.log(`   状态码: ${result.statusCode}`);
    } else {
      console.log(`❌ 连接失败`);
      console.log(`   错误: ${result.error}`);
    }
    console.log('');
  }

  // 3. 代理检测
  console.log('\n🔐 代理配置检测\n');
  console.log(`HTTP_PROXY: ${process.env.HTTP_PROXY || '(未设置)'}`);
  console.log(`HTTPS_PROXY: ${process.env.HTTPS_PROXY || '(未设置)'}`);
  console.log(`NO_PROXY: ${process.env.NO_PROXY || '(未设置)'}`);

  console.log('\n' + '='.repeat(60));
  console.log('诊断完成');
  console.log('='.repeat(60) + '\n');
}

main().catch(console.error);
