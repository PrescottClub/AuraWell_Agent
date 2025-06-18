"""
DeepSeek API Client - 异步重构版本
=============================

完全异步的DeepSeek API客户端，解决事件循环阻塞问题。
支持真正的并发调用和流式响应。

重构日期：2024-12-28
重构人：凤凰计划第二阶段
"""

import asyncio
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx
from openai import AsyncOpenAI

from .exceptions import ExternalServiceError

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """
    异步DeepSeek API客户端 - 重构版本
    
    特性：
    - 完全异步，不阻塞事件循环
    - 支持真正的并发调用
    - 异步流式响应
    - 连接池和超时管理
    - 详细的错误处理
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        初始化异步DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥，如未提供将从环境变量读取
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ExternalServiceError("DEEPSEEK_API_KEY is required")

        # 配置异步HTTP客户端
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),  # 30秒超时
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        
        # 配置异步OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
            http_client=self.http_client
        )
        
        self.model = "deepseek-reasoner"
        logger.info("DeepSeek异步客户端初始化成功")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    async def close(self):
        """关闭异步客户端连接"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("DeepSeek异步客户端连接已关闭")

    async def get_deepseek_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        获取DeepSeek响应 - 真正的异步实现
        
        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Returns:
            API响应内容
        """
        try:
            logger.info(f"发起异步DeepSeek API调用，模型: {model or self.model}")
            
            # 准备API参数
            api_params = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            
            # 真正的异步调用
            response = await self.client.chat.completions.create(**api_params)
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                logger.info("DeepSeek异步API调用成功")
                return content or ""
            else:
                raise ExternalServiceError("DeepSeek API返回空响应")
                
        except Exception as e:
            logger.error(f"DeepSeek异步API调用失败: {e}")
            raise ExternalServiceError(f"DeepSeek API error: {e}", service_name="deepseek")

    async def get_streaming_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        获取流式响应 - 真正的异步流
        
        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
            
        Yields:
            响应内容片段
        """
        try:
            logger.info(f"发起异步DeepSeek流式API调用，模型: {model or self.model}")
            
            # 准备API参数
            api_params = {
                "model": model or self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            # 真正的异步流式调用
            async_stream = await self.client.chat.completions.create(**api_params)
            
            async for chunk in async_stream:
                if chunk.choices and chunk.choices[0].delta:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                        
        except Exception as e:
            logger.error(f"DeepSeek异步流式API调用失败: {e}")
            raise ExternalServiceError(f"DeepSeek streaming API error: {e}", service_name="deepseek")

    async def generate_health_advice(
        self,
        user_query: str,
        user_context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        生成健康建议 - 异步版本
        
        Args:
            user_query: 用户查询
            user_context: 用户上下文信息
            max_tokens: 最大token数
            
        Returns:
            健康建议内容
        """
        try:
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是AuraWell的专业健康顾问，请根据用户的问题提供科学、实用的健康建议。"
                },
                {
                    "role": "user", 
                    "content": user_query
                }
            ]
            
            # 如果有用户上下文，添加到消息中
            if user_context:
                context_msg = f"用户背景信息：{json.dumps(user_context, ensure_ascii=False)}"
                messages.insert(1, {"role": "system", "content": context_msg})
            
            # 异步获取响应
            response = await self.get_deepseek_response(
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"生成健康建议失败: {e}")
            raise ExternalServiceError(f"Health advice generation failed: {e}")

    async def analyze_health_data(
        self,
        health_data: Dict[str, Any],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        分析健康数据 - 异步版本
        
        Args:
            health_data: 健康数据
            analysis_type: 分析类型
            
        Returns:
            分析结果
        """
        try:
            # 构建分析提示
            prompt = f"""
            请分析以下健康数据，提供{analysis_type}分析：
            
            健康数据：{json.dumps(health_data, ensure_ascii=False)}
            
            请从以下角度进行分析：
            1. 数据趋势分析
            2. 健康风险评估  
            3. 改进建议
            4. 行动计划
            
            请以JSON格式返回结构化结果。
            """
            
            messages = [
                {"role": "system", "content": "你是专业的健康数据分析师，擅长从健康数据中提取有价值的洞察。"},
                {"role": "user", "content": prompt}
            ]
            
            # 异步获取分析结果
            response = await self.get_deepseek_response(
                messages=messages,
                max_tokens=3000,
                temperature=0.3  # 较低温度以获得更稳定的分析结果
            )
            
            # 尝试解析JSON响应
            try:
                analysis_result = json.loads(response)
            except json.JSONDecodeError:
                # 如果不是JSON格式，包装成标准格式
                analysis_result = {
                    "analysis_type": analysis_type,
                    "raw_analysis": response,
                    "structured": False
                }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"健康数据分析失败: {e}")
            raise ExternalServiceError(f"Health data analysis failed: {e}")


# 工具函数和健康相关功能
def create_health_tools() -> List[Dict[str, Any]]:
    """创建健康工具定义"""
    return [
        {
            "type": "function",
            "function": {
                "name": "analyze_user_health_data",
                "description": "分析用户的健康数据，包括运动、饮食、睡眠等",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_type": {"type": "string", "enum": ["exercise", "nutrition", "sleep", "all"]},
                        "time_range": {"type": "string", "description": "时间范围，如'7days', '1month'"}
                    },
                    "required": ["data_type"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "generate_health_plan",
                "description": "基于用户数据生成个性化健康计划",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goals": {"type": "array", "items": {"type": "string"}},
                        "constraints": {"type": "array", "items": {"type": "string"}},
                        "duration": {"type": "string", "description": "计划持续时间"}
                    },
                    "required": ["goals"]
                }
            }
        }
    ]


async def demo_async_function_calling():
    """演示异步函数调用"""
    try:
        async with DeepSeekClient() as client:
            # 示例：并发健康查询
            tasks = [
                client.generate_health_advice("如何改善睡眠质量？"),
                client.generate_health_advice("适合办公室的运动有哪些？"),
                client.analyze_health_data({"sleep_hours": 6, "exercise_minutes": 30})
            ]
            
            # 真正的并发执行
            results = await asyncio.gather(*tasks)
            
            print("🎉 异步并发调用完成！")
            for i, result in enumerate(results):
                print(f"结果 {i+1}: {result[:100]}...")
                
    except Exception as e:
        print(f"❌ 异步演示失败: {e}")


if __name__ == "__main__":
    # 测试异步实现
    asyncio.run(demo_async_function_calling())
