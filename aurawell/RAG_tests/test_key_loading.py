#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的密钥加载功能
验证Document和UserRetrieve类能够从.env文件或环境变量中加载密钥
"""

import sys
import os

# 添加父目录到Python路径，以便导入rag模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
rag_dir = os.path.join(parent_dir, 'rag')
sys.path.insert(0, rag_dir)

def test_key_loading_from_env_file():
    """
    测试从.env文件加载密钥
    """
    print("=" * 80)
    print("测试从.env文件加载密钥")
    print("=" * 80)
    
    try:
        from RAGExtension import Document, UserRetrieve
        
        print("\n🔍 测试Document类初始化...")
        doc = Document()
        
        # 验证密钥是否正确加载
        assert doc.access_key_id is not None, "ALIBABA_CLOUD_ACCESS_KEY_ID未加载"
        assert doc.access_key_secret is not None, "ALIBABA_CLOUD_ACCESS_KEY_SECRET未加载"
        assert doc.dash_scope_key is not None, "DASHSCOPE_API_KEY未加载"
        assert doc.dash_vector_key is not None, "DASH_VECTOR_API未加载"
        
        print("✅ Document类密钥加载成功")
        
        print("\n🔍 测试UserRetrieve类初始化...")
        retriever = UserRetrieve()
        
        # 验证密钥是否正确加载
        assert retriever.dash_scope_key is not None, "DASHSCOPE_API_KEY未加载"
        assert retriever.dash_vector_key is not None, "DASH_VECTOR_API未加载"
        
        print("✅ UserRetrieve类密钥加载成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 从.env文件加载密钥失败: {e}")
        return False

def test_key_loading_from_environment():
    """
    测试从环境变量加载密钥（模拟.env文件不存在的情况）
    """
    print("\n" + "=" * 80)
    print("测试从环境变量加载密钥")
    print("=" * 80)
    
    # 备份当前环境变量
    original_env = {}
    test_keys = [
        "ALIBABA_CLOUD_ACCESS_KEY_ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET", 
        "DASHSCOPE_API_KEY",
        "DASH_VECTOR_API"
    ]
    
    for key in test_keys:
        original_env[key] = os.environ.get(key)
    
    try:
        # 设置测试环境变量
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"] = "test_access_key_id"
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"] = "test_access_key_secret"
        os.environ["DASHSCOPE_API_KEY"] = "test_dashscope_key"
        os.environ["DASH_VECTOR_API"] = "test_dash_vector_key"
        
        # 重新导入模块以测试环境变量加载
        import importlib
        import RAGExtension
        importlib.reload(RAGExtension)
        
        print("\n🔍 测试从环境变量加载Document类...")
        doc = RAGExtension.Document()
        
        # 验证是否加载了测试环境变量
        assert doc.access_key_id == "test_access_key_id", "环境变量ALIBABA_CLOUD_ACCESS_KEY_ID未正确加载"
        assert doc.access_key_secret == "test_access_key_secret", "环境变量ALIBABA_CLOUD_ACCESS_KEY_SECRET未正确加载"
        assert doc.dash_scope_key == "test_dashscope_key", "环境变量DASHSCOPE_API_KEY未正确加载"
        assert doc.dash_vector_key == "test_dash_vector_key", "环境变量DASH_VECTOR_API未正确加载"
        
        print("✅ Document类从环境变量加载密钥成功")
        
        print("\n🔍 测试从环境变量加载UserRetrieve类...")
        retriever = RAGExtension.UserRetrieve()
        
        # 验证是否加载了测试环境变量
        assert retriever.dash_scope_key == "test_dashscope_key", "环境变量DASHSCOPE_API_KEY未正确加载"
        assert retriever.dash_vector_key == "test_dash_vector_key", "环境变量DASH_VECTOR_API未正确加载"
        
        print("✅ UserRetrieve类从环境变量加载密钥成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 从环境变量加载密钥失败: {e}")
        return False
        
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

def test_missing_keys_handling():
    """
    测试缺少密钥时的错误处理
    """
    print("\n" + "=" * 80)
    print("测试缺少密钥时的错误处理")
    print("=" * 80)
    
    # 备份当前环境变量
    original_env = {}
    test_keys = [
        "ALIBABA_CLOUD_ACCESS_KEY_ID",
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET", 
        "DASHSCOPE_API_KEY",
        "DASH_VECTOR_API"
    ]
    
    for key in test_keys:
        original_env[key] = os.environ.get(key)
    
    try:
        # 清除所有相关环境变量
        for key in test_keys:
            if key in os.environ:
                del os.environ[key]
        
        # 重新导入模块
        import importlib
        import RAGExtension
        importlib.reload(RAGExtension)
        
        print("\n🔍 测试Document类在缺少密钥时的行为...")
        try:
            doc = RAGExtension.Document()
            print("❌ Document类应该在缺少密钥时抛出异常")
            return False
        except ValueError as e:
            print(f"✅ Document类正确处理缺少密钥的情况: {e}")
        
        print("\n🔍 测试UserRetrieve类在缺少密钥时的行为...")
        try:
            retriever = RAGExtension.UserRetrieve()
            print("❌ UserRetrieve类应该在缺少密钥时抛出异常")
            return False
        except ValueError as e:
            print(f"✅ UserRetrieve类正确处理缺少密钥的情况: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False
        
    finally:
        # 恢复原始环境变量
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value

def test_load_api_keys_function():
    """
    测试load_api_keys函数
    """
    print("\n" + "=" * 80)
    print("测试load_api_keys函数")
    print("=" * 80)
    
    try:
        from RAGExtension import load_api_keys
        
        print("\n🔍 测试load_api_keys函数...")
        keys, success = load_api_keys()
        
        print(f"📊 加载结果: success={success}")
        print(f"📋 密钥状态:")
        for key, value in keys.items():
            status = "✅ 已加载" if value else "❌ 未加载"
            print(f"  {key}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ load_api_keys函数测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试新的密钥加载功能...")
    
    # 运行所有测试
    tests = [
        ("load_api_keys函数测试", test_load_api_keys_function),
        ("从.env文件加载密钥", test_key_loading_from_env_file),
        ("从环境变量加载密钥", test_key_loading_from_environment),
        ("缺少密钥时的错误处理", test_missing_keys_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 '{test_name}' 执行失败: {e}")
            results.append((test_name, False))
    
    # 总结测试结果
    print("\n" + "=" * 80)
    print("测试结果总结")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！新的密钥加载功能工作正常。")
    else:
        print("⚠️  部分测试失败，请检查实现。")
