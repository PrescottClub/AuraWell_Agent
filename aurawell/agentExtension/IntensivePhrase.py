from deepseek import DeepSeekAPI
import re
import sys
import os
import requests
import json
import time
from typing import Dict, Any


class IntensivePhrase(DeepSeekAPI):
    def __init__(self, user_profile):
        super().__init__(user_profile)
        # 定义合法的意图列表
        self.legalIntent = {
            "信息查询", "设置目标", "运动记录", "睡眠记录",
            "运动建议", "睡眠建议", "成就记录", "健康建议", "寻求指导"
        }
        # 从环境变量获取 API 密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')

        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 未在 .env 文件中设置，请检查根目录下的.env文件")

    def generate_response(self, prompt: str, max_retries: int = 3, retry_delay: int = 5) -> str:
        """
        调用 DeepSeek API 生成响应

        Args:
            prompt: 提示文本
            max_retries: 最大重试次数
            retry_delay: 重试延迟(秒)

        Returns:
            str: API返回的响应文本
        """
        # DeepSeek API 端点
        api_url = "https://api.deepseek.com/v1/chat/completions"

        # 请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 请求体
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 低温度以获得更确定的输出
            "max_tokens": 50,  # 限制输出长度
            "top_p": 0.9,
            "stop": None
        }

        # 重试机制
        for attempt in range(max_retries):
            try:
                # 发送API请求
                response = requests.post(
                    api_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=15  # 15秒超时
                )

                # 检查响应状态
                if response.status_code == 200:
                    # 解析响应内容
                    response_data = response.json()
                    return response_data["choices"][0]["message"]["content"].strip()

                # 处理API错误
                elif response.status_code == 429:
                    # 速率限制错误，等待后重试
                    print(f"API速率限制，等待 {retry_delay}秒后重试...", file=sys.stderr)
                    time.sleep(retry_delay)
                    continue

                else:
                    # 其他API错误
                    error_msg = response.json().get("error", {}).get("message", "未知API错误")
                    raise Exception(f"API错误 {response.status_code}: {error_msg}")

            except requests.exceptions.Timeout:
                # 超时处理
                print(f"API请求超时，尝试 {attempt + 1}/{max_retries}", file=sys.stderr)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception("API请求多次超时")

            except requests.exceptions.RequestException as e:
                # 网络错误处理
                print(f"网络错误: {str(e)}", file=sys.stderr)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"网络错误多次重试失败: {str(e)}")

        # 所有重试均失败
        return ""

    def UserIntentAnalysis(self, user_prompt: str) -> str:
        """
        分析用户输入并返回合法的意图

        Args:
            user_prompt: 用户输入的文本

        Returns:
            str: 合法的用户意图，若无法确定则返回"Unknown"
        """
        # 构造意图分析提示
        prompt = f"""
        你是一个健康助手意图分类器。请严格分析用户的问题，将其分类到以下唯一合法的意图类别中：
        
        ### 合法意图列表：
        1. 信息查询 - 用户请求健康数据或事实信息
        2. 设置目标 - 用户设定健康或健身目标
        3. 运动记录 - 用户报告或查询运动活动
        4. 睡眠记录 - 用户报告或查询睡眠情况
        5. 运动建议 - 用户请求运动相关的指导
        6. 睡眠建议 - 用户请求睡眠改善建议
        7. 成就记录 - 用户报告或查询健康成就
        8. 健康建议 - 用户请求一般健康指导
        9. 寻求指导 - 用户需要操作或使用指导
        
        ### 输出要求：
        - 只输出意图名称，不要添加任何解释、前缀或后缀
        - 必须严格匹配上述列表中的完整意图名称
        - 如果无法明确分类，选择最接近的合法意图
        
        ### 用户问题：
        "{user_prompt}"
        
        ### 你的响应（只能是上述列表中的完整意图名称）：
        """
        try:
            # 调用DeepSeek API获取意图分析结果
            raw_response = self.generate_response(prompt)
            if len(raw_response) < 1:
                raise ValueError("未能通过DeepSeek API获得回答")
            # 使用正则表达式清洗API响应：
            # 1. 移除非中文字符、数字、标点和空格
            # 2. 保留连续的合法中文字符
            cleaned_response = re.sub(r'[^\u4e00-\u9fff]', '', raw_response)

            # 验证响应是否为合法意图
            if cleaned_response in self.legalIntent:
                return cleaned_response

            # 尝试模糊匹配：检查响应是否包含合法意图关键词
            for intent in self.legalIntent:
                if intent in cleaned_response:
                    return intent

            # 尝试部分匹配：检查响应开头是否匹配合法意图
            for intent in self.legalIntent:
                if cleaned_response.startswith(intent):
                    return intent

            # 最终回退到"Unknown"
            return "Unknown"

        except Exception as e:
            print(f"意图分析失败: {str(e)}", file=sys.stderr)
            return "Unknown"
