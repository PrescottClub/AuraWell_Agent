"""
DeepSeek API Client for AuraWell

This module provides a client interface for interacting with the DeepSeek API,
specifically optimized for health lifestyle orchestration tasks.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass
from openai import OpenAI
from pydantic import BaseModel
from ..config.settings import AuraWellSettings

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class APIUsage:
    """Data class to track API usage statistics"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


class DeepSeekResponse(BaseModel):
    """Pydantic model for DeepSeek API response"""

    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[APIUsage] = None
    model: str
    finish_reason: str


class DeepSeekClient:
    """
    Client for interacting with DeepSeek API

    Uses OpenAI library with DeepSeek's base URL for API calls.
    Prioritizes deepseek-reasoner model for reasoning and planning tasks.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        """
        Initialize DeepSeek client (via Alibaba Cloud DashScope)

        Args:
            api_key: DashScope API key. If None, will read from DASHSCOPE_API_KEY env var
            base_url: API base URL. If None, will read from DASHSCOPE_BASE_URL env var

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        # 优先使用阿里云DashScope服务访问DeepSeek模型
        self.api_key = api_key or os.getenv("QWEN_API") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("DEEP_SEEK_API") or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key not provided. Set QWEN_API, DASHSCOPE_API_KEY, DEEP_SEEK_API, or DEEPSEEK_API_KEY environment variable."
            )

        # 支持多种API端点：直接DeepSeek API或阿里云DashScope
        self.base_url = (
            base_url or
            os.getenv("DEEPSEEK_BASE_URL") or
            os.getenv("DASHSCOPE_BASE_URL") or
            # 根据API Key来源判断使用哪个端点
            self._determine_api_endpoint()
        )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=300.0  # 设置45秒超时，给LLM足够的响应时间
        )

        logger.info(f"DeepSeek client initialized successfully with base_url: {self.base_url}")

    def _determine_api_endpoint(self) -> str:
        """
        根据API密钥来源判断使用哪个API端点

        Returns:
            str: API端点URL
        """
        # 检查API密钥来源
        dashscope_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API")
        deepseek_key = os.getenv("DEEP_SEEK_API") or os.getenv("DEEPSEEK_API_KEY")

        if self.api_key == dashscope_key:
            # 使用阿里云DashScope端点
            logger.info("使用阿里云DashScope API端点")
            return "https://dashscope.aliyuncs.com/compatible-mode/v1"
        elif self.api_key == deepseek_key:
            # 使用DeepSeek直接API端点
            logger.info("使用DeepSeek直接API端点")
            return "https://api.deepseek.com/v1"
        else:
            # 默认根据密钥格式判断
            if self.api_key.startswith("sk-") and len(self.api_key) < 50:
                logger.info("根据密钥格式判断：使用DeepSeek直接API端点")
                return "https://api.deepseek.com/v1"
            else:
                logger.info("根据密钥格式判断：使用阿里云DashScope API端点")
                return "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def get_deepseek_response(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> DeepSeekResponse:
        """
        Get response from DeepSeek API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_name: DeepSeek model name (default: from settings)
            tools: Optional list of function tool definitions for function calling
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            DeepSeekResponse object containing the API response

        Raises:
            Exception: For API errors, network issues, or authentication failures
        """
        # Use default model from settings if not specified
        if model_name is None:
            model_name = AuraWellSettings.DEEPSEEK_DEFAULT_MODEL

        try:
            # Prepare API call parameters
            api_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            # Add tools if provided
            if tools:
                api_params["tools"] = tools
                api_params["tool_choice"] = "auto"

            logger.info(f"Making API call to DeepSeek with model: {model_name}")
            logger.debug(f"Messages: {json.dumps(messages, ensure_ascii=False)}")

            # Make API call
            response = self.client.chat.completions.create(**api_params)

            # Extract response data
            message = response.choices[0].message
            content = message.content or ""
            tool_calls = None

            # Process tool calls if present
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    tool_calls.append(
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                    )
                logger.info(
                    f"Function calls requested: {[tc['function']['name'] for tc in tool_calls]}"
                )

            # Track usage
            usage = None
            if response.usage:
                usage = APIUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    model=model_name,
                )
                logger.info(
                    f"Token usage - Prompt: {usage.prompt_tokens}, "
                    f"Completion: {usage.completion_tokens}, "
                    f"Total: {usage.total_tokens}"
                )

            return DeepSeekResponse(
                content=content,
                tool_calls=tool_calls,
                usage=usage,
                model=model_name,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"DeepSeek API call failed: {error_msg}")

            # 检查是否是超时错误
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise Exception(f"DeepSeek API 请求超时，请稍后重试: {error_msg}")
            # 检查是否是网络错误
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                raise Exception(f"DeepSeek API 网络连接失败，请检查网络: {error_msg}")
            # 检查是否是认证错误
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception(f"DeepSeek API 认证失败，请检查API密钥: {error_msg}")
            # 其他错误
            else:
                raise Exception(f"DeepSeek API 调用失败: {error_msg}")

    async def get_streaming_response(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Get streaming response from DeepSeek API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_name: DeepSeek model name (default: from settings)
            tools: Optional list of function tool definitions for function calling
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Yields:
            str: Token chunks from the streaming response

        Raises:
            Exception: For API errors, network issues, or authentication failures
        """
        # Use default model from settings if not specified
        if model_name is None:
            model_name = AuraWellSettings.DEEPSEEK_DEFAULT_MODEL

        try:
            # Prepare API call parameters
            api_params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,  # Enable streaming
            }

            # Add tools if provided
            if tools:
                api_params["tools"] = tools
                api_params["tool_choice"] = "auto"

            logger.info(
                f"Making streaming API call to DeepSeek with model: {model_name}"
            )
            logger.debug(f"Messages: {json.dumps(messages, ensure_ascii=False)}")

            # Make streaming API call
            stream = self.client.chat.completions.create(**api_params)

            # Process streaming response
            full_content = ""
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        token = delta.content
                        full_content += token
                        yield token

            logger.info(
                f"Streaming response completed. Total length: {len(full_content)}"
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"DeepSeek streaming API call failed: {error_msg}")

            # 检查是否是超时错误
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise Exception(f"DeepSeek 流式API 请求超时，请稍后重试: {error_msg}")
            # 检查是否是网络错误
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                raise Exception(f"DeepSeek 流式API 网络连接失败，请检查网络: {error_msg}")
            # 检查是否是认证错误
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception(f"DeepSeek 流式API 认证失败，请检查API密钥: {error_msg}")
            # 其他错误
            else:
                raise Exception(f"DeepSeek 流式API 调用失败: {error_msg}")


def create_health_tools() -> List[Dict[str, Any]]:
    """
    Create tool definitions for DeepSeek function calling

    Defines tools for health data orchestration and calendar integration.

    Returns:
        List of tool definitions for DeepSeek API
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_calendar_events",
                "description": "获取用户指定日期的日历事件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "日期格式 YYYY-MM-DD",
                        },
                        "time_window": {
                            "type": "string",
                            "enum": ["morning", "afternoon", "evening", "all_day"],
                            "description": "时间段过滤器，可选",
                        },
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_wearable_data",
                "description": "获取用户在指定健康平台的特定类型数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform_name": {
                            "type": "string",
                            "enum": ["XiaomiHealth", "AppleHealth", "BoheHealth"],
                            "description": "健康数据平台名称",
                        },
                        "data_type": {
                            "type": "string",
                            "enum": [
                                "steps",
                                "sleep_summary",
                                "heart_rate",
                                "workout",
                                "nutrition",
                            ],
                            "description": "数据类型",
                        },
                        "start_date": {
                            "type": "string",
                            "description": "开始日期 YYYY-MM-DD",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期 YYYY-MM-DD",
                        },
                    },
                    "required": [
                        "platform_name",
                        "data_type",
                        "start_date",
                        "end_date",
                    ],
                },
            },
        },
    ]

    return tools


def demo_function_calling():
    """
    Demonstration of DeepSeek function calling capabilities

    This function shows how to use the client with health-related tools
    """
    # This is a demo function that shows tool call output
    client = DeepSeekClient()
    tools = create_health_tools()

    messages = [
        {
            "role": "system",
            "content": "你是AuraWell健康助手，专注于个性化健康建议。根据用户的健康数据和日程安排提供建议。",
        },
        {
            "role": "user",
            "content": "我想了解一下今天的健康状况，请帮我获取步数和睡眠数据，日期是2024-01-15",
        },
    ]

    try:
        response = client.get_deepseek_response(
            messages=messages, tools=tools
        )

        print(f"Response: {response.content}")

        if response.tool_calls:
            print("\nFunction calls requested:")
            for tool_call in response.tool_calls:
                print(f"Function: {tool_call['function']['name']}")
                print(f"Arguments: {tool_call['function']['arguments']}")

        return response

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return None


if __name__ == "__main__":
    # Demo usage
    demo_function_calling()
