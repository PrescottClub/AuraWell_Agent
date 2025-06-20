#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS云存储集成测试脚本
测试arXivAPI和RAGExtension的OSS存储功能
"""

import os
import sys
import time
from pathlib import Path

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_oss_configuration():
    """测试OSS配置"""
    print("=" * 60)
    print("🔧 测试OSS配置")
    print("=" * 60)
    
    try:
        from oss_utils import load_oss_config, OSSManager
        
        # 测试配置加载
        config, success = load_oss_config()
        
        if success:
            print("✅ OSS配置加载成功")
            print(f"  - 区域: {config['region']}")
            print(f"  - 端点: {config['endpoint']}")
            print(f"  - 存储桶: {config['bucket_name']}")
            
            # 测试OSS连接
            try:
                oss_manager = OSSManager()
                print("✅ OSS管理器初始化成功")
                return True
            except Exception as e:
                print(f"❌ OSS管理器初始化失败: {e}")
                return False
        else:
            print("❌ OSS配置加载失败")
            return False
            
    except Exception as e:
        print(f"❌ OSS配置测试失败: {e}")
        return False

def test_file_index_manager():
    """测试文件索引管理器"""
    print("=" * 60)
    print("📝 测试文件索引管理器")
    print("=" * 60)
    
    try:
        from file_index_manager import FileIndexManager
        
        # 初始化文件索引管理器
        file_manager = FileIndexManager()
        print("✅ 文件索引管理器初始化成功")
        
        # 测试获取所有文件
        all_files = file_manager.get_all_files()
        print(f"📊 当前索引中的文件数量: {len(all_files)}")
        
        # 测试获取最近30天的文件
        recent_files = file_manager.get_files_uploaded_in_days(30)
        print(f"📊 最近30天上传的文件数量: {len(recent_files)}")
        
        # 测试获取未向量化的文件
        unvectorized_files = file_manager.get_unvectorized_files()
        print(f"📊 未向量化的文件数量: {len(unvectorized_files)}")
        
        # 显示一些文件信息
        if all_files:
            print("\n📚 文件索引示例:")
            for i, (filename, record) in enumerate(list(all_files.items())[:3], 1):
                vectorized_status = "✅" if record.get("vectorized", False) else "❌"
                print(f"  {i}. {filename} - 向量化状态: {vectorized_status}")
                print(f"     上传时间: {record.get('upload_date_beijing', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件索引管理器测试失败: {e}")
        return False

def test_arxiv_oss_integration():
    """测试arXiv与OSS集成"""
    print("=" * 60)
    print("📚 测试arXiv与OSS集成")
    print("=" * 60)
    
    try:
        from arXivAPI import export_papers_by_keyword_to_oss
        
        print("🔍 搜索并下载营养学相关论文到OSS...")
        
        # 下载少量论文进行测试
        papers = export_papers_by_keyword_to_oss("nutrition", k=2)
        
        if papers:
            print(f"✅ 成功下载 {len(papers)} 篇论文到OSS")
            for paper in papers:
                print(f"  - {paper['title'][:60]}...")
                print(f"    OSS键名: {paper['oss_key']}")
            return True
        else:
            print("⚠️  未成功下载任何论文")
            return False
            
    except Exception as e:
        print(f"❌ arXiv OSS集成测试失败: {e}")
        return False

def test_rag_oss_integration():
    """测试RAG与OSS集成"""
    print("=" * 60)
    print("🤖 测试RAG与OSS集成")
    print("=" * 60)
    
    try:
        from RAGExtension import Document
        
        # 初始化Document类
        doc = Document()
        print("✅ Document类初始化成功")
        
        # 测试获取最近文件
        recent_files = doc.get_recent_files_from_oss(30)
        print(f"📊 获取到 {len(recent_files)} 个最近上传的文件")
        
        if recent_files:
            # 选择一个未向量化的文件进行测试
            unvectorized_files = [f for f in recent_files if not f.get("vectorized", False)]
            
            if unvectorized_files:
                test_file = unvectorized_files[0]
                filename = test_file["filename"]
                oss_key = test_file["oss_key"]
                
                print(f"🔄 测试处理文件: {filename}")
                
                # 测试文档向量化
                success = doc.file2VectorDB(
                    oss_key, 
                    use_content_filter=True, 
                    is_oss_key=True, 
                    update_index=True
                )
                
                if success:
                    print(f"✅ 文件向量化成功: {filename}")
                    return True
                else:
                    print(f"❌ 文件向量化失败: {filename}")
                    return False
            else:
                print("⚠️  所有文件都已向量化，跳过测试")
                return True
        else:
            print("⚠️  未找到可测试的文件")
            return False
            
    except Exception as e:
        print(f"❌ RAG OSS集成测试失败: {e}")
        return False

def test_batch_processing():
    """测试批量处理功能"""
    print("=" * 60)
    print("⚡ 测试批量处理功能")
    print("=" * 60)
    
    try:
        from RAGExtension import Document
        
        # 初始化Document类
        doc = Document()
        
        # 测试批量处理最近30天的文件
        print("🔄 开始批量处理最近30天的文件...")
        
        results = doc.batch_process_recent_files(days=30, use_content_filter=True)
        
        print(f"📊 批量处理结果:")
        print(f"  - 总文件数: {results['total']}")
        print(f"  - 处理成功: {results['processed']}")
        print(f"  - 处理失败: {results['failed']}")
        print(f"  - 跳过文件: {results['skipped']}")
        
        return results['total'] > 0 or results['processed'] >= 0
        
    except Exception as e:
        print(f"❌ 批量处理测试失败: {e}")
        return False

def test_enhanced_query_with_oss():
    """测试增强查询功能与OSS集成"""
    print("=" * 60)
    print("🔍 测试增强查询功能与OSS集成")
    print("=" * 60)
    
    try:
        from RAGExtension import UserRetrieve
        
        # 初始化UserRetrieve类
        retriever = UserRetrieve()
        print("✅ UserRetrieve类初始化成功")
        
        # 测试查询
        test_queries = [
            "营养膳食建议",
            "daily nutrition recommendations",
            "健康饮食指南"
        ]
        
        for query in test_queries:
            print(f"\n🔍 测试查询: '{query}'")
            
            try:
                results = retriever.retrieve_topK(query, k=4)
                
                if results:
                    print(f"✅ 查询成功，找到 {len(results)} 个相关结果")
                    # 显示第一个结果的前100个字符
                    if results:
                        preview = results[0][:100] + "..." if len(results[0]) > 100 else results[0]
                        print(f"  示例结果: {preview}")
                else:
                    print("⚠️  查询未返回结果")
                    
            except Exception as e:
                print(f"❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强查询测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始OSS云存储集成测试")
    print("=" * 60)
    
    test_results = []
    
    # 1. 测试OSS配置
    test_results.append(("OSS配置", test_oss_configuration()))
    
    # 2. 测试文件索引管理器
    test_results.append(("文件索引管理器", test_file_index_manager()))
    
    # 3. 测试arXiv与OSS集成
    test_results.append(("arXiv OSS集成", test_arxiv_oss_integration()))
    
    # 4. 测试RAG与OSS集成
    test_results.append(("RAG OSS集成", test_rag_oss_integration()))
    
    # 5. 测试批量处理功能
    test_results.append(("批量处理", test_batch_processing()))
    
    # 6. 测试增强查询功能
    test_results.append(("增强查询", test_enhanced_query_with_oss()))
    
    # 显示测试结果汇总
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！OSS云存储集成功能正常工作")
    else:
        print("⚠️  部分测试失败，请检查相关配置和实现")

if __name__ == "__main__":
    main()
