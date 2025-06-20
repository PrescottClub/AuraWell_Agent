#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS功能快速测试脚本
运行核心功能的快速验证测试
"""

import unittest
import os
import sys
import time

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class QuickOSSTest(unittest.TestCase):
    """OSS功能快速测试"""
    
    def setUp(self):
        """测试前准备"""
        self.env_vars = {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }
    
    def test_oss_config_loading(self):
        """测试OSS配置加载"""
        from unittest.mock import patch
        
        with patch.dict(os.environ, self.env_vars):
            from oss_utils import load_oss_config
            
            config, success = load_oss_config()
            self.assertTrue(success)
            self.assertEqual(config['access_key_id'], 'test_key')
            self.assertEqual(config['bucket_name'], 'test-bucket')
    
    def test_oss_manager_mock_mode(self):
        """测试OSS管理器模拟模式"""
        from unittest.mock import patch
        
        with patch.dict(os.environ, self.env_vars):
            from oss_utils import OSSManager
            
            oss_manager = OSSManager(mock_mode=True)
            self.assertTrue(oss_manager.mock_mode)
            
            # 测试基本操作
            result = oss_manager.upload_string_as_file("test content", "test/file.txt")
            self.assertTrue(result)
            
            exists = oss_manager.file_exists("test/file.txt")
            self.assertTrue(exists)
            
            content = oss_manager.download_file_content("test/file.txt")
            self.assertEqual(content, "test content")
    
    def test_file_index_manager_basic(self):
        """测试文件索引管理器基本功能"""
        from unittest.mock import patch
        
        with patch.dict(os.environ, self.env_vars):
            from file_index_manager import FileIndexManager
            
            file_manager = FileIndexManager()
            
            # 测试添加文件记录
            result = file_manager.add_file_record("test.pdf", "nutrition/test.pdf", False)
            self.assertTrue(result)
            
            # 测试检查文件存在
            exists = file_manager.file_exists_in_index("test.pdf")
            self.assertTrue(exists)
            
            # 测试获取文件记录
            record = file_manager.get_file_record("test.pdf")
            self.assertIsNotNone(record)
            self.assertEqual(record["filename"], "test.pdf")
            self.assertFalse(record["vectorized"])
    
    def test_arxiv_xml_parsing(self):
        """测试arXiv XML解析"""
        from arXivAPI import parse_arxiv_xml
        
        sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2024.12345v1</id>
        <title>Test Paper</title>
        <published>2024-01-20T10:30:00Z</published>
        <summary>Test summary</summary>
        <author>
            <name>Test Author</name>
        </author>
        <link title="pdf" href="http://arxiv.org/pdf/2024.12345v1.pdf"/>
    </entry>
</feed>'''
        
        papers = parse_arxiv_xml(sample_xml)
        self.assertEqual(len(papers), 1)
        
        paper = papers[0]
        self.assertEqual(paper['title'], 'Test Paper')
        self.assertEqual(paper['id'], '2024.12345v1')
        self.assertEqual(paper['pdf_url'], 'http://arxiv.org/pdf/2024.12345v1.pdf')
    
    def test_language_detection(self):
        """测试语言检测功能"""
        from RAGExtension import detect_language
        
        # 测试中文检测
        self.assertEqual(detect_language("营养膳食建议"), "chinese")
        
        # 测试英文检测
        self.assertEqual(detect_language("daily nutrition recommendations"), "english")
        
        # 测试默认情况
        self.assertEqual(detect_language(""), "chinese")
    
    def test_time_utils(self):
        """测试时间工具函数"""
        from oss_utils import get_beijing_time, get_utc_time
        
        beijing_time = get_beijing_time()
        utc_time = get_utc_time()
        
        self.assertIsInstance(beijing_time, str)
        self.assertIsInstance(utc_time, str)
        self.assertIn('+08:00', beijing_time)
        self.assertIn('+00:00', utc_time)


class QuickIntegrationTest(unittest.TestCase):
    """快速集成测试"""
    
    def test_oss_file_operations_integration(self):
        """测试OSS文件操作集成"""
        from unittest.mock import patch
        
        env_vars = {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }
        
        with patch.dict(os.environ, env_vars):
            from oss_utils import OSSManager
            
            oss_manager = OSSManager(mock_mode=True)
            
            # 测试完整的文件操作流程
            test_files = [
                ("file1.txt", "content1"),
                ("file2.txt", "content2"),
                ("nutrition/paper1.pdf", "paper content 1")
            ]
            
            # 上传文件
            for key, content in test_files:
                result = oss_manager.upload_string_as_file(content, key)
                self.assertTrue(result)
            
            # 验证文件存在
            for key, _ in test_files:
                exists = oss_manager.file_exists(key)
                self.assertTrue(exists)
            
            # 下载并验证内容
            for key, expected_content in test_files:
                downloaded_content = oss_manager.download_file_content(key)
                self.assertEqual(downloaded_content, expected_content)
            
            # 测试文件列表
            all_files = oss_manager.list_files()
            self.assertEqual(len(all_files), 3)
            
            nutrition_files = oss_manager.list_files(prefix="nutrition/")
            self.assertEqual(len(nutrition_files), 1)
    
    def test_file_index_workflow(self):
        """测试文件索引工作流程"""
        from unittest.mock import patch
        
        env_vars = {
            'OSS_ACCESS_KEY_ID': 'test_key',
            'OSS_ACCESS_KEY_SECRET': 'test_secret',
            'OSS_BUCKET_NAME': 'test-bucket'
        }
        
        with patch.dict(os.environ, env_vars):
            from file_index_manager import FileIndexManager
            
            file_manager = FileIndexManager()
            
            # 添加多个文件
            test_files = [
                ("paper1.pdf", "nutrition/paper1.pdf", False),
                ("paper2.pdf", "nutrition/paper2.pdf", True),
                ("paper3.pdf", "nutrition/paper3.pdf", False)
            ]
            
            for filename, oss_key, vectorized in test_files:
                result = file_manager.add_file_record(filename, oss_key, vectorized)
                self.assertTrue(result)
            
            # 获取所有文件
            all_files = file_manager.get_all_files()
            self.assertEqual(len(all_files), 3)
            
            # 获取未向量化文件
            unvectorized = file_manager.get_unvectorized_files()
            self.assertEqual(len(unvectorized), 2)
            
            # 更新向量化状态
            result = file_manager.update_vectorization_status("paper1.pdf", True)
            self.assertTrue(result)
            
            # 验证状态更新
            updated_record = file_manager.get_file_record("paper1.pdf")
            self.assertTrue(updated_record["vectorized"])


def run_quick_tests():
    """运行快速测试"""
    print("🚀 开始运行OSS功能快速测试")
    print("=" * 50)
    
    start_time = time.time()
    
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类的所有测试方法
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(QuickOSSTest))
    suite.addTests(loader.loadTestsFromTestCase(QuickIntegrationTest))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 快速测试结果摘要")
    print("=" * 50)
    print(f"⏱️  测试持续时间: {duration:.2f} 秒")
    print(f"📈 测试统计:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"  成功率: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # 总体评估
    print(f"\n🎯 快速测试评估:")
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("  ✅ 所有快速测试通过！核心功能正常")
    elif success_rate >= 80:
        print("  ⚠️  大部分测试通过，核心功能基本正常")
    else:
        print("  ❌ 多个测试失败，需要检查核心功能")
    
    return result


if __name__ == '__main__':
    run_quick_tests()
