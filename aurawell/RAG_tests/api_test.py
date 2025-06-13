#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

from rag_utils import get_file_type
from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CredentialsConfig
from dotenv import load_dotenv

# 加载环境变量
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(os.path.dirname(current_dir))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")

print(f"Access Key ID: {access_key_id}")
print(f"Access Key Secret: {access_key_secret[:10]}...")

# 测试文件 - 修改路径指向rag文件夹下的testMaterial
file_path = "../rag/testMaterial/中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf"
file_extension = get_file_type(file_path)
print(f"File extension: '{file_extension}'")

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"File does not exist: {file_path}")
    exit(1)

print(f"File exists: {file_path}")
print(f"File size: {os.path.getsize(file_path)} bytes")

# 构造 Credential
cred_config = CredentialsConfig(
    type="access_key",
    access_key_id=access_key_id,
    access_key_secret=access_key_secret
)

cred = CredClient(config=cred_config)
config = open_api_models.Config(
    access_key_id=cred.get_credential().get_access_key_id(),
    access_key_secret=cred.get_credential().get_access_key_secret()
)

config.read_timeout = 2400
config.connect_timeout = 1200
config.endpoint = 'docmind-api.cn-hangzhou.aliyuncs.com'

client = docmind_api20220711Client(config)

print(f"Creating request with file_name_extension: '{file_extension}'")

# 创建请求
request = docmind_api20220711_models.SubmitDocParserJobAdvanceRequest(
    file_url_object=open(file_path, "rb"),
    file_name_extension=file_extension
)

runtime = util_models.RuntimeOptions(
    read_timeout=24000,
    connect_timeout=12000
)

print("Sending request to Alibaba Cloud DocMind API...")

try:
    response = client.submit_doc_parser_job_advance(request, runtime)
    print("Response received:")
    print(response.body)
    
    if response.body.data is None:
        print("Error: response.body.data is None")
        print(f"Full response: {response.body}")
    else:
        print(f"Success! Job ID: {response.body.data.id}")
        
except Exception as e:
    print(f"Exception occurred: {e}")
    import traceback
    traceback.print_exc()
