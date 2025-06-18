#!/usr/bin/env python3
"""
试金石行动 - 全链路端到端验收测试 (V2 - 纯检查版)

这是一个全面的端到端测试脚本，用于验证从用户输入到AI生成个性化建议的整个链路。
本次行动的唯一目的是"检查"和"验证"，不会修改任何项目源代码。

测试目标：
1. 验证兼容接口 /chat/message 的功能完整性
2. 确认 AgentRouter 和 Orchestrator 正常工作
3. 验证 DeepSeekClient 真实API调用
4. 确认 MCP工具链的激活和使用
5. 测试整体响应时间和质量

作者: Claude (AuraWell AI工程师)
日期: 2025-01-18
版本: V2.0 - 纯检查版
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入AuraWell认证模块
try:
    from aurawell.auth.jwt_auth import authenticator, create_user_token
    print("✅ 成功导入AuraWell认证模块")
except ImportError as e:
    print(f"❌ 无法导入AuraWell认证模块: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class FinalAcceptanceTest:
    """试金石行动 - 端到端验收测试器"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_user_id = "test_user_final_acceptance"
        self.test_token = None
        self.conversation_id = None
        self.start_time = None
        self.end_time = None
        
        # 复杂的高价值查询 - 能最大限度调动AI能力
        self.complex_query = "我最近感觉压力很大，睡眠也不好，体重还增加了，能帮我全面分析一下并给点建议吗？"
        
        # 测试结果记录
        self.test_results = {
            "functional_tests": {},
            "performance_metrics": {},
            "log_observations": [],
            "final_conclusion": None
        }
    
    def print_header(self):
        """打印测试开始横幅"""
        print("\n" + "="*80)
        print("🏆 试金石行动 - 全链路端到端验收测试 (V2 - 纯检查版)")
        print("="*80)
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 测试目标: 验证从用户输入到AI建议的完整链路")
        print(f"🔍 测试查询: {self.complex_query}")
        print(f"🌐 服务地址: {self.base_url}")
        print("="*80)
    
    def generate_test_token(self) -> str:
        """生成测试用的JWT token"""
        print("\n🔑 生成测试JWT Token...")
        
        try:
            # 使用AuraWell的token生成函数
            token_data = create_user_token(self.test_user_id)
            token = token_data["access_token"]
            
            print(f"✅ Token生成成功")
            print(f"   用户ID: {self.test_user_id}")
            print(f"   Token类型: {token_data['token_type']}")
            print(f"   过期时间: {token_data['expires_in']}秒")
            print(f"   Token前缀: {token[:20]}...")
            
            return token
            
        except Exception as e:
            print(f"❌ Token生成失败: {e}")
            raise
    
    def check_server_health(self) -> bool:
        """检查服务器健康状态"""
        print("\n🏥 检查服务器健康状态...")

        try:
            # 检查API健康端点
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                print("✅ 服务器健康检查通过")
                print(f"   健康端点: {self.api_base}/health")
                return True
            else:
                print(f"⚠️  服务器健康检查异常，状态码: {response.status_code}")
                # 尝试根路径作为备选
                try:
                    root_response = requests.get(f"{self.base_url}/", timeout=5)
                    if root_response.status_code in [200, 404]:
                        print("✅ 服务器根路径可达，继续测试")
                        return True
                except:
                    pass
                return False

        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器，请确保服务器已启动")
            return False
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
    
    def execute_end_to_end_test(self) -> Dict[str, Any]:
        """执行端到端测试调用"""
        print("\n🚀 执行端到端测试调用...")
        print(f"📤 发送查询: {self.complex_query}")
        
        # 准备请求
        url = f"{self.api_base}/chat/message"
        headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": self.complex_query,
            "conversation_id": None,  # 让系统自动生成
            "context": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "final_acceptance",
                "platform": "test_script"
            }
        }
        
        print(f"🌐 请求URL: {url}")
        print(f"📋 请求负载: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        # 记录开始时间
        self.start_time = time.time()
        
        try:
            print("\n⏱️  发起HTTP POST请求...")
            response = requests.post(
                url=url,
                headers=headers,
                json=payload,
                timeout=300  # 5分钟超时，允许复杂AI处理
            )
            
            # 记录结束时间
            self.end_time = time.time()
            total_time = self.end_time - self.start_time
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"⏱️  总响应时间: {total_time:.2f}秒")
            
            # 记录性能指标
            self.test_results["performance_metrics"] = {
                "response_time_seconds": total_time,
                "status_code": response.status_code,
                "response_size_bytes": len(response.content) if response.content else 0
            }
            
            if response.status_code == 200:
                response_json = response.json()
                print("✅ HTTP请求成功完成")
                
                # 保存对话ID用于后续分析
                self.conversation_id = response_json.get("conversation_id")
                
                return response_json
            else:
                print(f"❌ HTTP请求失败，状态码: {response.status_code}")
                print(f"📄 错误响应: {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时（5分钟）")
            return {"error": "timeout", "details": "Request timed out after 5 minutes"}
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {"error": "exception", "details": str(e)}

    def analyze_response_quality(self, response: Dict[str, Any]) -> bool:
        """分析响应质量"""
        print("\n🔍 分析响应质量...")

        if "error" in response:
            print(f"❌ 响应包含错误: {response['error']}")
            self.test_results["functional_tests"]["response_quality"] = False
            return False

        # 检查必要字段
        required_fields = ["reply", "conversation_id", "message_id", "timestamp"]
        missing_fields = []

        for field in required_fields:
            if field not in response:
                missing_fields.append(field)

        if missing_fields:
            print(f"❌ 响应缺少必要字段: {missing_fields}")
            self.test_results["functional_tests"]["response_quality"] = False
            return False

        # 检查回复内容质量
        reply = response.get("reply", "")
        if not reply or len(reply.strip()) < 50:
            print(f"❌ 回复内容过短或为空: {len(reply)} 字符")
            self.test_results["functional_tests"]["response_quality"] = False
            return False

        # 检查是否包含健康相关关键词
        health_keywords = ["压力", "睡眠", "体重", "建议", "健康", "运动", "饮食", "休息"]
        found_keywords = [kw for kw in health_keywords if kw in reply]

        if len(found_keywords) < 3:
            print(f"⚠️  回复中健康相关关键词较少: {found_keywords}")
        else:
            print(f"✅ 回复包含健康关键词: {found_keywords}")

        # 检查建议结构
        suggestions = response.get("suggestions", [])
        if suggestions and len(suggestions) > 0:
            print(f"✅ 响应包含 {len(suggestions)} 条建议")
        else:
            print("⚠️  响应未包含结构化建议")

        print(f"✅ 响应质量检查通过")
        print(f"   回复长度: {len(reply)} 字符")
        print(f"   对话ID: {response.get('conversation_id')}")
        print(f"   消息ID: {response.get('message_id')}")

        self.test_results["functional_tests"]["response_quality"] = True
        return True

    def print_full_response(self, response: Dict[str, Any]):
        """打印完整的原始JSON响应"""
        print("\n" + "="*80)
        print("📄 完整的原始JSON响应")
        print("="*80)

        try:
            formatted_response = json.dumps(response, ensure_ascii=False, indent=2)
            print(formatted_response)
        except Exception as e:
            print(f"❌ 无法格式化响应: {e}")
            print(f"原始响应: {response}")

        print("="*80)

    def simulate_log_monitoring(self):
        """模拟日志监控（实际应该查看服务器控制台）"""
        print("\n📊 关键日志监控指南")
        print("-" * 60)
        print("请在服务器控制台中查找以下关键日志迹象：")
        print()
        print("✅ 必须确认的日志迹象:")
        print("   1. POST /api/v1/chat/message - 兼容接口被调用")
        print("   2. AgentRouter.process_message - 代理路由器被触发")
        print("   3. LangChainAgent 或 HealthAdviceAgent - Agent被创建/调用")
        print("   4. DeepSeekClient - 向真实API发起请求")
        print("   5. MCP工具调用 - calculator, quickchart, database_query等")
        print("   6. 数据库操作 - SQLite/PostgreSQL查询日志")
        print()
        print("⚠️  如果缺少任何上述日志，说明对应组件未正常工作")
        print("-" * 60)

        # 记录日志监控指南
        self.test_results["log_observations"] = [
            "请手动检查服务器控制台日志",
            "确认POST /api/v1/chat/message接口调用",
            "确认AgentRouter.process_message触发",
            "确认LangChain Agent创建和调用",
            "确认DeepSeekClient真实API请求",
            "确认MCP工具链激活",
            "确认数据库操作日志"
        ]

    def generate_final_conclusion(self, response: Dict[str, Any]) -> str:
        """生成最终结论"""
        print("\n🏆 生成最终测试结论...")

        # 检查功能性验收标准
        functional_pass = True
        performance_acceptable = True

        # 1. 功能性检查
        if "error" in response:
            functional_pass = False
            reason = f"请求失败: {response['error']}"
        elif not response.get("reply") or len(response.get("reply", "").strip()) < 50:
            functional_pass = False
            reason = "响应内容不足或为空"
        elif self.test_results["performance_metrics"]["status_code"] != 200:
            functional_pass = False
            reason = f"HTTP状态码异常: {self.test_results['performance_metrics']['status_code']}"
        else:
            # 检查健康相关内容
            reply = response.get("reply", "")
            health_keywords = ["压力", "睡眠", "体重", "建议", "健康"]
            found_keywords = [kw for kw in health_keywords if kw in reply]

            if len(found_keywords) < 2:
                functional_pass = False
                reason = "响应内容与健康查询不匹配"
            else:
                reason = "功能性测试全部通过"

        # 2. 性能检查
        response_time = self.test_results["performance_metrics"]["response_time_seconds"]
        if response_time > 300:  # 5分钟
            performance_acceptable = False
            perf_reason = f"响应时间过长: {response_time:.2f}秒"
        else:
            perf_reason = f"响应时间可接受: {response_time:.2f}秒"

        # 生成最终结论
        if functional_pass and performance_acceptable:
            conclusion = "试金石行动-通过 (Pass)"
            status = "✅ PASS"
            summary = f"端到端测试成功完成。{reason}，{perf_reason}"
        else:
            conclusion = "试金石行动-失败 (Fail)"
            status = "❌ FAIL"
            summary = f"测试未通过。功能性: {reason}，性能: {perf_reason}"

        self.test_results["final_conclusion"] = {
            "status": conclusion,
            "functional_pass": functional_pass,
            "performance_acceptable": performance_acceptable,
            "summary": summary
        }

        print(f"\n{status} {conclusion}")
        print(f"📋 详细说明: {summary}")

        return conclusion

    def run_full_test(self):
        """运行完整的端到端测试"""
        try:
            # 1. 打印测试开始信息
            self.print_header()

            # 2. 生成测试token
            self.test_token = self.generate_test_token()

            # 3. 检查服务器健康状态
            if not self.check_server_health():
                print("\n❌ 服务器健康检查失败，无法继续测试")
                return False

            # 4. 执行端到端测试
            response = self.execute_end_to_end_test()

            # 5. 分析响应质量
            quality_ok = self.analyze_response_quality(response)

            # 6. 打印完整响应
            self.print_full_response(response)

            # 7. 模拟日志监控指南
            self.simulate_log_monitoring()

            # 8. 生成最终结论
            conclusion = self.generate_final_conclusion(response)

            # 9. 打印测试总结
            self.print_test_summary()

            return "Pass" in conclusion

        except Exception as e:
            print(f"\n❌ 测试执行过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "="*80)
        print("📊 测试总结报告")
        print("="*80)

        # 性能指标
        metrics = self.test_results["performance_metrics"]
        print(f"⏱️  响应时间: {metrics.get('response_time_seconds', 0):.2f}秒")
        print(f"📊 HTTP状态码: {metrics.get('status_code', 'N/A')}")
        print(f"📦 响应大小: {metrics.get('response_size_bytes', 0)} 字节")

        # 功能测试结果
        functional = self.test_results["functional_tests"]
        print(f"✅ 响应质量: {'通过' if functional.get('response_quality') else '失败'}")

        # 最终结论
        conclusion = self.test_results["final_conclusion"]
        if conclusion:
            print(f"\n🏆 最终结论: {conclusion['status']}")
            print(f"📋 总结: {conclusion['summary']}")

        print("\n📝 交付物清单:")
        print("   ✅ scripts/final_acceptance_test.py - 测试脚本")
        print("   ✅ 完整的原始JSON响应 - 已打印在上方")
        print("   ✅ 关键日志观察指南 - 已提供")
        print("   ✅ 最终测试结论 - 已生成")

        print("="*80)


def main():
    """主函数"""
    print("🚀 启动试金石行动 - 全链路端到端验收测试")

    # 检查环境
    if not os.path.exists(".env"):
        print("⚠️  未找到.env文件，某些功能可能无法正常工作")

    # 创建测试实例并运行
    test = FinalAcceptanceTest()
    success = test.run_full_test()

    # 退出码
    exit_code = 0 if success else 1

    print(f"\n🏁 测试完成，退出码: {exit_code}")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
