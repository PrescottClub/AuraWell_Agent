#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云OSS存储工具模块
提供文件上传、下载、列表查询等功能
"""

import os
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple
import tempfile

# 尝试导入oss2，如果失败则使用模拟模式
try:
    import oss2
    OSS2_AVAILABLE = True
    print("✅ oss2模块加载成功")
except ImportError:
    OSS2_AVAILABLE = False
    print("⚠️  oss2模块未安装，使用模拟模式")

def load_oss_config():
    """
    从.env文件或环境变量中加载OSS配置
    
    Returns:
        dict: OSS配置信息
        bool: 是否成功加载配置
    """
    # 尝试从.env文件加载
    try:
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 src/aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录（向上三级：rag -> aurawell -> src -> 项目根目录）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')
        
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            print(f"✅ 从.env文件加载OSS配置: {dotenv_path}")
        else:
            print(f"⚠️  .env文件不存在: {dotenv_path}")
    except Exception as e:
        print(f"⚠️  从.env文件加载配置失败: {e}")
    
    # 从环境变量读取配置
    config = {
        "access_key_id": os.getenv("OSS_ACCESS_KEY_ID") or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        "access_key_secret": os.getenv("OSS_ACCESS_KEY_SECRET") or os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
        "region": os.getenv("OSS_REGION", "cn-hangzhou"),
        "endpoint": os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com"),
        "endpoint_internal": os.getenv("OSS_ENDPOINT_INTERNAL", "oss-cn-hangzhou-internal.aliyuncs.com"),
        "bucket_name": os.getenv("OSS_BUCKET_NAME", "rag-knowledge-bucket")
    }
    
    # 检查必需的配置
    missing_keys = [key for key, value in config.items() if not value]
    success = len(missing_keys) == 0
    
    if success:
        print("🎉 OSS配置加载成功")
    else:
        print(f"⚠️  缺少OSS配置: {missing_keys}")
    
    return config, success

class OSSManager:
    """阿里云OSS存储管理器"""

    def __init__(self, use_internal_endpoint=False, mock_mode=None):
        """
        初始化OSS管理器

        Args:
            use_internal_endpoint (bool): 是否使用内网端点
            mock_mode (bool): 是否使用模拟模式，None时自动检测
        """
        self.config, success = load_oss_config()

        if not success:
            raise ValueError("❌ 无法加载OSS配置，请检查.env文件或环境变量设置")

        # 确定是否使用模拟模式
        self.mock_mode = mock_mode if mock_mode is not None else not OSS2_AVAILABLE

        if self.mock_mode:
            print("⚠️  OSS管理器运行在模拟模式")
            self.mock_storage = {}  # 模拟存储
            return

        # 选择端点
        endpoint = self.config["endpoint_internal"] if use_internal_endpoint else self.config["endpoint"]
        self.endpoint = f"https://{endpoint}"

        # 初始化OSS认证和Bucket
        self.auth = oss2.Auth(self.config["access_key_id"], self.config["access_key_secret"])
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.config["bucket_name"])

        print(f"✅ OSS管理器初始化完成，使用端点: {self.endpoint}")
    
    def upload_file(self, local_file_path: str, oss_key: str) -> bool:
        """
        上传文件到OSS

        Args:
            local_file_path (str): 本地文件路径
            oss_key (str): OSS中的文件键名

        Returns:
            bool: 上传是否成功
        """
        try:
            if not os.path.exists(local_file_path):
                print(f"❌ 本地文件不存在: {local_file_path}")
                return False

            if self.mock_mode:
                # 模拟模式：只记录文件信息
                with open(local_file_path, 'rb') as f:
                    content = f.read()
                self.mock_storage[oss_key] = {
                    'content': content,
                    'size': len(content),
                    'last_modified': datetime.now().isoformat(),
                    'etag': f"mock-etag-{hash(content) % 1000000}"
                }
                print(f"✅ 文件上传成功（模拟模式）: {oss_key}")
                return True

            with open(local_file_path, 'rb') as f:
                result = self.bucket.put_object(oss_key, f)

            print(f"✅ 文件上传成功: {oss_key}, ETag: {result.etag}")
            return True

        except Exception as e:
            print(f"❌ 文件上传失败: {e}")
            return False
    
    def upload_string_as_file(self, content: str, oss_key: str) -> bool:
        """
        将字符串内容作为文件上传到OSS

        Args:
            content (str): 要上传的字符串内容
            oss_key (str): OSS中的文件键名

        Returns:
            bool: 上传是否成功
        """
        try:
            if self.mock_mode:
                # 模拟模式：只记录内容
                content_bytes = content.encode('utf-8')
                self.mock_storage[oss_key] = {
                    'content': content_bytes,
                    'size': len(content_bytes),
                    'last_modified': datetime.now().isoformat(),
                    'etag': f"mock-etag-{hash(content) % 1000000}"
                }
                print(f"✅ 字符串内容上传成功（模拟模式）: {oss_key}")
                return True

            result = self.bucket.put_object(oss_key, content.encode('utf-8'))
            print(f"✅ 字符串内容上传成功: {oss_key}, ETag: {result.etag}")
            return True

        except Exception as e:
            print(f"❌ 字符串内容上传失败: {e}")
            return False
    
    def download_file(self, oss_key: str, local_file_path: str) -> bool:
        """
        从OSS下载文件
        
        Args:
            oss_key (str): OSS中的文件键名
            local_file_path (str): 本地保存路径
            
        Returns:
            bool: 下载是否成功
        """
        try:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            self.bucket.get_object_to_file(oss_key, local_file_path)
            print(f"✅ 文件下载成功: {oss_key} -> {local_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 文件下载失败: {e}")
            return False
    
    def download_file_content(self, oss_key: str) -> Optional[str]:
        """
        从OSS下载文件内容为字符串

        Args:
            oss_key (str): OSS中的文件键名

        Returns:
            Optional[str]: 文件内容，失败返回None
        """
        try:
            if self.mock_mode:
                # 模拟模式：从模拟存储获取内容
                if oss_key in self.mock_storage:
                    content = self.mock_storage[oss_key]['content'].decode('utf-8')
                    print(f"✅ 文件内容下载成功（模拟模式）: {oss_key}")
                    return content
                else:
                    print(f"❌ 文件不存在（模拟模式）: {oss_key}")
                    return None

            result = self.bucket.get_object(oss_key)
            content = result.read().decode('utf-8')
            print(f"✅ 文件内容下载成功: {oss_key}")
            return content

        except Exception as e:
            print(f"❌ 文件内容下载失败: {e}")
            return None
    
    def file_exists(self, oss_key: str) -> bool:
        """
        检查文件是否存在于OSS中

        Args:
            oss_key (str): OSS中的文件键名

        Returns:
            bool: 文件是否存在
        """
        try:
            if self.mock_mode:
                # 模拟模式：检查模拟存储
                return oss_key in self.mock_storage

            self.bucket.head_object(oss_key)
            return True
        except Exception as e:
            if self.mock_mode or "NoSuchKey" in str(e):
                return False
            print(f"❌ 检查文件存在性失败: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict]:
        """
        列出OSS中的文件

        Args:
            prefix (str): 文件前缀过滤
            max_keys (int): 最大返回数量

        Returns:
            List[Dict]: 文件信息列表
        """
        try:
            if self.mock_mode:
                # 模拟模式：从模拟存储获取文件列表
                files = []
                for key, info in self.mock_storage.items():
                    if key.startswith(prefix):
                        files.append({
                            'key': key,
                            'size': info['size'],
                            'last_modified': info['last_modified'],
                            'etag': info['etag']
                        })
                        if len(files) >= max_keys:
                            break
                print(f"✅ 成功列出 {len(files)} 个文件（模拟模式）")
                return files

            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=max_keys):
                files.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag
                })

            print(f"✅ 成功列出 {len(files)} 个文件")
            return files

        except Exception as e:
            print(f"❌ 列出文件失败: {e}")
            return []
    
    def delete_file(self, oss_key: str) -> bool:
        """
        删除OSS中的文件
        
        Args:
            oss_key (str): OSS中的文件键名
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.bucket.delete_object(oss_key)
            print(f"✅ 文件删除成功: {oss_key}")
            return True
            
        except Exception as e:
            print(f"❌ 文件删除失败: {e}")
            return False

def get_beijing_time() -> str:
    """
    获取北京时间（东八区）的ISO格式字符串
    
    Returns:
        str: 北京时间字符串
    """
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = datetime.now(beijing_tz)
    return beijing_time.isoformat()

def get_utc_time() -> str:
    """
    获取UTC时间的ISO格式字符串
    
    Returns:
        str: UTC时间字符串
    """
    utc_time = datetime.now(timezone.utc)
    return utc_time.isoformat()
