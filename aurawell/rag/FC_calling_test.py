# 阿里云FC函数调用测试, 目标FC函数的超时阈值为300秒，请在网络环境稳定的情况下进行测试

import pytest
import os
from dotenv import load_dotenv
from os import getenv
import requests
import hmac
import hashlib
import base64
from datetime import datetime

def env_retrieving()->dict:
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录（假设 rag_utils.py 在 aurawell/rag/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')

        # 加载指定路径下的 .env 文件
        load_dotenv(dotenv_path=dotenv_path)

        # 读取环境变量
        access_key_id = getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        dash_scope_key = getenv("DASHSCOPE_API_KEY") 
        dash_vector_key = getenv("DASH_VECTOR_API")
        cloud_region = getenv("FCreigion")
        service_name = getenv("SERVICE_NAME")
        function_name = getenv("FUNCTION_NAME")
        return {
            "ALIBABA_CLOUD_ACCESS_KEY_ID": access_key_id,
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": access_key_secret,
            "DASHSCOPE_API_KEY": dash_scope_key,
            "DASH_VECTOR_API": dash_vector_key,
            "ALIBABA_CLOUD_REGION": cloud_region,
            "ALIBABA_CLOUD_FC_SERVICE_NAME": service_name,
            "ALIBABA_CLOUD_FC_FUNCTION_NAME": function_name
        }
key_chain = env_retrieving()
# 1. 阿里云AccessKey
ACCESS_KEY_ID = key_chain["ALIBABA_CLOUD_ACCESS_KEY_ID"]  # 替换为你的阿里云AccessKey ID
ACCESS_KEY_SECRET = key_chain["ALIBABA_CLOUD_ACCESS_KEY_SECRET"]  # 替换为你的AccessKey Secret

# 2. 阿里云FC配置
REGION = key_chain["ALIBABA_CLOUD_REGION"]  # 例如：cn-hangzhou
SERVICE_NAME = key_chain["ALIBABA_CLOUD_FC_SERVICE_NAME"]  # 你的FC服务名称
FUNCTION_NAME = key_chain["ALIBABA_CLOUD_FC_FUNCTION_NAME"]  # 函数名称
ENDPOINT = f"https://{REGION}.api.aliyun.fc.com"  # FC服务的Endpoint

# 生成阿里云FC的认证头
def get_aliyun_auth_headers():
    method = "POST"
    path = f"/2016-08-15/proxy/{SERVICE_NAME}/{FUNCTION_NAME}"
    date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    string_to_sign = f"{method}\n\n\n{date}\n{path}"
    signature = hmac.new(
        ACCESS_KEY_SECRET.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1
    ).digest()
    signature = base64.b64encode(signature).decode("utf-8")
    
    auth_header = f"FC {ACCESS_KEY_ID}:{signature}"
    return {
        "Date": date,
        "Content-Type": "application/json",
        "Authorization": auth_header
    }

# Pytest测试用例
def test_ragmodule_retrieve_topk():
    # 构建请求URL
    url = f"{ENDPOINT}/2016-08-15/proxy/{SERVICE_NAME}/{FUNCTION_NAME}"
    
    # 范例请求数据
    payload = {
        "action": "RetrieveTopK",
        "query": {
            "user_query": "每日营养建议",
            "k": 3
        }
    }
    
    # 发送请求
    headers = get_aliyun_auth_headers()
    response = requests.post(url, json=payload, headers=headers)
    
    # 断言验证
    assert response.status_code == 200
    data = response.json()
    
    # 验证基础字段
    assert data["body"] == "检索成功"
    assert data["statusCode"] == 200
    
    # 验证返回结果
    results = data["results"]
    assert len(results) == 3  # 确保返回3个结果
    assert all(isinstance(item, str) for item in results)  # 确保结果为字符串数组
    

# 如果需要，可以添加其他测试场景（如错误处理测试）
# @pytest.mark.parametrize等参数化测试

