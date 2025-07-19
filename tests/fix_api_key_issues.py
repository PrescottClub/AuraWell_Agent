#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API密钥问题修复脚本
解决健康助手聊天服务中的API认证问题
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

# 加载.env文件
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ 已加载.env文件: {dotenv_path}")
else:
    print(f"⚠️  .env文件不存在: {dotenv_path}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIKeyFixer:
    """API密钥修复器"""
    
    def __init__(self):
        self.env_file_path = os.path.join(project_root, '.env')
        self.api_keys_status = {}
    
    def check_env_file(self):
        """检查.env文件"""
        print("\n🔍 检查.env文件...")
        
        if not os.path.exists(self.env_file_path):
            print("  ❌ .env文件不存在")
            return False
        
        print("  ✅ .env文件存在")
        return True
    
    def check_api_keys(self):
        """检查API密钥配置"""
        print("\n🔑 检查API密钥配置...")
        
        # 需要检查的API密钥
        api_keys_to_check = [
            ("DASHSCOPE_API_KEY", "阿里云DashScope API密钥"),
            ("QWEN_API", "Qwen API密钥"),
            ("DEEP_SEEK_API", "DeepSeek API密钥"),
            ("DEEPSEEK_API_KEY", "DeepSeek API密钥（备用）"),
        ]
        
        configured_keys = []
        missing_keys = []
        
        for env_key, description in api_keys_to_check:
            value = os.getenv(env_key)
            if value and len(value.strip()) > 0:
                # 检查密钥格式
                if len(value) > 10:  # 基本长度检查
                    configured_keys.append((env_key, description, value[:10] + "..."))
                    self.api_keys_status[env_key] = "configured"
                    print(f"  ✅ {description}: 已配置 ({value[:10]}...)")
                else:
                    missing_keys.append((env_key, description))
                    self.api_keys_status[env_key] = "invalid"
                    print(f"  ❌ {description}: 配置无效（长度过短）")
            else:
                missing_keys.append((env_key, description))
                self.api_keys_status[env_key] = "missing"
                print(f"  ❌ {description}: 未配置")
        
        print(f"\n  📊 统计: {len(configured_keys)} 个已配置, {len(missing_keys)} 个缺失")
        return len(configured_keys) > 0
    
    async def test_api_connectivity(self):
        """测试API连接性"""
        print("\n🌐 测试API连接性...")
        
        try:
            from aurawell.core.deepseek_client import DeepSeekClient
            from aurawell.core.service_factory import ServiceClientFactory
            
            # 测试DeepSeek客户端
            print("  🔄 测试DeepSeek客户端...")
            deepseek_client = ServiceClientFactory.get_deepseek_client()
            
            if deepseek_client:
                print("  ✅ DeepSeek客户端创建成功")
                
                # 测试简单API调用
                try:
                    test_messages = [{"role": "user", "content": "Hello"}]
                    response = deepseek_client.get_deepseek_response(
                        messages=test_messages,
                        model_name="deepseek-v3",
                        max_tokens=10,
                        temperature=0.1
                    )
                    print("  ✅ DeepSeek API调用成功")
                    print(f"  📝 测试响应: {response.content[:50]}...")
                    return True
                    
                except Exception as api_error:
                    print(f"  ❌ DeepSeek API调用失败: {api_error}")
                    if "401" in str(api_error) or "authentication" in str(api_error).lower():
                        print("  🔧 建议: 检查API密钥是否有效")
                    elif "quota" in str(api_error).lower():
                        print("  🔧 建议: 检查API配额是否充足")
                    return False
            else:
                print("  ❌ DeepSeek客户端创建失败")
                return False
                
        except Exception as e:
            print(f"  ❌ API连接性测试失败: {e}")
            return False
    
    def suggest_fixes(self):
        """提供修复建议"""
        print("\n💡 修复建议:")
        
        # 检查是否有任何API密钥配置
        has_any_key = any(status == "configured" for status in self.api_keys_status.values())
        
        if not has_any_key:
            print("  🔧 没有配置任何有效的API密钥，请按以下步骤操作:")
            print("     1. 编辑 .env 文件")
            print("     2. 添加以下任一API密钥:")
            print("        - DASHSCOPE_API_KEY=your_dashscope_api_key")
            print("        - DEEP_SEEK_API=your_deepseek_api_key")
            print("        - QWEN_API=your_qwen_api_key")
            print("     3. 重启应用程序")
        else:
            print("  🔧 已有部分API密钥配置，但可能存在问题:")
            
            for env_key, status in self.api_keys_status.items():
                if status == "invalid":
                    print(f"     - {env_key}: 密钥格式无效，请检查长度和格式")
                elif status == "missing":
                    print(f"     - {env_key}: 可选配置，用于备用服务")
        
        print("\n  📝 获取API密钥的方法:")
        print("     - 阿里云DashScope: https://dashscope.console.aliyun.com/")
        print("     - DeepSeek: https://platform.deepseek.com/")
        print("     - Qwen: https://help.aliyun.com/zh/model-studio/")
    
    def create_test_user(self):
        """创建测试用户"""
        print("\n👤 创建测试用户...")
        
        try:
            import asyncio
            from aurawell.database.connection import get_database
            from aurawell.models.user_models import UserProfile, UserCreate
            from aurawell.services.user_service import UserService
            
            async def create_user():
                db = await get_database()
                user_service = UserService(db)
                
                # 检查测试用户是否存在
                try:
                    existing_user = await user_service.get_user_profile("test_user_debug")
                    print("  ✅ 测试用户已存在")
                    return True
                except:
                    # 用户不存在，创建新用户
                    test_user_data = UserCreate(
                        username="test_user_debug",
                        email="test@example.com",
                        password="test_password",
                        profile=UserProfile(
                            age=30,
                            gender="male",
                            height=175.0,
                            weight=70.0,
                            activity_level="moderately_active",
                            health_goals=["general_wellness"],
                            dietary_preferences=[],
                            medical_conditions=[],
                            allergies=[]
                        )
                    )
                    
                    user = await user_service.create_user(test_user_data)
                    print("  ✅ 测试用户创建成功")
                    return True
            
            return asyncio.run(create_user())
            
        except Exception as e:
            print(f"  ❌ 创建测试用户失败: {e}")
            return False
    
    async def run_full_diagnosis(self):
        """运行完整诊断"""
        print("🔧 开始API密钥问题诊断和修复...")
        print("="*60)
        
        # 1. 检查.env文件
        env_exists = self.check_env_file()
        
        # 2. 检查API密钥
        keys_configured = self.check_api_keys()
        
        # 3. 测试API连接性
        if keys_configured:
            api_working = await self.test_api_connectivity()
        else:
            api_working = False
        
        # 4. 创建测试用户
        user_created = self.create_test_user()
        
        # 5. 提供修复建议
        self.suggest_fixes()
        
        # 总结
        print("\n" + "="*60)
        print("📊 诊断结果总结:")
        print(f"  .env文件: {'✅ 存在' if env_exists else '❌ 缺失'}")
        print(f"  API密钥: {'✅ 已配置' if keys_configured else '❌ 未配置'}")
        print(f"  API连接: {'✅ 正常' if api_working else '❌ 失败'}")
        print(f"  测试用户: {'✅ 就绪' if user_created else '❌ 失败'}")
        
        if api_working and user_created:
            print("\n🎉 所有问题已修复，聊天服务应该可以正常工作！")
        else:
            print("\n⚠️  仍有问题需要解决，请按照上述建议进行修复。")


async def main():
    """主函数"""
    fixer = APIKeyFixer()
    await fixer.run_full_diagnosis()


if __name__ == "__main__":
    asyncio.run(main())
