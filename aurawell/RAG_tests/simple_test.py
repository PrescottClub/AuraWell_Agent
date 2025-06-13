#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

print("Starting import tests...")

try:
    print("1. Testing basic imports...")
    import time
    print("   Basic imports OK")
    
    print("2. Testing dotenv...")
    from dotenv import load_dotenv
    print("   dotenv import OK")
    
    print("3. Testing numpy...")
    import numpy as np
    print("   numpy import OK")
    
    print("4. Testing OpenAI...")
    from openai import OpenAI
    print("   OpenAI import OK")
    
    print("5. Testing Alibaba Cloud imports...")
    from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
    from alibabacloud_tea_util import models as util_models
    from alibabacloud_credentials.client import Client as CredClient
    from alibabacloud_credentials.models import Config as CredentialsConfig
    print("   Alibaba Cloud imports OK")
    
    print("6. Testing DashVector...")
    import dashvector
    from dashvector import Doc
    print("   DashVector imports OK")
    
    print("7. Testing local imports...")
    from rag_utils import get_file_type, process_list
    print("   Local imports OK")
    
    print("8. Testing Document class initialization...")
    from RAGExtension import Document
    print("   Document class import OK")
    
    print("9. Creating Document instance...")
    obj = Document()
    print("   Document instance created OK")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
