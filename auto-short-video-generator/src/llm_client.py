"""LLM客户端 - 支持OpenAI、Anthropic和Coze"""
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from .coze_client import CozeClient

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端，统一接口"""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str = None,
        base_url: Optional[str] = None,
        bot_id: Optional[str] = None
    ):
        """初始化LLM客户端

        Args:
            provider: 'openai'、'anthropic' 或 'coze'
            api_key: API密钥（Coze使用access_token）
            model: 模型名称（Coze不需要）
            base_url: API基础URL（可选，用于OpenAI兼容接口）
            bot_id: Coze的机器人ID（仅Coze需要）
        """
        self.provider = provider.lower()
        self.model = model

        if self.provider == "openai":
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
        elif self.provider == "coze":
            self.client = CozeClient(access_token=api_key, bot_id=bot_id)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

        logger.info(f"LLM客户端初始化成功: {provider} - {model or bot_id}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = False
    ) -> str:
        """生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            json_mode: 是否使用JSON模式

        Returns:
            生成的文本
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, system_prompt, temperature, max_tokens, json_mode)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "coze":
                return self._generate_coze(prompt, system_prompt)
        except Exception as e:
            logger.error(f"LLM生成失败: {str(e)}")
            raise

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        json_mode: bool
    ) -> str:
        """OpenAI生成"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Anthropic生成"""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_coze(
        self,
        prompt: str,
        system_prompt: Optional[str]
    ) -> str:
        """Coze生成"""
        # 如果有系统提示词，将其合并到用户提示词中
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        return self.client.chat(full_prompt, stream=False)

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """生成JSON格式输出

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            解析后的JSON对象
        """
        # 确保提示词要求JSON输出
        if "JSON" not in prompt:
            prompt += "\n\n请以JSON格式返回结果。"

        # Coze有专门的chat_json方法
        if self.provider == "coze":
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            return self.client.chat_json(full_prompt)

        # OpenAI和Anthropic使用通用方法
        json_mode = (self.provider == "openai")
        response = self.generate(prompt, system_prompt, temperature, max_tokens, json_mode)

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
            raise ValueError(f"LLM返回的不是有效的JSON格式: {str(e)}")
