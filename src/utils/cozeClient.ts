import axios, { AxiosInstance } from 'axios';

/**
 * Coze API 客户端
 * 用于调用 Coze 的 LLM 工作流和 MCP 插件
 */
export class CozeClient {
  private apiToken: string;
  private axiosInstance: AxiosInstance;

  constructor(apiToken: string) {
    this.apiToken = apiToken;
    this.axiosInstance = axios.create({
      headers: {
        'Authorization': `Bearer ${this.apiToken}`,
        'Content-Type': 'application/json',
      },
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
        'https://api.coze.cn/v1/workflow/run',
        {
          workflow_id: workflowId,
          parameters,
        }
      );
      return response.data;
    } catch (error: any) {
      throw new Error(`Coze Workflow API 调用失败: ${error.message}`);
    }
  }

  /**
   * 调用 MCP 插件
   * @param pluginId - 插件 ID
   * @param method - MCP 方法名
   * @param params - 方法参数
   */
  async callMCPPlugin(pluginId: string, method: string, params: Record<string, any>): Promise<any> {
    try {
      const response = await this.axiosInstance.post(
        `https://mcp.coze.cn/v1/plugins/${pluginId}`,
        {
          jsonrpc: '2.0',
          method,
          params,
          id: Date.now(),
        }
      );
      return response.data.result;
    } catch (error: any) {
      throw new Error(`MCP 插件调用失败: ${error.message}`);
    }
  }

  /**
   * 生成图片 (Doubao-Seedream-4.0)
   * @param prompt - 图片描述
   * @param width - 宽度
   * @param height - 高度
   */
  async generateImage(prompt: string, width: number = 1920, height: number = 1080): Promise<string> {
    const result = await this.callMCPPlugin(
      process.env.PLUGIN_IMAGE_GENERATION_ID!,
      'tools/call',
      {
        name: 'generate_image',
        arguments: {
          prompt,
          width,
          height,
          style: 'anime', // 动漫风格
          quality: 'high',
        },
      }
    );
    return result.content[0].text; // 返回图片 URL
  }

  /**
   * 语音合成
   * @param text - 要合成的文本
   * @param voiceSpeed - 语速 (默认 0.9)
   */
  async synthesizeVoice(text: string, voiceSpeed: number = 0.9): Promise<string> {
    const result = await this.callMCPPlugin(
      process.env.PLUGIN_VOICE_SYNTHESIS_ID!,
      'tools/call',
      {
        name: 'synthesize_voice',
        arguments: {
          text,
          voice: 'gentle_female', // 温柔女声
          speed: voiceSpeed,
        },
      }
    );
    return result.content[0].text; // 返回音频 URL
  }

  /**
   * 视频剪辑
   * @param config - 剪辑配置
   */
  async editVideo(config: any): Promise<string> {
    const result = await this.callMCPPlugin(
      process.env.PLUGIN_VIDEO_EDIT_ID!,
      'tools/call',
      {
        name: 'edit_video',
        arguments: config,
      }
    );
    return result.content[0].text; // 返回视频 URL 或剪映草稿链接
  }

  /**
   * 添加文字到视频
   * @param videoUrl - 视频 URL
   * @param textConfig - 文字配置
   */
  async addTextToVideo(videoUrl: string, textConfig: any): Promise<string> {
    const result = await this.callMCPPlugin(
      process.env.PLUGIN_ADD_TEXT_ID!,
      'tools/call',
      {
        name: 'add_text',
        arguments: {
          video_url: videoUrl,
          ...textConfig,
        },
      }
    );
    return result.content[0].text;
  }
}
