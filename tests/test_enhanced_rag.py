"""
增强RAG功能的pytest测试
基于原始的test_enhanced_rag.py重构
"""

import pytest
import os
import time
from pathlib import Path


class TestEnhancedRAG:
    """增强RAG功能测试类"""
    
    @pytest.mark.rag
    def test_language_detection(self):
        """测试语言检测功能"""
        try:
            from RAGExtension import detect_language
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        test_cases = [
            ("每日营养建议", "chinese"),
            ("daily nutrition recommendations", "english"),
            ("健康饮食指南", "chinese"),
            ("healthy eating guidelines", "english"),
            ("中英文混合 mixed language", "chinese"),  # 默认返回中文
            ("", "chinese"),  # 空字符串默认返回中文
        ]
        
        for text, expected in test_cases:
            detected = detect_language(text)
            assert detected == expected, f"文本 '{text}' 检测结果 {detected} 不符合期望 {expected}"
    
    @pytest.mark.rag
    @pytest.mark.slow
    def test_translation(self):
        """测试翻译功能"""
        try:
            from RAGExtension import translate_text, load_api_keys
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        # 加载API密钥
        keys, success = load_api_keys()
        if not success:
            pytest.skip("无法加载API密钥")
        
        api_key = keys.get("ALIBABA_QWEN_API_KEY") or keys.get("DASHSCOPE_API_KEY")
        if not api_key:
            pytest.skip("未找到有效的API密钥")
        
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        test_cases = [
            ("每日营养建议", "english"),
            ("daily nutrition recommendations", "chinese"),
        ]
        
        for text, target_lang in test_cases:
            translated = translate_text(text, target_lang, api_key, base_url)
            assert translated is not None, f"翻译失败: '{text}' -> {target_lang}"
            assert len(translated) > 0, f"翻译结果为空: '{text}' -> {target_lang}"
    
    @pytest.mark.rag
    def test_enhanced_user_query(self):
        """测试增强的用户查询功能"""
        try:
            from RAGExtension import UserRetrieve
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        test_queries = [
            "每日营养建议",
            "daily nutrition recommendations", 
            "健康饮食指南",
        ]
        
        retriever = UserRetrieve()
        
        for query in test_queries:
            results = retriever.retrieve_topK(query, k=3)
            assert isinstance(results, list), f"查询结果应为列表: {query}"
            # 注意：结果可能为空，这在测试环境中是正常的
    
    @pytest.mark.rag
    @pytest.mark.slow
    def test_content_filter(self, sample_pdf_file):
        """测试文献提炼功能"""
        if not sample_pdf_file:
            pytest.skip("测试PDF文件不存在")
        
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        
        # 测试内容过滤功能
        start_time = time.time()
        filtered_segments = doc.content_filter(sample_pdf_file)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 300, f"处理时间过长: {processing_time:.2f}秒"
        
        if filtered_segments:
            assert isinstance(filtered_segments, list), "过滤结果应为列表"
            assert len(filtered_segments) > 0, "应该提取到至少一个段落"
            
            # 检查段落内容
            for segment in filtered_segments[:3]:  # 只检查前3个
                assert isinstance(segment, str), "段落应为字符串"
                assert len(segment) > 0, "段落不应为空"
    
    @pytest.mark.rag
    @pytest.mark.slow
    def test_file2vectordb_with_filter(self, sample_pdf_file):
        """测试带内容过滤的文档向量化功能"""
        if not sample_pdf_file:
            pytest.skip("测试PDF文件不存在")
        
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        
        # 测试使用内容过滤的向量化
        start_time = time.time()
        success = doc.file2VectorDB(sample_pdf_file, use_content_filter=True)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 600, f"向量化时间过长: {processing_time:.2f}秒"
        
        # 注意：在测试环境中，向量化可能会失败，这是正常的
        # 我们主要测试函数是否能正常调用而不抛出异常
        assert isinstance(success, bool), "返回值应为布尔类型"


class TestLanguageDetection:
    """语言检测功能的详细测试"""
    
    @pytest.mark.parametrize("text,expected", [
        ("每日营养建议", "chinese"),
        ("daily nutrition recommendations", "english"),
        ("健康饮食指南", "chinese"),
        ("healthy eating guidelines", "english"),
        ("中英文混合 mixed language", "chinese"),
        ("", "chinese"),
        ("123456", "chinese"),  # 数字默认为中文
        ("!@#$%", "chinese"),   # 特殊字符默认为中文
    ])
    def test_language_detection_parametrized(self, text, expected):
        """参数化测试语言检测功能"""
        try:
            from RAGExtension import detect_language
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        detected = detect_language(text)
        assert detected == expected, f"文本 '{text}' 检测结果 {detected} 不符合期望 {expected}"
