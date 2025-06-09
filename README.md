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
uvicorn aurawell.main:app --reload --host 0.0.0.0 --port 8000
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
- **前端界面**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

---

## 📖 功能特性

### 🤖 AI智能对话
- **自然语言交互** - 支持中英文健康咨询
- **上下文记忆** - 记住用户偏好和历史对话
- **智能推理** - DeepSeek模型提供深度健康分析
- **工具调用** - 自动调用健康工具获取数据

### 👤 用户管理
- **个人档案** - 完整的用户健康档案管理
- **安全认证** - JWT Token安全认证系统
- **数据隐私** - 严格的数据保护和加密存储

### 📊 健康数据集成
- **多平台支持** - 小米健康、苹果HealthKit、薄荷健康
- **数据同步** - 自动同步活动、睡眠、营养数据
- **数据可视化** - 直观的健康数据图表展示

### 🎯 健康目标管理
- **目标设定** - 个性化健康目标制定
- **进度追踪** - 实时跟踪目标完成情况
- **智能提醒** - 基于数据的动态建议

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
| **对话** | `/api/v1/chat` | POST | AI健康对话接口 |
| **用户** | `/api/v1/user/profile` | GET/PUT | 用户档案管理 |
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
│   ├── views/                   # 页面视图
│   ├── router/                  # 路由配置
│   └── stores/                  # 状态管理
└── public/                      # 静态资源
```

---

## 🔄 系统特性

### ✅ 已实现功能

- ✅ **LangChain架构** - 现代化AI对话系统
- ✅ **完整REST API** - 17个核心端点，完整测试覆盖
- ✅ **JWT认证系统** - 安全的Bearer Token认证
- ✅ **健康数据集成** - 支持主流健康平台
- ✅ **Vue.js前端** - 现代化响应式用户界面
- ✅ **性能监控** - 响应时间监控和缓存系统
- ✅ **游戏化系统** - 成就追踪和进度可视化

### 📈 性能指标

- **API响应时间**: < 200ms (平均)
- **数据库查询**: < 50ms (平均)
- **测试覆盖率**: 85%+
- **API端点**: 17个完整实现

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
