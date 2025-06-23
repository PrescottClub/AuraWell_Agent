#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件索引管理器单元测试
测试file_index_manager.py中的所有功能
"""

import unittest
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from file_index_manager import FileIndexManager


class TestFileIndexManager(unittest.TestCase):
    """测试文件索引管理器基本功能"""
    
    def setUp(self):
        """测试前准备"""
        # 使用模拟的OSS管理器
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.file_manager = FileIndexManager()
    
    def test_file_index_manager_init(self):
        """测试文件索引管理器初始化"""
        self.assertIsNotNone(self.file_manager.oss_manager)
        self.assertEqual(self.file_manager.index_file_key, "file_status/file_index.json")
        self.assertEqual(self.file_manager.nutrition_prefix, "nutrition/")
    
    def test_add_file_record(self):
        """测试添加文件记录"""
        filename = "test_paper.pdf"
        oss_key = "nutrition/test_paper.pdf"
        
        # 添加文件记录
        result = self.file_manager.add_file_record(filename, oss_key, vectorized=False)
        self.assertTrue(result)
        
        # 验证记录是否正确添加
        record = self.file_manager.get_file_record(filename)
        self.assertIsNotNone(record)
        self.assertEqual(record["filename"], filename)
        self.assertEqual(record["oss_key"], oss_key)
        self.assertFalse(record["vectorized"])
        self.assertIn("upload_date_utc", record)
        self.assertIn("upload_date_beijing", record)
        self.assertIn("last_updated", record)
    
    def test_update_vectorization_status(self):
        """测试更新向量化状态"""
        filename = "test_paper.pdf"
        oss_key = "nutrition/test_paper.pdf"
        
        # 先添加文件记录
        self.file_manager.add_file_record(filename, oss_key, vectorized=False)
        
        # 更新向量化状态
        result = self.file_manager.update_vectorization_status(filename, True)
        self.assertTrue(result)
        
        # 验证状态是否更新
        record = self.file_manager.get_file_record(filename)
        self.assertTrue(record["vectorized"])
    
    def test_update_vectorization_status_nonexistent(self):
        """测试更新不存在文件的向量化状态"""
        result = self.file_manager.update_vectorization_status("nonexistent.pdf", True)
        self.assertFalse(result)
    
    def test_file_exists_in_index(self):
        """测试检查文件是否在索引中"""
        filename = "test_paper.pdf"
        oss_key = "nutrition/test_paper.pdf"
        
        # 文件不存在时
        self.assertFalse(self.file_manager.file_exists_in_index(filename))
        
        # 添加文件后
        self.file_manager.add_file_record(filename, oss_key)
        self.assertTrue(self.file_manager.file_exists_in_index(filename))
    
    def test_get_file_record(self):
        """测试获取文件记录"""
        filename = "test_paper.pdf"
        oss_key = "nutrition/test_paper.pdf"
        
        # 不存在的文件
        record = self.file_manager.get_file_record("nonexistent.pdf")
        self.assertIsNone(record)
        
        # 存在的文件
        self.file_manager.add_file_record(filename, oss_key, vectorized=True)
        record = self.file_manager.get_file_record(filename)
        self.assertIsNotNone(record)
        self.assertEqual(record["filename"], filename)
        self.assertTrue(record["vectorized"])
    
    def test_remove_file_record(self):
        """测试移除文件记录"""
        filename = "test_paper.pdf"
        oss_key = "nutrition/test_paper.pdf"
        
        # 添加文件记录
        self.file_manager.add_file_record(filename, oss_key)
        self.assertTrue(self.file_manager.file_exists_in_index(filename))
        
        # 移除文件记录
        result = self.file_manager.remove_file_record(filename)
        self.assertTrue(result)
        self.assertFalse(self.file_manager.file_exists_in_index(filename))
        
        # 移除不存在的文件记录
        result = self.file_manager.remove_file_record("nonexistent.pdf")
        self.assertTrue(result)  # 不存在也算成功


class TestFileIndexManagerTimeQueries(unittest.TestCase):
    """测试文件索引管理器时间查询功能"""
    
    def setUp(self):
        """测试前准备"""
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.file_manager = FileIndexManager()
        
        # 准备测试数据
        self.test_files = [
            ("recent_file1.pdf", "nutrition/recent_file1.pdf", False),
            ("recent_file2.pdf", "nutrition/recent_file2.pdf", True),
            ("old_file1.pdf", "nutrition/old_file1.pdf", False),
            ("old_file2.pdf", "nutrition/old_file2.pdf", True)
        ]
    
    def test_get_files_uploaded_in_days(self):
        """测试获取指定天数内上传的文件"""
        beijing_tz = timezone(timedelta(hours=8))
        now = datetime.now(beijing_tz)
        
        # 模拟不同时间的文件
        recent_time = now - timedelta(days=5)  # 5天前
        old_time = now - timedelta(days=35)    # 35天前
        
        # 手动构建测试数据
        test_index = {
            "recent_file1.pdf": {
                "filename": "recent_file1.pdf",
                "oss_key": "nutrition/recent_file1.pdf",
                "upload_date_beijing": recent_time.isoformat(),
                "vectorized": False
            },
            "recent_file2.pdf": {
                "filename": "recent_file2.pdf",
                "oss_key": "nutrition/recent_file2.pdf",
                "upload_date_beijing": recent_time.isoformat(),
                "vectorized": True
            },
            "old_file1.pdf": {
                "filename": "old_file1.pdf",
                "oss_key": "nutrition/old_file1.pdf",
                "upload_date_beijing": old_time.isoformat(),
                "vectorized": False
            }
        }
        
        # 模拟_load_index方法
        with patch.object(self.file_manager, '_load_index', return_value=test_index):
            # 测试获取30天内的文件
            recent_files = self.file_manager.get_files_uploaded_in_days(30)
            self.assertEqual(len(recent_files), 2)
            
            # 测试获取10天内的文件
            very_recent_files = self.file_manager.get_files_uploaded_in_days(10)
            self.assertEqual(len(very_recent_files), 2)
            
            # 测试获取1天内的文件
            today_files = self.file_manager.get_files_uploaded_in_days(1)
            self.assertEqual(len(today_files), 0)
    
    def test_get_unvectorized_files(self):
        """测试获取未向量化的文件"""
        test_index = {
            "vectorized_file.pdf": {
                "filename": "vectorized_file.pdf",
                "vectorized": True
            },
            "unvectorized_file1.pdf": {
                "filename": "unvectorized_file1.pdf",
                "vectorized": False
            },
            "unvectorized_file2.pdf": {
                "filename": "unvectorized_file2.pdf",
                "vectorized": False
            },
            "no_status_file.pdf": {
                "filename": "no_status_file.pdf"
                # 没有vectorized字段，应该被视为未向量化
            }
        }
        
        with patch.object(self.file_manager, '_load_index', return_value=test_index):
            unvectorized_files = self.file_manager.get_unvectorized_files()
            self.assertEqual(len(unvectorized_files), 3)
            
            # 验证返回的都是未向量化的文件
            for file_record in unvectorized_files:
                self.assertFalse(file_record.get("vectorized", False))
    
    def test_get_all_files(self):
        """测试获取所有文件记录"""
        test_index = {
            "file1.pdf": {"filename": "file1.pdf"},
            "file2.pdf": {"filename": "file2.pdf"},
            "file3.pdf": {"filename": "file3.pdf"}
        }
        
        with patch.object(self.file_manager, '_load_index', return_value=test_index):
            all_files = self.file_manager.get_all_files()
            self.assertEqual(len(all_files), 3)
            self.assertEqual(all_files, test_index)


class TestFileIndexManagerErrorHandling(unittest.TestCase):
    """测试文件索引管理器错误处理"""
    
    def setUp(self):
        """测试前准备"""
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.file_manager = FileIndexManager()
    
    def test_load_index_error_handling(self):
        """测试加载索引时的错误处理"""
        # 模拟OSS下载失败
        with patch.object(self.file_manager.oss_manager, 'download_file_content', return_value=None):
            index_data = self.file_manager._load_index()
            self.assertEqual(index_data, {})
    
    def test_save_index_error_handling(self):
        """测试保存索引时的错误处理"""
        # 模拟OSS上传失败
        with patch.object(self.file_manager.oss_manager, 'upload_string_as_file', return_value=False):
            result = self.file_manager._save_index({"test": "data"})
            self.assertFalse(result)
    
    def test_invalid_json_handling(self):
        """测试处理无效JSON的情况"""
        # 模拟返回无效JSON
        with patch.object(self.file_manager.oss_manager, 'download_file_content', return_value="invalid json"):
            index_data = self.file_manager._load_index()
            self.assertEqual(index_data, {})
    
    def test_add_file_record_with_save_failure(self):
        """测试添加文件记录时保存失败的情况"""
        with patch.object(self.file_manager, '_save_index', return_value=False):
            result = self.file_manager.add_file_record("test.pdf", "nutrition/test.pdf")
            self.assertFalse(result)


class TestFileIndexManagerIntegration(unittest.TestCase):
    """测试文件索引管理器集成功能"""
    
    def setUp(self):
        """测试前准备"""
        with patch.dict(os.environ, {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }):
            self.file_manager = FileIndexManager()
    
    def test_complete_file_lifecycle(self):
        """测试完整的文件生命周期"""
        filename = "lifecycle_test.pdf"
        oss_key = "nutrition/lifecycle_test.pdf"
        
        # 1. 添加文件记录
        add_result = self.file_manager.add_file_record(filename, oss_key, vectorized=False)
        self.assertTrue(add_result)
        
        # 2. 验证文件存在
        exists = self.file_manager.file_exists_in_index(filename)
        self.assertTrue(exists)
        
        # 3. 获取文件记录
        record = self.file_manager.get_file_record(filename)
        self.assertIsNotNone(record)
        self.assertFalse(record["vectorized"])
        
        # 4. 更新向量化状态
        update_result = self.file_manager.update_vectorization_status(filename, True)
        self.assertTrue(update_result)
        
        # 5. 验证状态更新
        updated_record = self.file_manager.get_file_record(filename)
        self.assertTrue(updated_record["vectorized"])
        
        # 6. 移除文件记录
        remove_result = self.file_manager.remove_file_record(filename)
        self.assertTrue(remove_result)
        
        # 7. 验证文件已移除
        final_exists = self.file_manager.file_exists_in_index(filename)
        self.assertFalse(final_exists)
    
    def test_multiple_files_management(self):
        """测试多文件管理"""
        files_data = [
            ("file1.pdf", "nutrition/file1.pdf", False),
            ("file2.pdf", "nutrition/file2.pdf", True),
            ("file3.pdf", "nutrition/file3.pdf", False),
            ("file4.pdf", "nutrition/file4.pdf", True)
        ]
        
        # 添加多个文件
        for filename, oss_key, vectorized in files_data:
            result = self.file_manager.add_file_record(filename, oss_key, vectorized)
            self.assertTrue(result)
        
        # 验证所有文件都存在
        all_files = self.file_manager.get_all_files()
        self.assertEqual(len(all_files), 4)
        
        # 获取未向量化的文件
        unvectorized = self.file_manager.get_unvectorized_files()
        self.assertEqual(len(unvectorized), 2)
        
        # 验证未向量化文件的名称
        unvectorized_names = [f["filename"] for f in unvectorized]
        self.assertIn("file1.pdf", unvectorized_names)
        self.assertIn("file3.pdf", unvectorized_names)
    
    def test_time_based_queries_integration(self):
        """测试基于时间的查询集成"""
        beijing_tz = timezone(timedelta(hours=8))
        
        # 创建不同时间的文件记录
        files_with_times = [
            ("recent1.pdf", datetime.now(beijing_tz) - timedelta(days=1)),
            ("recent2.pdf", datetime.now(beijing_tz) - timedelta(days=15)),
            ("old1.pdf", datetime.now(beijing_tz) - timedelta(days=45)),
            ("old2.pdf", datetime.now(beijing_tz) - timedelta(days=60))
        ]
        
        # 构建测试索引
        test_index = {}
        for filename, upload_time in files_with_times:
            test_index[filename] = {
                "filename": filename,
                "oss_key": f"nutrition/{filename}",
                "upload_date_beijing": upload_time.isoformat(),
                "vectorized": False
            }
        
        with patch.object(self.file_manager, '_load_index', return_value=test_index):
            # 测试30天内的文件
            recent_30_days = self.file_manager.get_files_uploaded_in_days(30)
            self.assertEqual(len(recent_30_days), 2)
            
            # 测试7天内的文件
            recent_7_days = self.file_manager.get_files_uploaded_in_days(7)
            self.assertEqual(len(recent_7_days), 1)
            
            # 测试90天内的文件
            recent_90_days = self.file_manager.get_files_uploaded_in_days(90)
            self.assertEqual(len(recent_90_days), 4)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFileIndexManager))
    suite.addTests(loader.loadTestsFromTestCase(TestFileIndexManagerTimeQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestFileIndexManagerErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestFileIndexManagerIntegration))
    
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
