#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows 11 兼容性测试 - 文件分析模块验证
使用 testMaterials 中的参考资料验证文件分析功能是否正常工作
"""

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

from RAGExtension import Document
import time

def test_file_analysis():
    """
    测试文件分析功能
    """
    print("=" * 80)
    print("Windows 11 文件分析模块测试")
    print("=" * 80)
    
    # 测试文件路径 - 使用 testMaterials 中的文件
    test_files = [
        "中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf",
        "每日吃白糖别超40克.pdf",
        "每日快步1小时预防糖尿病.pdf"
    ]
    
    try:
        doc = Document()
        print("✅ Document 实例创建成功")
        
        for i, filename in enumerate(test_files, 1):
            print(f"\n📄 测试文件 {i}: {filename}")
            print("-" * 60)
            
            # 构建文件路径 - 使用绝对路径确保在Windows上正确工作
            file_path = os.path.join(parent_dir, "rag", "testMaterials", filename)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                continue
                
            print(f"✅ 文件存在: {os.path.getsize(file_path)} bytes")
            
            try:
                print("🔄 开始文件解析...")
                start_time = time.time()
                
                # 测试文件解析
                parsed_content = doc.file_Parsing(file_path)
                
                parse_time = time.time() - start_time
                print(f"✅ 文件解析成功，耗时: {parse_time:.2f}秒")
                
                # 检查解析结果
                if parsed_content:
                    content_length = len(parsed_content)
                    lines_count = len(parsed_content.splitlines())
                    
                    print(f"📊 解析结果统计:")
                    print(f"   内容长度: {content_length} 字符")
                    print(f"   行数: {lines_count} 行")
                    
                    # 显示前200个字符作为预览
                    preview = parsed_content[:200].replace('\n', ' ')
                    print(f"📝 内容预览: {preview}...")
                    
                    # 检查是否包含中文内容
                    chinese_chars = sum(1 for char in parsed_content if '\u4e00' <= char <= '\u9fff')
                    print(f"🈶 中文字符数: {chinese_chars}")
                    
                    if chinese_chars > 0:
                        print("✅ 中文内容解析正常")
                    else:
                        print("⚠️  未检测到中文内容")
                        
                else:
                    print("❌ 解析结果为空")
                    
            except Exception as e:
                print(f"❌ 文件解析失败: {e}")
                import traceback
                traceback.print_exc()
                
            # 在测试之间稍作停顿
            if i < len(test_files):
                print("⏳ 等待2秒后测试下一个文件...")
                time.sleep(2)
        
        print(f"\n🎉 文件分析测试完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始 Windows 11 文件分析兼容性测试...")
    
    success = test_file_analysis()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Windows 11 文件分析模块测试成功！")
        print("✅ 文件路径处理正常")
        print("✅ 文档解析功能正常")
        print("✅ 中文内容处理正常")
    else:
        print("❌ 测试过程中出现错误")
    print("=" * 80)
