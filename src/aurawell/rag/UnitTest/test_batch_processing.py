#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理功能单元测试
测试RAGExtension.py中的批量处理功能
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class TestBatchProcessing(unittest.TestCase):
    """测试批量处理功能"""
    
    def setUp(self):
        """测试前准备"""
        self.env_vars = {
            'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
            'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
            'DASHSCOPE_API_KEY': 'test_dashscope_key',
            'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
            'DASH_VECTOR_API': 'test_vector_key'
        }
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    @patch('RAGExtension.Document.file2VectorDB')
    def test_batch_process_recent_files_success(self, mock_file2vectordb, mock_get_recent):
        """测试批量处理最近文件成功"""
        from RAGExtension import Document
        
        # 模拟最近文件数据
        mock_recent_files = [
            {
                "filename": "unvectorized1.pdf",
                "oss_key": "nutrition/unvectorized1.pdf",
                "vectorized": False
            },
            {
                "filename": "unvectorized2.pdf",
                "oss_key": "nutrition/unvectorized2.pdf",
                "vectorized": False
            },
            {
                "filename": "vectorized1.pdf",
                "oss_key": "nutrition/vectorized1.pdf",
                "vectorized": True
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        
        # 模拟向量化成功
        mock_file2vectordb.return_value = True
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30, use_content_filter=True)
        
        # 验证结果
        self.assertEqual(results["total"], 2)  # 只有2个未向量化文件
        self.assertEqual(results["processed"], 2)
        self.assertEqual(results["failed"], 0)
        self.assertEqual(results["skipped"], 0)
        
        # 验证调用
        mock_get_recent.assert_called_once_with(30)
        self.assertEqual(mock_file2vectordb.call_count, 2)
        
        # 验证调用参数
        call_args_list = mock_file2vectordb.call_args_list
        self.assertEqual(call_args_list[0][0][0], "nutrition/unvectorized1.pdf")
        self.assertEqual(call_args_list[1][0][0], "nutrition/unvectorized2.pdf")
        
        # 验证关键字参数
        for call_args in call_args_list:
            kwargs = call_args[1]
            self.assertTrue(kwargs["use_content_filter"])
            self.assertTrue(kwargs["is_oss_key"])
            self.assertTrue(kwargs["update_index"])
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    def test_batch_process_no_recent_files(self, mock_get_recent):
        """测试没有最近文件的情况"""
        from RAGExtension import Document
        
        # 模拟没有最近文件
        mock_get_recent.return_value = []
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30)
        
        # 验证结果
        self.assertEqual(results["total"], 0)
        self.assertEqual(results["processed"], 0)
        self.assertEqual(results["failed"], 0)
        self.assertEqual(results["skipped"], 0)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    def test_batch_process_all_vectorized(self, mock_get_recent):
        """测试所有文件都已向量化的情况"""
        from RAGExtension import Document
        
        # 模拟所有文件都已向量化
        mock_recent_files = [
            {
                "filename": "vectorized1.pdf",
                "oss_key": "nutrition/vectorized1.pdf",
                "vectorized": True
            },
            {
                "filename": "vectorized2.pdf",
                "oss_key": "nutrition/vectorized2.pdf",
                "vectorized": True
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30)
        
        # 验证结果
        self.assertEqual(results["total"], 0)  # 没有未向量化文件
        self.assertEqual(results["processed"], 0)
        self.assertEqual(results["failed"], 0)
        self.assertEqual(results["skipped"], 2)  # 跳过了2个已向量化文件
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    @patch('RAGExtension.Document.file2VectorDB')
    def test_batch_process_partial_failure(self, mock_file2vectordb, mock_get_recent):
        """测试部分处理失败的情况"""
        from RAGExtension import Document
        
        # 模拟未向量化文件
        mock_recent_files = [
            {
                "filename": "success.pdf",
                "oss_key": "nutrition/success.pdf",
                "vectorized": False
            },
            {
                "filename": "failure.pdf",
                "oss_key": "nutrition/failure.pdf",
                "vectorized": False
            },
            {
                "filename": "success2.pdf",
                "oss_key": "nutrition/success2.pdf",
                "vectorized": False
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        
        # 模拟部分成功部分失败
        mock_file2vectordb.side_effect = [True, False, True]
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30)
        
        # 验证结果
        self.assertEqual(results["total"], 3)
        self.assertEqual(results["processed"], 2)
        self.assertEqual(results["failed"], 1)
        self.assertEqual(results["skipped"], 0)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    @patch('RAGExtension.Document.file2VectorDB')
    def test_batch_process_with_exception(self, mock_file2vectordb, mock_get_recent):
        """测试处理过程中发生异常的情况"""
        from RAGExtension import Document
        
        # 模拟未向量化文件
        mock_recent_files = [
            {
                "filename": "exception.pdf",
                "oss_key": "nutrition/exception.pdf",
                "vectorized": False
            },
            {
                "filename": "success.pdf",
                "oss_key": "nutrition/success.pdf",
                "vectorized": False
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        
        # 模拟第一个文件处理时抛出异常，第二个成功
        mock_file2vectordb.side_effect = [Exception("处理异常"), True]
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30)
        
        # 验证结果
        self.assertEqual(results["total"], 2)
        self.assertEqual(results["processed"], 1)
        self.assertEqual(results["failed"], 1)
        self.assertEqual(results["skipped"], 0)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    @patch('RAGExtension.Document.file2VectorDB')
    def test_batch_process_different_days(self, mock_file2vectordb, mock_get_recent):
        """测试不同天数参数的批量处理"""
        from RAGExtension import Document
        
        # 模拟文件数据
        mock_recent_files = [
            {
                "filename": "test.pdf",
                "oss_key": "nutrition/test.pdf",
                "vectorized": False
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        mock_file2vectordb.return_value = True
        
        doc = Document()
        
        # 测试不同的天数参数
        test_days = [7, 15, 30, 60]
        
        for days in test_days:
            results = doc.batch_process_recent_files(days=days)
            
            # 验证get_recent_files_from_oss被正确调用
            mock_get_recent.assert_called_with(days)
            
            # 验证结果
            self.assertEqual(results["total"], 1)
            self.assertEqual(results["processed"], 1)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    @patch('RAGExtension.Document.file2VectorDB')
    def test_batch_process_content_filter_options(self, mock_file2vectordb, mock_get_recent):
        """测试不同内容过滤选项的批量处理"""
        from RAGExtension import Document
        
        # 模拟文件数据
        mock_recent_files = [
            {
                "filename": "test.pdf",
                "oss_key": "nutrition/test.pdf",
                "vectorized": False
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        mock_file2vectordb.return_value = True
        
        doc = Document()
        
        # 测试启用内容过滤
        results1 = doc.batch_process_recent_files(days=30, use_content_filter=True)
        self.assertEqual(results1["processed"], 1)
        
        # 验证file2VectorDB被正确调用
        last_call_kwargs = mock_file2vectordb.call_args[1]
        self.assertTrue(last_call_kwargs["use_content_filter"])
        
        # 测试禁用内容过滤
        results2 = doc.batch_process_recent_files(days=30, use_content_filter=False)
        self.assertEqual(results2["processed"], 1)
        
        # 验证file2VectorDB被正确调用
        last_call_kwargs = mock_file2vectordb.call_args[1]
        self.assertFalse(last_call_kwargs["use_content_filter"])


class TestBatchProcessingErrorHandling(unittest.TestCase):
    """测试批量处理的错误处理"""
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    def test_batch_process_get_files_exception(self, mock_get_recent):
        """测试获取文件列表时发生异常"""
        from RAGExtension import Document
        
        # 模拟获取文件时抛出异常
        mock_get_recent.side_effect = Exception("获取文件列表失败")
        
        doc = Document()
        results = doc.batch_process_recent_files(days=30)
        
        # 验证返回默认结果
        self.assertEqual(results["total"], 0)
        self.assertEqual(results["processed"], 0)
        self.assertEqual(results["failed"], 0)
        self.assertEqual(results["skipped"], 0)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.get_recent_files_from_oss')
    def test_batch_process_malformed_file_records(self, mock_get_recent):
        """测试处理格式错误的文件记录"""
        from RAGExtension import Document
        
        # 模拟格式错误的文件记录
        mock_recent_files = [
            {
                "filename": "normal.pdf",
                "oss_key": "nutrition/normal.pdf",
                "vectorized": False
            },
            {
                # 缺少必要字段的记录
                "filename": "malformed.pdf"
                # 缺少oss_key和vectorized字段
            },
            {
                "filename": "another_normal.pdf",
                "oss_key": "nutrition/another_normal.pdf",
                "vectorized": False
            }
        ]
        mock_get_recent.return_value = mock_recent_files
        
        doc = Document()
        
        # 应该能够处理格式错误的记录而不崩溃
        with patch.object(doc, 'file2VectorDB', return_value=True) as mock_file2vectordb:
            results = doc.batch_process_recent_files(days=30)
            
            # 应该只处理格式正确的文件
            # 注意：malformed.pdf没有vectorized字段，会被视为未向量化
            self.assertGreaterEqual(results["total"], 2)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestBatchProcessingErrorHandling))
    
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
