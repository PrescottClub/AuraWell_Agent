import os
import json
from alibabacloud_fc20230330.client import Client as FC20230330Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_fc20230330 import models as fc20230330_models

# 正常请求数据
valid_event = {
    "action": "RetrieveTopK",
    "query": {
        "user_query": "每日营养建议",
        "k": 3
    }
}

# 异常情况：缺少 user_query
missing_user_query = {
    "action": "RetrieveTopK",
    "query": {
        "k": 3
    }
}

# 异常情况：k 不是正整数
invalid_k_value = {
    "action": "RetrieveTopK",
    "query": {
        "user_query": "每日营养建议",
        "k": -1
    }
}

def read_credentials()-> FC20230330Client:
        """
        使用凭据初始化账号Client
        @return: Client
        @throws Exception
        """
        credential = CredentialClient()
        config = open_api_models.Config(
            type="access_key",
            access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
            region_id='cn-hangzhou',
            endpoint="1535508388697445.cn-hangzhou.fc.aliyuncs.com"
        )

        return FC20230330Client(config)

def normal_test():
    json_str = json.dumps(valid_event, ensure_ascii=False)
    bytes_data = json_str.encode('utf-8')

    client = read_credentials()
    request = fc20230330_models.InvokeFunctionRequest(body=bytes_data,qualifier='LATEST')
    response = client.invoke_function(function_name='RAGmoudle', request=request)
    status_code = response.status_code
    print("响应状态码：", status_code)
    result = response.body.read().decode('utf-8')
    # print("函数返回结果：", result)
    parsed_response = json.loads(result)
    # 打印解析后的结果（中文可读）
    print("解析后结果：", parsed_response)
    print(type(parsed_response))
    print(parsed_response['results'])
    print(len(parsed_response['results']))
    # print(response.body)
    return None

def test_invalid_event():
    # 异常情况：缺少 user_query
    missing_user_query = {
    "action": "RetrieveTopK",
    "query": {
        "k": 3
        }
    }
    json_str = json.dumps(missing_user_query, ensure_ascii=False)
    bytes_data = json_str.encode('utf-8')

    client = read_credentials()
    request = fc20230330_models.InvokeFunctionRequest(body=bytes_data,qualifier='LATEST')
    response = client.invoke_function(function_name='RAGmoudle', request=request)
    status_code = response.status_code
    result = response.body.read().decode('utf-8')
    parsed_response = json.loads(result)
    print(type(parsed_response))
    print(parsed_response)
    print(parsed_response.get("statusCode", None))

if __name__ == "__main__":
    # normal_test()
    test_invalid_event()