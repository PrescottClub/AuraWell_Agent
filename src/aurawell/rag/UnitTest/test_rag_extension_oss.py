#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGExtension OSS功能单元测试
测试RAGExtension.py中的OSS集成功能
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timezone, timedelta

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


class TestDocumentOSSMethods(unittest.TestCase):
    """测试Document类的OSS相关方法"""
    
    def setUp(self):
        """测试前准备"""
        # 模拟环境变量
        self.env_vars = {
            'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
            'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
            'DASHSCOPE_API_KEY': 'test_dashscope_key',
            'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
            'DASH_VECTOR_API': 'test_vector_key',
            'OSS_BUCKET_NAME': 'test-bucket'
        }
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    def test_document_init_with_oss(self):
        """测试Document类初始化包含OSS功能"""
        from RAGExtension import Document
        
        doc = Document()
        
        # 验证基本属性存在
        self.assertIsNotNone(doc.access_key_id)
        self.assertIsNotNone(doc.access_key_secret)
        self.assertIsNotNone(doc.dash_scope_key)
        self.assertIsNotNone(doc.qwen_api_key)
        self.assertIsNotNone(doc.dash_vector_key)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.FileIndexManager')
    def test_get_recent_files_from_oss(self, mock_file_manager_class):
        """测试从OSS获取最近文件"""
        from RAGExtension import Document
        
        # 模拟文件管理器
        mock_file_manager = MagicMock()
        mock_recent_files = [
            {
                "filename": "recent1.pdf",
                "oss_key": "nutrition/recent1.pdf",
                "upload_date_beijing": "2024-01-20T10:30:00+08:00",
                "vectorized": False
            },
            {
                "filename": "recent2.pdf",
                "oss_key": "nutrition/recent2.pdf",
                "upload_date_beijing": "2024-01-19T15:45:00+08:00",
                "vectorized": True
            }
        ]
        mock_file_manager.get_files_uploaded_in_days.return_value = mock_recent_files
        mock_file_manager_class.return_value = mock_file_manager
        
        doc = Document()
        recent_files = doc.get_recent_files_from_oss(30)
        
        # 验证结果
        self.assertEqual(len(recent_files), 2)
        self.assertEqual(recent_files[0]["filename"], "recent1.pdf")
        self.assertFalse(recent_files[0]["vectorized"])
        self.assertTrue(recent_files[1]["vectorized"])
        
        # 验证调用
        mock_file_manager.get_files_uploaded_in_days.assert_called_once_with(30)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.OSSManager')
    @patch('RAGExtension.tempfile.NamedTemporaryFile')
    def test_download_file_from_oss(self, mock_tempfile, mock_oss_manager_class):
        """测试从OSS下载文件"""
        from RAGExtension import Document
        
        # 模拟临时文件
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test_download.pdf'
        mock_tempfile.return_value = mock_temp
        
        # 模拟OSS管理器
        mock_oss_manager = MagicMock()
        mock_oss_manager.download_file.return_value = True
        mock_oss_manager_class.return_value = mock_oss_manager
        
        doc = Document()
        result_path = doc.download_file_from_oss("nutrition/test.pdf")
        
        # 验证结果
        self.assertEqual(result_path, '/tmp/test_download.pdf')
        
        # 验证调用
        mock_oss_manager.download_file.assert_called_once_with(
            "nutrition/test.pdf", 
            '/tmp/test_download.pdf'
        )
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.OSSManager')
    def test_download_file_from_oss_failure(self, mock_oss_manager_class):
        """测试从OSS下载文件失败"""
        from RAGExtension import Document
        
        # 模拟OSS管理器下载失败
        mock_oss_manager = MagicMock()
        mock_oss_manager.download_file.return_value = False
        mock_oss_manager_class.return_value = mock_oss_manager
        
        doc = Document()
        result_path = doc.download_file_from_oss("nutrition/nonexistent.pdf")
        
        # 应该返回None
        self.assertIsNone(result_path)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.OSSManager')
    def test_upload_parsed_content_to_oss(self, mock_oss_manager_class):
        """测试上传解析内容到OSS"""
        from RAGExtension import Document
        
        # 模拟OSS管理器
        mock_oss_manager = MagicMock()
        mock_oss_manager.upload_string_as_file.return_value = True
        mock_oss_manager_class.return_value = mock_oss_manager
        
        doc = Document()
        test_content = "这是测试解析内容"
        filename = "test_paper.pdf"
        
        result = doc.upload_parsed_content_to_oss(test_content, filename)
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证调用
        mock_oss_manager.upload_string_as_file.assert_called_once()
        call_args = mock_oss_manager.upload_string_as_file.call_args
        
        # 验证OSS键名
        self.assertEqual(call_args[0][1], "parsed_content/test_paper.md")
        
        # 验证内容包含原始信息
        uploaded_content = call_args[0][0]
        self.assertIn("test_paper.pdf", uploaded_content)
        self.assertIn(test_content, uploaded_content)


class TestDocumentContentFilter(unittest.TestCase):
    """测试Document类的内容过滤功能"""
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.download_file_from_oss')
    @patch('RAGExtension.Document._Document__doc_analysation')
    @patch('RAGExtension.Document.file_Parsing')
    @patch('RAGExtension.Document.upload_parsed_content_to_oss')
    @patch('RAGExtension.Document._vectorize_and_store_segments')
    @patch('RAGExtension.OpenAI')
    def test_content_filter_with_oss_file(self, mock_openai, mock_vectorize, mock_upload, 
                                         mock_file_parsing, mock_doc_analysis, mock_download):
        """测试使用OSS文件的内容过滤"""
        from RAGExtension import Document
        
        # 模拟下载文件
        mock_download.return_value = '/tmp/downloaded_file.pdf'
        
        # 模拟文档解析
        mock_doc_analysis.return_value = {"test": "data"}
        mock_file_parsing.return_value = "这是测试文档内容，包含营养建议和健康指导。"
        
        # 模拟OpenAI客户端
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "营养建议段落1;;健康指导段落2;;膳食建议段落3"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # 模拟上传和向量化
        mock_upload.return_value = True
        mock_vectorize.return_value = None
        
        doc = Document()
        
        # 使用OSS文件进行内容过滤
        result = doc.content_filter("nutrition/test_paper.pdf", is_oss_key=True)
        
        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "营养建议段落1")
        self.assertEqual(result[1], "健康指导段落2")
        self.assertEqual(result[2], "膳食建议段落3")
        
        # 验证调用
        mock_download.assert_called_once_with("nutrition/test_paper.pdf")
        mock_doc_analysis.assert_called_once_with('/tmp/downloaded_file.pdf')
        mock_file_parsing.assert_called_once_with('/tmp/downloaded_file.pdf')
        mock_upload.assert_called_once()
        mock_vectorize.assert_called_once_with(result)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.download_file_from_oss')
    def test_content_filter_oss_download_failure(self, mock_download):
        """测试OSS文件下载失败的情况"""
        from RAGExtension import Document
        
        # 模拟下载失败
        mock_download.return_value = None
        
        doc = Document()
        result = doc.content_filter("nutrition/nonexistent.pdf", is_oss_key=True)
        
        # 应该返回空列表
        self.assertEqual(result, [])


class TestDocumentFile2VectorDB(unittest.TestCase):
    """测试Document类的file2VectorDB OSS功能"""
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.content_filter')
    @patch('RAGExtension.FileIndexManager')
    def test_file2vectordb_with_oss_success(self, mock_file_manager_class, mock_content_filter):
        """测试使用OSS文件的向量化成功"""
        from RAGExtension import Document
        
        # 模拟内容过滤成功
        mock_content_filter.return_value = ["段落1", "段落2", "段落3"]
        
        # 模拟文件管理器
        mock_file_manager = MagicMock()
        mock_file_manager.update_vectorization_status.return_value = True
        mock_file_manager_class.return_value = mock_file_manager
        
        doc = Document()
        result = doc.file2VectorDB(
            "nutrition/test.pdf", 
            use_content_filter=True, 
            is_oss_key=True, 
            update_index=True
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证调用
        mock_content_filter.assert_called_once_with("nutrition/test.pdf", is_oss_key=True)
        mock_file_manager.update_vectorization_status.assert_called_once_with("test.pdf", True)
    
    @patch.dict(os.environ, {
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'DASHSCOPE_API_KEY': 'test_dashscope_key',
        'ALIBABA_QWEN_API_KEY': 'test_qwen_key',
        'DASH_VECTOR_API': 'test_vector_key'
    })
    @patch('RAGExtension.Document.content_filter')
    @patch('RAGExtension.Document.download_file_from_oss')
    @patch('RAGExtension.Document._Document__doc_analysation')
    @patch('RAGExtension.Document._Document__content_vectorised')
    @patch('RAGExtension.dashvector.Client')
    @patch('RAGExtension.FileIndexManager')
    def test_file2vectordb_fallback_to_original(self, mock_file_manager_class, mock_dashvector, 
                                               mock_content_vectorised, mock_doc_analysis, 
                                               mock_download, mock_content_filter):
        """测试回退到原始方法"""
        from RAGExtension import Document
        
        # 模拟内容过滤失败
        mock_content_filter.return_value = []
        
        # 模拟下载成功
        mock_download.return_value = '/tmp/downloaded.pdf'
        
        # 模拟原始方法
        mock_doc_analysis.return_value = {"test": "data"}
        mock_content_vectorised.return_value = [("文本1", [0.1, 0.2]), ("文本2", [0.3, 0.4])]
        
        # 模拟向量数据库
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_collection.insert.return_value = True
        mock_client.get.return_value = mock_collection
        mock_dashvector.return_value = mock_client
        
        # 模拟文件管理器
        mock_file_manager = MagicMock()
        mock_file_manager.update_vectorization_status.return_value = True
        mock_file_manager_class.return_value = mock_file_manager
        
        doc = Document()
        result = doc.file2VectorDB(
            "nutrition/test.pdf", 
            use_content_filter=True, 
            is_oss_key=True, 
            update_index=True
        )
        
        # 验证结果
        self.assertTrue(result)
        
        # 验证回退到原始方法
        mock_download.assert_called_once_with("nutrition/test.pdf")
        mock_doc_analysis.assert_called_once_with('/tmp/downloaded.pdf')
        mock_content_vectorised.assert_called_once()
        
        # 验证向量数据库插入
        self.assertEqual(mock_collection.insert.call_count, 2)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentOSSMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentContentFilter))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentFile2VectorDB))
    
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
