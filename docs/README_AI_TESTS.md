# AuraWell AI模型可用性测试

## 📋 概述

这个测试套件用于检查AuraWell项目中所有生成式AI模型和服务的可用性，包括：

- **默认模型配置** (测试.env中配置的DASHSCOPE_DEFAULT_MODEL)
- **DeepSeek AI模型** (deepseek-v3, deepseek-r1, deepseek-r1-0528)
- **Qwen系列模型** (qwen-plus, qwen-turbo, qwen-max, qwen-long, qwen3系列)
- **RAG服务** (本地RAG模块 + 阿里云函数计算)
- **MCP工具服务** (Brave搜索, GitHub, Weather, Figma)
- **服务工厂** (DeepSeek客户端工厂, MCP工具接口工厂)
- **环境配置** (API密钥配置检查)

## 🚀 快速开始

### 方法1: 使用bash脚本 (推荐)

```bash
# 直接运行测试脚本
./tests/run_ai_tests.sh
```

### 方法2: 直接运行Python测试

```bash
# 设置Python路径并运行测试
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python tests/test_ai_models_availability.py
```

## 📊 测试结果

测试完成后会生成以下输出：

### 1. 终端输出
- 实时显示每个AI模型的测试状态
- 显示响应时间和测试响应内容
- 提供配置建议和故障排除信息

### 2. 详细报告文件
- 文件位置: `tests/ai_models_test_report.json`
- 包含完整的测试结果、时间戳、错误信息等
- JSON格式，便于程序化处理

## 🔧 测试内容详解

### 默认模型配置测试
- 测试.env文件中配置的`DASHSCOPE_DEFAULT_MODEL`
- 验证默认模型的可用性和响应性能

### DeepSeek AI模型测试
- **deepseek-v3**: DeepSeek V3模型（671B参数，MoE架构）
- **deepseek-r1**: DeepSeek R1推理模型（685B参数）
- **deepseek-r1-0528**: DeepSeek R1升级版（2025年5月28日发布）
- 自动读取.env中的`DEEPSEEK_SERIES_V3`和`DEEPSEEK_SERIES_R1`配置

### Qwen系列模型测试
- **qwen-plus**: Qwen Plus模型
- **qwen-turbo**: Qwen Turbo快速模型
- **qwen-max**: Qwen Max高性能模型
- **qwen-long**: Qwen Long长文本模型
- **qwen3系列**: Qwen3深度思考模型（qwen3-plus, qwen3-turbo, qwen3-max）
- 自动读取.env中的`QWEN_PLUS`、`QWEN_FAST`等配置

### RAG服务测试
- 测试本地RAG模块的可用性
- 检查阿里云函数计算RAG服务
- 验证文档检索功能

### MCP工具服务测试
- **Brave Search**: 网络搜索功能
- **GitHub API**: GitHub集成
- **Weather API**: 天气信息服务
- **Figma API**: 设计工具集成

### 环境配置测试
检查以下环境变量的配置状态：
- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥
- `QWEN_API`: Qwen API密钥
- `DEEP_SEEK_API`: DeepSeek API密钥
- `ALIBABA_CLOUD_ACCESS_KEY_ID`: 阿里云访问密钥ID
- `ALIBABA_CLOUD_ACCESS_KEY_SECRET`: 阿里云访问密钥Secret
- `DASH_VECTOR_API`: DashVector API密钥
- `BRAVE_API_KEY`: Brave搜索API密钥
- `GITHUB_TOKEN`: GitHub Token
- `WEATHER_API_KEY`: 天气API密钥
- `FIGMA_TOKEN`: Figma Token

## 📈 测试统计

测试完成后会显示：
- **总测试数**: 执行的测试总数
- **可用服务**: 成功通过测试的服务数量
- **已配置API**: 已配置API密钥的服务数量
- **成功率**: 测试通过率百分比

## 🔍 故障排除

### 常见问题

1. **API密钥未配置**
   - 编辑项目根目录下的 `.env` 文件
   - 添加相应的API密钥
   - 重新运行测试

2. **模型不存在或无权访问**
   - 检查API密钥是否有效
   - 确认模型名称是否正确
   - 验证账户是否有访问权限

3. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 验证API端点是否可访问

4. **Python环境问题**
   - 确保使用正确的Python环境
   - 安装所需的依赖包: `pip install -r requirements.txt`
   - 检查Python路径设置

### 环境要求

- **Python版本**: 3.10+
- **推荐环境**: AuraWellPython310 conda环境
- **必需包**: openai, asyncio, unittest

## 📝 配置示例

在 `.env` 文件中添加API密钥：

```bash
# AI服务配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here
QWEN_API=your_qwen_api_key_here
DEEP_SEEK_API=your_deepseek_api_key_here

# 阿里云配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
DASH_VECTOR_API=your_dashvector_api_key

# 可选服务配置
BRAVE_API_KEY=your_brave_api_key_here
GITHUB_TOKEN=your_github_token_here
WEATHER_API_KEY=your_weather_api_key_here
FIGMA_TOKEN=your_figma_token_here
```

## 🔄 定期测试建议

建议在以下情况下运行AI模型可用性测试：

1. **部署前**: 确保所有AI服务正常工作
2. **配置更改后**: 验证新的API密钥或配置
3. **定期检查**: 每周或每月检查服务状态
4. **故障排除**: 当AI功能出现问题时

## 📞 技术支持

如果遇到问题，请：

1. 查看测试输出的错误信息
2. 检查 `tests/ai_models_test_report.json` 详细报告
3. 参考本文档的故障排除部分
4. 确认API密钥和网络配置

---

**注意**: 这个测试套件会实际调用AI服务API，可能会产生少量的API使用费用。测试使用的是最小的token数量以减少成本。
