import pytest
import json
import os
from index import handler
# 这是入口函数的本地测试文件，一个合理的入口函数可以避免服务崩溃，减少非法请求对资源的消耗
# 模拟 context 参数（实际在阿里云FC中由平台提供）
class MockContext:
    def __init__(self):
        pass

# 获取测试文件路径
def get_test_file_path():
    """获取一个存在的测试PDF文件路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "testMaterials", "每日吃白糖别超40克.pdf")
    return test_file

# 测试用例参数化数据
test_cases = [
    # 正常输入 - 使用存在的测试文件
    (
        json.dumps({"action": "FileExport", "query": {"file_path": get_test_file_path()}}),
        MockContext(),
        200,
        "正常 FileExport 请求"
    ),
    (
        json.dumps({"action": "FileAnalysation", "query": {"file_path": get_test_file_path()}}),
        MockContext(),
        200,
        "正常 FileAnalysation 请求"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": "营养建议", "k": 3}}),
        MockContext(),
        200,
        "正常 RetrieveTopK 请求"
    ),

    # 缺少必要参数
    (
        json.dumps({"action": "FileExport", "query": {}}),
        MockContext(),
        400,
        "缺少 file_path 参数"
    ),
    (
        json.dumps({"action": "FileAnalysation", "query": {}}),
        MockContext(),
        400,
        "缺少 file_path 参数"
    ),

    # 文件不存在的情况
    (
        json.dumps({"action": "FileExport", "query": {"file_path": "nonexistent.pdf"}}),
        MockContext(),
        400,
        "文件不存在"
    ),
    (
        json.dumps({"action": "FileAnalysation", "query": {"file_path": "nonexistent.pdf"}}),
        MockContext(),
        400,
        "文件不存在"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"k": 3}}),
        MockContext(),
        400,
        "缺少 user_query 参数"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": "营养建议", "k": None}}),
        MockContext(),
        400,
        "k 参数必须为正整数"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": "营养建议", "k": 0}}),
        MockContext(),
        400,
        "k 参数必须为正整数"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": "营养建议", "k": -5}}),
        MockContext(),
        400,
        "k 参数必须为正整数"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": "营养建议", "k": "abc"}}),
        MockContext(),
        400,
        "k 参数必须为正整数"
    ),

    # 无效的 action
    (
        json.dumps({"action": "InvalidAction", "query": {}}),
        MockContext(),
        400,
        "无效的 action 参数"
    ),

    # 非法输入（非 JSON 字符串）
    (
        "invalid_json_string",
        MockContext(),
        500,
        "异常输入导致解析失败"
    ),
    (
        json.dumps({"action": "RetrieveTopK", "query": {"user_query": None, "k": 3}}),
        MockContext(),
        400,
        "user_query 参数为空"
    ),
]

@pytest.mark.parametrize("event, context, expected_status, description", test_cases)
def test_handler(event, context, expected_status, description):
    result = handler(event, context)
    assert result["statusCode"] == expected_status, f"预期状态码 {expected_status}，实际为 {result['statusCode']}，描述：{description}"
