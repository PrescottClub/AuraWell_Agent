# AuraWell 云服务器部署指南

## 🌟 项目概述

AuraWell 是一个智能健康管理平台，集成了大语言模型(LLM)和检索增强生成(RAG)技术，为用户提供个性化的健康建议和管理服务。

### 🎯 部署目标

- **服务器IP**: 166.108.224.73
- **后端端口**: 8001
- **前端端口**: 5173
- **系统要求**: Ubuntu 22.04
- **Python版本**: 3.10.18
- **Node.js版本**: 18.18.2

## 🚀 快速部署

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd AuraWell

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入您的API密钥
```

### 2. 一键启动

#### Ubuntu 22.04 云服务器部署

```bash
# 启动服务
./start_aurawell.sh

# 重启服务
./restart_aurawell.sh
```

#### macOS 开发环境部署

```bash
# 启动服务
./scripts/start_aurawell_macos.sh

# 重启服务
./scripts/restart_aurawell_macos.sh
```

### 3. 验证部署

```bash
# 运行完整测试套件
python run_tests.py
```

## 📋 功能特性

### ✅ 已实现功能

1. **RAG模组集成**
   - ✅ 前端健康助手模块启用大模型问答
   - ✅ RAG检索服务集成
   - ✅ `/rag` 命令支持
   - ✅ 检索结果与LLM回答结合

2. **启动脚本**
   - ✅ Ubuntu 22.04兼容
   - ✅ Python/Node.js版本检测
   - ✅ Nginx服务检测
   - ✅ 端口占用检测和释放
   - ✅ 自动依赖安装

3. **测试套件**
   - ✅ Selenium前端自动化测试
   - ✅ RAG模块单元测试
   - ✅ LLM交互功能测试
   - ✅ 集成测试

## 🧪 测试账号

- **用户名**: `test_user`
- **密码**: `test_password`

## 🔧 技术架构

### 后端技术栈
- **框架**: FastAPI
- **AI引擎**: DeepSeek + LangChain
- **RAG**: 阿里云DashVector + 本地实现
- **数据库**: SQLite (开发) / MySQL (生产)

### 前端技术栈
- **框架**: Vue.js 3
- **UI库**: Ant Design Vue
- **构建工具**: Vite
- **状态管理**: Pinia

## 📖 使用指南

### 1. 访问应用

#### 云服务器访问 (Ubuntu)
- **前端界面**: http://166.108.224.73:5173
- **API文档**: http://166.108.224.73:8001/docs
- **健康检查**: http://166.108.224.73:8001/api/v1/health

#### 本地开发访问 (macOS)
- **前端界面**: http://localhost:5173
- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/api/v1/health

### 2. 健康助手使用

1. 登录系统 (test_user / test_password)
2. 进入健康助手模块
3. 普通对话：直接输入问题
4. RAG检索：使用 `/rag 您的查询内容`

#### RAG使用示例

```
/rag 高血压的饮食建议
/rag 糖尿病患者运动注意事项
/rag 减肥的健康方法
```

### 3. API使用

#### 聊天API

**云服务器:**
```bash
curl -X POST "http://166.108.224.73:8001/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我需要健康建议",
    "conversation_id": null
  }'
```

**本地开发:**
```bash
curl -X POST "http://localhost:8001/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，我需要健康建议",
    "conversation_id": null
  }'
```

#### RAG检索API

**云服务器:**
```bash
curl -X POST "http://166.108.224.73:8001/api/v1/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "高血压的饮食建议",
    "k": 3
  }'
```

**本地开发:**
```bash
curl -X POST "http://localhost:8001/api/v1/rag/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "高血压的饮食建议",
    "k": 3
  }'
```

## 💻 macOS 开发环境

### 系统要求

- **操作系统**: macOS 10.15+ (推荐 macOS 12+)
- **Python**: 3.10.x (推荐使用conda管理)
- **Node.js**: 18+ (推荐使用Homebrew安装)

### 环境准备

```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Node.js
brew install node

# 安装Python (可选，如果未使用conda)
brew install python@3.10

# 安装conda (推荐)
brew install --cask anaconda
```

### conda环境设置

```bash
# 创建AuraWell专用环境
conda create -n AuraWellPython310 python=3.10

# 激活环境
conda activate AuraWellPython310

# 安装依赖
pip install -r requirements.txt
```

### macOS特定功能

- **自动检测conda环境**: 脚本会自动激活AuraWellPython310环境
- **本地地址绑定**: 使用127.0.0.1而非0.0.0.0
- **macOS版本检测**: 自动检测macOS版本信息
- **Homebrew集成**: 提供Homebrew安装建议

## 🛠️ 运维管理

### 服务管理

#### Ubuntu云服务器

```bash
# 查看服务状态
ps aux | grep -E "(uvicorn|npm)"

# 查看日志
tail -f backend.log
tail -f frontend.log

# 重启服务
./restart_aurawell.sh

# 停止服务
pkill -f "uvicorn"
pkill -f "npm run dev"
```

#### macOS开发环境

```bash
# 查看服务状态
ps aux | grep -E "(uvicorn|npm)"

# 查看日志
tail -f backend.log
tail -f frontend.log

# 重启服务
./scripts/restart_aurawell_macos.sh

# 停止服务
pkill -f "uvicorn"
pkill -f "npm run dev"
```

### 监控检查

```bash
# 检查端口占用
lsof -i :8001
lsof -i :5173

# 检查服务健康
curl http://localhost:8001/api/v1/health
curl http://localhost:5173
```

## 🧪 测试说明

### 运行测试

```bash
# 完整测试套件
python run_tests.py

# 单独运行测试
python tests/test_frontend_selenium.py
python tests/test_rag_module.py
python tests/test_llm_interaction.py
```

### 测试覆盖

1. **前端测试**
   - 页面加载测试
   - 用户登录功能
   - 导航菜单测试
   - 健康助手聊天
   - RAG功能测试
   - 响应式设计

2. **后端测试**
   - RAG服务初始化
   - RAG检索功能
   - LLM响应生成
   - Agent消息处理
   - 对话记忆功能

3. **集成测试**
   - API端点测试
   - RAG与LLM集成
   - 前后端交互

## 🔍 故障排除

### 常见问题

#### Ubuntu云服务器

1. **服务启动失败**
   ```bash
   # 检查端口占用
   ./restart_aurawell.sh

   # 查看错误日志
   cat backend.log
   cat frontend.log
   ```

2. **RAG功能异常**
   ```bash
   # 检查API密钥配置
   cat .env | grep -E "(DASHSCOPE|DASH_VECTOR)"

   # 测试RAG服务
   curl -X POST http://166.108.224.73:8001/api/v1/rag/retrieve \
     -H "Content-Type: application/json" \
     -d '{"user_query":"test","k":1}'
   ```

3. **前端无法访问**
   ```bash
   # 检查前端服务
   curl http://166.108.224.73:5173

   # 重启前端
   cd frontend && npm run dev
   ```

#### macOS开发环境

1. **服务启动失败**
   ```bash
   # 检查端口占用
   ./scripts/restart_aurawell_macos.sh

   # 查看错误日志
   cat backend.log
   cat frontend.log
   ```

2. **Python环境问题**
   ```bash
   # 检查conda环境
   conda env list
   conda activate AuraWellPython310

   # 重新安装依赖
   pip install -r requirements.txt
   ```

3. **Node.js版本问题**
   ```bash
   # 检查Node.js版本
   node --version

   # 使用Homebrew更新
   brew upgrade node
   ```

4. **权限问题**
   ```bash
   # 修复文件权限
   chmod +x scripts/*.sh

   # 清理npm缓存
   npm cache clean --force
   ```

### 日志分析

- **后端日志**: `backend.log`
- **前端日志**: `frontend.log`
- **测试报告**: `test_report_*.txt`

## 📞 技术支持

### 联系方式
- **项目**: AuraWell Health Assistant
- **版本**: 1.0.0
- **部署环境**: Ubuntu 22.04
- **更新时间**: 2025-06-23

### 相关文档
- [API文档](http://166.108.224.73:8001/docs)
- [前端界面](http://166.108.224.73:5173)
- [项目仓库](https://github.com/your-repo/aurawell)

## 📋 快速参考

### 启动脚本对比

| 功能 | Ubuntu云服务器 | macOS开发环境 |
|------|---------------|---------------|
| 启动脚本 | `./start_aurawell.sh` | `./scripts/start_aurawell_macos.sh` |
| 重启脚本 | `./restart_aurawell.sh` | `./scripts/restart_aurawell_macos.sh` |
| 前端地址 | http://166.108.224.73:5173 | http://localhost:5173 |
| 后端地址 | http://166.108.224.73:8001 | http://localhost:8001 |
| 主机绑定 | 0.0.0.0 | 127.0.0.1 |
| 系统检查 | 严格Ubuntu检查 | macOS版本检测 |
| Python管理 | 系统Python + conda | conda优先 |
| 包管理器 | apt | Homebrew |

### 环境变量配置

```bash
# 必需的API密钥
DASHSCOPE_API_KEY=your_dashscope_key
DASH_VECTOR_API_KEY=your_dashvector_key
DASH_VECTOR_ENDPOINT=your_dashvector_endpoint

# 可选配置
DATABASE_URL=sqlite:///./aurawell.db
SECRET_KEY=your_secret_key
```

### 测试命令

```bash
# 完整测试套件
python run_tests.py

# 单独测试
python tests/test_frontend_selenium.py
python tests/test_rag_module.py
python tests/test_llm_interaction.py
```

---

🎉 **部署完成！**

- **云服务器**: 访问 http://166.108.224.73:5173 开始使用 AuraWell 健康助手！
- **本地开发**: 访问 http://localhost:5173 开始使用 AuraWell 健康助手！
