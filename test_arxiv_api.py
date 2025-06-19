#!/usr/bin/env python3
"""
测试修改后的 arXivAPI.py 功能
"""

import sys
import os

# 添加 aurawell/rag 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'aurawell', 'rag'))

from arXivAPI import export_papers_by_keyword

def test_keyword_search():
    """测试关键词搜索功能"""
    print("=== 测试 arXivAPI 关键词搜索功能 ===\n")
    
    # 测试不同的关键词
    test_cases = [
        {"keyword": "machine learning", "k": 3},
        {"keyword": "nutrition", "k": 2},
        {"keyword": "artificial intelligence", "k": 2}
    ]
    
    for test_case in test_cases:
        print(f"测试关键词: '{test_case['keyword']}', 数量: {test_case['k']}")
        print("-" * 50)
        
        try:
            results = export_papers_by_keyword(
                keyword=test_case['keyword'], 
                k=test_case['k']
            )
            
            print(f"成功导出 {len(results)} 篇论文\n")
            
        except Exception as e:
            print(f"测试失败: {str(e)}\n")

if __name__ == "__main__":
    test_keyword_search()
