"""
RAG索引功能的pytest测试
基于原始的test_index.py重构
"""

import pytest
import json
import os
from pathlib import Path


class TestRAGIndex:
    """RAG索引功能测试类"""
    
    def test_file_export_success(self, sample_pdf_file, mock_context):
        """测试文件导出功能 - 成功案例"""
        if not sample_pdf_file:
            pytest.skip("测试PDF文件不存在")
        
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileExport", 
            "query": {"file_path": sample_pdf_file}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 200
    
    def test_file_analysis_success(self, sample_pdf_file, mock_context):
        """测试文件分析功能 - 成功案例"""
        if not sample_pdf_file:
            pytest.skip("测试PDF文件不存在")
        
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileAnalysation", 
            "query": {"file_path": sample_pdf_file}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 200
    
    def test_retrieve_topk_success(self, mock_context):
        """测试检索TopK功能 - 成功案例"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "RetrieveTopK", 
            "query": {"user_query": "营养建议", "k": 3}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 200
    
    def test_file_export_missing_path(self, mock_context):
        """测试文件导出功能 - 缺少文件路径"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileExport", 
            "query": {}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_file_analysis_missing_path(self, mock_context):
        """测试文件分析功能 - 缺少文件路径"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileAnalysation", 
            "query": {}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_file_export_nonexistent_file(self, mock_context):
        """测试文件导出功能 - 文件不存在"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileExport", 
            "query": {"file_path": "nonexistent.pdf"}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_file_analysis_nonexistent_file(self, mock_context):
        """测试文件分析功能 - 文件不存在"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "FileAnalysation", 
            "query": {"file_path": "nonexistent.pdf"}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    @pytest.mark.parametrize("k_value,expected_status", [
        (None, 400),
        (0, 400),
        (-5, 400),
        ("abc", 400),
    ])
    def test_retrieve_topk_invalid_k(self, k_value, expected_status, mock_context):
        """测试检索TopK功能 - 无效的k参数"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "RetrieveTopK", 
            "query": {"user_query": "营养建议", "k": k_value}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == expected_status
    
    def test_retrieve_topk_missing_query(self, mock_context):
        """测试检索TopK功能 - 缺少查询参数"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "RetrieveTopK", 
            "query": {"k": 3}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_retrieve_topk_empty_query(self, mock_context):
        """测试检索TopK功能 - 空查询参数"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "RetrieveTopK", 
            "query": {"user_query": None, "k": 3}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_invalid_action(self, mock_context):
        """测试无效的action参数"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = json.dumps({
            "action": "InvalidAction", 
            "query": {}
        })
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 400
    
    def test_invalid_json_input(self, mock_context):
        """测试无效的JSON输入"""
        try:
            from index import handler
        except ImportError:
            pytest.skip("index模块不可用")
        
        event = "invalid_json_string"
        
        result = handler(event, mock_context)
        assert result["statusCode"] == 500
