import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

from aurawell.agent.tools_registry import HealthToolsRegistry

# 加载环境变量
load_dotenv()

class ConversationAgent:
    """
    负责管理与DeepSeek模型的对话、处理工具调用并维护对话历史的核心智能体。
    """
    def __init__(self, user_id: str, demo_mode: bool = False):
        self.user_id = user_id
        self.demo_mode = demo_mode
        self.tools_registry = HealthToolsRegistry()
        self.history: List[Dict[str, Any]] = [
            {"role": "system", "content": "You are AuraWell, a personalized health and wellness assistant. Your goal is to help users understand their health data and achieve their wellness goals. You should be encouraging, clear, and provide actionable advice. When you need to access health data or perform specific actions, use the available tools."}
        ]
        
        if not demo_mode:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                print("Warning: DEEPSEEK_API_KEY not found. Switching to demo mode.")
                print("To use the full AI functionality, please set DEEPSEEK_API_KEY in your .env file.")
                self.demo_mode = True
            else:
                try:
                    from deepseek import DeepSeekAPI
                    self.client = DeepSeekAPI(api_key=api_key)
                except (ImportError, Exception) as e:
                    print(f"Warning: DeepSeek library issue: {e}. Switching to demo mode.")
                    self.demo_mode = True

    async def a_run(self, user_message: str) -> str:
        """
        异步处理用户消息，与DeepSeek API交互，并根据需要执行工具。

        Args:
            user_message: 用户输入的文本消息。

        Returns:
            一个字符串，表示给用户的最终回复。
        """
        self.history.append({"role": "user", "content": user_message})
        
        if self.demo_mode:
            return await self._demo_response(user_message)

        tools = self.tools_registry.get_tools_schema()
        
        try:
            # 使用 DeepSeek API 的 chat_completion 方法
            # 构建提示词包含历史对话
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])
            
            response = self.client.chat_completion(
                prompt=prompt,
                model="deepseek-chat"
            )
            
            # 简化处理，直接返回回复
            ai_response = response
            self.history.append({"role": "assistant", "content": ai_response})

            # 返回实际的API响应
            return ai_response
            
        except Exception as e:
            print(f"API调用失败: {e}")
            return f"抱歉，AI服务暂时不可用。已切换到演示模式。\n{await self._demo_response(user_message)}"

    async def _demo_response(self, user_message: str) -> str:
        """演示模式下的响应处理"""
        user_message_lower = user_message.lower()
        
        # 模拟不同的用户意图和相应的工具调用
        if any(word in user_message_lower for word in ["活动", "运动", "steps", "activity"]):
            print("Demo mode: Simulating get_user_activity_summary tool call")
            result = await self.tools_registry.get_tool("get_user_activity_summary")(self.user_id, 7)
            return f"根据您的活动数据分析: {result['message']} 在演示模式下，我模拟调用了活动摘要工具。建议您每天保持适量运动，目标是每天8000-10000步。"
            
        elif any(word in user_message_lower for word in ["睡眠", "sleep", "休息"]):
            print("Demo mode: Simulating analyze_sleep_quality tool call")
            result = await self.tools_registry.get_tool("analyze_sleep_quality")(self.user_id, "2024-06-01_to_2024-06-07")
            return f"睡眠质量分析: {result['message']} 在演示模式下，我模拟分析了您的睡眠数据。建议保持每晚7-8小时的优质睡眠。"
            
        elif any(word in user_message_lower for word in ["目标", "goals", "计划"]):
            print("Demo mode: Simulating update_health_goals tool call")
            demo_goals = {"daily_steps": 8000, "sleep_hours": 7.5, "exercise_minutes": 30}
            result = await self.tools_registry.get_tool("update_health_goals")(self.user_id, demo_goals)
            return f"健康目标设置: {result['message']} 在演示模式下，我帮您设置了示例健康目标：每天8000步、7.5小时睡眠、30分钟运动。"
            
        elif any(word in user_message_lower for word in ["成就", "achievements", "进度"]):
            print("Demo mode: Simulating check_achievements tool call")
            result = await self.tools_registry.get_tool("check_achievements")(self.user_id)
            return f"成就检查: {result[0]['achievement']} 在演示模式下，我查看了您的成就进度。继续保持健康的生活方式！"
            
        elif any(word in user_message_lower for word in ["洞察", "insights", "建议", "advice"]):
            print("Demo mode: Simulating get_health_insights tool call")
            result = await self.tools_registry.get_tool("get_health_insights")(self.user_id)
            return f"健康洞察: {result[0]['insight']} 在演示模式下，我生成了健康建议。建议您保持规律的作息，均衡饮食，适量运动。"
            
        else:
            return f"您好！我是AuraWell健康助手。当前运行在演示模式下。我可以帮您查看活动数据、分析睡眠质量、设置健康目标、检查成就进度，或提供健康洞察。请尝试询问关于这些方面的问题！\n\n（注意：要使用完整的AI功能，请在.env文件中设置DEEPSEEK_API_KEY）"

    async def _handle_tool_calls(self, tool_calls: List[Dict]) -> str:
        """处理并执行模型请求的工具调用。"""
        tool_results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_to_call = self.tools_registry.get_tool(tool_name)
            
            try:
                tool_args = json.loads(tool_call.function.arguments)
                # 确保 user_id 始终是我们初始化的 user_id
                if 'user_id' in tool_args:
                    tool_args['user_id'] = self.user_id
            except json.JSONDecodeError:
                print(f"Error: Could not decode arguments for tool {tool_name}")
                continue

            if tool_to_call:
                print(f"Executing tool: {tool_name} with args: {tool_args}")
                # 执行异步工具函数
                result = await tool_to_call(**tool_args)
                
                tool_response = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
                tool_results.append(tool_response)
            else:
                print(f"Warning: Tool '{tool_name}' not found.")
        
        self.history.extend(tool_results)

        # 将工具调用的结果发回给模型以获得最终回复
        try:
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.history])
            final_response = self.client.chat_completion(
                prompt=prompt,
                model="deepseek-chat"
            )
            
            self.history.append({"role": "assistant", "content": final_response})
            return final_response
        except Exception as e:
            return f"工具调用执行完成，但获取最终回复时出错: {e}" 