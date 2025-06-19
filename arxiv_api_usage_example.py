#!/usr/bin/env python3
"""
arXivAPI.py 使用示例

修改后的 arXivAPI.py 模块可以根据外部输入的关键词导出k个相关文献
至项目根目录下的 nutrition_article 文件夹，并且不使用数据库存储信息。
"""

import sys
import os

# 添加 aurawell/rag 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'aurawell', 'rag'))

from arXivAPI import export_papers_by_keyword

def main():
    """主函数：演示如何使用修改后的 arXivAPI"""
    
    print("=== arXivAPI 使用示例 ===\n")
    
    # 示例1：搜索营养学相关论文
    print("示例1：搜索营养学相关论文")
    print("-" * 40)
    results1 = export_papers_by_keyword(
        keyword="nutrition",  # 关键词
        k=3                   # 导出3篇论文
    )
    print(f"成功导出 {len(results1)} 篇营养学论文\n")
    
    # 示例2：搜索机器学习相关论文
    print("示例2：搜索机器学习相关论文")
    print("-" * 40)
    results2 = export_papers_by_keyword(
        keyword="machine learning",  # 多词关键词
        k=2                          # 导出2篇论文
    )
    print(f"成功导出 {len(results2)} 篇机器学习论文\n")
    
    # 示例3：搜索深度学习相关论文
    print("示例3：搜索深度学习相关论文")
    print("-" * 40)
    results3 = export_papers_by_keyword(
        keyword="deep learning",
        k=2
    )
    print(f"成功导出 {len(results3)} 篇深度学习论文\n")
    
    # 显示总结
    total_papers = len(results1) + len(results2) + len(results3)
    print(f"总共成功导出 {total_papers} 篇论文到 nutrition_article 文件夹")
    
    # 显示文件夹内容
    nutrition_dir = "nutrition_article"
    if os.path.exists(nutrition_dir):
        files = [f for f in os.listdir(nutrition_dir) if f.endswith('.pdf')]
        print(f"\n当前 {nutrition_dir} 文件夹包含 {len(files)} 个PDF文件:")
        for file in sorted(files):
            print(f"  - {file}")

def interactive_search():
    """交互式搜索功能"""
    print("\n=== 交互式论文搜索 ===")
    
    while True:
        keyword = input("\n请输入搜索关键词 (输入 'quit' 退出): ").strip()
        
        if keyword.lower() == 'quit':
            print("退出搜索")
            break
            
        if not keyword:
            print("请输入有效的关键词")
            continue
            
        try:
            k = int(input("请输入要下载的论文数量 (默认5): ") or "5")
        except ValueError:
            k = 5
            
        print(f"\n开始搜索关键词 '{keyword}'...")
        results = export_papers_by_keyword(keyword=keyword, k=k)
        
        if results:
            print(f"✅ 成功导出 {len(results)} 篇论文")
        else:
            print("❌ 未找到相关论文或下载失败")

if __name__ == "__main__":
    # 运行基本示例
    main()
    
    # 可选：运行交互式搜索
    # interactive_search()
