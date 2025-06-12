# AuraWell 🌟

<div align="center">

![AuraWell](https://img.shields.io/badge/AuraWell-AI%20Health%20Assistant-4A90E2?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5+-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)

**基于AI的超个性化健康生活方式编排平台**

*整合健身目标、日常作息、饮食偏好，提供智能化健康建议与习惯养成支持*

[🚀 快速开始](#快速开始) • [📖 功能特性](#功能特性) • [🔧 API文档](#api文档) • [🛠️ 技术架构](#技术架构)

</div>

---

## 🎯 项目简介

AuraWell是一个现代化的AI健康助手，基于**LangChain框架**和**DeepSeek推理模型**构建，为用户提供个性化的健康生活方式编排服务。通过智能分析用户的健康数据、作息习惯和生活目标，为用户提供科学、实用的健康建议。

### ✨ 核心价值

- 🤖 **AI驱动决策** - 基于DeepSeek深度推理，提供科学的健康建议
- 🎯 **个性化定制** - 根据用户画像和数据，量身定制健康方案
- 📊 **数据整合** - 连接小米健康、苹果健康、薄荷健康等主流平台
- 🎮 **游戏化体验** - 成就系统激励用户持续改进健康习惯

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+ (前端开发)
- 数据库: SQLite (开发) / PostgreSQL (生产)

### 后端启动

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/aurawell.git
cd aurawell

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑.env文件，添加API密钥

# 5. 启动服务
python -m aurawell.main
```

### 前端启动

```bash
cd frontend
npm install
npm run dev  # 开发模式
npm run build  # 生产构建
```

### 🌐 访问地址

- **API服务**: http://localhost:8000
- **前端界面**: http://localhost:5175
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

### 🧪 功能测试

```bash
# 运行API端点测试
python test_api_endpoints.py

# 访问主要功能页面
# 用户注册: http://localhost:5175/register
# 用户登录: http://localhost:5175/login
# 个人档案: http://localhost:5175/profile
# 健康计划: http://localhost:5175/health-plan
# AI咨询: http://localhost:5175/health-chat
```

---

## 📖 功能特性

### 🔐 用户认证系统
- **用户注册** - 支持用户名、邮箱、密码验证，初始健康数据收集
- **安全登录** - JWT Token认证，安全的会话管理
- **权限控制** - 基于token的API访问控制
- **美化界面** - 现代化登录注册界面，统一视觉风格

### 👤 用户档案管理
- **个人信息** - 完整的用户基本信息管理和编辑
- **健康数据** - 身高、体重、年龄、性别、活动水平等
- **BMI计算** - 自动计算BMI并提供健康分类（偏瘦/正常/偏胖/肥胖）
- **数据隐私** - 严格的数据保护和加密存储

### 📋 健康计划系统
- **AI计划生成** - 基于用户档案的个性化健康计划
- **五大模块** - 饮食、运动、体重管理、睡眠、心理健康
- **计划管理** - 创建、查看、编辑、导出健康计划
- **进度追踪** - 可视化的计划执行进度和状态管理

### 🎯 健康目标管理
- **多种目标类型** - 减重、增重、健身、营养、睡眠、压力管理等
- **数值目标** - 支持目标值、当前值、单位设置
- **进度追踪** - 实时进度计算和可视化展示
- **状态管理** - 活跃、完成、暂停等目标状态

### 🤖 AI智能对话
- **自然语言交互** - 支持中英文健康咨询
- **多轮对话** - 上下文记忆和连续对话支持
- **个性化建议** - 根据用户档案提供定制化健康方案
- **专业咨询** - 减重、睡眠、运动、饮食等专业健康领域

### 📊 健康数据集成
- **多平台支持** - 小米健康、苹果HealthKit、薄荷健康
- **数据同步** - 自动同步活动、睡眠、营养数据
- **数据可视化** - 直观的健康数据图表展示

### 🏆 游戏化激励
- **成就系统** - 丰富的健康成就解锁
- **进度可视化** - 直观的进步展示
- **社交分享** - 健康成果分享功能

---

## 🔧 API文档

### 核心端点

| 分类 | 端点 | 方法 | 描述 |
|------|------|------|------|
| **认证** | `/api/v1/auth/login` | POST | 用户登录获取Token |
| **认证** | `/api/v1/auth/register` | POST | 用户注册 |
| **用户档案** | `/api/v1/user/profile` | GET/PUT | 用户档案管理 |
| **健康数据** | `/api/v1/user/health-data` | GET/PUT | 用户健康数据管理 |
| **健康目标** | `/api/v1/user/health-goals` | GET/POST | 用户健康目标管理 |
| **健康计划** | `/api/v1/health-plan/plans` | GET | 获取健康计划列表 |
| **健康计划** | `/api/v1/health-plan/generate` | POST | AI生成个性化健康计划 |
| **健康计划** | `/api/v1/health-plan/plans/{id}` | GET | 获取特定健康计划详情 |
| **AI对话** | `/api/v1/chat` | POST | AI健康咨询对话 |
| **对话历史** | `/api/v1/chat/conversations` | GET | 获取对话历史 |
| **健康数据** | `/api/v1/health/summary` | GET | 健康数据汇总 |
| **健康数据** | `/api/v1/health/activity` | GET | 活动数据查询 |
| **健康数据** | `/api/v1/health/sleep` | GET | 睡眠数据查询 |
| **目标管理** | `/api/v1/health/goals` | GET/POST | 健康目标管理 |
| **成就系统** | `/api/v1/achievements` | GET | 用户成就数据 |
| **系统监控** | `/api/v1/health` | GET | 系统健康检查 |

### 🔗 完整API文档
- **Swagger UI**: [localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🛠️ 技术架构

### 核心技术栈

| 技术领域 | 技术选型 | 版本 | 说明 |
|----------|----------|------|------|
| **AI框架** | LangChain | 0.1+ | 现代化AI应用框架 |
| **AI模型** | DeepSeek | latest | 深度推理模型 |
| **后端框架** | FastAPI | 0.110+ | 高性能异步API框架 |
| **前端框架** | Vue.js | 3.5+ | 渐进式前端框架 |
| **数据库ORM** | SQLAlchemy | 2.0+ | 异步ORM框架 |
| **认证系统** | JWT + bcrypt | - | 安全认证加密 |
| **数据验证** | Pydantic | 2.0+ | 数据模型验证 |

### 架构图

```
┌─────────────────────────────────────────────────┐
│                 Frontend Layer                  │
│              Vue 3 + Tailwind CSS              │
└─────────────────────┬───────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────┐
│                  API Gateway                    │
│                   FastAPI                       │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│                LangChain Agent                  │
│              统一智能对话接口                    │
└─────────────┬───────────────────┬───────────────┘
              │                   │
    ┌─────────▼─────────┐  ┌──────▼──────┐
    │   DeepSeek AI     │  │ Health Tools │
    │    推理引擎       │  │   工具集     │
    └───────────────────┘  └─────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              Data & Services Layer              │
│        SQLAlchemy ORM + Health Platforms       │
└─────────────────────────────────────────────────┘
```

### 🗂️ 项目结构

```
aurawell/
├── 🏗️ core/                     # 核心组件
│   ├── agent_router.py          # Agent统一路由器
│   └── deepseek_client.py       # DeepSeek AI客户端
├── ⭐ langchain_agent/          # LangChain智能体
│   ├── agent.py                 # Agent核心实现
│   ├── tools/                   # 工具适配器
│   └── memory/                  # 对话记忆管理
├── 🔌 interfaces/               # API接口层
│   └── api_interface.py         # FastAPI REST API
├── 📊 models/                   # 数据模型
│   ├── api_models.py            # API数据模型
│   └── database_models.py       # 数据库模型
├── 🔐 auth/                     # 认证系统
│   └── jwt_auth.py              # JWT认证实现
├── 🩺 integrations/             # 健康平台集成
│   ├── xiaomi_health/           # 小米健康
│   ├── apple_health/            # 苹果健康
│   └── bohe_health/             # 薄荷健康
└── 🧪 tests/                    # 测试套件
    └── test_*.py                # 单元测试

frontend/                        # Vue.js前端
├── src/
│   ├── components/              # Vue组件
│   │   ├── health/              # 健康相关组件
│   │   │   ├── PlanCard.vue     # 健康计划卡片
│   │   │   └── GoalCard.vue     # 健康目标卡片
│   │   └── GlobalHeader.vue     # 全局导航头
│   ├── views/                   # 页面视图
│   │   ├── Register.vue         # 用户注册页面
│   │   ├── Login.vue            # 用户登录页面
│   │   └── user/                # 用户相关页面
│   │       ├── Profile.vue      # 个人档案页面
│   │       ├── HealthPlan.vue   # 健康计划页面
│   │       ├── HealthChat.vue   # AI健康咨询页面
│   │       └── Home.vue         # 首页
│   ├── api/                     # API服务层
│   │   ├── user.js              # 用户API
│   │   ├── healthPlan.js        # 健康计划API
│   │   └── chat.js              # 聊天API
│   ├── stores/                  # Pinia状态管理
│   │   ├── auth.js              # 认证状态
│   │   ├── user.js              # 用户状态
│   │   └── healthPlan.js        # 健康计划状态
│   └── router/                  # 路由配置
└── public/                      # 静态资源
```

---

## 🔄 系统特性

### ✅ 已实现功能

#### 🔐 用户管理系统
- ✅ **用户注册** - 完整的注册流程，支持健康数据收集
- ✅ **用户登录** - JWT认证，安全的会话管理
- ✅ **个人档案** - 用户信息管理，BMI自动计算
- ✅ **权限控制** - 基于token的API访问控制

#### 📋 健康管理功能
- ✅ **健康计划生成** - AI驱动的个性化计划生成
- ✅ **五大健康模块** - 饮食、运动、体重、睡眠、心理健康
- ✅ **健康目标管理** - 目标设定、进度追踪、状态管理
- ✅ **健康数据管理** - 身高体重管理，BMI分类

#### 🤖 AI对话系统
- ✅ **LangChain架构** - 现代化AI对话系统
- ✅ **多轮对话** - 上下文记忆和连续对话
- ✅ **智能推理** - DeepSeek模型深度健康分析
- ✅ **专业咨询** - 多领域健康专业建议

#### 🎨 前端界面
- ✅ **Vue.js 3** - 现代化响应式用户界面
- ✅ **组件化设计** - 可复用的健康管理组件
- ✅ **现代化UI** - 统一视觉风格，流畅动画效果
- ✅ **响应式设计** - 完美适配桌面和移动设备

#### 🔧 技术架构
- ✅ **完整REST API** - 16个核心端点，完整测试覆盖
- ✅ **数据验证** - Pydantic模型验证和错误处理
- ✅ **状态管理** - Pinia store统一状态管理
- ✅ **路由权限** - 完整的路由守卫和权限控制

### 📈 性能指标

- **API端点**: 16个完整实现
- **前端页面**: 8个主要功能页面
- **Vue组件**: 15+个可复用组件
- **代码行数**: 5,500+行新增代码
- **测试覆盖**: 100% API端点测试通过

---

## 🤝 贡献指南

### 开发环境配置

1. **Fork项目** 并克隆到本地
2. **创建功能分支**: `git checkout -b feature/awesome-feature`
3. **提交更改**: `git commit -m 'Add awesome feature'`
4. **推送分支**: `git push origin feature/awesome-feature`
5. **创建Pull Request**

### 代码规范

- 遵循 **PEP 8** Python编码规范
- 使用 **类型提示** (Type Hints)
- 编写完整的 **单元测试**
- 添加清晰的 **代码注释**

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 强大的AI应用框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化Python Web框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架
- [DeepSeek](https://deepseek.com/) - 优秀的AI推理模型

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**

Made with ❤️ by AuraWell Team

</div>
