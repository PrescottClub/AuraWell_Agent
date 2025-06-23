# AuraWell 网页应用部署测试指南

## 📋 测试概述

本测试套件用于验证AuraWell网页应用部署后的功能完整性，确保所有核心模块正常工作。

### 🎯 验收标准

1. ✅ **可以使用测试账号登录网站**
2. ✅ **可以点击主界面上方的所有标签，且不会出现错误**
3. ✅ **可以在健康助手模块中与大模型进行对话**
4. ✅ **可以在聊天界面输入"/rag 营养建议"，且用户可以在网页中看到由RAG模块返回的输出**

### 🧪 测试账号

- **用户名**: `test_user`
- **密码**: `test_password`

## 🚀 快速测试

### 1. 一键运行完整测试

```bash
# 在项目根目录运行
python tests/run_deployment_tests.py
```

这个脚本会：
- 自动检查服务状态
- 验证测试依赖
- 运行所有测试模块
- 生成详细测试报告

### 2. 检查服务状态

```bash
# 检查前后端服务是否运行
python tests/check_services.py

# 等待服务启动（最多60秒）
python tests/check_services.py --wait
```

### 3. 单独运行主要测试

```bash
# 前端Selenium测试（主要测试）
python tests/test_frontend_selenium.py

# RAG模块测试
python tests/test_rag_module.py

# LLM交互测试
python tests/test_llm_interaction.py
```

## 🔧 环境准备

### 必需依赖

```bash
# Python依赖
pip install selenium requests

# Firefox浏览器（推荐）
# macOS: brew install firefox
# Ubuntu: sudo apt install firefox

# geckodriver
# macOS: brew install geckodriver
# Ubuntu: sudo apt install firefox-geckodriver
```

### 启动服务

```bash
# 使用启动脚本（推荐）
./start_aurawell.sh

# macOS启动脚本
scripts/start_aurawell_macos.sh

# 手动启动
cd frontend && npm run dev  # 前端 (端口5173)
python -m src.aurawell.main  # 后端 (端口8001)
```

## 📊 测试详情

### 主要测试模块

#### 1. 前端Selenium测试 (`test_frontend_selenium.py`)

**测试内容**:
- 首页加载验证
- 用户登录功能（test_user/test_password）
- 导航标签点击测试（首页、健康咨询、健康计划、健康报告、家庭管理、个人档案）
- 健康助手对话功能
- RAG功能测试（"/rag 营养建议"）
- 错误处理验证

**使用技术**:
- Selenium WebDriver
- Firefox浏览器（无头模式）
- 自动化UI交互测试

#### 2. RAG模块测试 (`test_rag_module.py`)

**测试内容**:
- RAG服务初始化
- 本地RAG检索功能
- RAG服务健康检查
- 查询验证和性能测试
- 备用机制测试

#### 3. LLM交互测试 (`test_llm_interaction.py`)

**测试内容**:
- AI对话功能
- 响应时间验证
- 对话质量检查

### 测试流程

1. **环境检查** - 验证依赖和服务状态
2. **登录测试** - 使用测试账号登录
3. **导航测试** - 点击所有主界面标签
4. **对话测试** - 与健康助手进行对话
5. **RAG测试** - 执行"/rag 营养建议"命令
6. **结果验证** - 检查所有功能是否正常

## 📈 测试报告

测试完成后会显示：

```
📊 AuraWell 部署测试最终结果
==========================================
  前端Selenium测试: ✅ 通过
  RAG模块测试: ✅ 通过  
  LLM交互测试: ✅ 通过

🎯 总体成功率: 100.0% (3/3)

🎉 AuraWell 部署测试通过！应用可以正常使用。
```

### 成功率标准

- **≥80%**: 测试通过，应用可正常使用
- **60-79%**: 部分通过，需要修复问题
- **<60%**: 测试失败，需要检查配置

## 🐛 故障排除

### 常见问题

1. **前端JavaScript错误**
   ```bash
   # 自动修复前端问题（推荐）
   python tests/fix_frontend_issues.py

   # 手动检查合并冲突
   find frontend/src -name "*.js" -o -name "*.vue" | xargs grep -l "<<<<<<< HEAD"
   ```

2. **服务未启动**
   ```bash
   # 检查服务状态
   python tests/check_services.py

   # 启动服务
   ./start_aurawell.sh
   ```

3. **Firefox/geckodriver问题**
   ```bash
   # 检查安装
   firefox --version
   geckodriver --version

   # 安装（macOS）
   brew install firefox geckodriver
   ```

4. **RAG功能失败**
   - 检查.env文件API密钥配置
   - 确保网络连接正常
   - 验证RAG模块依赖完整

5. **登录失败**
   - 确认测试账号已配置
   - 检查认证服务状态
   - 验证数据库连接

### 调试模式

修改测试文件启用可视化调试：

```python
# 在test_frontend_selenium.py中注释掉无头模式
# firefox_options.add_argument('--headless')
```

## 🔄 CI/CD集成

可以将测试集成到持续集成流程：

```yaml
# GitHub Actions示例
- name: AuraWell Deployment Tests
  run: |
    ./start_aurawell.sh &
    sleep 30
    python tests/run_deployment_tests.py
```

## 📞 技术支持

如遇到问题：

1. 查看测试日志输出
2. 检查服务状态和配置
3. 参考故障排除指南
4. 联系开发团队

---

**建议**: 每次部署后运行完整测试套件，确保应用功能完整性。使用Firefox浏览器进行测试以获得最佳兼容性。
