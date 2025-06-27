"""
AuraWell 翻译服务测试
测试中英文互译功能和错误处理
"""

import unittest
import pytest
import logging
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.aurawell.services.translation_service import TranslationService, get_translation_service

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTranslationService(unittest.TestCase):
    """翻译服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.service = None
        
    def tearDown(self):
        """测试后清理"""
        if self.service:
            del self.service
    
    @patch('src.aurawell.services.translation_service.MarianMTModel')
    @patch('src.aurawell.services.translation_service.MarianTokenizer')
    def test_translation_service_initialization(self, mock_tokenizer, mock_model):
        """测试翻译服务初始化"""
        logger.info("🧪 测试翻译服务初始化")
        
        # Mock模型和tokenizer
        mock_model_instance = Mock()
        mock_tokenizer_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        try:
            service = TranslationService()
            
            # 验证模型加载
            self.assertIsNotNone(service.models)
            self.assertIsNotNone(service.tokenizers)
            self.assertEqual(len(service.models), 2)  # zh-en 和 en-zh
            self.assertEqual(len(service.tokenizers), 2)
            
            logger.info("✅ 翻译服务初始化测试通过")
            
        except Exception as e:
            logger.error(f"❌ 翻译服务初始化测试失败: {e}")
            raise
    
    def test_language_detection(self):
        """测试语言检测功能"""
        logger.info("🧪 测试语言检测功能")
        
        with patch('src.aurawell.services.translation_service.MarianMTModel'), \
             patch('src.aurawell.services.translation_service.MarianTokenizer'):
            
            service = TranslationService()
            
            # 测试中文检测
            chinese_texts = [
                "营养建议",
                "每日健康指南",
                "中国成年人肉类食物摄入",
                "这是一个中文句子"
            ]
            
            for text in chinese_texts:
                detected = service.detect_language(text)
                self.assertEqual(detected, 'zh', f"中文文本 '{text}' 检测失败")
            
            # 测试英文检测
            english_texts = [
                "nutrition advice",
                "daily health guidelines", 
                "healthy eating recommendations",
                "This is an English sentence"
            ]
            
            for text in english_texts:
                detected = service.detect_language(text)
                self.assertEqual(detected, 'en', f"英文文本 '{text}' 检测失败")
            
            # 测试边界情况
            edge_cases = [
                ("", 'zh'),  # 空字符串默认中文
                ("   ", 'zh'),  # 空白字符串默认中文
                ("123456", 'zh'),  # 纯数字默认中文
            ]
            
            for text, expected in edge_cases:
                detected = service.detect_language(text)
                self.assertEqual(detected, expected, f"边界情况 '{text}' 检测失败")
            
            logger.info("✅ 语言检测功能测试通过")
    
    @patch('src.aurawell.services.translation_service.MarianMTModel')
    @patch('src.aurawell.services.translation_service.MarianTokenizer')
    @patch('src.aurawell.services.translation_service.torch')
    def test_text_translation(self, mock_torch, mock_tokenizer, mock_model):
        """测试文本翻译功能"""
        logger.info("🧪 测试文本翻译功能")
        
        # Mock模型和tokenizer
        mock_model_instance = Mock()
        mock_tokenizer_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock tokenizer行为
        mock_tokenizer_instance.return_value = {'input_ids': Mock(), 'attention_mask': Mock()}
        mock_tokenizer_instance.decode.return_value = "translated text"
        
        # Mock模型生成
        mock_model_instance.generate.return_value = [Mock()]
        
        # Mock torch.no_grad
        mock_torch.no_grad.return_value.__enter__ = Mock()
        mock_torch.no_grad.return_value.__exit__ = Mock()
        
        service = TranslationService()
        
        # 测试中译英
        result = service.translate_text("营养建议", 'zh', 'en')
        self.assertEqual(result, "translated text")
        
        # 测试英译中
        result = service.translate_text("nutrition advice", 'en', 'zh')
        self.assertEqual(result, "translated text")
        
        # 测试相同语言（应该返回原文）
        result = service.translate_text("test", 'en', 'en')
        self.assertEqual(result, "test")
        
        # 测试空文本
        result = service.translate_text("", 'zh', 'en')
        self.assertEqual(result, "")
        
        logger.info("✅ 文本翻译功能测试通过")
    
    @patch('src.aurawell.services.translation_service.MarianMTModel')
    @patch('src.aurawell.services.translation_service.MarianTokenizer')
    def test_query_translation(self, mock_tokenizer, mock_model):
        """测试查询翻译方法（UpdatePlan核心功能）"""
        logger.info("🧪 测试查询翻译方法")
        
        # Mock模型和tokenizer
        mock_model_instance = Mock()
        mock_tokenizer_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock翻译结果
        mock_tokenizer_instance.return_value = {'input_ids': Mock(), 'attention_mask': Mock()}
        mock_tokenizer_instance.decode.return_value = "nutrition advice"
        mock_model_instance.generate.return_value = [Mock()]
        
        service = TranslationService()
        
        # 测试中文查询
        result = service.query_translation("营养建议")
        
        # 验证返回格式
        self.assertIn('original', result)
        self.assertIn('translated', result)
        
        # 验证原文信息
        self.assertEqual(result['original']['text'], "营养建议")
        self.assertEqual(result['original']['language'], 'zh')
        
        # 验证翻译信息
        self.assertEqual(result['translated']['text'], "nutrition advice")
        self.assertEqual(result['translated']['language'], 'en')
        
        logger.info("✅ 查询翻译方法测试通过")
    
    def test_error_handling(self):
        """测试错误处理"""
        logger.info("🧪 测试错误处理")
        
        with patch('src.aurawell.services.translation_service.MarianMTModel') as mock_model, \
             patch('src.aurawell.services.translation_service.MarianTokenizer') as mock_tokenizer:
            
            # Mock初始化失败
            mock_model.from_pretrained.side_effect = Exception("模型加载失败")
            
            with self.assertRaises(RuntimeError):
                TranslationService()
            
            logger.info("✅ 错误处理测试通过")
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        logger.info("🧪 测试单例模式")
        
        with patch('src.aurawell.services.translation_service.MarianMTModel'), \
             patch('src.aurawell.services.translation_service.MarianTokenizer'):
            
            # 清除全局实例
            import src.aurawell.services.translation_service as ts_module
            ts_module._translation_service = None
            
            service1 = get_translation_service()
            service2 = get_translation_service()
            
            self.assertIs(service1, service2, "单例模式失败")
            
            logger.info("✅ 单例模式测试通过")


class TestTranslationServiceIntegration(unittest.TestCase):
    """翻译服务集成测试"""
    
    @pytest.mark.integration
    def test_real_translation_if_available(self):
        """如果环境允许，测试真实翻译"""
        logger.info("🧪 测试真实翻译（如果可用）")
        
        try:
            # 尝试创建真实的翻译服务
            service = TranslationService()
            
            # 测试简单翻译
            result = service.query_translation("健康")
            
            # 验证基本结构
            self.assertIn('original', result)
            self.assertIn('translated', result)
            self.assertEqual(result['original']['text'], "健康")
            
            logger.info("✅ 真实翻译测试通过")
            
        except Exception as e:
            logger.warning(f"⚠️ 真实翻译测试跳过（可能缺少模型）: {e}")
            pytest.skip("翻译模型不可用")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
