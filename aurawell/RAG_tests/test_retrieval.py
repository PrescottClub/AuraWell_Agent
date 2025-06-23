#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 RAGExtension 的检索功能
测试用户查询是否能检索出最相近的5个字段
"""

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

from RAGExtension import UserRetrieve
import time

def test_user_queries():
    """
    测试用户查询检索功能
    """
    print("=" * 60)
    print("RAG 检索功能测试")
    print("=" * 60)
    
    # 初始化检索器
    print("正在初始化 UserRetrieve...")
    try:
        retriever = UserRetrieve()
        print("✅ UserRetrieve 初始化成功")
    except Exception as e:
        print(f"❌ UserRetrieve 初始化失败: {e}")
        return
    
    # 测试查询列表
    test_queries = [
        "每日营养建议",
        "运动后的营养补充建议", 
        "高血压高血脂的饮食建议"
    ]
    
    print(f"\n开始测试 {len(test_queries)} 个用户查询...")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 测试查询 {i}: '{query}'")
        print("-" * 40)
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 执行检索，获取最相近的5个字段
            results = retriever.retrieve_topK(query, k=5)
            
            # 记录结束时间
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"✅ 检索成功! 耗时: {elapsed_time:.2f}秒")
            print(f"📊 检索到 {len(results)} 个相关字段:")
            
            # 显示检索结果
            for j, result in enumerate(results, 1):
                # 限制显示长度，避免输出过长
                display_text = result[:200] + "..." if len(result) > 200 else result
                print(f"  {j}. {display_text}")
                print()
            
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 在查询之间添加短暂延迟
        if i < len(test_queries):
            print("⏳ 等待 2 秒后进行下一个查询...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

def test_single_query(query, k=5):
    """
    测试单个查询
    
    Args:
        query (str): 查询字符串
        k (int): 返回结果数量
    """
    print(f"🔍 单独测试查询: '{query}'")
    print("-" * 40)
    
    try:
        retriever = UserRetrieve()
        results = retriever.retrieve_topK(query, k=k)
        
        print(f"✅ 检索成功! 找到 {len(results)} 个相关字段:")
        for i, result in enumerate(results, 1):
            display_text = result[:150] + "..." if len(result) > 150 else result
            print(f"  {i}. {display_text}")
            print()
            
        return results
        
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return None

if __name__ == "__main__":
    # 运行完整测试
    test_user_queries()
    
    print("\n" + "=" * 60)
    print("额外测试: 单个查询详细结果")
    print("=" * 60)
    
    # 额外测试：显示第一个查询的详细结果
    detailed_results = test_single_query("每日营养建议", k=3)
    
    if detailed_results:
        print("\n📋 详细结果分析:")
        for i, result in enumerate(detailed_results, 1):
            print(f"\n结果 {i} (长度: {len(result)} 字符):")
            print(f"内容: {result}")
            print("-" * 30)
