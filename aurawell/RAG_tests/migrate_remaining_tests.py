#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量转移剩余测试文件的脚本
"""

import os
import shutil

def add_import_header(content):
    """
    为测试文件添加导入头部
    """
    header = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

'''
    
    # 移除原有的shebang和编码声明
    lines = content.split('\n')
    start_index = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('#') and ('python' in line or 'coding' in line or line.strip() == '#'):
            continue
        else:
            start_index = i
            break
    
    # 重新组合内容
    remaining_content = '\n'.join(lines[start_index:])
    return header + remaining_content

def update_file_paths(content):
    """
    更新文件中的路径引用
    """
    # 更新testMaterial路径
    content = content.replace('./testMaterial/', '../rag/testMaterial/')
    content = content.replace('"./testMaterial/', '"../rag/testMaterial/')
    content = content.replace("'./testMaterial/", "'../rag/testMaterial/")
    
    return content

def migrate_test_file(source_path, dest_path):
    """
    迁移单个测试文件
    """
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加导入头部
        content = add_import_header(content)
        
        # 更新路径
        content = update_file_paths(content)
        
        # 写入新文件
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 成功迁移: {os.path.basename(source_path)}")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败 {os.path.basename(source_path)}: {e}")
        return False

def main():
    """
    主函数：批量迁移测试文件
    """
    print("=" * 60)
    print("批量迁移RAG测试文件")
    print("=" * 60)
    
    # 定义源目录和目标目录
    source_dir = "../rag"
    dest_dir = "."
    
    # 需要迁移的测试文件列表
    test_files = [
        "test_filtered_vectorization.py",
        "test_complete_workflow.py"
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        source_path = os.path.join(source_dir, test_file)
        dest_path = os.path.join(dest_dir, test_file)
        
        if os.path.exists(source_path):
            if migrate_test_file(source_path, dest_path):
                success_count += 1
        else:
            print(f"⚠️  源文件不存在: {test_file}")
    
    print("\n" + "=" * 60)
    print("迁移完成")
    print("=" * 60)
    print(f"成功迁移: {success_count}/{total_count} 个文件")
    
    if success_count == total_count:
        print("🎉 所有测试文件迁移成功！")
    else:
        print("⚠️  部分文件迁移失败，请检查错误信息")

if __name__ == "__main__":
    main()
