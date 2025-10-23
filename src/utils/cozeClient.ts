import axios, { AxiosInstance } from 'axios';

/**
 * MCP JSON-RPC 响应接口
 */
interface MCPResponse {
  jsonrpc: '2.0';
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
  id: number;
}

/**
 * MCP Content 项
 */
interface MCPContent {
  type: 'text' | 'image' | 'resource';
  text?: string;
  data?: any;
  mimeType?: string;
}

/**
 * Coze API 客户端
 * 用于调用 Coze 的 LLM 工作流和 MCP 插件
 *
 * MCP (Model Context Protocol) 使用 JSON-RPC 2.0 协议
 * 参考文档: https://www.coze.cn/open/docs/developer_guides/call_plugin_tool
 */
export class CozeClient {
  private apiToken: string;
  private axiosInstance: AxiosInstance;
  private mcpBaseUrl: string;
  private apiBaseUrl: string;

  constructor(apiToken: string) {
    this.apiToken = apiToken;
    this.mcpBaseUrl = 'https://mcp.coze.cn/v1/plugins';
    this.apiBaseUrl = 'https://api.coze.cn/v1';

    this.axiosInstance = axios.create({
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 秒超时
    });
  }

  /**
   * 调用 Coze 工作流 API
   * @param workflowId - 工作流 ID
   * @param parameters - 工作流参数
   */
  async runWorkflow(workflowId: string, parameters: Record<string, any>): Promise<any> {
    try {
      const response = await this.axiosInstance.post(
        `${this.apiBaseUrl}/workflow/run`,
        {
          workflow_id: workflowId,
          parameters,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Workflow API Error:', error.response?.data || error.message);
      throw new Error(`Coze Workflow API 调用失败: ${error.message}`);
    }
  }

  /**
   * 调用 MCP 插件（通用方法）
   * 使用 JSON-RPC 2.0 协议
   *
   * @param pluginId - 插件 ID
   * @param method - MCP 方法名 (如: 'tools/list', 'tools/call')
   * @param params - 方法参数
   * @returns MCP 响应结果
   */
  async callMCPPlugin(
    pluginId: string,
    method: string,
    params: Record<string, any> = {}
  ): Promise<any> {
    const requestId = Date.now();

    try {
      const response = await this.axiosInstance.post<MCPResponse>(
        `${this.mcpBaseUrl}/${pluginId}`,
        {
          jsonrpc: '2.0',
          method,
          params,
          id: requestId,
        }
      );

      const data = response.data;

      // 检查 JSON-RPC 错误
      if (data.error) {
        throw new Error(
          `MCP 错误 [${data.error.code}]: ${data.error.message}`
        );
      }

      return data.result;
    } catch (error: any) {
      if (error.response) {
        console.error('MCP Plugin Error:', error.response.data);
        throw new Error(
          `MCP 插件调用失败 (HTTP ${error.response.status}): ${
            error.response.data?.error?.message || error.message
          }`
        );
      }
      console.error('MCP Plugin Error:', error.message);
      throw new Error(`MCP 插件调用失败: ${error.message}`);
    }
  }

  /**
   * 列出插件提供的所有工具
   * @param pluginId - 插件 ID
   */
  async listPluginTools(pluginId: string): Promise<any> {
    return this.callMCPPlugin(pluginId, 'tools/list', {});
  }

  /**
   * 调用插件工具（通用方法）
   * @param pluginId - 插件 ID
   * @param toolName - 工具名称
   * @param arguments_ - 工具参数
   */
  async callPluginTool(
    pluginId: string,
    toolName: string,
    arguments_: Record<string, any>
  ): Promise<any> {
    const result = await this.callMCPPlugin(pluginId, 'tools/call', {
      name: toolName,
      arguments: arguments_,
    });

    // MCP 响应通常包含 content 数组
    if (result && result.content && Array.isArray(result.content)) {
      // 提取文本内容
      const textContent = result.content.find((item: MCPContent) => item.type === 'text');
      if (textContent && textContent.text) {
        return textContent.text;
      }
      // 如果没有文本内容，返回第一个内容项
      return result.content[0];
    }

    return result;
  }

  /**
   * 生成图片 (Doubao-Seedream-4.0)
   * @param prompt - 图片描述
   * @param width - 宽度
   * @param height - 高度
   */
  async generateImage(prompt: string, width: number = 1920, height: number = 1080): Promise<string> {
    const result = await this.callPluginTool(
      process.env.PLUGIN_IMAGE_GENERATION_ID!,
      'generate_image',
      {
        prompt,
        width,
        height,
        style: 'anime', // 动漫风格
        quality: 'high',
      }
    );

    // 返回图片 URL（可能是字符串或包含在对象中）
    if (typeof result === 'string') {
      return result;
    }
    if (result && result.url) {
      return result.url;
    }
    if (result && result.image_url) {
      return result.image_url;
    }

    throw new Error('无法从响应中提取图片 URL');
  }

  /**
   * 语音合成
   * @param text - 要合成的文本
   * @param voiceSpeed - 语速 (默认 0.9)
   */
  async synthesizeVoice(text: string, voiceSpeed: number = 0.9): Promise<string> {
    const result = await this.callPluginTool(
      process.env.PLUGIN_VOICE_SYNTHESIS_ID!,
      'synthesize_voice',
      {
        text,
        voice: 'gentle_female', // 温柔女声
        speed: voiceSpeed,
      }
    );

    // 返回音频 URL
    if (typeof result === 'string') {
      return result;
    }
    if (result && result.url) {
      return result.url;
    }
    if (result && result.audio_url) {
      return result.audio_url;
    }

    throw new Error('无法从响应中提取音频 URL');
  }

  /**
   * 视频剪辑
   * @param config - 剪辑配置
   */
  async editVideo(config: any): Promise<string> {
    const result = await this.callPluginTool(
      process.env.PLUGIN_VIDEO_EDIT_ID!,
      'edit_video',
      config
    );

    // 返回视频 URL 或剪映草稿链接
    if (typeof result === 'string') {
      return result;
    }
    if (result && result.url) {
      return result.url;
    }
    if (result && result.video_url) {
      return result.video_url;
    }
    if (result && result.draft_url) {
      return result.draft_url;
    }

    throw new Error('无法从响应中提取视频 URL');
  }

  /**
   * 添加文字到视频
   * @param videoUrl - 视频 URL
   * @param textConfig - 文字配置
   */
  async addTextToVideo(videoUrl: string, textConfig: any): Promise<string> {
    const result = await this.callPluginTool(
      process.env.PLUGIN_ADD_TEXT_ID!,
      'add_text',
      {
        video_url: videoUrl,
        ...textConfig,
      }
    );

    // 返回处理后的视频 URL
    if (typeof result === 'string') {
      return result;
    }
    if (result && result.url) {
      return result.url;
    }
    if (result && result.video_url) {
      return result.video_url;
    }

    throw new Error('无法从响应中提取视频 URL');
  }
}
