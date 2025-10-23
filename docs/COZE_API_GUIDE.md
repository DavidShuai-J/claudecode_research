# Coze API 调用指南

本文档基于你提供的配置信息，说明如何正确调用 Coze 插件 API。

## 1. API 认证

所有 API 调用都需要在 Header 中包含 Bearer Token：

```bash
Authorization: Bearer pat_iRAbnGWILCaudRctPMkZ8fFGuH9xxoiz4CtHsGBhGwGlVrdgB3nS2o8KvOrOImrL
```

## 2. MCP (Model Context Protocol) 插件调用

根据你提供的 MCP 配置，插件调用使用 **JSON-RPC 2.0** 协议。

### 2.1 MCP 配置格式

```json
{
  "mcpServers": {
    "server_name": {
      "url": "https://mcp.coze.cn/v1/plugins/{plugin_id}",
      "headers": {
        "Authorization": "Bearer ${COZE_API_TOKEN}"
      }
    }
  }
}
```

### 2.2 JSON-RPC 2.0 调用格式

MCP 使用标准的 JSON-RPC 2.0 格式：

```json
{
  "jsonrpc": "2.0",
  "method": "method_name",
  "params": {
    "参数1": "值1",
    "参数2": "值2"
  },
  "id": 1
}
```

### 2.3 常见的 MCP 方法

根据 MCP 协议，常见方法包括：

- `tools/list` - 列出插件提供的所有工具
- `tools/call` - 调用特定的工具
- `resources/list` - 列出可用资源
- `prompts/list` - 列出可用提示

## 3. 插件详情查询

### 3.1 方法 1: 通过 MCP 协议

```bash
POST https://mcp.coze.cn/v1/plugins/{plugin_id}
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

### 3.2 方法 2: 通过 Coze API

```bash
GET https://api.coze.cn/v1/plugins/{plugin_id}
Authorization: Bearer {your_token}
```

或

```bash
GET https://api.coze.com/v1/plugins/{plugin_id}
Authorization: Bearer {your_token}
```

## 4. 插件工具调用

### 4.1 MCP 标准调用格式

```bash
POST https://mcp.coze.cn/v1/plugins/{plugin_id}
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "arg1": "value1",
      "arg2": "value2"
    }
  },
  "id": 1
}
```

### 4.2 响应格式

成功响应：

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "结果内容"
      }
    ]
  },
  "id": 1
}
```

错误响应：

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "错误信息"
  },
  "id": 1
}
```

## 5. 具体插件调用示例

### 5.1 语音合成插件

```bash
POST https://mcp.coze.cn/v1/plugins/7426655854067351562
Content-Type: application/json
Authorization: Bearer pat_iRAbnGWILCaudRct...

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "synthesize_voice",
    "arguments": {
      "text": "你好，这是一个测试",
      "voice": "gentle_female",
      "speed": 0.9
    }
  },
  "id": 1
}
```

### 5.2 图像生成插件 (Seedream-4.0)

```bash
POST https://mcp.coze.cn/v1/plugins/7548380026094370867
Content-Type: application/json
Authorization: Bearer pat_iRAbnGWILCaudRct...

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "generate_image",
    "arguments": {
      "prompt": "低饱和度动漫风格书籍背景图",
      "width": 1920,
      "height": 1080,
      "style": "anime"
    }
  },
  "id": 1
}
```

### 5.3 视频剪辑插件

```bash
POST https://mcp.coze.cn/v1/plugins/7514607540051640360
Content-Type: application/json
Authorization: Bearer pat_iRAbnGWILCaudRct...

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "edit_video",
    "arguments": {
      "background_url": "https://...",
      "audio_tracks": [...],
      "effects": [...]
    }
  },
  "id": 1
}
```

### 5.4 添加文字插件

```bash
POST https://mcp.coze.cn/v1/plugins/7439198625538031666
Content-Type: application/json
Authorization: Bearer pat_iRAbnGWILCaudRct...

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "add_text",
    "arguments": {
      "video_url": "https://...",
      "text": "显示的文字",
      "position": "center",
      "style": {
        "color": "#FFFFFF",
        "fontSize": 48
      }
    }
  },
  "id": 1
}
```

## 6. Workflow API 调用

Workflow API 使用不同的格式（非 MCP）：

```bash
POST https://api.coze.cn/v1/workflow/run
Content-Type: application/json
Authorization: Bearer pat_iRAbnGWILCaudRct...

{
  "workflow_id": "7564000473180553225",
  "parameters": {
    "input": "请生成一个关于明朝锦衣卫的短视频脚本"
  }
}
```

## 7. 完整的 cURL 示例

### 7.1 查询插件工具列表

```bash
curl -X POST 'https://mcp.coze.cn/v1/plugins/7426655854067351562' \
  -H "Authorization: Bearer pat_iRAbnGWILCaudRctPMkZ8fFGuH9xxoiz4CtHsGBhGwGlVrdgB3nS2o8KvOrOImrL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

### 7.2 调用语音合成工具

```bash
curl -X POST 'https://mcp.coze.cn/v1/plugins/7426655854067351562' \
  -H "Authorization: Bearer pat_iRAbnGWILCaudRctPMkZ8fFGuH9xxoiz4CtHsGBhGwGlVrdgB3nS2o8KvOrOImrL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "synthesize_voice",
      "arguments": {
        "text": "你好世界",
        "voice": "gentle_female",
        "speed": 0.9
      }
    },
    "id": 1
  }'
```

## 8. 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| -32700 | Parse error | 检查 JSON 格式 |
| -32600 | Invalid Request | 检查请求格式是否符合 JSON-RPC 2.0 |
| -32601 | Method not found | 检查方法名是否正确 |
| -32602 | Invalid params | 检查参数格式和类型 |
| -32603 | Internal error | 服务器内部错误 |
| 401 | Unauthorized | 检查 API Token |
| 403 | Forbidden | 检查权限 |
| 404 | Not Found | 检查插件 ID 是否正确 |

## 9. 最佳实践

1. **使用 JSON-RPC ID**: 每个请求使用唯一的 ID，便于追踪
2. **错误重试**: 对于网络错误，实现指数退避重试
3. **超时设置**: 设置合理的超时时间（建议 30-60 秒）
4. **日志记录**: 记录所有 API 调用的请求和响应
5. **参数验证**: 在调用前验证参数格式和类型

## 10. 参考链接

- Coze 官方文档: https://www.coze.cn/open/docs
- 获取插件详情: https://www.coze.cn/open/docs/developer_guides/get_plugin
- 调用插件工具: https://www.coze.cn/open/docs/developer_guides/call_plugin_tool
- JSON-RPC 2.0 规范: https://www.jsonrpc.org/specification
