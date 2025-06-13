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

# 测试文件类型检测 - 修改路径指向rag文件夹下的testMaterial
test_file = "../rag/testMaterial/中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf"
print(f"Testing file: {test_file}")
file_type = get_file_type(test_file)
print(f"File type returned: '{file_type}'")

# 检查支持的格式 - 更新为正确的格式（不带点号）
supported_formats = ["pdf", "docx", "xlsx"]
print(f"Supported formats: {supported_formats}")
print(f"Is file type supported: {file_type in supported_formats}")

# 测试环境变量
from rag_utils import env_reader
print("Testing environment variables:")
env_result = env_reader()
print(f"Environment variables loaded: {env_result}")
