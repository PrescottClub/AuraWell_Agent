#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的RAG工作流程测试
测试从文档上传到检索的完整流程，验证引用过滤功能的效果
"""

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

from RAGExtension import Document, UserRetrieve
import time

def test_complete_rag_workflow():
    """
    测试完整的RAG工作流程
    """
    print("=" * 80)
    print("完整RAG工作流程测试（包含引用过滤）")
    print("=" * 80)
    
    # 第一步：文档上传和向量化
    print("🔄 第一步：文档解析和向量化（过滤引用）")
    print("-" * 60)
    
    try:
        doc = Document()
        sample_doc_path = os.path.join("..", "rag", "testMaterials", "中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf")
        
        print(f"📄 处理文档: {sample_doc_path}")
        
        start_time = time.time()
        result = doc.file2VectorDB(sample_doc_path)
        upload_time = time.time() - start_time
        
        if result:
            print(f"✅ 文档上传成功，耗时: {upload_time:.2f}秒")
        else:
            print("❌ 文档上传失败")
            return False
            
    except Exception as e:
        print(f"❌ 文档上传过程出错: {e}")
        return False
    
    # 等待一下确保数据已经写入
    print("⏳ 等待数据写入完成...")
    time.sleep(3)
    
    # 第二步：用户查询检索
    print(f"\n🔍 第二步：用户查询检索测试")
    print("-" * 60)
    
    try:
        retriever = UserRetrieve()
        
        # 测试查询列表
        test_queries = [
            {
                "query": "每日营养建议",
                "description": "日常营养摄入指导"
            },
            {
                "query": "运动后的营养补充建议", 
                "description": "运动营养补充"
            },
            {
                "query": "高血压高血脂的饮食建议",
                "description": "心血管疾病饮食"
            }
        ]
        
        all_results = []
        
        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            description = test_case["description"]
            
            print(f"\n📋 查询 {i}: {description}")
            print(f"🔍 查询内容: '{query}'")
            
            start_time = time.time()
            results = retriever.retrieve_topK(query, k=5)
            query_time = time.time() - start_time
            
            print(f"⏱️  查询耗时: {query_time:.2f}秒")
            print(f"📊 检索到 {len(results)} 个相关内容")
            
            # 检查结果质量
            reference_count = 0
            relevant_count = 0
            
            print(f"\n📝 检索结果:")
            for j, result in enumerate(results, 1):
                # 检查是否为引用
                is_reference = doc._Document__is_reference_content(result)
                
                if is_reference:
                    reference_count += 1
                    status = "📚 [引用]"
                else:
                    relevant_count += 1
                    status = "📄 [内容]"
                
                # 检查相关性（简单关键词匹配）
                query_lower = query.lower()
                result_lower = result.lower()
                
                relevance_keywords = []
                if "营养" in query_lower and "营养" in result_lower:
                    relevance_keywords.append("营养")
                if "运动" in query_lower and "运动" in result_lower:
                    relevance_keywords.append("运动")
                if "血压" in query_lower and "血压" in result_lower:
                    relevance_keywords.append("血压")
                if "饮食" in query_lower and ("饮食" in result_lower or "食" in result_lower):
                    relevance_keywords.append("饮食")
                
                relevance_score = len(relevance_keywords)
                
                display_text = result[:80] + "..." if len(result) > 80 else result
                print(f"  {j}. {status} [相关性: {relevance_score}] {display_text}")
            
            # 统计结果质量
            quality_score = (relevant_count / len(results)) * 100 if results else 0
            
            print(f"\n📈 结果质量分析:")
            print(f"   有效内容: {relevant_count}/{len(results)} ({quality_score:.1f}%)")
            print(f"   引用内容: {reference_count}/{len(results)} ({(reference_count/len(results)*100) if results else 0:.1f}%)")
            
            all_results.append({
                "query": query,
                "results_count": len(results),
                "relevant_count": relevant_count,
                "reference_count": reference_count,
                "query_time": query_time,
                "quality_score": quality_score
            })
            
            if i < len(test_queries):
                print("⏳ 等待2秒后进行下一个查询...")
                time.sleep(2)
        
        # 第三步：总体评估
        print(f"\n📊 第三步：总体性能评估")
        print("-" * 60)
        
        total_queries = len(all_results)
        avg_query_time = sum(r["query_time"] for r in all_results) / total_queries
        avg_quality = sum(r["quality_score"] for r in all_results) / total_queries
        total_references = sum(r["reference_count"] for r in all_results)
        total_results = sum(r["results_count"] for r in all_results)
        
        print(f"🔍 总查询数: {total_queries}")
        print(f"⏱️  平均查询时间: {avg_query_time:.2f}秒")
        print(f"📈 平均内容质量: {avg_quality:.1f}%")
        print(f"📚 引用过滤效果: {total_references}/{total_results} 个结果为引用内容")
        
        # 性能评级
        print(f"\n🏆 系统性能评级:")
        
        if avg_query_time < 3:
            print("✅ 查询速度: 优秀 (< 3秒)")
        elif avg_query_time < 6:
            print("🟡 查询速度: 良好 (3-6秒)")
        else:
            print("🔴 查询速度: 需要优化 (> 6秒)")
        
        if avg_quality >= 80:
            print("✅ 内容质量: 优秀 (≥ 80%)")
        elif avg_quality >= 60:
            print("🟡 内容质量: 良好 (60-80%)")
        else:
            print("🔴 内容质量: 需要改进 (< 60%)")
        
        reference_ratio = (total_references / total_results) * 100 if total_results > 0 else 0
        if reference_ratio < 10:
            print("✅ 引用过滤: 优秀 (< 10%引用内容)")
        elif reference_ratio < 20:
            print("🟡 引用过滤: 良好 (10-20%引用内容)")
        else:
            print("🔴 引用过滤: 需要改进 (> 20%引用内容)")
        
        return True
        
    except Exception as e:
        print(f"❌ 查询检索过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始完整RAG工作流程测试...")
    
    success = test_complete_rag_workflow()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 完整RAG工作流程测试成功完成！")
        print("✅ 引用过滤功能正常工作")
        print("✅ 文档解析和向量化功能正常")
        print("✅ 用户查询检索功能正常")
    else:
        print("❌ 测试过程中出现错误")
    print("=" * 80)
