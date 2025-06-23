#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXivAPI模块单元测试
测试arXivAPI.py中的OSS集成功能
"""

import unittest
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock, mock_open

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from arXivAPI import (
    fetch_papers_by_keyword, 
    parse_arxiv_xml, 
    download_pdf_to_oss,
    export_papers_by_keyword_to_oss,
    download_pdf
)


class TestArxivXMLParsing(unittest.TestCase):
    """测试arXiv XML解析功能"""
    
    def setUp(self):
        """测试前准备"""
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2024.12345v1</id>
        <title>Test Paper on Nutrition</title>
        <published>2024-01-20T10:30:00Z</published>
        <summary>This is a test paper about nutrition and health.</summary>
        <author>
            <name>John Doe</name>
        </author>
        <author>
            <name>Jane Smith</name>
        </author>
        <link title="pdf" href="http://arxiv.org/pdf/2024.12345v1.pdf"/>
    </entry>
    <entry>
        <id>http://arxiv.org/abs/2024.67890v1</id>
        <title>Another Test Paper</title>
        <published>2024-01-21T15:45:00Z</published>
        <summary>Another test paper for validation.</summary>
        <author>
            <name>Alice Johnson</name>
        </author>
        <link title="pdf" href="http://arxiv.org/pdf/2024.67890v1.pdf"/>
    </entry>
</feed>'''
    
    def test_parse_arxiv_xml(self):
        """测试XML解析功能"""
        papers = parse_arxiv_xml(self.sample_xml)
        
        self.assertEqual(len(papers), 2)
        
        # 测试第一篇论文
        paper1 = papers[0]
        self.assertEqual(paper1['title'], 'Test Paper on Nutrition')
        self.assertEqual(paper1['id'], '2024.12345v1')
        self.assertEqual(paper1['published'], '2024-01-20T10:30:00Z')
        self.assertEqual(paper1['summary'], 'This is a test paper about nutrition and health.')
        self.assertEqual(len(paper1['authors']), 2)
        self.assertIn('John Doe', paper1['authors'])
        self.assertIn('Jane Smith', paper1['authors'])
        self.assertEqual(paper1['pdf_url'], 'http://arxiv.org/pdf/2024.12345v1.pdf')
        
        # 测试第二篇论文
        paper2 = papers[1]
        self.assertEqual(paper2['title'], 'Another Test Paper')
        self.assertEqual(paper2['id'], '2024.67890v1')
        self.assertEqual(len(paper2['authors']), 1)
        self.assertEqual(paper2['authors'][0], 'Alice Johnson')
    
    def test_parse_arxiv_xml_no_pdf_link(self):
        """测试没有PDF链接的情况"""
        xml_no_pdf = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/2024.12345v1</id>
        <title>Test Paper</title>
        <published>2024-01-20T10:30:00Z</published>
        <summary>Test summary</summary>
        <author>
            <name>Test Author</name>
        </author>
    </entry>
</feed>'''
        
        papers = parse_arxiv_xml(xml_no_pdf)
        self.assertEqual(len(papers), 1)
        
        # 应该自动构建PDF URL
        paper = papers[0]
        self.assertEqual(paper['pdf_url'], 'https://arxiv.org/pdf/2024.12345v1.pdf')


class TestDownloadPDFToOSS(unittest.TestCase):
    """测试PDF下载到OSS功能"""
    
    @patch('arXivAPI.OSSManager')
    @patch('arXivAPI.FileIndexManager')
    @patch('arXivAPI.urllib.request.urlretrieve')
    @patch('arXivAPI.tempfile.NamedTemporaryFile')
    def test_download_pdf_to_oss_success(self, mock_tempfile, mock_urlretrieve, mock_file_manager_class, mock_oss_manager_class):
        """测试成功下载PDF到OSS"""
        # 设置模拟对象
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test_file.pdf'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        mock_oss_manager = MagicMock()
        mock_oss_manager.upload_file.return_value = True
        mock_oss_manager_class.return_value = mock_oss_manager
        
        mock_file_manager = MagicMock()
        mock_file_manager.file_exists_in_index.return_value = False
        mock_file_manager.add_file_record.return_value = True
        mock_file_manager_class.return_value = mock_file_manager
        
        # 测试下载
        pdf_url = "https://arxiv.org/pdf/2024.12345v1.pdf"
        success, oss_key, filename = download_pdf_to_oss(pdf_url)
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(oss_key, "nutrition/2024.12345v1.pdf")
        self.assertEqual(filename, "2024.12345v1.pdf")
        
        # 验证调用
        mock_urlretrieve.assert_called_once()
        mock_oss_manager.upload_file.assert_called_once()
        mock_file_manager.add_file_record.assert_called_once()
    
    @patch('arXivAPI.OSSManager')
    @patch('arXivAPI.FileIndexManager')
    def test_download_pdf_to_oss_file_exists(self, mock_file_manager_class, mock_oss_manager_class):
        """测试文件已存在的情况"""
        mock_file_manager = MagicMock()
        mock_file_manager.file_exists_in_index.return_value = True
        mock_file_manager_class.return_value = mock_file_manager
        
        pdf_url = "https://arxiv.org/pdf/2024.12345v1.pdf"
        success, oss_key, filename = download_pdf_to_oss(pdf_url)
        
        # 应该跳过下载
        self.assertTrue(success)
        self.assertEqual(oss_key, "nutrition/2024.12345v1.pdf")
        self.assertEqual(filename, "2024.12345v1.pdf")
    
    def test_download_pdf_to_oss_invalid_url(self):
        """测试无效URL的情况"""
        success, oss_key, filename = download_pdf_to_oss(None)
        
        self.assertFalse(success)
        self.assertIsNone(oss_key)
        self.assertIsNone(filename)
    
    @patch('arXivAPI.OSSManager')
    @patch('arXivAPI.FileIndexManager')
    @patch('arXivAPI.urllib.request.urlretrieve')
    @patch('arXivAPI.tempfile.NamedTemporaryFile')
    def test_download_pdf_to_oss_upload_failure(self, mock_tempfile, mock_urlretrieve, mock_file_manager_class, mock_oss_manager_class):
        """测试上传失败的情况"""
        # 设置模拟对象
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test_file.pdf'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        mock_oss_manager = MagicMock()
        mock_oss_manager.upload_file.return_value = False  # 上传失败
        mock_oss_manager_class.return_value = mock_oss_manager
        
        mock_file_manager = MagicMock()
        mock_file_manager.file_exists_in_index.return_value = False
        mock_file_manager_class.return_value = mock_file_manager
        
        pdf_url = "https://arxiv.org/pdf/2024.12345v1.pdf"
        success, oss_key, filename = download_pdf_to_oss(pdf_url)
        
        # 应该返回失败
        self.assertFalse(success)
        self.assertIsNone(oss_key)
        self.assertEqual(filename, "2024.12345v1.pdf")


class TestExportPapersToOSS(unittest.TestCase):
    """测试批量导出论文到OSS功能"""
    
    @patch('arXivAPI.fetch_papers_by_keyword')
    @patch('arXivAPI.download_pdf_to_oss')
    def test_export_papers_by_keyword_to_oss_success(self, mock_download, mock_fetch):
        """测试成功导出论文到OSS"""
        # 模拟搜索结果
        mock_papers = [
            {
                'title': 'Test Paper 1',
                'authors': ['Author 1'],
                'published': '2024-01-20',
                'pdf_url': 'https://arxiv.org/pdf/2024.12345v1.pdf',
                'id': '2024.12345v1'
            },
            {
                'title': 'Test Paper 2',
                'authors': ['Author 2'],
                'published': '2024-01-21',
                'pdf_url': 'https://arxiv.org/pdf/2024.67890v1.pdf',
                'id': '2024.67890v1'
            }
        ]
        mock_fetch.return_value = mock_papers
        
        # 模拟下载成功
        mock_download.side_effect = [
            (True, 'nutrition/2024.12345v1.pdf', '2024.12345v1.pdf'),
            (True, 'nutrition/2024.67890v1.pdf', '2024.67890v1.pdf')
        ]
        
        # 执行导出
        result = export_papers_by_keyword_to_oss("nutrition", k=2)
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Test Paper 1')
        self.assertEqual(result[0]['oss_key'], 'nutrition/2024.12345v1.pdf')
        self.assertEqual(result[1]['title'], 'Test Paper 2')
        self.assertEqual(result[1]['oss_key'], 'nutrition/2024.67890v1.pdf')
        
        # 验证调用
        mock_fetch.assert_called_once_with("nutrition", max_results=2)
        self.assertEqual(mock_download.call_count, 2)
    
    @patch('arXivAPI.fetch_papers_by_keyword')
    def test_export_papers_by_keyword_to_oss_no_results(self, mock_fetch):
        """测试没有搜索结果的情况"""
        mock_fetch.return_value = []
        
        result = export_papers_by_keyword_to_oss("nonexistent_topic", k=5)
        
        self.assertEqual(len(result), 0)
    
    @patch('arXivAPI.fetch_papers_by_keyword')
    @patch('arXivAPI.download_pdf_to_oss')
    def test_export_papers_by_keyword_to_oss_partial_failure(self, mock_download, mock_fetch):
        """测试部分下载失败的情况"""
        # 模拟搜索结果
        mock_papers = [
            {
                'title': 'Success Paper',
                'authors': ['Author 1'],
                'published': '2024-01-20',
                'pdf_url': 'https://arxiv.org/pdf/success.pdf',
                'id': 'success'
            },
            {
                'title': 'Failure Paper',
                'authors': ['Author 2'],
                'published': '2024-01-21',
                'pdf_url': 'https://arxiv.org/pdf/failure.pdf',
                'id': 'failure'
            }
        ]
        mock_fetch.return_value = mock_papers
        
        # 模拟一个成功一个失败
        mock_download.side_effect = [
            (True, 'nutrition/success.pdf', 'success.pdf'),
            (False, None, 'failure.pdf')
        ]
        
        result = export_papers_by_keyword_to_oss("test", k=2)
        
        # 应该只返回成功的论文
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Success Paper')
    
    @patch('arXivAPI.fetch_papers_by_keyword')
    @patch('arXivAPI.download_pdf_to_oss')
    def test_export_papers_by_keyword_to_oss_no_pdf_url(self, mock_download, mock_fetch):
        """测试没有PDF URL的情况"""
        mock_papers = [
            {
                'title': 'No PDF Paper',
                'authors': ['Author 1'],
                'published': '2024-01-20',
                'pdf_url': None,  # 没有PDF URL
                'id': 'no_pdf'
            }
        ]
        mock_fetch.return_value = mock_papers
        
        result = export_papers_by_keyword_to_oss("test", k=1)
        
        # 应该跳过没有PDF URL的论文
        self.assertEqual(len(result), 0)
        mock_download.assert_not_called()


class TestDownloadPDFLegacy(unittest.TestCase):
    """测试传统PDF下载功能（兼容性测试）"""
    
    @patch('arXivAPI.get_download_path')
    @patch('arXivAPI.urllib.request.urlretrieve')
    @patch('arXivAPI.os.makedirs')
    def test_download_pdf_success(self, mock_makedirs, mock_urlretrieve, mock_get_path):
        """测试成功下载PDF到本地"""
        mock_get_path.return_value = '/test/download/path'
        
        pdf_url = "https://arxiv.org/pdf/2024.12345v1.pdf"
        result = download_pdf(pdf_url)
        
        expected_path = '/test/download/path/2024.12345v1.pdf'
        self.assertEqual(result, expected_path)
        
        mock_makedirs.assert_called_once_with('/test/download/path', exist_ok=True)
        mock_urlretrieve.assert_called_once_with(pdf_url, expected_path)
    
    def test_download_pdf_invalid_url(self):
        """测试无效URL的情况"""
        result = download_pdf(None)
        self.assertIsNone(result)
        
        result = download_pdf("")
        self.assertIsNone(result)
    
    @patch('arXivAPI.get_download_path')
    @patch('arXivAPI.urllib.request.urlretrieve')
    @patch('arXivAPI.os.makedirs')
    def test_download_pdf_custom_directory(self, mock_makedirs, mock_urlretrieve, mock_get_path):
        """测试使用自定义目录下载"""
        custom_dir = '/custom/download/path'
        pdf_url = "https://arxiv.org/pdf/test.pdf"
        
        result = download_pdf(pdf_url, save_dir=custom_dir)
        
        expected_path = '/custom/download/path/test.pdf'
        self.assertEqual(result, expected_path)
        
        mock_makedirs.assert_called_once_with(custom_dir, exist_ok=True)
        mock_urlretrieve.assert_called_once_with(pdf_url, expected_path)
        # 不应该调用get_download_path
        mock_get_path.assert_not_called()


class TestArxivAPIIntegration(unittest.TestCase):
    """测试arXivAPI集成功能"""
    
    @patch('arXivAPI.urllib.request.urlopen')
    def test_fetch_papers_by_keyword_integration(self, mock_urlopen):
        """测试关键词搜索集成"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.return_value = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>http://arxiv.org/abs/test.123v1</id>
        <title>Integration Test Paper</title>
        <published>2024-01-20T10:30:00Z</published>
        <summary>Test summary for integration</summary>
        <author>
            <name>Test Author</name>
        </author>
        <link title="pdf" href="http://arxiv.org/pdf/test.123v1.pdf"/>
    </entry>
</feed>'''.encode('utf-8')
        
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # 执行搜索
        papers = fetch_papers_by_keyword("nutrition", max_results=1)
        
        # 验证结果
        self.assertEqual(len(papers), 1)
        paper = papers[0]
        self.assertEqual(paper['title'], 'Integration Test Paper')
        self.assertEqual(paper['id'], 'test.123v1')
        self.assertEqual(paper['pdf_url'], 'http://arxiv.org/pdf/test.123v1.pdf')


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestArxivXMLParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadPDFToOSS))
    suite.addTests(loader.loadTestsFromTestCase(TestExportPapersToOSS))
    suite.addTests(loader.loadTestsFromTestCase(TestDownloadPDFLegacy))
    suite.addTests(loader.loadTestsFromTestCase(TestArxivAPIIntegration))
    
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
