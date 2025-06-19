# AuraWell 🌟 - 超个性化健康生活方式编排AI Agent

<div align="center">

![AuraWell](https://img.shields.io/badge/AuraWell-Health%20AI%20Agent-4A90E2?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-R1%20Reasoner-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-13%20Services-00D4AA?style=for-the-badge&logo=chainlink&logoColor=white)

**基于13个MCP智能服务器协作的超个性化健康AI助手**

*整合健身目标、日常作息、饮食偏好、工作日程及社交活动，提供情境化建议与习惯养成支持*

</div>

---

## 📋 项目简介

AuraWell是一个创新的超个性化健康生活方式编排AI Agent，采用Model Context Protocol (MCP)架构，集成13个专业化智能服务器，为用户提供全方位的健康管理解决方案。

### 🎯 核心特色

- **🤖 智能AI推理**: 基于DeepSeek-R1模型，具备复杂健康推理和分析能力
- **🔗 MCP智能协作**: 13个专业服务器自动协作，实现真正的AI自动化健康管理
- **👨‍👩‍👧‍👦 家庭健康管理**: 支持多成员健康数据管理和权限控制
- **📊 数据驱动决策**: 自动分析健康数据，识别健康模式和风险
- **🔬 科学研究支撑**: 实时获取最新医学研究，确保建议的科学性

---

## 🚀 核心功能

### 🗣️ **AI健康对话**
- 实时流式对话，支持WebSocket连接
- 五维度健康建议：营养、运动、体重、睡眠、心理
- 自动工具选择和链式调用
- 上下文记忆和会话管理

### 📈 **智能健康分析**
- 自动数据可视化图表生成
- 健康趋势分析和风险识别
- 个性化健康报告生成
- BMI、基础代谢等指标自动计算

### 👪 **家庭健康协作**
- 一个账号管理全家健康
- Owner/Manager/Viewer三级权限体系
- 家庭健康周报月报自动生成
- 互动激励系统和健康挑战

### 🧠 **知识图谱记忆**
- 构建用户健康画像
- 记录健康偏好和历史
- 跟踪健康改善进展
- 积累家庭健康知识

---

## 🏗️ 技术架构

### 核心技术栈
```
🌐 前端: Vue 3 + TypeScript + Tailwind CSS
📡 后端: FastAPI + SQLAlchemy + WebSocket
🤖 AI引擎: DeepSeek-R1 + 13个MCP智能服务器
🗄️ 数据库: SQLite + Alembic迁移
🔐 认证: JWT Token + 权限控制
```

### MCP智能服务器
- **🧠 推理分析**: sequential-thinking - 深度推理健康状况
- **📊 数据处理**: database-sqlite + calculator - 数据分析和指标计算
- **📈 可视化**: quickchart - 自动生成健康图表
- **🔍 信息研究**: brave-search + fetch - 获取最新健康研究
- **🧭 知识管理**: memory - 构建健康知识图谱
- **⚡ 代码执行**: run-python - 执行复杂算法
- **🌤️ 环境感知**: weather - 天气相关健康建议
- **📁 文档管理**: filesystem + github + notion
- **🎨 设计协作**: figma - UI/UX设计资源
- **⏰ 时间管理**: time - 智能提醒调度

---

## 🛠️ 本地开发指南

### 环境要求
- Python 3.11+
- Node.js 18+
- npm 或 yarn

### 快速开始

#### 1. 克隆项目
```bash
git clone <repository-url>
cd AuraWell_Agent
```

#### 2. 后端环境配置

安装Python依赖：
```bash
pip install -r requirements.txt
```

创建环境变量文件：
```bash
cp env.example .env
```

配置`.env`文件（必填项）：
```env
# 基础配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./aurawell.db

# DeepSeek API配置
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 开发环境配置
DEVELOPMENT_MODE=true
DEBUG=true

# CORS配置
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# RAG服务配置（可选）
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-secret-key
ALIBABA_CLOUD_REGION=cn-hangzhou

# 健康数据集成（可选）
MINT_HEALTH_API_KEY=your-mint-api-key
XIAOMI_HEALTH_API_KEY=your-xiaomi-api-key
```

初始化数据库：
```bash
alembic upgrade head
```

启动后端服务：
```bash
uvicorn src.aurawell.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 前端环境配置

安装前端依赖：
```bash
cd frontend
npm install
```

启动前端开发服务器：
```bash
npm run dev
```

#### 4. 访问应用

启动成功后，您可以访问：

- **前端应用**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **WebSocket测试**: ws://localhost:8000/ws

### 开发工作流

1. **修改后端代码**: 代码保存后自动重启（--reload模式）
2. **修改前端代码**: 代码保存后自动热更新
3. **数据库更改**: 
   ```bash
   alembic revision --autogenerate -m "描述更改"
   alembic upgrade head
   ```
4. **API测试**: 访问 http://localhost:8000/docs 进行交互式API测试

---

## 📁 项目结构

```
AuraWell_Agent/
├── src/aurawell/           # 后端Python代码
│   ├── core/              # 核心业务逻辑
│   ├── database/          # 数据库模型
│   ├── repositories/      # 数据访问层
│   ├── services/          # 业务服务层
│   └── interfaces/        # API接口层
├── frontend/              # Vue.js前端代码
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # Pinia状态管理
│   │   └── api/          # API调用
├── migrations/            # 数据库迁移文件
├── deployment/            # 部署配置
├── requirements.txt       # Python依赖
└── .env                  # 环境变量配置
```

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！请阅读以下指南：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

---

## 📝 许可证

本项目采用MIT许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

---

## 🆘 获得帮助

如果您在使用过程中遇到问题：

1. 查看 [API文档](http://localhost:8000/docs)
2. 检查环境变量配置是否正确
3. 确认所有依赖项已正确安装
4. 查看控制台错误信息

---

<div align="center">

**让AI助力您的健康生活！** 🌟

Made with ❤️ by AuraWell Team

</div>
