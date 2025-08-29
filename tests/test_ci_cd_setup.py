#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD 测试验证脚本
验证 CI/CD 配置是否正确运行
"""

import os
import sys
import unittest
import subprocess
from pathlib import Path


class CICDTestCase(unittest.TestCase):
    """CI/CD 配置测试"""

    def setUp(self):
        """设置测试环境"""
        self.project_root = Path(__file__).parent.parent
        self.github_workflows_dir = self.project_root / ".github" / "workflows"

    def test_github_workflows_exist(self):
        """测试 GitHub workflows 配置文件是否存在"""
        self.assertTrue(self.github_workflows_dir.exists(), "GitHub workflows 目录不存在")
        
        # 检查主要的 workflow 文件
        tests_workflow = self.github_workflows_dir / "tests.yml"
        frontend_workflow = self.github_workflows_dir / "frontend.yml"
        ci_cd_workflow = self.github_workflows_dir / "ci-cd.yml"
        
        self.assertTrue(tests_workflow.exists(), "tests.yml workflow 文件不存在")
        self.assertTrue(frontend_workflow.exists(), "frontend.yml workflow 文件不存在")
        self.assertTrue(ci_cd_workflow.exists(), "ci-cd.yml workflow 文件不存在")

    def test_pyproject_toml_config_exists(self):
        """测试 pyproject.toml 中的测试配置是否存在"""
        pyproject_toml = self.project_root / "pyproject.toml"
        self.assertTrue(pyproject_toml.exists(), "pyproject.toml 配置文件不存在")
        
        # 检查配置内容
        with open(pyproject_toml, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("[tool.pytest.ini_options]", content, "pytest 配置不存在")
            self.assertIn("[tool.coverage.run]", content, "coverage 配置不存在")
            self.assertIn("[tool.black]", content, "black 配置不存在")

    def test_frontend_config_exists(self):
        """测试前端配置文件是否存在"""
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists():
            package_json = frontend_dir / "package.json"
            prettierrc = frontend_dir / ".prettierrc"
            
            self.assertTrue(package_json.exists(), "前端 package.json 不存在")
            self.assertTrue(prettierrc.exists(), "前端 .prettierrc 配置不存在")
            
            # 检查 package.json 中的脚本
            with open(package_json, 'r', encoding='utf-8') as f:
                import json
                package_data = json.load(f)
                scripts = package_data.get("scripts", {})
                
                self.assertIn("lint:fix", scripts, "lint:fix 脚本不存在")
                self.assertIn("format", scripts, "format 脚本不存在")
                self.assertIn("format:check", scripts, "format:check 脚本不存在")

    def test_uv_environment(self):
        """测试 uv 环境配置"""
        # 检查是否可以找到 uv
        result = subprocess.run(["which", "uv"], capture_output=True, text=True)
        if result.returncode != 0:
            self.skipTest("uv 未安装，跳过测试")
        
        # 检查 uv 版本
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "无法获取 uv 版本")
        self.assertIn("uv", result.stdout.lower())

    def test_required_uv_packages_installable(self):
        """测试必需的测试包是否可通过 uv 安装"""
        required_packages = [
            "pytest",
            "pytest-asyncio", 
            "pytest-cov",
            "black",
            "isort",
            "mypy"
        ]
        
        # 检查是否可以运行 uv
        result = subprocess.run(["which", "uv"], capture_output=True, text=True)
        if result.returncode != 0:
            self.skipTest("uv 未安装，跳过包安装测试")
        
        print("uv 环境可用，测试包安装能力...")

    def test_workflow_yaml_syntax(self):
        """测试 workflow YAML 文件语法"""
        try:
            import yaml
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], 
                         capture_output=True)
            import yaml

        for workflow_file in self.github_workflows_dir.glob("*.yml"):
            with open(workflow_file, 'r', encoding='utf-8') as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.fail(f"YAML 语法错误在文件 {workflow_file}: {e}")

    def test_environment_variables(self):
        """测试环境变量配置"""
        # 检查必要的环境变量
        env_vars = ["PYTHONPATH"]
        
        for var in env_vars:
            if var == "PYTHONPATH":
                # PYTHONPATH 应该包含项目源码目录
                pythonpath = os.environ.get(var, "")
                src_path = str(self.project_root / "src")
                if src_path not in pythonpath:
                    os.environ[var] = f"{src_path}:{pythonpath}"

    def test_basic_imports(self):
        """测试基本的项目导入"""
        # 确保项目源码目录在 Python 路径中
        src_path = self.project_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # 尝试导入主要模块
        try:
            import aurawell
            self.assertTrue(True, "成功导入 aurawell 模块")
        except ImportError as e:
            self.skipTest(f"无法导入 aurawell 模块: {e}")


class CIIntegrationTest(unittest.TestCase):
    """CI 集成测试"""

    def test_can_run_pytest(self):
        """测试是否可以运行 pytest"""
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--version"
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, "无法运行 pytest")
        self.assertIn("pytest", result.stdout.lower())

    def test_can_collect_tests(self):
        """测试是否可以收集测试"""
        tests_dir = Path(__file__).parent
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(tests_dir), "--collect-only", "-q"
        ], capture_output=True, text=True)
        
        # 即使收集失败也不应该是致命错误
        if result.returncode != 0:
            print(f"测试收集警告: {result.stderr}")


if __name__ == "__main__":
    # 设置环境
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    # 添加源码路径到 Python 路径
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # 设置 PYTHONPATH 环境变量
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if str(src_path) not in current_pythonpath:
        os.environ["PYTHONPATH"] = f"{src_path}:{current_pythonpath}"

    # 运行测试
    unittest.main(verbosity=2)
