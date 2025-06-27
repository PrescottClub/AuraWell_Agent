"""
AuraWell 翻译服务模块
实现中英文互译功能，支持RAG模块的双语查询
"""

import logging
import os
from typing import Dict, Optional, Tuple
import torch
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect, DetectorFactory
import warnings

# 设置langdetect的随机种子以确保结果一致性
DetectorFactory.seed = 0

# 忽略transformers的警告
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

logger = logging.getLogger(__name__)


class TranslationService:
    """
    翻译服务类，提供中英文互译功能
    使用MarianMT轻量级翻译模型，支持CPU推理
    """
    
    def __init__(self):
        """初始化翻译服务"""
        self.device = "cpu"  # 使用CPU进行推理
        self.models = {}
        self.tokenizers = {}
        self._initialize_models()
        
    def _initialize_models(self):
        """初始化翻译模型"""
        try:
            logger.info("正在初始化翻译模型...")
            
            # 中译英模型
            zh_en_model_name = "Helsinki-NLP/opus-mt-zh-en"
            logger.info(f"加载中译英模型: {zh_en_model_name}")
            self.models['zh-en'] = MarianMTModel.from_pretrained(zh_en_model_name)
            self.tokenizers['zh-en'] = MarianTokenizer.from_pretrained(zh_en_model_name)
            
            # 英译中模型
            en_zh_model_name = "Helsinki-NLP/opus-mt-en-zh"
            logger.info(f"加载英译中模型: {en_zh_model_name}")
            self.models['en-zh'] = MarianMTModel.from_pretrained(en_zh_model_name)
            self.tokenizers['en-zh'] = MarianTokenizer.from_pretrained(en_zh_model_name)
            
            # 将模型移动到CPU
            for key in self.models:
                self.models[key].to(self.device)
                self.models[key].eval()  # 设置为评估模式
                
            logger.info("✅ 翻译模型初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 翻译模型初始化失败: {e}")
            raise RuntimeError(f"翻译模型初始化失败: {e}")
    
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text (str): 待检测的文本
            
        Returns:
            str: 语言代码 ('zh' 或 'en')
        """
        try:
            if not text or not text.strip():
                logger.warning("输入文本为空，默认返回中文")
                return 'zh'
                
            detected = detect(text)
            
            # 将检测结果映射到我们支持的语言
            if detected in ['zh-cn', 'zh', 'zh-tw']:
                return 'zh'
            elif detected == 'en':
                return 'en'
            else:
                # 对于其他语言，通过字符判断
                chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
                if chinese_chars > len(text) * 0.3:  # 如果中文字符超过30%
                    return 'zh'
                else:
                    return 'en'
                    
        except Exception as e:
            logger.warning(f"语言检测失败: {e}，默认返回中文")
            return 'zh'
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        翻译文本
        
        Args:
            text (str): 待翻译的文本
            source_lang (str): 源语言 ('zh' 或 'en')
            target_lang (str): 目标语言 ('zh' 或 'en')
            
        Returns:
            str: 翻译后的文本
        """
        try:
            if not text or not text.strip():
                logger.warning("输入文本为空")
                return text
                
            if source_lang == target_lang:
                logger.info("源语言和目标语言相同，直接返回原文")
                return text
                
            # 确定模型键
            if source_lang == 'zh' and target_lang == 'en':
                model_key = 'zh-en'
            elif source_lang == 'en' and target_lang == 'zh':
                model_key = 'en-zh'
            else:
                logger.error(f"不支持的翻译方向: {source_lang} -> {target_lang}")
                return text
                
            if model_key not in self.models:
                logger.error(f"翻译模型 {model_key} 未加载")
                return text
                
            # 执行翻译
            model = self.models[model_key]
            tokenizer = self.tokenizers[model_key]
            
            # 编码输入文本
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 生成翻译
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            
            # 解码输出
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"翻译成功: {text[:50]}... -> {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            # 记录错误到日志但不抛出异常，返回原文
            return text
    
    def query_translation(self, user_query: str) -> Dict[str, Dict[str, str]]:
        """
        查询翻译方法 - 实现UpdatePlan要求的核心功能
        
        Args:
            user_query (str): 用户查询文本
            
        Returns:
            Dict[str, Dict[str, str]]: 包含原文和翻译的字典
            格式: {
                "original": {"language": "zh/en", "text": "原文"},
                "translated": {"language": "en/zh", "text": "翻译"}
            }
        """
        try:
            if not user_query or not user_query.strip():
                logger.warning("查询文本为空")
                return {
                    "original": {"language": "zh", "text": ""},
                    "translated": {"language": "en", "text": ""}
                }
            
            # 1. 检测原查询语言
            detected_lang = self.detect_language(user_query)
            logger.info(f"检测到查询语言: {detected_lang}")
            
            # 2. 确定翻译目标语言
            if detected_lang == 'zh':
                target_lang = 'en'
            else:
                target_lang = 'zh'
            
            # 3. 执行翻译
            translated_text = self.translate_text(user_query, detected_lang, target_lang)
            
            # 4. 构造返回结果
            result = {
                "original": {
                    "language": detected_lang,
                    "text": user_query
                },
                "translated": {
                    "language": target_lang,
                    "text": translated_text
                }
            }
            
            logger.info(f"查询翻译完成: {detected_lang} -> {target_lang}")
            return result
            
        except Exception as e:
            logger.error(f"查询翻译失败: {e}")
            # 返回包含错误信息的结果，但不抛出异常
            return {
                "original": {"language": "zh", "text": user_query},
                "translated": {"language": "en", "text": user_query},
                "error": str(e)
            }


# 全局翻译服务实例
_translation_service = None


def get_translation_service() -> TranslationService:
    """获取翻译服务实例（单例模式）"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service


if __name__ == "__main__":
    # 测试代码
    service = TranslationService()
    
    # 测试中文查询
    result1 = service.query_translation("营养建议")
    print("中文查询测试:", result1)
    
    # 测试英文查询
    result2 = service.query_translation("nutrition advice")
    print("英文查询测试:", result2)
