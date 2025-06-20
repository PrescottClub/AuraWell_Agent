#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强RAG功能测试脚本
测试新增的中英文双语查询和文献提炼功能
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from RAGExtension import UserRetrieve, Document, detect_language, translate_text

def test_language_detection():
    """测试语言检测功能"""
    print("=" * 60)
    print("🔍 测试语言检测功能")
    print("=" * 60)
    
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
        status = "✅" if detected == expected else "❌"
        print(f"{status} 文本: '{text}' -> 检测结果: {detected} (期望: {expected})")
    
    print()

def test_translation():
    """测试翻译功能"""
    print("=" * 60)
    print("🔄 测试翻译功能")
    print("=" * 60)
    
    try:
        # 加载API密钥
        from RAGExtension import load_api_keys
        keys, success = load_api_keys()
        
        if not success:
            print("❌ 无法加载API密钥，跳过翻译测试")
            return
        
        api_key = keys["ALIBABA_QWEN_API_KEY"] or keys["DASHSCOPE_API_KEY"]
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        test_cases = [
            ("每日营养建议", "english"),
            ("daily nutrition recommendations", "chinese"),
            ("健康饮食指南", "english"),
            ("healthy eating guidelines", "chinese"),
        ]
        
        for text, target_lang in test_cases:
            print(f"🔄 翻译: '{text}' -> {target_lang}")
            translated = translate_text(text, target_lang, api_key, base_url)
            print(f"✅ 结果: '{translated}'")
            print()
            
    except Exception as e:
        print(f"❌ 翻译测试失败: {e}")
    
    print()

def test_enhanced_user_query():
    """测试增强的用户查询功能"""
    print("=" * 60)
    print("🔍 测试增强的用户查询功能")
    print("=" * 60)
    
    test_queries = [
        "每日营养建议",
        "daily nutrition recommendations", 
        "健康饮食指南",
        "healthy eating guidelines",
        "中英文混合 mixed query"
    ]
    
    try:
        retriever = UserRetrieve()
        
        for query in test_queries:
            print(f"🔍 测试查询: '{query}'")
            print("-" * 40)
            
            try:
                # 测试增强的检索功能
                results = retriever.retrieve_topK(query, k=6)
                
                print(f"✅ 检索成功! 找到 {len(results)} 个相关字段:")
                for i, result in enumerate(results[:3], 1):  # 只显示前3个结果
                    display_text = result[:100] + "..." if len(result) > 100 else result
                    print(f"  {i}. {display_text}")
                
                print()
                
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                print()
                
    except Exception as e:
        print(f"❌ 初始化UserRetrieve失败: {e}")
    
    print()

def test_content_filter():
    """测试文献提炼功能"""
    print("=" * 60)
    print("📄 测试文献提炼功能")
    print("=" * 60)
    
    try:
        doc = Document()
        
        # 查找测试文档
        test_files = [
            "中国居民膳食指南2022.pdf",
            "中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf",
            "每日吃白糖别超40克.pdf"
        ]
        
        test_file_found = None
        for filename in test_files:
            file_path = os.path.join(current_dir, "testMaterials", filename)
            if os.path.exists(file_path):
                test_file_found = file_path
                break
        
        if not test_file_found:
            print("❌ 未找到测试文档，跳过文献提炼测试")
            return
        
        print(f"📄 使用测试文档: {os.path.basename(test_file_found)}")
        
        # 测试内容过滤功能
        print("🔄 开始文献提炼...")
        start_time = time.time()
        
        filtered_segments = doc.content_filter(test_file_found)
        
        end_time = time.time()
        print(f"⏱️  处理耗时: {end_time - start_time:.2f}秒")
        
        if filtered_segments:
            print(f"✅ 成功提取 {len(filtered_segments)} 个高密度信息段落:")
            for i, segment in enumerate(filtered_segments[:5], 1):  # 只显示前5个
                display_text = segment[:150] + "..." if len(segment) > 150 else segment
                print(f"  {i}. {display_text}")
            
            if len(filtered_segments) > 5:
                print(f"  ... 还有 {len(filtered_segments) - 5} 个段落")
        else:
            print("❌ 未提取到有效的高密度信息段落")
        
    except Exception as e:
        print(f"❌ 文献提炼测试失败: {e}")
    
    print()

def test_file2vectordb_with_filter():
    """测试带内容过滤的文档向量化功能"""
    print("=" * 60)
    print("💾 测试带内容过滤的文档向量化功能")
    print("=" * 60)
    
    try:
        doc = Document()
        
        # 查找测试文档
        test_file = os.path.join(current_dir, "testMaterials", "每日吃白糖别超40克.pdf")
        
        if not os.path.exists(test_file):
            print("❌ 未找到测试文档，跳过向量化测试")
            return
        
        print(f"📄 使用测试文档: {os.path.basename(test_file)}")
        
        # 测试使用内容过滤的向量化
        print("🔄 开始文档向量化（使用内容过滤）...")
        start_time = time.time()
        
        success = doc.file2VectorDB(test_file, use_content_filter=True)
        
        end_time = time.time()
        print(f"⏱️  处理耗时: {end_time - start_time:.2f}秒")
        
        if success:
            print("✅ 文档向量化成功!")
        else:
            print("❌ 文档向量化失败")
        
    except Exception as e:
        print(f"❌ 文档向量化测试失败: {e}")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始增强RAG功能测试")
    print("=" * 60)
    
    # 1. 测试语言检测
    test_language_detection()
    
    # 2. 测试翻译功能
    test_translation()
    
    # 3. 测试增强的用户查询
    test_enhanced_user_query()
    
    # 4. 测试文献提炼
    test_content_filter()
    
    # 5. 测试带内容过滤的文档向量化
    test_file2vectordb_with_filter()
    
    print("=" * 60)
    print("🎉 所有测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
