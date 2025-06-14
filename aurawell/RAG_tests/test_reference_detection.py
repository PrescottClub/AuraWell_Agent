#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文献引用检测功能
验证 __is_reference_content 方法是否能正确识别引用内容
"""

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

from RAGExtension import Document

def test_reference_detection():
    """
    测试引用检测功能
    """
    print("=" * 80)
    print("文献引用检测功能测试")
    print("=" * 80)
    
    # 创建Document实例
    doc = Document()
    
    # 测试用例：包含各种类型的引用和非引用内容
    test_cases = [
        # 引用内容 (应该返回 True)
        {
            "text": "[19]邹玉峰,薛思雯,徐幸莲,等.《膳食指南科学报告》对肉类食品摄入的建议[J].中国食物与营养,2015,21(10) :5-8. DOI:10.3969/j.issn.1006-9577.2015.10.001.",
            "expected": True,
            "type": "中文期刊引用"
        },
        {
            "text": "Zou YF, Xue SW, Xu XL, et al. Recommendations for meat foods intake from scientific report of 2015 dietary guidelines[J]. Food Nutr China,2015,21(10):5-8. DOI:10.3969/j.issn.1006-9577.2015.10.001.",
            "expected": True,
            "type": "英文期刊引用"
        },
        {
            "text": "[1] 张三,李四,王五,等.营养学研究进展[J].营养学报,2020,15(3):123-130.",
            "expected": True,
            "type": "带方括号编号的引用"
        },
        {
            "text": "[5-8] 多篇文献的引用格式",
            "expected": True,
            "type": "范围引用"
        },
        {
            "text": "Smith A, Johnson B, et al. Nutritional guidelines for healthy living[J]. Health Journal, 2021, 45(2): 67-89.",
            "expected": True,
            "type": "标准英文期刊格式"
        },
        {
            "text": "ISBN: 978-7-5123-4567-8",
            "expected": True,
            "type": "ISBN引用"
        },
        {
            "text": "ISSN: 1234-5678",
            "expected": True,
            "type": "ISSN引用"
        },
        
        # 非引用内容 (应该返回 False)
        {
            "text": "每日营养建议包括多种食物的摄入。",
            "expected": False,
            "type": "普通营养建议"
        },
        {
            "text": "🟥经常吃全谷物、大豆制品，适量吃坚果。",
            "expected": False,
            "type": "格式化营养指导"
        },
        {
            "text": "运动后应该及时补充水分和电解质。",
            "expected": False,
            "type": "运动营养建议"
        },
        {
            "text": "高血压患者应该控制盐分摄入，每天不超过5克。",
            "expected": False,
            "type": "疾病饮食建议"
        },
        {
            "text": "| 宝塔第四层|动物性食物 120～200克	·每周至少 2次水产品·每天一个鸡蛋|",
            "expected": False,
            "type": "表格内容"
        },
        {
            "text": "",
            "expected": False,
            "type": "空字符串"
        },
        {
            "text": "短文本",
            "expected": False,
            "type": "过短文本"
        }
    ]
    
    print(f"开始测试 {len(test_cases)} 个测试用例...\n")
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        case_type = test_case["type"]
        
        # 调用引用检测方法
        result = doc._Document__is_reference_content(text)
        
        # 检查结果是否正确
        is_correct = result == expected
        if is_correct:
            correct_predictions += 1
            status = "✅ 正确"
        else:
            status = "❌ 错误"
        
        print(f"测试 {i:2d}: {status} | {case_type}")
        print(f"         预期: {'引用' if expected else '非引用'} | 实际: {'引用' if result else '非引用'}")
        
        # 显示文本内容（限制长度）
        display_text = text[:60] + "..." if len(text) > 60 else text
        print(f"         内容: {display_text}")
        print()
    
    # 计算准确率
    accuracy = (correct_predictions / total_tests) * 100
    
    print("=" * 80)
    print("测试结果总结")
    print("=" * 80)
    print(f"总测试用例: {total_tests}")
    print(f"正确预测: {correct_predictions}")
    print(f"错误预测: {total_tests - correct_predictions}")
    print(f"准确率: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print("🎉 检测性能: 优秀")
    elif accuracy >= 80:
        print("👍 检测性能: 良好")
    elif accuracy >= 70:
        print("⚠️  检测性能: 一般")
    else:
        print("🔴 检测性能: 需要改进")
    
    return accuracy

def test_with_real_document():
    """
    使用真实文档测试引用过滤效果
    """
    print("\n" + "=" * 80)
    print("真实文档引用过滤测试")
    print("=" * 80)
    
    try:
        doc = Document()
        # 修改路径指向rag文件夹下的testMaterials - 使用绝对路径确保在Windows上正确工作
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sample_doc_path = os.path.join(parent_dir, "rag", "testMaterials", "中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf")
        
        print("正在解析文档并检测引用...")
        
        # 解析文档
        raw_content = doc._Document__doc_analysation(sample_doc_path)
        
        # 统计原始内容和过滤后内容
        original_count = 0
        filtered_count = 0
        reference_count = 0
        
        layouts = raw_content.get("layouts", []) if raw_content.get("layouts", None) is not None else []
        
        for layout in layouts:
            markdown = layout.get("markdownContent", "")
            if markdown:
                original_count += 1
                
                if doc._Document__is_reference_content(markdown):
                    reference_count += 1
                    print(f"🔍 检测到引用: {markdown[:100]}...")
                else:
                    filtered_count += 1
        
        print(f"\n📊 统计结果:")
        print(f"原始内容块数: {original_count}")
        print(f"检测到的引用: {reference_count}")
        print(f"过滤后内容: {filtered_count}")
        print(f"引用比例: {(reference_count/original_count)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 真实文档测试失败: {e}")

if __name__ == "__main__":
    # 运行引用检测测试
    accuracy = test_reference_detection()
    
    # 运行真实文档测试
    test_with_real_document()
