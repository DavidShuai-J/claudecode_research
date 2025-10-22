"""扣子(Coze) API客户端 - 支持文本生成、图像生成、视频生成"""
import json
import logging
import requests
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class CozeClient:
    """扣子API客户端"""

    def __init__(
        self,
        access_token: str,
        bot_id: Optional[str] = None,
        image_workflow_id: Optional[str] = None,
        video_workflow_id: Optional[str] = None
    ):
        """初始化Coze客户端

        Args:
            access_token: 扣子API访问令牌
            bot_id: Chat机器人ID（用于文本生成）
            image_workflow_id: 图像生成工作流ID
            video_workflow_id: 视频生成工作流ID
        """
        self.access_token = access_token
        self.bot_id = bot_id
        self.image_workflow_id = image_workflow_id
        self.video_workflow_id = video_workflow_id

        self.chat_api_url = "https://api.coze.cn/v3/chat"
        self.workflow_api_url = "https://api.coze.cn/v1/workflow/run"

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        logger.info("扣子API客户端初始化成功")

    def chat(
        self,
        user_input: str,
        user_id: str = "default_user",
        stream: bool = False,
        conversation_id: Optional[str] = None
    ) -> str:
        """调用Chat API进行文本生成

        Args:
            user_input: 用户输入文本
            user_id: 用户ID
            stream: 是否使用流式输出
            conversation_id: 会话ID（可选）

        Returns:
            生成的文本内容
        """
        if not self.bot_id:
            raise ValueError("bot_id未设置，无法调用Chat API")

        payload = {
            "bot_id": self.bot_id,
            "user_id": user_id,
            "stream": stream,
            "additional_messages": [
                {
                    "content_type": "text",
                    "role": "user",
                    "type": "question",
                    "content": user_input
                }
            ],
            "parameters": {}
        }

        if conversation_id:
            payload["conversation_id"] = conversation_id

        try:
            response = requests.post(
                self.chat_api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            if stream:
                # 处理流式响应
                return self._handle_stream_response(response)
            else:
                # 处理普通响应
                result = response.json()
                return self._extract_chat_content(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Coze Chat API调用失败: {str(e)}")
            raise

    def _handle_stream_response(self, response) -> str:
        """处理流式响应

        Args:
            response: requests响应对象

        Returns:
            完整的响应文本
        """
        full_content = []

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')

                # 处理SSE格式数据
                if line_str.startswith('data:'):
                    data_str = line_str[5:].strip()

                    if data_str == '[DONE]':
                        break

                    try:
                        data = json.loads(data_str)
                        # 提取消息内容
                        if 'messages' in data:
                            for msg in data['messages']:
                                if msg.get('type') == 'answer':
                                    content = msg.get('content', '')
                                    if content:
                                        full_content.append(content)
                    except json.JSONDecodeError:
                        continue

        return ''.join(full_content)

    def _extract_chat_content(self, result: Dict[str, Any]) -> str:
        """从Chat API响应中提取内容

        Args:
            result: API响应JSON

        Returns:
            提取的文本内容
        """
        # 根据Coze API的响应格式提取内容
        if 'messages' in result:
            for msg in result['messages']:
                if msg.get('type') == 'answer' and msg.get('role') == 'assistant':
                    return msg.get('content', '')

        # 如果格式不匹配，记录警告并返回完整响应
        logger.warning(f"未能从响应中提取内容，返回原始数据: {result}")
        return str(result)

    def generate_image(
        self,
        prompt: str,
        workflow_id: Optional[str] = None,
        max_wait_time: int = 120
    ) -> str:
        """调用Workflow API生成图像

        Args:
            prompt: 图像描述提示词
            workflow_id: 工作流ID（可选，默认使用初始化时的image_workflow_id）
            max_wait_time: 最大等待时间（秒）

        Returns:
            生成的图像URL
        """
        wf_id = workflow_id or self.image_workflow_id
        if not wf_id:
            raise ValueError("image_workflow_id未设置，无法生成图像")

        return self._run_workflow(wf_id, {"input": prompt}, max_wait_time)

    def generate_video(
        self,
        prompt: str,
        workflow_id: Optional[str] = None,
        max_wait_time: int = 300
    ) -> str:
        """调用Workflow API生成视频

        Args:
            prompt: 视频描述提示词
            workflow_id: 工作流ID（可选，默认使用初始化时的video_workflow_id）
            max_wait_time: 最大等待时间（秒）

        Returns:
            生成的视频URL
        """
        wf_id = workflow_id or self.video_workflow_id
        if not wf_id:
            raise ValueError("video_workflow_id未设置，无法生成视频")

        return self._run_workflow(wf_id, {"input": prompt}, max_wait_time)

    def _run_workflow(
        self,
        workflow_id: str,
        parameters: Dict[str, Any],
        max_wait_time: int = 120
    ) -> str:
        """运行Workflow

        Args:
            workflow_id: 工作流ID
            parameters: 工作流参数
            max_wait_time: 最大等待时间（秒）

        Returns:
            工作流输出结果（通常是URL）
        """
        payload = {
            "workflow_id": workflow_id,
            "parameters": parameters
        }

        try:
            response = requests.post(
                self.workflow_api_url,
                headers=self.headers,
                json=payload,
                timeout=max_wait_time
            )
            response.raise_for_status()

            result = response.json()
            logger.debug(f"Workflow响应: {result}")

            # 从响应中提取结果
            return self._extract_workflow_result(result)

        except requests.exceptions.RequestException as e:
            logger.error(f"Coze Workflow API调用失败: {str(e)}")
            raise

    def _extract_workflow_result(self, result: Dict[str, Any]) -> str:
        """从Workflow API响应中提取结果

        Args:
            result: API响应JSON

        Returns:
            提取的结果（URL或文本）
        """
        # 根据Coze Workflow API的响应格式提取结果
        # 需要根据实际API响应格式调整

        # 常见的响应格式
        if 'data' in result:
            data = result['data']

            # 如果是URL
            if isinstance(data, str) and (data.startswith('http://') or data.startswith('https://')):
                return data

            # 如果是嵌套结构
            if isinstance(data, dict):
                # 尝试常见的字段名
                for key in ['url', 'image_url', 'video_url', 'output', 'result']:
                    if key in data:
                        return str(data[key])

        # 如果找不到明确的结果，返回完整响应
        logger.warning(f"未能从Workflow响应中提取结果，返回原始数据: {result}")
        return str(result)

    def chat_json(
        self,
        user_input: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """调用Chat API并期望返回JSON格式

        Args:
            user_input: 用户输入文本（应包含返回JSON的指令）
            user_id: 用户ID

        Returns:
            解析后的JSON对象
        """
        # 确保提示词要求JSON输出
        if "JSON" not in user_input:
            user_input += "\n\n请以JSON格式返回结果。"

        response = self.chat(user_input, user_id, stream=False)

        # 尝试解析JSON
        try:
            # 清理可能的markdown代码块
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}\n原始响应: {response}")
            raise ValueError(f"Coze返回的不是有效的JSON格式: {str(e)}")
