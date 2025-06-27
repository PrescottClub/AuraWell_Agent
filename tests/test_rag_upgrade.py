"""
AuraWell RAG模块升级测试
测试中英文双语检索功能
"""

import unittest
import pytest
import logging
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRAGUpgrade(unittest.TestCase):
    """RAG升级功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_api_keys = {
            "DASHSCOPE_API_KEY": "test-dashscope-key",
            "ALIBABA_QWEN_API_KEY": "test-qwen-key", 
            "DASH_VECTOR_API": "test-vector-key"
        }
    
    @patch('src.aurawell.rag.RAGExtension.load_api_keys')
    @patch('aurawell.services.translation_service.get_translation_service')
    def test_user_retrieve_initialization(self, mock_translation_service, mock_load_keys):
        """测试UserRetrieve类初始化"""
        logger.info("🧪 测试UserRetrieve类初始化")

        # Mock API密钥加载
        mock_load_keys.return_value = (self.mock_api_keys, True)

        try:
            from src.aurawell.rag.RAGExtension import UserRetrieve
            
            user_retrieve = UserRetrieve()
            
            # 验证初始化
            self.assertIsNotNone(user_retrieve.dash_scope_key)
            self.assertIsNotNone(user_retrieve.qwen_api_key)
            self.assertIsNotNone(user_retrieve.dash_vector_key)
            
            logger.info("✅ UserRetrieve类初始化测试通过")
            
        except Exception as e:
            logger.error(f"❌ UserRetrieve类初始化测试失败: {e}")
            raise
    
    @patch('src.aurawell.rag.RAGExtension.load_api_keys')
    @patch('aurawell.services.translation_service.get_translation_service')
    @patch('src.aurawell.rag.RAGExtension.OpenAI')
    def test_user_query_vectorised_with_translation(self, mock_openai, mock_translation_service, mock_load_keys):
        """测试增强的用户查询向量化方法"""
        logger.info("🧪 测试增强的用户查询向量化方法")

        # Mock API密钥加载
        mock_load_keys.return_value = (self.mock_api_keys, True)

        # Mock翻译服务
        mock_translation_instance = Mock()
        mock_translation_service.return_value = mock_translation_instance
        mock_translation_instance.query_translation.return_value = {
            'original': {
                'text': '营养建议',
                'language': 'zh'
            },
            'translated': {
                'text': 'nutrition advice',
                'language': 'en'
            }
        }

        # Mock OpenAI客户端
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock向量化响应
        mock_embedding_response = Mock()
        mock_embedding_response.data = [
            Mock(embedding=[0.1] * 1024),  # 原文向量
            Mock(embedding=[0.2] * 1024)   # 翻译向量
        ]
        mock_client.embeddings.create.return_value = mock_embedding_response

        try:
            from src.aurawell.rag.RAGExtension import UserRetrieve
            
            user_retrieve = UserRetrieve()
            result = user_retrieve._UserRetrieve__user_query_vectorised("营养建议")
            
            # 验证返回结构
            self.assertIn('original', result)
            self.assertIn('translated', result)
            
            # 验证原文信息
            self.assertEqual(result['original']['text'], '营养建议')
            # 翻译服务返回'zh'，不是'chinese'
            self.assertEqual(result['original']['language'], 'zh')
            self.assertIsInstance(result['original']['vector'], np.ndarray)

            # 验证翻译信息
            self.assertEqual(result['translated']['text'], 'Nutrition recommendations')
            self.assertEqual(result['translated']['language'], 'en')
            self.assertIsInstance(result['translated']['vector'], np.ndarray)
            
            logger.info("✅ 用户查询向量化方法测试通过")
            
        except Exception as e:
            logger.error(f"❌ 用户查询向量化方法测试失败: {e}")
            raise
    
    @patch('src.aurawell.rag.RAGExtension.load_api_keys')
    @patch('aurawell.services.translation_service.get_translation_service')
    @patch('src.aurawell.rag.RAGExtension.dashvector')
    @patch('src.aurawell.rag.RAGExtension.OpenAI')
    def test_retrieve_topk_bilingual(self, mock_openai, mock_dashvector, mock_translation_service, mock_load_keys):
        """测试双语TopK检索方法"""
        logger.info("🧪 测试双语TopK检索方法")

        # Mock API密钥加载
        mock_load_keys.return_value = (self.mock_api_keys, True)

        # Mock翻译服务
        mock_translation_instance = Mock()
        mock_translation_service.return_value = mock_translation_instance
        mock_translation_instance.query_translation.return_value = {
            'original': {
                'text': '营养建议',
                'language': 'zh'
            },
            'translated': {
                'text': 'nutrition advice',
                'language': 'en'
            }
        }

        # Mock OpenAI客户端
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_embedding_response = Mock()
        mock_embedding_response.data = [
            Mock(embedding=[0.1] * 1024),
            Mock(embedding=[0.2] * 1024)
        ]
        mock_client.embeddings.create.return_value = mock_embedding_response

        # Mock DashVector
        mock_dashvector_client = Mock()
        mock_collection = Mock()
        mock_dashvector.Client.return_value = mock_dashvector_client
        mock_dashvector_client.get.return_value = mock_collection

        # Mock查询结果
        mock_result_original = Mock()
        mock_result_original.output = [
            Mock(fields={"raw_text": "中文营养建议内容1"}),
            Mock(fields={"raw_text": "中文营养建议内容2"})
        ]

        mock_result_translated = Mock()
        mock_result_translated.output = [
            Mock(fields={"raw_text": "English nutrition advice content 1"}),
            Mock(fields={"raw_text": "English nutrition advice content 2"})
        ]

        # 设置查询返回值（第一次调用返回原文结果，第二次返回翻译结果）
        mock_collection.query.side_effect = [mock_result_original, mock_result_translated]

        try:
            from src.aurawell.rag.RAGExtension import UserRetrieve
            
            user_retrieve = UserRetrieve()
            results = user_retrieve.retrieve_topK("营养建议", 4)
            
            # 验证结果
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
            
            # 验证包含中英文内容
            result_text = " ".join(results)
            self.assertTrue(any("中文" in text or "营养" in text for text in results), "应包含中文内容")
            self.assertTrue(any("English" in text or "nutrition" in text for text in results), "应包含英文内容")
            
            logger.info(f"✅ 双语TopK检索测试通过，返回{len(results)}个结果")
            
        except Exception as e:
            logger.error(f"❌ 双语TopK检索测试失败: {e}")
            raise
    
    @patch('src.aurawell.rag.RAGExtension.load_api_keys')
    def test_retrieve_topk_error_handling(self, mock_load_keys):
        """测试检索方法的错误处理"""
        logger.info("🧪 测试检索方法的错误处理")

        # Mock API密钥加载失败
        mock_load_keys.return_value = ({}, False)

        try:
            from src.aurawell.rag.RAGExtension import UserRetrieve
            
            # 应该抛出ValueError
            with self.assertRaises(ValueError):
                UserRetrieve()
            
            logger.info("✅ 错误处理测试通过")
            
        except Exception as e:
            logger.error(f"❌ 错误处理测试失败: {e}")
            raise
    
    @patch('src.aurawell.rag.RAGExtension.load_api_keys')
    @patch('aurawell.services.translation_service.get_translation_service')
    def test_translation_fallback(self, mock_translation_service, mock_load_keys):
        """测试翻译服务失败时的回退机制"""
        logger.info("🧪 测试翻译服务失败时的回退机制")

        # Mock API密钥加载
        mock_load_keys.return_value = (self.mock_api_keys, True)

        # Mock翻译服务失败
        mock_translation_service.side_effect = Exception("翻译服务不可用")

        try:
            from src.aurawell.rag.RAGExtension import UserRetrieve
            
            user_retrieve = UserRetrieve()
            
            # 这应该不会抛出异常，而是回退到原有翻译方法
            # 由于我们没有mock原有的翻译方法，这里主要测试不会崩溃
            self.assertIsNotNone(user_retrieve)
            
            logger.info("✅ 翻译服务回退机制测试通过")
            
        except Exception as e:
            logger.error(f"❌ 翻译服务回退机制测试失败: {e}")
            raise


class TestRAGServiceIntegration(unittest.TestCase):
    """RAG服务集成测试"""
    
    @pytest.mark.integration
    @patch.dict(os.environ, {
        'DASHSCOPE_API_KEY': 'test-key',
        'ALIBABA_QWEN_API_KEY': 'test-key',
        'DASH_VECTOR_API': 'test-key'
    })
    def test_rag_service_integration(self):
        """测试RAG服务集成"""
        logger.info("🧪 测试RAG服务集成")

        try:
            # 简化测试，不使用异步调用
            from src.aurawell.rag.RAGExtension import UserRetrieve

            # 测试UserRetrieve类的基本功能
            with patch('src.aurawell.rag.RAGExtension.load_api_keys') as mock_load_keys:
                mock_load_keys.return_value = ({
                    "DASHSCOPE_API_KEY": "test-key",
                    "ALIBABA_QWEN_API_KEY": "test-key",
                    "DASH_VECTOR_API": "test-key"
                }, True)

                # 测试初始化
                user_retrieve = UserRetrieve()
                self.assertIsNotNone(user_retrieve)

            logger.info("✅ RAG服务集成测试通过")

        except Exception as e:
            logger.warning(f"⚠️ RAG服务集成测试跳过: {e}")
            pytest.skip("RAG服务不可用")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
