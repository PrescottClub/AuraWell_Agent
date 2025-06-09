# AuraWell - 超个性化健康生活方式编排AI Agent

<div align="center">

![AuraWell Logo](https://img.shields.io/badge/AuraWell-Health_Assistant-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Vue](https://img.shields.io/badge/Vue-3.5+-4FC08D?style=for-the-badge&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-1F4B99?style=for-the-badge)

*基于LangChain和DeepSeek的超个性化健康生活方式编排平台*

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [架构文档](#-架构文档) • [API文档](#-api文档) • [贡献](#-贡献)

</div>

## 📖 项目简介

AuraWell是一个基于人工智能的超个性化健康生活方式编排Agent，采用现代化的LangChain框架和DeepSeek推理模型，通过整合用户的健身目标、日常作息、饮食偏好、工作日程及社交活动，提供情境化的健康建议与习惯养成支持。

### 🎯 核心理念

- **AI驱动**: 基于DeepSeek推理模型提供智能健康分析
- **个性化**: 根据用户独特的生活方式和健康数据提供定制化建议
- **现代化架构**: 采用LangChain框架构建可扩展的AI系统
- **标准化API**: RESTful API设计，支持多种客户端集成
- **隐私优先**: 遵循R.A.I.L.G.U.A.R.D安全原则，保护用户隐私

## ✨ 功能特性

### 🤖 LangChain智能体架构 ✅ **最新！**
- **双引擎架构**: 支持传统Agent和LangChain Agent并行运行
- **Agent Router**: 智能路由系统，基于功能开关选择最适合的AI引擎  
- **工具适配器**: 无缝集成现有健康工具到LangChain框架
- **对话记忆**: 基于数据库的持久化对话历史管理
- **DeepSeek集成**: 支持deepseek-reasoner推理模型，提供深度思考能力

### 🚀 完整REST API接口 ✅
- **17个核心API端点**: 覆盖认证、用户管理、健康数据、成就系统
- **JWT认证系统**: Bearer Token认证，安全的用户会话管理
- **自动文档生成**: Swagger UI + ReDoc，完整的OpenAPI 3.0规范
- **CORS支持**: 前端集成就绪，支持跨域请求
- **性能监控**: 响应时间 < 500ms，慢请求日志记录
- **异常处理**: 结构化错误响应和自定义异常类型

### 🗄️ 现代化数据层 ✅
- **SQLAlchemy 2.0+**: 异步ORM架构，支持SQLite/PostgreSQL
- **Repository模式**: 完整的数据访问层，支持CRUD和复杂查询
- **数据库连接池**: 异步连接管理和自动重连机制
- **数据迁移**: 自动化schema管理和数据库初始化
- **缓存系统**: 智能缓存管理，支持用户数据和AI响应缓存

### 🔐 安全认证系统 ✅
- **JWT Token认证**: 基于Bearer Token的无状态认证
- **密码安全**: bcrypt加密存储，防止明文泄露
- **中间件保护**: 统一的认证中间件和权限验证
- **API密钥管理**: 环境变量管理敏感配置信息
- **CORS配置**: 精确的跨域资源共享控制

### 🔗 健康平台集成 ✅
- **小米健康**: 步数、心率、睡眠数据同步，支持OAuth 2.0认证
- **薄荷健康**: 营养摄入和体重管理，食物数据库集成
- **苹果健康**: HealthKit数据集成，iOS设备数据获取
- **通用API客户端**: 可扩展的第三方平台集成框架
- **速率限制**: 智能API调用管理，防止频率超限

### 🎮 游戏化激励系统 ✅
- **成就系统**: 18种健康成就，5个难度等级(青铜/白银/黄金/铂金/钻石)
- **进度追踪**: 实时进度更新和可视化统计
- **智能通知**: 多优先级通知系统，支持多渠道推送
- **数据洞察**: 个人健康趋势分析和建议生成

### 🌐 现代化前端界面 ✅
- **Vue 3 + Vite**: 现代化前端框架，快速开发体验
- **Tailwind CSS**: 原子化CSS框架，响应式设计
- **组件化架构**: 可复用的UI组件库
- **开发环境**: 热重载、快速构建、现代化工具链

### �� AI能力扩展 (准备中)
- **RAG知识增强**: 向量数据库和健康知识库检索 (Phase 2)
- **MCP协议集成**: 模型上下文协议，支持外部工具发现 (Phase 3)
- **多模态支持**: 文本、图像、语音的综合处理能力 (规划中)

## 🛠️ 技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端框架** | Python | 3.8+ | 主要开发语言 |
| **API框架** | FastAPI | 0.110+ | 现代化REST API框架 |
| **AI框架** | LangChain | 0.1+ | 智能体和工具链管理 |
| **AI模型** | DeepSeek | deepseek-reasoner | 深度推理和对话模型 |
| **前端框架** | Vue 3 + Vite | 3.5+ | 现代化前端开发 |
| **样式框架** | Tailwind CSS | 3.4+ | 原子化CSS设计 |
| **数据库** | SQLAlchemy | 2.0+ | 异步ORM，支持SQLite/PostgreSQL |
| **数据验证** | Pydantic | 2.8+ | 数据模型和验证 |
| **认证** | JWT + bcrypt | - | Bearer Token认证和密码加密 |
| **缓存** | 内存缓存 | - | 智能数据缓存系统 |
| **日志** | 结构化日志 | - | 安全审计和性能监控 |
| **健康平台** | 多平台API | - | 小米/薄荷/苹果健康集成 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (用于前端开发)
- pip (Python包管理器)
- npm/yarn (JavaScript包管理器)
- Git

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/PrescottClub/AuraWell_Agent.git
   cd AuraWell_Agent
   ```

2. **后端环境配置**
   ```bash
   # 安装Python依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   cp env.example .env
   # 编辑.env文件，添加你的API密钥
   ```

3. **前端环境配置**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **环境变量配置**
   编辑`.env`文件：
   ```bash
   # DeepSeek AI配置 (必需)
   DEEPSEEK_API_KEY=your_deepseek_api_key
   
   # 数据库配置
   DATABASE_URL=sqlite:///./aurawell.db
   
   # JWT配置
   SECRET_KEY=your_jwt_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # 健康平台配置 (可选)
   XIAOMI_HEALTH_API_KEY=your_xiaomi_api_key
   XIAOMI_HEALTH_CLIENT_ID=your_xiaomi_client_id
   XIAOMI_HEALTH_CLIENT_SECRET=your_xiaomi_client_secret
   
   BOHE_HEALTH_API_KEY=your_bohe_api_key
   BOHE_HEALTH_CLIENT_ID=your_bohe_client_id
   
   APPLE_HEALTH_CLIENT_ID=your_apple_health_client_id
   APPLE_HEALTH_CLIENT_SECRET=your_apple_health_client_secret
   
   # CORS配置
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

### 运行应用

1. **启动后端API服务器** ✅
   ```bash
   python run_api_server.py
   ```
   - API服务器运行在: `http://127.0.0.1:8000`
   - Swagger UI文档: `http://127.0.0.1:8000/docs`
   - ReDoc文档: `http://127.0.0.1:8000/redoc`

2. **启动前端开发服务器** ✅
   ```bash
   cd frontend
   npm run dev
   ```
   - 前端应用运行在: `http://localhost:5173`

3. **命令行界面体验** ✅
   ```bash
   python -m aurawell.interfaces.cli_interface
   ```

### 运行测试

1. **API接口测试**
   ```bash
   python -m pytest tests/test_api_interface.py -v
   ```

2. **基础功能测试**
   ```bash
   python examples/basic_test.py
   ```

3. **LangChain智能体测试**
   ```bash
   python examples/simplified_demo.py
   ```

4. **游戏化系统演示**
   ```bash
   python examples/phase4_gamification_demo.py
   ```

## 📊 项目架构

### 高层架构图

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
│                 Agent Router                    │
│           智能路由 + 功能开关系统                 │
└────────────┬────────────────────────┬───────────┘
             │                        │
             │                        │
┌────────────▼──────────┐  ┌──────────▼───────────┐
│   传统 Agent 引擎      │  │   LangChain 引擎     │
│  ConversationAgent    │  │   LangChainAgent     │
│  HealthToolsRegistry  │  │   Tools + Memory     │
└────────────┬──────────┘  └──────────┬───────────┘
             │                        │
             └────────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│                 共享服务层                           │
│  Database │ Health APIs │ Gamification │ Auth      │
└─────────────────────────────────────────────────────┘
```

### 目录结构

```
aurawell/                          # 主应用包
├── agent/                         # 🔄 传统智能体模块
│   ├── conversation_agent.py      # 传统对话代理
│   ├── health_tools.py            # 健康工具函数集
│   └── tools_registry.py          # 工具注册中心
├── langchain_agent/               # 🆕 LangChain智能体模块
│   ├── agent.py                   # LangChain Agent核心
│   ├── tools/                     # 工具适配器
│   │   ├── adapter.py            # 工具适配器基类
│   │   └── health_tools.py       # 健康工具适配
│   └── memory/                    # 对话记忆管理
│       └── conversation_memory.py # 数据库记忆存储
├── core/                          # 核心AI和编排逻辑
│   ├── agent_router.py            # 🆕 智能体路由器
│   ├── feature_flags.py           # 🆕 功能开关管理
│   └── deepseek_client.py         # DeepSeek AI客户端
├── interfaces/                    # 用户接口层
│   ├── api_interface.py           # FastAPI REST接口
│   └── cli_interface.py           # 命令行界面
├── models/                        # 数据模型层
│   ├── api_models.py              # API请求响应模型
│   ├── health_data_model.py       # 健康数据模型
│   ├── user_profile.py            # 用户档案模型
│   ├── enums.py                   # 枚举定义
│   └── error_codes.py             # 错误代码定义
├── database/                      # 数据库层
│   ├── connection.py              # 数据库连接管理
│   ├── base.py                    # SQLAlchemy基础类
│   ├── models.py                  # 数据库ORM模型
│   └── migrations.py              # 数据库迁移工具
├── repositories/                  # 数据访问层
│   ├── base.py                    # Repository基础类
│   ├── user_repository.py         # 用户数据Repository
│   ├── health_data_repository.py  # 健康数据Repository
│   └── achievement_repository.py  # 成就数据Repository
├── services/                      # 业务服务层
│   ├── database_service.py        # 数据库服务
│   └── health_service.py          # 健康数据服务
├── auth/                          # 认证授权
│   ├── jwt_auth.py                # JWT认证实现
│   └── password_utils.py          # 密码工具
├── middleware/                    # 中间件
│   ├── cors_middleware.py         # CORS配置
│   ├── error_handler.py           # 错误处理中间件
│   └── auth_middleware.py         # 认证中间件
├── utils/                         # 工具函数
│   ├── cache.py                   # 缓存管理
│   ├── async_tasks.py             # 异步任务处理
│   ├── date_utils.py              # 日期工具
│   └── encryption_utils.py        # 加密工具
├── integrations/                  # 第三方集成
│   ├── generic_health_api_client.py  # 通用API客户端
│   ├── xiaomi_health_client.py    # 小米健康
│   ├── bohe_health_client.py      # 薄荷健康
│   └── apple_health_client.py     # 苹果健康
├── gamification/                  # 游戏化系统
│   └── achievement_system.py      # 成就管理
├── config/                        # 配置管理
│   ├── settings.py                # 应用设置
│   └── logging_config.py          # 日志配置
├── rag/                           # 🚧 RAG模块 (准备中)
│   └── __init__.py               # Phase 2实现
└── mcp/                           # 🚧 MCP模块 (准备中)
    └── __init__.py               # Phase 3实现

frontend/                          # Vue.js前端应用
├── src/                          # 源代码
│   ├── components/               # Vue组件
│   ├── views/                    # 页面视图
│   ├── router/                   # 路由配置
│   └── utils/                    # 前端工具
├── public/                       # 静态资源
└── package.json                  # 前端依赖配置

tests/                            # 测试代码
├── test_api_interface.py         # API接口测试
└── conftest.py                   # 测试配置

examples/                         # 示例代码
├── basic_test.py                 # 基础功能测试
├── simplified_demo.py            # LangChain演示
└── phase4_gamification_demo.py   # 游戏化演示

docs/                             # 项目文档
├── LANGCHAIN_MIGRATION_PHASE1_SUMMARY.md  # LangChain迁移总结
└── issue_langchain_full_migration.md      # 完整迁移计划
```

## 🔌 API文档

### 认证端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录，获取JWT token | 无 |

### 用户管理

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/user/profile` | 获取用户档案 | Bearer Token |
| PUT | `/api/v1/user/profile` | 更新用户档案 | Bearer Token |

### AI对话

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v1/chat` | AI对话接口（支持LangChain和传统引擎） | Bearer Token |

### 健康数据

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health/summary` | 获取健康数据摘要 | Bearer Token |
| GET | `/api/v1/health/activity` | 获取活动数据 | Bearer Token |
| GET | `/api/v1/health/sleep` | 获取睡眠数据 | Bearer Token |

### 健康目标

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health/goals` | 获取健康目标列表 | Bearer Token |
| POST | `/api/v1/health/goals` | 创建新的健康目标 | Bearer Token |
| GET | `/api/v1/health/goals/paginated` | 分页获取健康目标 | Bearer Token |

### 成就系统

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/achievements` | 获取用户成就和进度 | Bearer Token |

### 系统监控

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| GET | `/api/v1/health` | 系统健康检查 | 无 |
| GET | `/api/v1/system/performance` | 获取性能指标 | Bearer Token |

### API文档访问

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## 🔄 开发状态

### 已完成功能 ✅

- [x] **LangChain基础架构**: Agent Router + 双引擎支持
- [x] **完整REST API**: 17个核心端点，100%测试通过
- [x] **现代化数据库**: SQLAlchemy 2.0异步ORM
- [x] **JWT认证系统**: 安全的Bearer Token认证
- [x] **健康平台集成**: 小米健康/薄荷健康/苹果健康
- [x] **游戏化系统**: 成就系统和进度追踪
- [x] **Vue前端界面**: 现代化响应式设计
- [x] **性能监控**: 缓存系统和响应时间监控
- [x] **代码质量**: 结构化日志和异常处理

### 进行中功能 🚧

- [ ] **RAG知识增强** (Phase 2): 向量数据库和健康知识库
- [ ] **MCP协议集成** (Phase 3): 模型上下文协议支持
- [ ] **多模态AI** (Phase 4): 图像和语音处理能力

### 性能指标 📈

- **API响应时间**: < 500ms (监控慢请求)
- **测试覆盖率**: 100% (17/17 API测试通过)
- **数据库性能**: 异步连接池 + 查询优化
- **缓存命中率**: 智能缓存管理
- **并发支持**: 异步处理架构

## 🤝 贡献指南

### 开发环境设置

1. Fork此仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

### 代码规范

- 遵循PEP 8 Python编码规范
- 使用类型提示 (Type Hints)
- 函数和类名使用英文，注释支持中文
- 提交前运行测试: `pytest tests/`

### 安全原则

项目遵循R.A.I.L.G.U.A.R.D安全原则：
- **Risk First**: 优先考虑用户数据安全
- **Always Constraints**: 绝不硬编码敏感信息
- **Interpret Securely**: 严格验证所有输入数据
- **Local Defaults**: 敏感配置通过环境变量管理
- **Gen Path Checks**: AI生成内容需要人工审查
- **Uncertainty Disclosure**: 明确标识AI建议的置信度
- **Auditability**: 关键操作全程日志记录
- **Revision + Dialogue**: 支持代码审查和协作

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 联系我们

- **项目主页**: [GitHub Repository](https://github.com/PrescottClub/AuraWell_Agent)
- **问题反馈**: [GitHub Issues](https://github.com/PrescottClub/AuraWell_Agent/issues)
- **技术讨论**: [GitHub Discussions](https://github.com/PrescottClub/AuraWell_Agent/discussions)

---

<div align="center">

**AuraWell - 让AI成为你的个人健康伙伴** 🤖💚

*基于LangChain和DeepSeek构建的下一代健康管理平台*

</div>
