#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuraWell AI模型可用性测试
测试项目中所有生成式AI模型和服务的可用性
"""

import os
import sys
import asyncio
import unittest
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

# 导入项目模块
try:
    from aurawell.config.settings import AuraWellSettings
    from aurawell.core.deepseek_client import DeepSeekClient
    from aurawell.services.rag_service import RAGService
    from aurawell.core.service_factory import ServiceClientFactory
except ImportError as e:
    print(f"❌ 导入项目模块失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIModelTestResult:
    """AI模型测试结果"""
    
    def __init__(self, service_name: str, model_name: str, endpoint: str):
        self.service_name = service_name
        self.model_name = model_name
        self.endpoint = endpoint
        self.is_available = False
        self.response_time = 0.0
        self.error_message = ""
        self.test_response = ""
        self.api_key_configured = False
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'service_name': self.service_name,
            'model_name': self.model_name,
            'endpoint': self.endpoint,
            'is_available': self.is_available,
            'response_time': self.response_time,
            'error_message': self.error_message,
            'test_response': self.test_response[:100] + "..." if len(self.test_response) > 100 else self.test_response,
            'api_key_configured': self.api_key_configured,
            'timestamp': self.timestamp.isoformat()
        }


class AIModelsAvailabilityTest(unittest.TestCase):
    """AI模型可用性测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.settings = AuraWellSettings()
        self.test_results: List[AIModelTestResult] = []
        self.test_message = [{"role": "user", "content": "你好，请简单回复一句话测试连接。"}]
        
        # 加载环境变量
        self._load_env_file()
        
        print("\n" + "="*80)
        print("🤖 AuraWell AI模型可用性测试开始")
        print("="*80)
    
    def _load_env_file(self):
        """加载.env文件"""
        env_path = os.path.join(project_root, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            print(f"✅ 已加载环境变量文件: {env_path}")
        else:
            print(f"⚠️  环境变量文件不存在: {env_path}")
    
    def test_deepseek_models(self):
        """测试DeepSeek系列模型"""
        print("\n🧠 测试DeepSeek AI模型...")

        # 测试配置的模型列表 - 基于.env文件中的实际配置
        models_to_test = [
            # 从环境变量读取配置的模型
            (os.getenv("DEEPSEEK_SERIES_V3", "deepseek-v3"), "DeepSeek V3 (配置)"),
            (os.getenv("DEEPSEEK_SERIES_R1", "deepseek-r1-0528"), "DeepSeek R1 (配置)"),
            # 额外测试标准模型名称
            ("deepseek-v3", "DeepSeek V3 (标准)"),
            ("deepseek-r1", "DeepSeek R1 (标准)"),
        ]
        
        # 获取API配置
        api_key = (
            os.getenv('DASHSCOPE_API_KEY') or 
            os.getenv('QWEN_API') or 
            os.getenv('DEEP_SEEK_API') or 
            os.getenv('DEEPSEEK_API_KEY')
        )
        
        base_url = (
            os.getenv('DEEPSEEK_BASE_URL') or
            os.getenv('DASHSCOPE_BASE_URL') or
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        for model_name, display_name in models_to_test:
            result = AIModelTestResult("DeepSeek", display_name, base_url)
            result.model_name = model_name
            result.api_key_configured = bool(api_key)
            
            if not api_key:
                result.error_message = "API Key未配置"
                print(f"  ❌ {display_name}: API Key未配置")
                self.test_results.append(result)
                continue
            
            try:
                print(f"  🔄 测试 {display_name} ({model_name})...")
                start_time = datetime.now()
                
                # 创建客户端并测试
                client = DeepSeekClient(api_key=api_key, base_url=base_url)
                response = client.get_deepseek_response(
                    messages=self.test_message,
                    model_name=model_name,
                    max_tokens=50,
                    temperature=0.1
                )
                
                end_time = datetime.now()
                result.response_time = (end_time - start_time).total_seconds()
                result.is_available = True
                result.test_response = response.content
                
                print(f"  ✅ {display_name}: 可用 (响应时间: {result.response_time:.2f}s)")
                print(f"     响应: {response.content[:50]}...")
                
            except Exception as e:
                result.error_message = str(e)
                print(f"  ❌ {display_name}: 不可用 - {str(e)}")
            
            self.test_results.append(result)
    
    def test_qwen_models(self):
        """测试Qwen系列模型"""
        print("\n🌟 测试Qwen AI模型...")

        # 测试配置的模型列表 - 基于.env文件中的实际配置
        models_to_test = [
            # 从环境变量读取配置的模型
            (os.getenv("QWEN_PLUS", "qwen-plus"), "Qwen Plus (配置)"),
            (os.getenv("QWEN_FAST", "qwen-turbo"), "Qwen Turbo (配置)"),
            # 标准Qwen模型
            ("qwen-max", "Qwen Max"),
            ("qwen-long", "Qwen Long"),
            # Qwen3系列（仅在环境变量中配置时测试）
        ]

        # 如果配置了Qwen3系列，则添加到测试列表（仅测试已配置的）
        qwen3_models = [
            ("QWEN3_PLUS", "qwen3-plus", "Qwen3 Plus"),
            ("QWEN3_TURBO", "qwen3-turbo", "Qwen3 Turbo"),
            ("QWEN3_MAX", "qwen3-max", "Qwen3 Max"),
        ]

        for env_key, model_name, display_name in qwen3_models:
            if os.getenv(env_key):
                models_to_test.append((os.getenv(env_key), f"{display_name} (配置)"))
                print(f"  📝 检测到配置的Qwen3模型: {display_name}")

        # 移除重复项
        seen = set()
        unique_models = []
        for model_name, display_name in models_to_test:
            if model_name not in seen:
                seen.add(model_name)
                unique_models.append((model_name, display_name))
        models_to_test = unique_models
        
        # 获取API配置
        api_key = (
            os.getenv('DASHSCOPE_API_KEY') or 
            os.getenv('QWEN_API') or 
            os.getenv('ALIBABA_QWEN_API_KEY')
        )
        
        base_url = (
            os.getenv('DASHSCOPE_BASE_URL') or
            "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        for model_name, display_name in models_to_test:
            result = AIModelTestResult("Qwen", display_name, base_url)
            result.model_name = model_name
            result.api_key_configured = bool(api_key)
            
            if not api_key:
                result.error_message = "API Key未配置"
                print(f"  ❌ {display_name}: API Key未配置")
                self.test_results.append(result)
                continue
            
            try:
                print(f"  🔄 测试 {display_name} ({model_name})...")
                start_time = datetime.now()
                
                # 创建客户端并测试
                client = DeepSeekClient(api_key=api_key, base_url=base_url)
                response = client.get_deepseek_response(
                    messages=self.test_message,
                    model_name=model_name,
                    max_tokens=50,
                    temperature=0.1
                )
                
                end_time = datetime.now()
                result.response_time = (end_time - start_time).total_seconds()
                result.is_available = True
                result.test_response = response.content
                
                print(f"  ✅ {display_name}: 可用 (响应时间: {result.response_time:.2f}s)")
                print(f"     响应: {response.content[:50]}...")
                
            except Exception as e:
                result.error_message = str(e)
                print(f"  ❌ {display_name}: 不可用 - {str(e)}")
            
            self.test_results.append(result)

    def test_default_model_configuration(self):
        """测试默认模型配置"""
        print("\n⚙️  测试默认模型配置...")

        # 测试默认模型
        default_model = os.getenv("DASHSCOPE_DEFAULT_MODEL", "deepseek-v3")
        result = AIModelTestResult("DefaultModel", f"Default Model ({default_model})", "Configuration")

        try:
            print(f"  🔄 测试默认模型: {default_model}...")
            start_time = datetime.now()

            # 获取API配置
            api_key = (
                os.getenv('DASHSCOPE_API_KEY') or
                os.getenv('QWEN_API') or
                os.getenv('DEEP_SEEK_API')
            )

            base_url = (
                os.getenv('DASHSCOPE_BASE_URL') or
                "https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            if not api_key:
                result.error_message = "API Key未配置"
                print(f"  ❌ 默认模型: API Key未配置")
                self.test_results.append(result)
                return

            # 创建客户端并测试
            client = DeepSeekClient(api_key=api_key, base_url=base_url)
            response = client.get_deepseek_response(
                messages=self.test_message,
                model_name=default_model,
                max_tokens=50,
                temperature=0.1
            )

            end_time = datetime.now()
            result.response_time = (end_time - start_time).total_seconds()
            result.is_available = True
            result.test_response = response.content
            result.api_key_configured = True

            print(f"  ✅ 默认模型 ({default_model}): 可用 (响应时间: {result.response_time:.2f}s)")
            print(f"     响应: {response.content[:50]}...")

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ 默认模型 ({default_model}): 不可用 - {str(e)}")

        self.test_results.append(result)

    async def test_rag_service(self):
        """测试RAG服务"""
        print("\n📚 测试RAG服务...")
        
        result = AIModelTestResult("RAG", "RAG Service", "Local/Cloud")
        
        try:
            print("  🔄 测试RAG服务...")
            start_time = datetime.now()
            
            # 创建RAG服务实例
            rag_service = RAGService()
            
            # 测试RAG检索
            test_query = "营养建议"
            rag_results = await rag_service.retrieve_from_rag(test_query, k=2)
            
            end_time = datetime.now()
            result.response_time = (end_time - start_time).total_seconds()
            result.is_available = len(rag_results) > 0
            result.test_response = f"检索到 {len(rag_results)} 条结果"
            
            if result.is_available:
                print(f"  ✅ RAG服务: 可用 (响应时间: {result.response_time:.2f}s)")
                print(f"     检索结果: {len(rag_results)} 条")
                for i, res in enumerate(rag_results[:2], 1):
                    print(f"     {i}. {res[:50]}...")
            else:
                result.error_message = "RAG服务返回空结果"
                print("  ❌ RAG服务: 返回空结果")
                
        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ RAG服务: 不可用 - {str(e)}")
        
        self.test_results.append(result)
    
    def test_mcp_services(self):
        """测试MCP工具服务"""
        print("\n🔧 测试MCP工具服务...")
        
        # 测试的MCP服务列表
        mcp_services = [
            ("Brave Search", "BRAVE_API_KEY", "https://api.search.brave.com"),
            ("GitHub API", "GITHUB_TOKEN", "https://api.github.com"),
            ("Weather API", "WEATHER_API_KEY", "weather service"),
            ("Figma API", "FIGMA_TOKEN", "https://api.figma.com"),
        ]
        
        for service_name, env_key, endpoint in mcp_services:
            result = AIModelTestResult("MCP", service_name, endpoint)
            
            api_key = os.getenv(env_key)
            result.api_key_configured = bool(api_key)
            
            if api_key:
                result.is_available = True
                result.test_response = "API Key已配置"
                print(f"  ✅ {service_name}: API Key已配置")
            else:
                result.error_message = f"{env_key}未配置"
                print(f"  ❌ {service_name}: {env_key}未配置")
            
            self.test_results.append(result)

    def test_service_factory(self):
        """测试服务工厂"""
        print("\n🏭 测试服务工厂...")

        try:
            print("  🔄 测试DeepSeek客户端工厂...")
            deepseek_client = ServiceClientFactory.get_deepseek_client()

            result = AIModelTestResult("ServiceFactory", "DeepSeek Client", "Factory")
            result.is_available = deepseek_client is not None
            result.test_response = f"客户端类型: {type(deepseek_client).__name__}"

            if result.is_available:
                print(f"  ✅ DeepSeek客户端工厂: 可用")
                print(f"     客户端类型: {type(deepseek_client).__name__}")
            else:
                result.error_message = "无法创建DeepSeek客户端"
                print("  ❌ DeepSeek客户端工厂: 不可用")

            self.test_results.append(result)

        except Exception as e:
            result = AIModelTestResult("ServiceFactory", "DeepSeek Client", "Factory")
            result.error_message = str(e)
            print(f"  ❌ 服务工厂测试失败: {str(e)}")
            self.test_results.append(result)

        try:
            print("  🔄 测试MCP工具接口工厂...")
            mcp_interface = ServiceClientFactory.get_mcp_tools_interface()

            result = AIModelTestResult("ServiceFactory", "MCP Tools", "Factory")
            result.is_available = mcp_interface is not None
            result.test_response = f"接口类型: {type(mcp_interface).__name__}"

            if result.is_available:
                print(f"  ✅ MCP工具接口工厂: 可用")
                print(f"     接口类型: {type(mcp_interface).__name__}")
            else:
                result.error_message = "无法创建MCP工具接口"
                print("  ❌ MCP工具接口工厂: 不可用")

            self.test_results.append(result)

        except Exception as e:
            result = AIModelTestResult("ServiceFactory", "MCP Tools", "Factory")
            result.error_message = str(e)
            print(f"  ❌ MCP工具接口工厂测试失败: {str(e)}")
            self.test_results.append(result)

    def test_environment_configuration(self):
        """测试环境配置"""
        print("\n⚙️  测试环境配置...")

        # 检查关键环境变量
        env_vars_to_check = [
            ("DASHSCOPE_API_KEY", "阿里云DashScope API密钥"),
            ("QWEN_API", "Qwen API密钥"),
            ("DEEP_SEEK_API", "DeepSeek API密钥"),
            ("ALIBABA_CLOUD_ACCESS_KEY_ID", "阿里云访问密钥ID"),
            ("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "阿里云访问密钥Secret"),
            ("DASH_VECTOR_API", "DashVector API密钥"),
            ("BRAVE_API_KEY", "Brave搜索API密钥"),
            ("GITHUB_TOKEN", "GitHub Token"),
            ("WEATHER_API_KEY", "天气API密钥"),
            ("FIGMA_TOKEN", "Figma Token"),
        ]

        configured_count = 0
        total_count = len(env_vars_to_check)

        for env_var, description in env_vars_to_check:
            value = os.getenv(env_var)
            if value:
                configured_count += 1
                print(f"  ✅ {description}: 已配置")
            else:
                print(f"  ❌ {description}: 未配置")

        result = AIModelTestResult("Environment", "Configuration", "Local")
        result.is_available = configured_count > 0
        result.test_response = f"已配置 {configured_count}/{total_count} 个环境变量"

        if configured_count == 0:
            result.error_message = "没有配置任何API密钥"

        print(f"\n  📊 环境配置统计: {configured_count}/{total_count} 个API密钥已配置")
        self.test_results.append(result)

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📊 AI模型可用性测试报告")
        print("="*80)

        # 统计信息
        total_tests = len(self.test_results)
        available_services = sum(1 for r in self.test_results if r.is_available)
        configured_apis = sum(1 for r in self.test_results if r.api_key_configured)

        print(f"\n📈 测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  可用服务: {available_services}")
        print(f"  已配置API: {configured_apis}")
        print(f"  成功率: {(available_services/total_tests*100):.1f}%")

        # 按服务分组显示结果
        services = {}
        for result in self.test_results:
            if result.service_name not in services:
                services[result.service_name] = []
            services[result.service_name].append(result)

        for service_name, results in services.items():
            print(f"\n🔧 {service_name} 服务:")
            for result in results:
                status = "✅ 可用" if result.is_available else "❌ 不可用"
                api_status = "🔑 已配置" if result.api_key_configured else "🔓 未配置"

                print(f"  {status} {result.model_name}")
                if result.response_time > 0:
                    print(f"    响应时间: {result.response_time:.2f}s")
                if result.test_response:
                    print(f"    测试响应: {result.test_response}")
                if result.error_message:
                    print(f"    错误信息: {result.error_message}")
                if hasattr(result, 'api_key_configured'):
                    print(f"    API状态: {api_status}")
                print()

        # 保存详细报告到文件
        self._save_detailed_report()

        # 生成建议
        self._generate_recommendations()

    def _save_detailed_report(self):
        """保存详细报告到文件"""
        try:
            report_data = {
                'test_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(self.test_results),
                    'available_services': sum(1 for r in self.test_results if r.is_available),
                    'configured_apis': sum(1 for r in self.test_results if r.api_key_configured),
                },
                'results': [result.to_dict() for result in self.test_results]
            }

            report_file = os.path.join(project_root, 'tests', 'ai_models_test_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            print(f"📄 详细报告已保存: {report_file}")

        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")

    def _generate_recommendations(self):
        """生成配置建议"""
        print("\n💡 配置建议:")

        # 检查未配置的关键服务
        unconfigured_services = []
        for result in self.test_results:
            if not result.api_key_configured and result.service_name in ['DeepSeek', 'Qwen']:
                unconfigured_services.append(result)

        if unconfigured_services:
            print("  🔧 建议配置以下API密钥以启用AI功能:")
            for result in unconfigured_services:
                if result.service_name == 'DeepSeek':
                    print("    - DASHSCOPE_API_KEY 或 DEEP_SEEK_API (DeepSeek AI服务)")
                elif result.service_name == 'Qwen':
                    print("    - QWEN_API 或 DASHSCOPE_API_KEY (Qwen AI服务)")

        # 检查RAG服务
        rag_results = [r for r in self.test_results if r.service_name == 'RAG']
        if rag_results and not rag_results[0].is_available:
            print("    - ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET (RAG服务)")

        # 检查MCP服务
        mcp_results = [r for r in self.test_results if r.service_name == 'MCP' and not r.api_key_configured]
        if mcp_results:
            print("  🔧 可选配置以下API密钥以启用扩展功能:")
            for result in mcp_results:
                if "Brave" in result.model_name:
                    print("    - BRAVE_API_KEY (网络搜索功能)")
                elif "GitHub" in result.model_name:
                    print("    - GITHUB_TOKEN (GitHub集成)")
                elif "Weather" in result.model_name:
                    print("    - WEATHER_API_KEY (天气信息)")
                elif "Figma" in result.model_name:
                    print("    - FIGMA_TOKEN (设计工具集成)")

        print("\n📝 配置方法:")
        print("  1. 编辑项目根目录下的 .env 文件")
        print("  2. 添加相应的API密钥")
        print("  3. 重新运行测试验证配置")

    async def run_all_tests(self):
        """运行所有测试"""
        # 同步测试
        self.test_default_model_configuration()
        self.test_deepseek_models()
        self.test_qwen_models()
        self.test_mcp_services()
        self.test_service_factory()
        self.test_environment_configuration()

        # 异步测试
        await self.test_rag_service()

        # 生成报告
        self.generate_test_report()


async def main():
    """主函数"""
    try:
        # 创建测试实例
        test_instance = AIModelsAvailabilityTest()
        test_instance.setUp()

        # 运行所有测试
        await test_instance.run_all_tests()

        print("\n🎉 AI模型可用性测试完成!")

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(main())
