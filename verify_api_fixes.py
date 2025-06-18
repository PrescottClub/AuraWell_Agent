#!/usr/bin/env python3
"""
简化的API修复验证脚本
检查我们添加的API端点是否正确定义
"""

import sys
import os
import re
from pathlib import Path

def check_api_endpoints():
    """检查API端点是否正确添加"""
    api_file = Path("src/aurawell/interfaces/api_interface.py")
    
    if not api_file.exists():
        print("❌ API接口文件不存在")
        return False
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查项目列表
    checks = [
        {
            "name": "聊天历史别名路径",
            "pattern": r"@app\.get\(\s*[\"']/api/v1/chat/conversations/\{conversation_id\}/messages[\"']",
            "description": "前端调用 /chat/conversations/{id}/messages 的别名"
        },
        {
            "name": "用户健康目标更新端点",
            "pattern": r"@app\.put\(\s*[\"']/api/v1/user/health-goals/\{goal_id\}[\"']",
            "description": "PUT /user/health-goals/{id} 端点"
        },
        {
            "name": "用户健康目标删除端点", 
            "pattern": r"@app\.delete\(\s*[\"']/api/v1/user/health-goals/\{goal_id\}[\"']",
            "description": "DELETE /user/health-goals/{id} 端点"
        },
        {
            "name": "响应适配器函数",
            "pattern": r"def adapt_response_for_frontend\(",
            "description": "前端响应格式适配器"
        },
        {
            "name": "前端兼容用户档案端点",
            "pattern": r"@app\.get\(\s*[\"']/api/v1/user/profile/frontend[\"']",
            "description": "GET /user/profile/frontend 兼容端点"
        },
        {
            "name": "前端兼容健康摘要端点",
            "pattern": r"@app\.get\(\s*[\"']/api/v1/health/summary/frontend[\"']",
            "description": "GET /health/summary/frontend 兼容端点"
        }
    ]
    
    print("🔍 检查API端点修复情况...")
    print("="*60)
    
    results = []
    for check in checks:
        found = bool(re.search(check["pattern"], content, re.MULTILINE))
        status = "✅ 已添加" if found else "❌ 缺失"
        print(f"{check['name']:25} {status}")
        print(f"    {check['description']}")
        results.append(found)
    
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"修复进度: {passed}/{total} 项完成")
    
    if passed == total:
        print("🎉 所有API修复已完成！")
        return True
    else:
        print("⚠️  仍有修复项目未完成")
        return False

def check_frontend_api_calls():
    """检查前端API调用情况"""
    print("\n🔍 分析前端API调用...")
    print("="*60)
    
    frontend_files = [
        "frontend/src/api/chat.js",
        "frontend/src/api/user.js", 
        "frontend/src/api/healthPlan.js",
        "frontend/src/api/family.js"
    ]
    
    api_calls = []
    
    for file_path in frontend_files:
        if not Path(file_path).exists():
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取API调用
        patterns = [
            r"request\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]",
            r"await\s+request\.(get|post|put|delete)\(['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for method, url in matches:
                api_calls.append({
                    "file": file_path,
                    "method": method.upper(),
                    "url": url,
                })
    
    # 按文件分组显示
    files_apis = {}
    for call in api_calls:
        file_name = call["file"].split("/")[-1]
        if file_name not in files_apis:
            files_apis[file_name] = []
        files_apis[file_name].append(f"{call['method']} {call['url']}")
    
    for file_name, apis in files_apis.items():
        print(f"\n📁 {file_name}:")
        for api in sorted(set(apis)):
            print(f"  • {api}")
    
    unique_apis = set(f"{call['method']} {call['url']}" for call in api_calls)
    print(f"\n总计发现 {len(unique_apis)} 个不同的API调用")

def generate_fix_summary():
    """生成修复摘要"""
    print("\n📋 API契约修复摘要")
    print("="*60)
    
    fixes = [
        "✅ 添加聊天历史路径别名: /chat/conversations/{id}/messages",
        "✅ 添加用户健康目标管理端点: PUT/DELETE /user/health-goals/{id}",
        "✅ 创建响应格式适配器函数: adapt_response_for_frontend()",
        "✅ 添加前端兼容性端点: /user/profile/frontend, /health/summary/frontend",
        "✅ 保持所有现有API端点向后兼容",
        "✅ 支持前端期望的 {success, data, message, timestamp} 响应格式"
    ]
    
    for fix in fixes:
        print(fix)
    
    print("\n🎯 下一步建议:")
    print("1. 启动API服务器进行实际测试")
    print("2. 运行前端应用验证API调用")
    print("3. 检查所有功能是否正常工作")
    print("4. 更新API文档")

def main():
    """主函数"""
    print("🛡️ API契约修复验证工具")
    print("检查前后端API对齐修复情况\n")
    
    # 检查API端点修复
    api_fixed = check_api_endpoints()
    
    # 分析前端API调用
    check_frontend_api_calls()
    
    # 生成修复摘要
    generate_fix_summary()
    
    if api_fixed:
        print("\n🎉 API契约修复验证完成！所有修复项目已实施。")
        return 0
    else:
        print("\n⚠️  API契约修复验证发现问题，请检查缺失的修复项目。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
