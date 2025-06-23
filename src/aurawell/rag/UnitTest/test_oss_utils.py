#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS工具模块单元测试
测试oss_utils.py中的所有功能
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from oss_utils import load_oss_config, OSSManager, get_beijing_time, get_utc_time


class TestOSSConfig(unittest.TestCase):
    """测试OSS配置加载功能"""
    
    def setUp(self):
        """测试前准备"""
        self.test_env_vars = {
            'OSS_ACCESS_KEY_ID': 'test_access_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret_key',
            'OSS_REGION': 'cn-hangzhou',
            'OSS_ENDPOINT': 'oss-cn-hangzhou.aliyuncs.com',
            'OSS_BUCKET_NAME': 'test-bucket'
        }
    
    @patch.dict(os.environ, {
        'OSS_ACCESS_KEY_ID': 'test_access_key',
        'OSS_ACCESS_KEY_SECRET': 'test_secret_key',
        'OSS_REGION': 'cn-hangzhou',
        'OSS_ENDPOINT': 'oss-cn-hangzhou.aliyuncs.com',
        'OSS_BUCKET_NAME': 'test-bucket'
    })
    def test_load_oss_config_success(self):
        """测试成功加载OSS配置"""
        config, success = load_oss_config()
        
        self.assertTrue(success)
        self.assertEqual(config['access_key_id'], 'test_access_key')
        self.assertEqual(config['access_key_secret'], 'test_secret_key')
        self.assertEqual(config['region'], 'cn-hangzhou')
        self.assertEqual(config['endpoint'], 'oss-cn-hangzhou.aliyuncs.com')
        self.assertEqual(config['bucket_name'], 'test-bucket')
    
    @patch('oss_utils.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_load_oss_config_missing_keys(self, mock_load_dotenv):
        """测试缺少必需配置时的处理"""
        # 阻止加载.env文件
        mock_load_dotenv.return_value = None

        config, success = load_oss_config()

        self.assertFalse(success)
        self.assertIsNone(config['access_key_id'])
        self.assertIsNone(config['access_key_secret'])
    
    @patch('oss_utils.load_dotenv')
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'fallback_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'fallback_secret'
    }, clear=True)
    def test_load_oss_config_fallback(self, mock_load_dotenv):
        """测试使用回退配置"""
        # 阻止加载.env文件
        mock_load_dotenv.return_value = None

        config, success = load_oss_config()

        self.assertTrue(success)
        self.assertEqual(config['access_key_id'], 'fallback_key')
        self.assertEqual(config['access_key_secret'], 'fallback_secret')


class TestOSSManager(unittest.TestCase):
    """测试OSS管理器功能"""
    
    def setUp(self):
        """测试前准备"""
        # 使用模拟模式进行测试
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.oss_manager = OSSManager(mock_mode=True)
    
    def test_oss_manager_init_mock_mode(self):
        """测试OSS管理器模拟模式初始化"""
        self.assertTrue(self.oss_manager.mock_mode)
        self.assertIsInstance(self.oss_manager.mock_storage, dict)
    
    def test_upload_string_as_file_mock(self):
        """测试字符串上传功能（模拟模式）"""
        test_content = "这是测试内容"
        test_key = "test/file.txt"
        
        result = self.oss_manager.upload_string_as_file(test_content, test_key)
        
        self.assertTrue(result)
        self.assertIn(test_key, self.oss_manager.mock_storage)
        self.assertEqual(
            self.oss_manager.mock_storage[test_key]['content'],
            test_content.encode('utf-8')
        )
    
    def test_upload_file_mock(self):
        """测试文件上传功能（模拟模式）"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            temp_file.write("测试文件内容")
            temp_file_path = temp_file.name
        
        try:
            test_key = "test/uploaded_file.txt"
            result = self.oss_manager.upload_file(temp_file_path, test_key)
            
            self.assertTrue(result)
            self.assertIn(test_key, self.oss_manager.mock_storage)
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
    
    def test_upload_file_not_exists(self):
        """测试上传不存在的文件"""
        result = self.oss_manager.upload_file("nonexistent_file.txt", "test/key")
        self.assertFalse(result)
    
    def test_download_file_content_mock(self):
        """测试下载文件内容功能（模拟模式）"""
        # 先上传一个文件
        test_content = "测试下载内容"
        test_key = "test/download_test.txt"
        
        self.oss_manager.upload_string_as_file(test_content, test_key)
        
        # 下载内容
        downloaded_content = self.oss_manager.download_file_content(test_key)
        
        self.assertEqual(downloaded_content, test_content)
    
    def test_download_file_content_not_exists(self):
        """测试下载不存在文件的内容"""
        result = self.oss_manager.download_file_content("nonexistent/file.txt")
        self.assertIsNone(result)
    
    def test_file_exists_mock(self):
        """测试文件存在性检查（模拟模式）"""
        test_key = "test/exists_test.txt"
        
        # 文件不存在时
        self.assertFalse(self.oss_manager.file_exists(test_key))
        
        # 上传文件后
        self.oss_manager.upload_string_as_file("test", test_key)
        self.assertTrue(self.oss_manager.file_exists(test_key))
    
    def test_list_files_mock(self):
        """测试文件列表功能（模拟模式）"""
        # 上传几个测试文件
        test_files = [
            ("test/file1.txt", "内容1"),
            ("test/file2.txt", "内容2"),
            ("other/file3.txt", "内容3")
        ]
        
        for key, content in test_files:
            self.oss_manager.upload_string_as_file(content, key)
        
        # 测试无前缀列表
        all_files = self.oss_manager.list_files()
        self.assertEqual(len(all_files), 3)
        
        # 测试带前缀列表
        test_files_only = self.oss_manager.list_files(prefix="test/")
        self.assertEqual(len(test_files_only), 2)
        
        # 验证文件信息结构
        file_info = test_files_only[0]
        self.assertIn('key', file_info)
        self.assertIn('size', file_info)
        self.assertIn('last_modified', file_info)
        self.assertIn('etag', file_info)
    
    def test_list_files_with_max_keys(self):
        """测试文件列表的最大数量限制"""
        # 上传多个文件
        for i in range(5):
            self.oss_manager.upload_string_as_file(f"内容{i}", f"test/file{i}.txt")
        
        # 限制返回数量
        limited_files = self.oss_manager.list_files(max_keys=3)
        self.assertLessEqual(len(limited_files), 3)


class TestTimeUtils(unittest.TestCase):
    """测试时间工具函数"""
    
    def test_get_beijing_time(self):
        """测试获取北京时间"""
        beijing_time = get_beijing_time()
        
        self.assertIsInstance(beijing_time, str)
        self.assertIn('+08:00', beijing_time)  # 检查时区信息
    
    def test_get_utc_time(self):
        """测试获取UTC时间"""
        utc_time = get_utc_time()
        
        self.assertIsInstance(utc_time, str)
        self.assertIn('+00:00', utc_time)  # 检查UTC时区信息


class TestOSSManagerIntegration(unittest.TestCase):
    """测试OSS管理器集成功能"""
    
    def setUp(self):
        """测试前准备"""
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.oss_manager = OSSManager(mock_mode=True)
    
    def test_upload_download_cycle(self):
        """测试上传-下载循环"""
        test_content = "这是一个完整的上传下载测试"
        test_key = "integration/test_file.txt"
        
        # 上传
        upload_result = self.oss_manager.upload_string_as_file(test_content, test_key)
        self.assertTrue(upload_result)
        
        # 检查存在性
        exists = self.oss_manager.file_exists(test_key)
        self.assertTrue(exists)
        
        # 下载
        downloaded_content = self.oss_manager.download_file_content(test_key)
        self.assertEqual(downloaded_content, test_content)
        
        # 列表中应该包含该文件
        files = self.oss_manager.list_files(prefix="integration/")
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['key'], test_key)
    
    def test_json_file_operations(self):
        """测试JSON文件操作"""
        test_data = {
            "file1.pdf": {
                "filename": "file1.pdf",
                "upload_date": "2024-01-20T10:30:00+08:00",
                "vectorized": False
            },
            "file2.pdf": {
                "filename": "file2.pdf", 
                "upload_date": "2024-01-20T11:30:00+08:00",
                "vectorized": True
            }
        }
        
        json_key = "test/index.json"
        json_content = json.dumps(test_data, ensure_ascii=False, indent=2)
        
        # 上传JSON
        upload_result = self.oss_manager.upload_string_as_file(json_content, json_key)
        self.assertTrue(upload_result)
        
        # 下载并解析JSON
        downloaded_content = self.oss_manager.download_file_content(json_key)
        parsed_data = json.loads(downloaded_content)
        
        self.assertEqual(parsed_data, test_data)
        self.assertEqual(len(parsed_data), 2)
        self.assertFalse(parsed_data["file1.pdf"]["vectorized"])
        self.assertTrue(parsed_data["file2.pdf"]["vectorized"])


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestOSSConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestOSSManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestOSSManagerIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print(f"\n{'='*60}")
    print(f"测试完成: 运行 {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"{'='*60}")
