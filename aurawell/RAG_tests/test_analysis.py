#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG 检索功能分析报告
分析检索结果的质量和相关性
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

def analyze_retrieval_quality():
    """
    分析检索质量和相关性
    """
    print("=" * 80)
    print("RAG 检索功能质量分析报告")
    print("=" * 80)
    
    retriever = UserRetrieve()
    
    # 测试查询和期望关键词
    test_cases = [
        {
            "query": "每日营养建议",
            "expected_keywords": ["营养", "膳食", "食物", "摄入", "每天", "建议"],
            "description": "用户询问日常营养摄入建议"
        },
        {
            "query": "运动后的营养补充建议", 
            "expected_keywords": ["运动", "补充", "水", "饮料", "能量", "恢复"],
            "description": "用户询问运动后如何补充营养"
        },
        {
            "query": "高血压高血脂的饮食建议",
            "expected_keywords": ["血压", "血脂", "盐", "油", "清淡", "控制"],
            "description": "用户询问心血管疾病的饮食指导"
        }
    ]
    
    overall_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 测试案例 {i}: {test_case['description']}")
        print(f"🔍 查询: '{test_case['query']}'")
        print(f"🎯 期望关键词: {test_case['expected_keywords']}")
        print("-" * 60)
        
        try:
            start_time = time.time()
            results = retriever.retrieve_topK(test_case['query'], k=5)
            end_time = time.time()
            
            # 分析结果质量
            analysis = analyze_results(results, test_case['expected_keywords'])
            analysis['query'] = test_case['query']
            analysis['response_time'] = end_time - start_time
            overall_results.append(analysis)
            
            print(f"⏱️  响应时间: {analysis['response_time']:.2f}秒")
            print(f"📈 相关性评分: {analysis['relevance_score']:.1f}/10")
            print(f"🎯 关键词匹配率: {analysis['keyword_match_rate']:.1f}%")
            print(f"📝 检索到的字段数: {analysis['total_results']}")
            
            print(f"\n📋 检索结果详情:")
            for j, (result, score) in enumerate(zip(results, analysis['individual_scores']), 1):
                print(f"  {j}. [相关性: {score:.1f}/10] {result[:100]}{'...' if len(result) > 100 else ''}")
            
            if analysis['matched_keywords']:
                print(f"\n✅ 匹配的关键词: {analysis['matched_keywords']}")
            if analysis['missing_keywords']:
                print(f"❌ 未匹配的关键词: {analysis['missing_keywords']}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            
        print("\n" + "=" * 60)
        
        # 添加延迟
        if i < len(test_cases):
            time.sleep(1)
    
    # 生成总体报告
    generate_summary_report(overall_results)

def analyze_results(results, expected_keywords):
    """
    分析检索结果的质量
    
    Args:
        results: 检索结果列表
        expected_keywords: 期望的关键词列表
        
    Returns:
        dict: 分析结果
    """
    analysis = {
        'total_results': len(results),
        'individual_scores': [],
        'matched_keywords': [],
        'missing_keywords': [],
        'relevance_score': 0,
        'keyword_match_rate': 0
    }
    
    # 分析每个结果的相关性
    total_score = 0
    matched_keywords_set = set()
    
    for result in results:
        result_lower = result.lower()
        score = 0
        result_matched_keywords = []
        
        # 检查关键词匹配
        for keyword in expected_keywords:
            if keyword in result_lower:
                score += 2
                result_matched_keywords.append(keyword)
                matched_keywords_set.add(keyword)
        
        # 基于内容长度和结构给额外分数
        if len(result.strip()) > 10:  # 有实际内容
            score += 1
        if any(char in result for char in ['🟥', '|', '·']):  # 包含格式化标记
            score += 0.5
            
        # 限制最高分为10分
        score = min(score, 10)
        analysis['individual_scores'].append(score)
        total_score += score
    
    # 计算平均相关性评分
    if results:
        analysis['relevance_score'] = total_score / len(results)
    
    # 计算关键词匹配率
    analysis['matched_keywords'] = list(matched_keywords_set)
    analysis['missing_keywords'] = [kw for kw in expected_keywords if kw not in matched_keywords_set]
    analysis['keyword_match_rate'] = (len(matched_keywords_set) / len(expected_keywords)) * 100
    
    return analysis

def generate_summary_report(results):
    """
    生成总体分析报告
    """
    print("\n" + "=" * 80)
    print("📊 总体分析报告")
    print("=" * 80)
    
    if not results:
        print("❌ 没有可分析的结果")
        return
    
    # 计算平均指标
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    avg_relevance = sum(r['relevance_score'] for r in results) / len(results)
    avg_keyword_match = sum(r['keyword_match_rate'] for r in results) / len(results)
    
    print(f"🔍 测试查询数量: {len(results)}")
    print(f"⏱️  平均响应时间: {avg_response_time:.2f}秒")
    print(f"📈 平均相关性评分: {avg_relevance:.1f}/10")
    print(f"🎯 平均关键词匹配率: {avg_keyword_match:.1f}%")
    
    # 性能评估
    print(f"\n📋 性能评估:")
    if avg_response_time < 3:
        print("✅ 响应速度: 优秀 (< 3秒)")
    elif avg_response_time < 6:
        print("🟡 响应速度: 良好 (3-6秒)")
    else:
        print("🔴 响应速度: 需要优化 (> 6秒)")
        
    if avg_relevance >= 7:
        print("✅ 相关性: 优秀 (≥ 7分)")
    elif avg_relevance >= 5:
        print("🟡 相关性: 良好 (5-7分)")
    else:
        print("🔴 相关性: 需要改进 (< 5分)")
        
    if avg_keyword_match >= 70:
        print("✅ 关键词匹配: 优秀 (≥ 70%)")
    elif avg_keyword_match >= 50:
        print("🟡 关键词匹配: 良好 (50-70%)")
    else:
        print("🔴 关键词匹配: 需要改进 (< 50%)")
    
    # 详细结果
    print(f"\n📝 详细结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. '{result['query']}'")
        print(f"     相关性: {result['relevance_score']:.1f}/10, "
              f"匹配率: {result['keyword_match_rate']:.1f}%, "
              f"响应时间: {result['response_time']:.2f}秒")

if __name__ == "__main__":
    analyze_retrieval_quality()
