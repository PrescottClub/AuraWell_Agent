# AuraWell 项目测试文档

本文档介绍如何使用pytest运行AuraWell项目的测试。

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest配置和fixtures
├── pytest.ini              # pytest配置文件
├── README.md                # 本文档
├── run_tests.py             # Python测试运行脚本
├── run_tests.sh             # Bash测试运行脚本
├── quick_test.py            # 快速测试脚本
├── verify_setup.py          # 测试环境验证脚本
├── test_basic.py            # 基础功能测试
├── test_enhanced_rag.py     # 增强RAG功能测试
├── test_oss_integration.py  # OSS集成测试
└── test_rag_index.py        # RAG索引功能测试
```

## 快速开始

### 1. 验证测试环境

首先验证pytest测试环境是否正确配置：

```bash
python tests/verify_setup.py
```

### 2. 环境准备

确保您在正确的conda环境中：

```bash
conda activate AuraWellPython310
```

安装pytest（如果尚未安装）：

```bash
pip install pytest pytest-cov
```

### 2. 运行测试

#### 方法一：使用交互式脚本（推荐）

```bash
cd /path/to/AuraWell
./tests/run_tests.sh
```

这将显示一个交互式菜单，您可以选择要运行的测试类型。

#### 方法二：使用命令行参数

```bash
# 运行所有测试
./tests/run_tests.sh all

# 运行RAG相关测试
./tests/run_tests.sh rag

# 运行OSS相关测试
./tests/run_tests.sh oss

# 运行快速测试（排除慢速测试）
./tests/run_tests.sh fast

# 生成覆盖率报告
./tests/run_tests.sh coverage
```

#### 方法三：直接使用pytest

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_basic.py -v

# 运行带特定标记的测试
python -m pytest tests/ -m "rag" -v

# 排除慢速测试
python -m pytest tests/ -m "not slow" -v

# 生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term -v
```

## 测试标记

项目使用以下pytest标记来分类测试：

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.rag` - RAG功能相关测试
- `@pytest.mark.oss` - OSS功能相关测试
- `@pytest.mark.api` - API功能相关测试
- `@pytest.mark.slow` - 慢速测试（可能需要较长时间）

## 测试文件说明

### test_basic.py
- 基础功能测试
- 环境配置验证
- 项目结构检查
- 参数化测试示例

### test_rag_index.py
- RAG索引功能测试
- 文件导出和分析测试
- TopK检索功能测试
- 错误处理测试

### test_enhanced_rag.py
- 增强RAG功能测试
- 语言检测测试
- 翻译功能测试
- 文献提炼测试
- 向量化功能测试

### test_oss_integration.py
- OSS云存储集成测试
- 配置加载测试
- 文件索引管理测试
- arXiv集成测试
- 批量处理测试

## 配置文件

### conftest.py
提供全局fixtures：
- `project_root_path` - 项目根目录路径
- `test_data_path` - 测试数据目录路径
- `sample_pdf_file` - 示例PDF文件路径
- `mock_context` - 模拟阿里云FC context对象

### pytest.ini
配置pytest行为：
- 测试发现规则
- 输出格式
- 标记定义
- 警告过滤

## 最佳实践

### 1. 测试命名
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 2. 测试组织
- 按功能模块组织测试文件
- 使用测试类分组相关测试
- 使用标记分类测试类型

### 3. 测试编写
- 每个测试应该独立运行
- 使用fixtures提供测试数据
- 使用参数化测试减少重复代码
- 添加适当的断言消息

### 4. 错误处理
- 在测试环境中某些功能可能不可用
- 使用`pytest.skip()`跳过不适用的测试
- 提供清晰的跳过原因

## 故障排除

### 常见问题

1. **导入错误**
   - 确保在正确的conda环境中
   - 检查模块路径配置
   - 查看conftest.py中的路径设置

2. **测试跳过**
   - 某些测试在测试环境中可能会被跳过
   - 这通常是正常的，特别是需要外部服务的测试

3. **慢速测试**
   - 使用`-m "not slow"`排除慢速测试
   - 慢速测试通常涉及文件处理或网络请求

4. **覆盖率报告**
   - 覆盖率报告生成在`htmlcov/`目录
   - 在浏览器中打开`htmlcov/index.html`查看详细报告

## 持续集成

建议在CI/CD流水线中运行以下测试：

```bash
# 快速测试（用于PR检查）
python -m pytest tests/ -m "not slow" -v

# 完整测试（用于主分支）
python -m pytest tests/ -v --cov=src --cov-report=xml
```

## 贡献指南

添加新测试时：

1. 选择合适的测试文件或创建新文件
2. 使用适当的测试标记
3. 添加清晰的文档字符串
4. 确保测试在隔离环境中可以运行
5. 更新本README文档（如需要）
