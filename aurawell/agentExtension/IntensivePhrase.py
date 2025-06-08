from deepseek import DeepSeekAPI
import re
import sys
import os
import requests
import json
import time
from typing import Dict, Any
from dotenv import load_dotenv  # 新增 dotenv 支持


class IntensivePhrase(DeepSeekAPI):
    def __init__(self, user_profile):
        super().__init__(user_profile)
        # 加载环境变量文件
        load_dotenv()  # 从 .env 文件加载环境变量

        # 定义合法的意图列表
        self.legal_intents = {
            "信息查询", "设置目标", "运动记录", "睡眠记录",
            "运动建议", "睡眠建议", "成就记录", "健康建议", "寻求指导"
        }

        # 从环境变量获取 API 密钥
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未在环境变量中设置，请检查.env文件")

        # 意图分析提示模板
        self.intent_prompt = """分析用户输入并严格分类到以下意图之一：
        - 信息查询 (fact queries)
        - 设置目标 (goal setting) 
        - 运动记录 (exercise logs)
        - 睡眠记录 (sleep logs)
        - 运动建议 (exercise advice)
        - 睡眠建议 (sleep advice)
        - 成就记录 (achievement records)
        - 健康建议 (health advice)
        - 寻求指导 (guidance seeking)
        - Unknown (其他所有情况)

        用JSON格式响应：
        {{
            "detected_intent": "匹配到的意图或Unknown",
            "confidence": 0.0-1.0,
            "reason": "分类依据说明"
        }}

        用户输入: "{user_input}"
        """

    def generate_response(self, prompt: str, max_retries: int = 3, retry_delay: int = 5) -> Dict[str, Any]:
        """
        增强版API调用方法，包含重试机制和错误处理

        Args:
            prompt: 输入文本
            max_retries: 最大重试次数 (默认3)
            retry_delay: 重试间隔(秒) (默认5)

        Returns:
            dict: 解析后的API响应或错误信息
        """
        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "max_tokens": 150
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=15
                )

                # 处理成功响应
                if response.status_code == 200:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON response"}

                # 处理速率限制
                elif response.status_code == 429:
                    print(f"API速率限制，等待 {retry_delay}秒后重试... (尝试 {attempt + 1}/{max_retries})",
                          file=sys.stderr)
                    time.sleep(retry_delay)
                    continue

                # 处理其他HTTP错误
                else:
                    error_msg = response.json().get("error", {}).get("message", "未知API错误")
                    return {"error": f"API错误 {response.status_code}: {error_msg}"}

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return {"error": "API请求超时"}

            except requests.exceptions.RequestException as e:
                return {"error": f"网络错误: {str(e)}"}

        return {"error": "达到最大重试次数"}

    def UserIntentAnalysis(self, user_input: str) -> Dict[str, Any]:
        """
        完整意图分析方法，包含输入验证和结果处理

        Args:
            user_input: 用户输入文本

        Returns:
            {
                "detected_intent": str,
                "confidence": float,
                "reason": str,
                "valid": bool,
                "error": str (可选)
            }
        """
        if not user_input or not isinstance(user_input, str):
            return {
                "detected_intent": "Unknown",
                "confidence": 0.0,
                "reason": "无效输入",
                "valid": False,
                "error": "输入必须是非空字符串"
            }

        try:
            # 生成格式化提示
            formatted_prompt = self.intent_prompt.format(user_input=user_input)

            # 调用API
            api_response = self.generate_response(formatted_prompt)

            # 错误处理
            if "error" in api_response:
                raise Exception(api_response["error"])

            # 解析响应内容
            content_str = api_response["choices"][0]["message"]["content"]
            try:
                content = json.loads(content_str)
            except json.JSONDecodeError:
                # 尝试从非标准响应中提取意图
                cleaned = re.sub(r'[^\u4e00-\u9fff]', '', content_str)
                detected_intent = next((intent for intent in self.legal_intents if intent in cleaned), "Unknown")
                return {
                    "detected_intent": detected_intent,
                    "confidence": 0.7 if detected_intent != "Unknown" else 1.0,
                    "reason": "从非JSON响应中提取意图",
                    "valid": detected_intent in self.legal_intents
                }

            # 验证响应结构
            required_keys = {"detected_intent", "confidence", "reason"}  # 注意保持与prompt一致
            if not all(k in content for k in required_keys):
                raise ValueError("API响应缺少必要字段")

            # 标准化意图
            detected_intent = content["detected_intent"]  # 注意保持与prompt一致
            if detected_intent not in self.legal_intents:
                detected_intent = "Unknown"

            # 确保置信度在0-1范围内
            confidence = max(0.0, min(1.0, float(content["confidence"])))

            return {
                "detected_intent": detected_intent,
                "confidence": confidence,
                "reason": content["reason"],
                "valid": detected_intent in self.legal_intents
            }

        except Exception as e:
            return {
                "detected_intent": "Unknown",
                "confidence": 0.0,
                "reason": f"分析过程中出错: {str(e)}",
                "valid": False,
                "error": str(e)
            }
