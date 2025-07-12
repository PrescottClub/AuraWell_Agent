import pytest
import os
import json
from dotenv import load_dotenv
from alibabacloud_fc_open20210406.client import Client
from alibabacloud_tea_openapi import models as open_api_models


def env_retrieving():
    """
    从环境变量中加载阿里云函数计算相关配置
    优先从当前目录的.env文件加载，然后从环境变量读取
    """
    # 尝试从当前目录加载.env文件
    current_dir = os.getcwd()
    dotenv_path = os.path.join(current_dir, '.env')

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(f"✅ 从当前目录加载.env文件: {dotenv_path}")
    else:
        # 如果当前目录没有.env文件，尝试从项目根目录加载
        project_root = os.getenv('PROJECT_ROOT', os.path.dirname(current_dir))
        dotenv_path = os.path.join(project_root, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            print(f"✅ 从项目根目录加载.env文件: {dotenv_path}")
        else:
            print("⚠️  未找到.env文件，将直接从环境变量读取")

    # 读取环境变量
    config = {
        'access_key_id': os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        'access_key_secret': os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        'region': os.getenv('FC_REGION', 'cn-hangzhou'),
        'service_name': os.getenv('FC_SERVICE_NAME', 'RAGmodule'),
        'function_name': os.getenv('FC_FUNCTION_NAME', 'RAGmodule'),
        'endpoint': os.getenv('ENDPOINT'),
        'function_url': os.getenv('FC_FUNCTION_URL')  # FC 3.0 使用函数URL
    }

    return config


class FCClient:
    """阿里云函数计算FC 3.0客户端包装器"""

    def __init__(self, access_key_id, access_key_secret, region, function_url=None):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region = region
        self.function_url = function_url

        # 创建FC 3.0官方SDK客户端
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region
        )
        self.client = Client(config)
    
    def invoke_function(self, service_name=None, function_name=None, body=None):
        """调用函数计算服务 - 使用FC 3.0官方SDK"""
        try:
            # 如果有函数URL，直接使用HTTP触发器调用
            if self.function_url:
                print(f"🌐 使用函数URL调用: {self.function_url}")
                print(f"📋 请求体: {body}")

                # 使用FC 3.0 SDK的HTTP触发器调用
                response = self.client.invoke_httptrigger(
                    url=self.function_url,
                    method="POST",
                    body=body.encode('utf-8') if isinstance(body, str) else body,
                    headers={"Content-Type": "application/json"}
                )

                print(f"📊 响应状态码: {response.status_code}")
                print(f"📄 响应内容: {getattr(response, 'text', getattr(response, 'content', str(response)))}")

                return FCResponse(response)
            else:
                # 如果没有函数URL，尝试构建传统的调用方式
                print("⚠️  未提供函数URL，FC 3.0推荐使用函数URL进行调用")
                raise Exception("FC 3.0需要函数URL进行调用，请在环境变量中设置FC_FUNCTION_URL")

        except Exception as e:
            print(f"❌ FC 3.0调用失败: {e}")
            raise


class FCResponse:
    """FC 3.0响应对象包装器"""

    def __init__(self, response):
        self.response = response
        # FC 3.0 SDK返回的是requests.Response对象
        self.status_code = getattr(response, 'status_code', 200)
        self.body = FCResponseBody(response)


class FCResponseBody:
    """FC 3.0响应体对象包装器"""

    def __init__(self, response):
        self.response = response
        # FC 3.0 SDK返回的是requests.Response对象
        if hasattr(response, 'text'):
            self.content = response.text
        elif hasattr(response, 'content'):
            self.content = response.content
        else:
            self.content = str(response)

    def read(self):
        if isinstance(self.content, str):
            return self.content.encode('utf-8')
        return self.content

    def decode(self, encoding='utf-8'):
        if isinstance(self.content, bytes):
            return self.content.decode(encoding)
        return str(self.content)


@pytest.fixture
def fc_client():
    """创建阿里云函数计算FC 3.0客户端fixture"""
    print("🔧 初始化FC 3.0客户端...")

    # 加载环境变量
    config = env_retrieving()

    # 检查必需的环境变量
    required_vars = ['access_key_id', 'access_key_secret', 'region']
    missing_vars = [var for var in required_vars if not config.get(var)]

    if missing_vars:
        pytest.skip(f"缺少必需的环境变量: {missing_vars}")

    print("✅ 环境变量检查:")
    for key, value in config.items():
        if value and 'key' in key.lower():
            # 隐藏敏感信息
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")

    # 创建FC 3.0客户端
    client = FCClient(
        access_key_id=config['access_key_id'],
        access_key_secret=config['access_key_secret'],
        region=config['region'],
        function_url=config.get('function_url')
    )

    return client


@pytest.fixture
def fc_config():
    """提供FC配置信息的fixture"""
    config = env_retrieving()
    return config
