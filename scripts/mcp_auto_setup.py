#!/usr/bin/env python3
"""
AuraWell MCP 自动化设置脚本
自动检测并启动相关的MCP服务器，实现智能化开发环境
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPAutoSetup:
    """MCP服务器自动化设置和管理"""
    
    def __init__(self, config_path: str = ".cursor/mcp_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.running_servers = {}
        
    def _load_config(self) -> Dict:
        """加载MCP配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            return {}
    
    def check_environment(self) -> Dict[str, bool]:
        """检查环境依赖"""
        checks = {
            'node_js': self._check_nodejs(),
            'npm': self._check_npm(),
            'database': self._check_database(),
            'env_vars': self._check_env_variables()
        }
        
        logger.info("环境检查结果:")
        for check, status in checks.items():
            logger.info(f"  {check}: {'✓' if status else '✗'}")
            
        return checks
    
    def _check_nodejs(self) -> bool:
        """检查Node.js是否安装"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_npm(self) -> bool:
        """检查npm是否可用"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_database(self) -> bool:
        """检查数据库文件是否存在"""
        return Path("aurawell.db").exists()
    
    def _check_env_variables(self) -> bool:
        """检查必要的环境变量"""
        required_vars = ['BRAVE_API_KEY']
        optional_vars = ['NOTION_API_KEY', 'DEEPSEEK_API_KEY']
        
        missing_required = [var for var in required_vars if not os.getenv(var)]
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        
        if missing_required:
            logger.warning(f"缺少必需的环境变量: {missing_required}")
            return False
            
        if missing_optional:
            logger.info(f"缺少可选的环境变量: {missing_optional}")
            
        return True
    
    def install_mcp_packages(self, force_reinstall: bool = False) -> bool:
        """安装必要的MCP包"""
        packages = [
            "@modelcontextprotocol/server-sqlite",
            "@modelcontextprotocol/server-brave-search", 
            "@modelcontextprotocol/server-memory",
            "@modelcontextprotocol/server-sequential-thinking",
            "@modelcontextprotocol/server-quickchart",
            "@modelcontextprotocol/server-calculator",
            "@modelcontextprotocol/server-notion"
        ]
        
        logger.info("开始安装MCP包...")
        
        for package in packages:
            try:
                cmd = ['npm', 'install', '-g'] + (['-f'] if force_reinstall else []) + [package]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✓ 成功安装: {package}")
                else:
                    logger.error(f"✗ 安装失败: {package} - {result.stderr}")
                    return False
                    
            except Exception as e:
                logger.error(f"安装包时出错 {package}: {e}")
                return False
        
        logger.info("所有MCP包安装完成!")
        return True
    
    def start_auto_servers(self) -> Dict[str, bool]:
        """启动配置为自动启动的MCP服务器"""
        if not self.config.get('mcpServers'):
            logger.error("没有找到MCP服务器配置")
            return {}
        
        results = {}
        
        for server_name, server_config in self.config['mcpServers'].items():
            if server_config.get('autoStart', False):
                success = self._start_server(server_name, server_config)
                results[server_name] = success
                
                if success:
                    logger.info(f"✓ 成功启动服务器: {server_name}")
                else:
                    logger.error(f"✗ 启动失败: {server_name}")
        
        return results
    
    def _start_server(self, name: str, config: Dict) -> bool:
        """启动单个MCP服务器"""
        try:
            command = config['command']
            args = config.get('args', [])
            env_vars = config.get('env', {})
            
            # 准备环境变量
            env = os.environ.copy()
            for key, value in env_vars.items():
                # 替换环境变量占位符
                if value.startswith('${') and value.endswith('}'):
                    env_var_name = value[2:-1]
                    env_value = os.getenv(env_var_name)
                    if env_value:
                        env[key] = env_value
                    else:
                        logger.warning(f"环境变量 {env_var_name} 未设置，跳过服务器 {name}")
                        return False
                else:
                    env[key] = value
            
            # 启动服务器
            full_command = [command] + args
            logger.info(f"启动命令: {' '.join(full_command)}")
            
            process = subprocess.Popen(
                full_command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待一秒检查是否成功启动
            time.sleep(1)
            if process.poll() is None:
                self.running_servers[name] = {
                    'process': process,
                    'config': config,
                    'start_time': time.time()
                }
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"服务器 {name} 启动失败: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"启动服务器 {name} 时出错: {e}")
            return False
    
    def health_check(self) -> Dict[str, bool]:
        """检查运行中服务器的健康状态"""
        results = {}
        
        for name, server_info in self.running_servers.items():
            process = server_info['process']
            
            if process.poll() is None:
                # 进程仍在运行
                uptime = time.time() - server_info['start_time']
                results[name] = True
                logger.info(f"✓ {name} 运行正常 (运行时间: {uptime:.1f}秒)")
            else:
                # 进程已停止
                results[name] = False
                logger.error(f"✗ {name} 已停止运行")
                # 从运行列表中移除
                del self.running_servers[name]
        
        return results
    
    def stop_all_servers(self):
        """停止所有运行中的MCP服务器"""
        logger.info("正在停止所有MCP服务器...")
        
        for name, server_info in self.running_servers.items():
            process = server_info['process']
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✓ 成功停止: {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"强制终止: {name}")
            except Exception as e:
                logger.error(f"停止服务器 {name} 时出错: {e}")
        
        self.running_servers.clear()
    
    def suggest_tools_for_context(self, context: str) -> List[str]:
        """根据上下文建议合适的MCP工具"""
        suggestions = []
        auto_suggestions = self.config.get('auto_suggestions', {})
        
        if auto_suggestions.get('enabled', False):
            contexts = auto_suggestions.get('contexts', {})
            
            for context_name, context_config in contexts.items():
                triggers = context_config.get('triggers', [])
                
                # 检查是否有触发词匹配
                for trigger in triggers:
                    if trigger.lower() in context.lower():
                        suggested_tools = context_config.get('suggested_tools', [])
                        suggestions.extend(suggested_tools)
                        logger.info(f"匹配上下文 '{context_name}': 建议工具 {suggested_tools}")
                        break
        
        return list(set(suggestions))  # 去重
    
    def run_workflow(self, workflow_name: str) -> bool:
        """执行预定义的工作流"""
        workflows = self.config.get('integration_workflows', {})
        
        if workflow_name not in workflows:
            logger.error(f"工作流 '{workflow_name}' 未找到")
            return False
        
        workflow = workflows[workflow_name]
        logger.info(f"开始执行工作流: {workflow.get('name', workflow_name)}")
        
        for step in workflow.get('steps', []):
            tool = step.get('tool')
            action = step.get('action')
            description = step.get('description', '')
            
            logger.info(f"执行步骤: {description} (工具: {tool}, 动作: {action})")
            
            # 这里可以集成实际的工具调用逻辑
            # 目前只是日志记录
            time.sleep(0.5)  # 模拟执行时间
        
        logger.info(f"工作流 '{workflow_name}' 执行完成")
        return True

def main():
    """主函数"""
    print("🚀 AuraWell MCP 自动化设置")
    print("=" * 50)
    
    # 创建日志目录
    Path("logs").mkdir(exist_ok=True)
    
    # 初始化设置器
    setup = MCPAutoSetup()
    
    # 检查环境
    print("\n📋 检查环境依赖...")
    env_checks = setup.check_environment()
    
    if not all(env_checks.values()):
        print("❌ 环境检查失败，请解决上述问题后重试")
        return False
    
    # 安装MCP包
    print("\n📦 安装MCP包...")
    if not setup.install_mcp_packages():
        print("❌ MCP包安装失败")
        return False
    
    # 启动自动服务器
    print("\n🔥 启动MCP服务器...")
    server_results = setup.start_auto_servers()
    
    if server_results:
        print(f"✅ 成功启动 {sum(server_results.values())}/{len(server_results)} 个服务器")
        
        # 健康检查
        print("\n🔍 执行健康检查...")
        health_results = setup.health_check()
        
        # 示例：测试工具建议
        print("\n💡 测试智能工具建议...")
        test_contexts = [
            "我想分析用户的健康数据",
            "需要搜索最新的营养研究",
            "想要构建用户健康画像"
        ]
        
        for context in test_contexts:
            suggestions = setup.suggest_tools_for_context(context)
            print(f"  上下文: '{context}'")
            print(f"  建议工具: {suggestions}")
        
        print("\n🎉 MCP环境设置完成！")
        print("现在可以在Cursor中智能使用MCP工具了")
        
        return True
    else:
        print("❌ 没有成功启动任何服务器")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断操作")
        exit(1)
    except Exception as e:
        logger.error(f"脚本执行出错: {e}")
        exit(1) 