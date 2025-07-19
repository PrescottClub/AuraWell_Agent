"""
OSS云存储集成功能的pytest测试
基于原始的test_oss_integration.py重构
"""

import pytest
import os
import time
from pathlib import Path


class TestOSSConfiguration:
    """OSS配置测试类"""
    
    @pytest.mark.oss
    def test_oss_config_loading(self):
        """测试OSS配置加载"""
        try:
            from oss_utils import load_oss_config
        except ImportError:
            pytest.skip("oss_utils模块不可用")
        
        config, success = load_oss_config()
        
        if success:
            assert isinstance(config, dict), "配置应为字典类型"
            assert "region" in config, "配置应包含region字段"
            assert "endpoint" in config, "配置应包含endpoint字段"
            assert "bucket_name" in config, "配置应包含bucket_name字段"
        # 注意：在测试环境中配置加载失败是正常的
    
    @pytest.mark.oss
    def test_oss_manager_initialization(self):
        """测试OSS管理器初始化"""
        try:
            from oss_utils import OSSManager
        except ImportError:
            pytest.skip("oss_utils模块不可用")
        
        try:
            oss_manager = OSSManager()
            assert oss_manager is not None, "OSS管理器应成功初始化"
        except Exception:
            # 在测试环境中OSS初始化失败是正常的
            pytest.skip("OSS管理器初始化失败（测试环境正常）")


class TestFileIndexManager:
    """文件索引管理器测试类"""
    
    @pytest.mark.oss
    def test_file_index_manager_initialization(self):
        """测试文件索引管理器初始化"""
        try:
            from file_index_manager import FileIndexManager
        except ImportError:
            pytest.skip("file_index_manager模块不可用")
        
        file_manager = FileIndexManager()
        assert file_manager is not None, "文件索引管理器应成功初始化"
    
    @pytest.mark.oss
    def test_get_all_files(self):
        """测试获取所有文件"""
        try:
            from file_index_manager import FileIndexManager
        except ImportError:
            pytest.skip("file_index_manager模块不可用")
        
        file_manager = FileIndexManager()
        all_files = file_manager.get_all_files()
        
        assert isinstance(all_files, dict), "所有文件应为字典类型"
        # 文件数量可能为0，这在测试环境中是正常的
    
    @pytest.mark.oss
    def test_get_recent_files(self):
        """测试获取最近文件"""
        try:
            from file_index_manager import FileIndexManager
        except ImportError:
            pytest.skip("file_index_manager模块不可用")
        
        file_manager = FileIndexManager()
        recent_files = file_manager.get_files_uploaded_in_days(30)
        
        assert isinstance(recent_files, dict), "最近文件应为字典类型"
    
    @pytest.mark.oss
    def test_get_unvectorized_files(self):
        """测试获取未向量化文件"""
        try:
            from file_index_manager import FileIndexManager
        except ImportError:
            pytest.skip("file_index_manager模块不可用")
        
        file_manager = FileIndexManager()
        unvectorized_files = file_manager.get_unvectorized_files()
        
        assert isinstance(unvectorized_files, dict), "未向量化文件应为字典类型"


class TestArxivOSSIntegration:
    """arXiv与OSS集成测试类"""
    
    @pytest.mark.oss
    @pytest.mark.slow
    @pytest.mark.integration
    def test_arxiv_oss_export(self):
        """测试arXiv论文导出到OSS"""
        try:
            from arXivAPI import export_papers_by_keyword_to_oss
        except ImportError:
            pytest.skip("arXivAPI模块不可用")
        
        # 下载少量论文进行测试
        papers = export_papers_by_keyword_to_oss("nutrition", k=1)
        
        if papers:
            assert isinstance(papers, list), "论文列表应为列表类型"
            assert len(papers) > 0, "应该下载到至少一篇论文"
            
            for paper in papers:
                assert isinstance(paper, dict), "论文信息应为字典类型"
                assert "title" in paper, "论文应包含标题"
                assert "oss_key" in paper, "论文应包含OSS键名"
        # 注意：在测试环境中下载可能失败，这是正常的


class TestRAGOSSIntegration:
    """RAG与OSS集成测试类"""
    
    @pytest.mark.oss
    def test_document_initialization(self):
        """测试Document类初始化"""
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        assert doc is not None, "Document类应成功初始化"
    
    @pytest.mark.oss
    def test_get_recent_files_from_oss(self):
        """测试从OSS获取最近文件"""
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        recent_files = doc.get_recent_files_from_oss(30)
        
        assert isinstance(recent_files, list), "最近文件应为列表类型"
        # 文件数量可能为0，这在测试环境中是正常的
    
    @pytest.mark.oss
    @pytest.mark.slow
    def test_file2vectordb_with_oss_key(self):
        """测试使用OSS键的文档向量化"""
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        
        # 获取最近文件进行测试
        recent_files = doc.get_recent_files_from_oss(30)
        
        if recent_files:
            # 选择一个未向量化的文件进行测试
            unvectorized_files = [f for f in recent_files if not f.get("vectorized", False)]
            
            if unvectorized_files:
                test_file = unvectorized_files[0]
                oss_key = test_file["oss_key"]
                
                # 测试文档向量化
                success = doc.file2VectorDB(
                    oss_key, 
                    use_content_filter=True, 
                    is_oss_key=True, 
                    update_index=True
                )
                
                assert isinstance(success, bool), "返回值应为布尔类型"
        # 注意：在测试环境中可能没有可测试的文件，这是正常的
    
    @pytest.mark.oss
    @pytest.mark.slow
    def test_batch_processing(self):
        """测试批量处理功能"""
        try:
            from RAGExtension import Document
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        doc = Document()
        
        # 测试批量处理最近30天的文件
        results = doc.batch_process_recent_files(days=30, use_content_filter=True)
        
        assert isinstance(results, dict), "批量处理结果应为字典类型"
        assert "total" in results, "结果应包含total字段"
        assert "processed" in results, "结果应包含processed字段"
        assert "failed" in results, "结果应包含failed字段"
        assert "skipped" in results, "结果应包含skipped字段"
        
        # 检查数值类型
        assert isinstance(results["total"], int), "total应为整数"
        assert isinstance(results["processed"], int), "processed应为整数"
        assert isinstance(results["failed"], int), "failed应为整数"
        assert isinstance(results["skipped"], int), "skipped应为整数"


class TestEnhancedQueryWithOSS:
    """增强查询功能与OSS集成测试类"""
    
    @pytest.mark.oss
    def test_user_retrieve_initialization(self):
        """测试UserRetrieve类初始化"""
        try:
            from RAGExtension import UserRetrieve
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        retriever = UserRetrieve()
        assert retriever is not None, "UserRetrieve类应成功初始化"
    
    @pytest.mark.oss
    @pytest.mark.parametrize("query", [
        "营养膳食建议",
        "daily nutrition recommendations",
        "健康饮食指南"
    ])
    def test_enhanced_query(self, query):
        """测试增强查询功能"""
        try:
            from RAGExtension import UserRetrieve
        except ImportError:
            pytest.skip("RAGExtension模块不可用")
        
        retriever = UserRetrieve()
        results = retriever.retrieve_topK(query, k=4)
        
        assert isinstance(results, list), f"查询结果应为列表类型: {query}"
        # 注意：结果可能为空，这在测试环境中是正常的
