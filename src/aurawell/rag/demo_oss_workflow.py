#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS云存储工作流程演示脚本
展示完整的文献管理和RAG处理流程
"""

import os
import sys
import time

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def demo_arxiv_to_oss():
    """演示：从arXiv下载文献到OSS"""
    print("=" * 60)
    print("📚 演示：从arXiv下载文献到OSS云存储")
    print("=" * 60)
    
    try:
        from arXivAPI import export_papers_by_keyword_to_oss
        
        print("🔍 搜索营养学相关论文...")
        papers = export_papers_by_keyword_to_oss("nutrition", k=3)
        
        if papers:
            print(f"\n✅ 成功下载 {len(papers)} 篇论文到OSS")
            return papers
        else:
            print("❌ 未成功下载任何论文")
            return []
            
    except Exception as e:
        print(f"❌ arXiv下载演示失败: {e}")
        return []

def demo_file_index_management():
    """演示：文件索引管理"""
    print("=" * 60)
    print("📝 演示：文件索引管理")
    print("=" * 60)
    
    try:
        from file_index_manager import FileIndexManager
        
        file_manager = FileIndexManager()
        
        # 获取所有文件
        all_files = file_manager.get_all_files()
        print(f"📊 索引中的总文件数: {len(all_files)}")
        
        # 获取最近30天的文件
        recent_files = file_manager.get_files_uploaded_in_days(30)
        print(f"📊 最近30天上传的文件数: {len(recent_files)}")
        
        # 获取未向量化的文件
        unvectorized_files = file_manager.get_unvectorized_files()
        print(f"📊 未向量化的文件数: {len(unvectorized_files)}")
        
        # 显示文件详情
        if all_files:
            print("\n📋 文件索引详情:")
            for i, (filename, record) in enumerate(list(all_files.items())[:5], 1):
                status = "✅ 已向量化" if record.get("vectorized", False) else "❌ 未向量化"
                print(f"  {i}. {filename}")
                print(f"     状态: {status}")
                print(f"     上传时间: {record.get('upload_date_beijing', 'N/A')}")
                print(f"     OSS键名: {record.get('oss_key', 'N/A')}")
                print()
        
        return recent_files
        
    except Exception as e:
        print(f"❌ 文件索引管理演示失败: {e}")
        return []

def demo_batch_vectorization():
    """演示：批量向量化处理"""
    print("=" * 60)
    print("⚡ 演示：批量向量化处理")
    print("=" * 60)
    
    try:
        from RAGExtension import Document
        
        doc = Document()
        
        print("🔄 开始批量处理最近30天的文件...")
        results = doc.batch_process_recent_files(days=30, use_content_filter=True)
        
        print(f"\n📊 批量处理结果:")
        print(f"  - 总文件数: {results['total']}")
        print(f"  - 处理成功: {results['processed']}")
        print(f"  - 处理失败: {results['failed']}")
        print(f"  - 跳过文件: {results['skipped']}")
        
        return results
        
    except Exception as e:
        print(f"❌ 批量向量化演示失败: {e}")
        return {"total": 0, "processed": 0, "failed": 0, "skipped": 0}

def demo_enhanced_query():
    """演示：增强查询功能"""
    print("=" * 60)
    print("🔍 演示：增强查询功能")
    print("=" * 60)
    
    try:
        from RAGExtension import UserRetrieve
        
        retriever = UserRetrieve()
        
        # 测试不同类型的查询
        test_queries = [
            ("中文查询", "营养膳食建议"),
            ("英文查询", "daily nutrition recommendations"),
            ("混合查询", "健康饮食 healthy eating"),
            ("专业术语", "膳食纤维摄入量")
        ]
        
        for query_type, query in test_queries:
            print(f"\n🔍 {query_type}: '{query}'")
            print("-" * 40)
            
            try:
                results = retriever.retrieve_topK(query, k=4)
                
                if results:
                    print(f"✅ 找到 {len(results)} 个相关结果")
                    
                    # 显示前2个结果的摘要
                    for i, result in enumerate(results[:2], 1):
                        preview = result[:100] + "..." if len(result) > 100 else result
                        print(f"  结果{i}: {preview}")
                else:
                    print("⚠️  未找到相关结果")
                    
            except Exception as e:
                print(f"❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强查询演示失败: {e}")
        return False

def demo_oss_file_operations():
    """演示：OSS文件操作"""
    print("=" * 60)
    print("☁️  演示：OSS文件操作")
    print("=" * 60)
    
    try:
        from oss_utils import OSSManager
        
        oss_manager = OSSManager()
        
        # 列出nutrition目录下的文件
        print("📂 列出nutrition目录下的文件:")
        files = oss_manager.list_files(prefix="nutrition/", max_keys=10)
        
        if files:
            for i, file_info in enumerate(files, 1):
                print(f"  {i}. {file_info['key']}")
                print(f"     大小: {file_info['size']} 字节")
                print(f"     修改时间: {file_info['last_modified']}")
                print()
        else:
            print("  📭 目录为空")
        
        # 列出file_status目录下的文件
        print("📂 列出file_status目录下的文件:")
        status_files = oss_manager.list_files(prefix="file_status/", max_keys=10)
        
        if status_files:
            for i, file_info in enumerate(status_files, 1):
                print(f"  {i}. {file_info['key']}")
                print(f"     大小: {file_info['size']} 字节")
                print()
        else:
            print("  📭 目录为空")
        
        return True
        
    except Exception as e:
        print(f"❌ OSS文件操作演示失败: {e}")
        return False

def demo_complete_workflow():
    """演示：完整工作流程"""
    print("🚀 OSS云存储RAG系统完整工作流程演示")
    print("=" * 60)
    
    workflow_steps = [
        ("📚 步骤1: 从arXiv下载文献到OSS", demo_arxiv_to_oss),
        ("📝 步骤2: 文件索引管理", demo_file_index_management),
        ("☁️  步骤3: OSS文件操作", demo_oss_file_operations),
        ("⚡ 步骤4: 批量向量化处理", demo_batch_vectorization),
        ("🔍 步骤5: 增强查询功能", demo_enhanced_query),
    ]
    
    results = []
    
    for step_name, step_func in workflow_steps:
        print(f"\n{step_name}")
        try:
            result = step_func()
            results.append((step_name, True, result))
            print(f"✅ {step_name} 完成")
        except Exception as e:
            results.append((step_name, False, str(e)))
            print(f"❌ {step_name} 失败: {e}")
        
        print()
        time.sleep(1)  # 短暂暂停，便于观察
    
    # 显示工作流程总结
    print("=" * 60)
    print("📊 工作流程总结")
    print("=" * 60)
    
    successful_steps = sum(1 for _, success, _ in results if success)
    total_steps = len(results)
    
    print(f"🎯 完成情况: {successful_steps}/{total_steps} 步骤成功")
    
    for step_name, success, result in results:
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
    
    if successful_steps == total_steps:
        print("\n🎉 所有步骤都成功完成！OSS云存储RAG系统运行正常")
    else:
        print(f"\n⚠️  {total_steps - successful_steps} 个步骤需要检查")
    
    print("\n💡 系统功能说明:")
    print("  - 📚 自动从arXiv下载营养学相关论文")
    print("  - ☁️  文件存储在阿里云OSS中，支持大规模存储")
    print("  - 📝 JSON索引文件记录所有文件的状态和元数据")
    print("  - 🤖 智能内容过滤，提取高密度信息段落")
    print("  - 🔍 中英文双语查询，自动翻译和检索")
    print("  - ⚡ 批量处理功能，自动向量化新上传的文件")
    print("  - 🎯 向量数据库存储，支持语义相似度搜索")

def main():
    """主函数"""
    print("🌟 欢迎使用OSS云存储RAG系统演示")
    print("=" * 60)
    
    # 运行完整工作流程演示
    demo_complete_workflow()

if __name__ == "__main__":
    main()
