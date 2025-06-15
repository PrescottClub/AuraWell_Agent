# AuraWell 🌟 - 超个性化健康生活方式编排AI Agent

<div align="center">

![AuraWell](https://img.shields.io/badge/AuraWell-AI%20Health%20Assistant-4A90E2?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-R1/V3-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0+-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![Alibaba Cloud](https://img.shields.io/badge/Alibaba%20Cloud-FC-FF6A00?style=for-the-badge&logo=alibabacloud&logoColor=white)

**基于阿里云Serverless的家庭健康管理AI Agent**

*整合健身目标、日常作息、饮食偏好、工作日程及社交活动，提供情境化建议与习惯养成支持*

[🚀 快速开始](#快速开始) • [🏠 家庭健康](#家庭健康管理) • [🤖 AI Agent](#ai-agent架构) • [☁️ 云架构](#阿里云架构)

</div>

---

## 🎯 项目简介

AuraWell是一个基于**阿里云Serverless架构**的超个性化健康生活方式编排AI Agent，专注为**家庭用户群体**提供智能健康管理服务。通过集成**DeepSeek R1推理模型**、**LangChain工具链**和**RAG知识检索**，为每个家庭成员提供个性化的健康建议与习惯养成支持。

### 🌟 核心创新

- 🏠 **家庭多用户管理** - 主账号+家庭成员架构，支持多角色权限控制
- 🤖 **智能Agent编排** - DeepSeek R1 + LangChain + RAG，科学可信的健康建议
- ☁️ **Serverless架构** - 阿里云FC + API Gateway，弹性扩缩容，按需付费
- 🔄 **实时数据同步** - 对接Apple Health、华为健康、小米运动等主流平台
- 📊 **智能健康报告** - AI生成周/月报告，图文结合，深度解读
- 💬 **流式对话体验** - WebSocket + Token流式输出，打字机式交互体验

---

## 🏠 家庭健康管理

### 👨‍👩‍👧‍👦 多用户架构

```
主账号 (Owner)
├── 配偶 (Manager)
├── 父母 (Viewer)
└── 孩子 (Viewer)

权限体系
├── Owner: 全部成员数据，创建邀请，接收告警
├── Manager: 指定成员数据，设置目标，相关告警
└── Viewer: 个人数据，生成个人计划
```

### 🔐 权限控制体系

| 角色 | 权限范围 | 功能访问 |
|------|----------|----------|
| **Owner** | 全部成员数据 | 创建/邀请成员、设置权限、接收所有告警 |
| **Manager** | 指定成员数据 | 查看数据、设置目标、接收相关告警 |
| **Viewer** | 自己数据 | 查看个人数据、生成个人计划 |

### 🚨 智能告警机制

- **健康异常监测** - 体重骤变、心率异常、睡眠不达标
- **多渠道推送** - 微信、短信、App内通知
- **触发机制** - 火山引擎函数 + 消息队列
- **权限过滤** - 仅推送给有权限的家庭成员

---

## 🤖 AI Agent架构

### 🧠 核心智能引擎

**DeepSeek R1/V3** - 阿里云DashScope托管
- **深度推理能力** - 复杂健康场景的逻辑分析
- **流式输出** - Token级别的实时响应
- **工具调用** - Function Calling支持复杂工具链

**LangChain工具链** - 可插拔智能决策
```python
tools = [
    UserProfileLookup(),    # 用户档案查询
    CalcMetrics(),         # BMI/BMR/TDEE计算
    SearchKnowledge(),     # RAG知识检索
    HealthDataSync(),      # 健康数据同步
    FamilyPermission()     # 家庭权限控制
]
```

**RAG知识检索** - OpenSearch Vector
- **权威医学文献** - 中国居民膳食指南、WHO健康标准
- **实时更新** - 最新健康科学研究
- **个性化检索** - 基于用户画像的精准匹配

### 💬 五模块结构化输出

- 🍎 **饮食营养** - 个性化营养需求计算
- 🏃‍♂️ **运动健身** - 基于体质的运动计划
- ⚖️ **体重管理** - 科学减重/增重策略
- 😴 **睡眠优化** - 睡眠质量改善建议
- 🧘‍♀️ **心理健康** - 压力管理和情绪调节

---

## ☁️ 阿里云架构

### 🏗️ Serverless技术栈

| 服务 | 用途 | 特性 |
|------|------|------|
| **Function Compute** | 后端运行时 | 按请求计费，弹性扩缩容，150,000 CU·s免费额度 |
| **API Gateway** | 统一入口 | WebSocket支持，JWT认证，流控限流 |
| **DashScope** | AI推理 | DeepSeek R1/V3，OpenAI兼容，100万Token免费 |
| **OpenSearch Vector** | 知识检索 | RAG向量检索，自动运维，ANN查询 |
| **RDS MySQL** | 数据存储 | 用户档案、健康数据、权限管理 |
| **OSS** | 文件存储 | 健康报告、用户头像、数据备份 |
| **SLS** | 日志监控 | 函数日志、错误告警、性能监控 |

### 🔄 系统整体流程

```
用户输入 → API Gateway → Function Compute → LangChain Agent
                                    ↓
DeepSeek R1 ← Vector Search ← RDS MySQL
    ↓              ↓              ↓
Token流式输出 → WebSocket → 前端实时显示
```

---

## 🚀 快速开始

### 📋 环境要求

- Python 3.10+
- Node.js 18+
- 阿里云账号 (开通FC、API Gateway、DashScope等服务)

### ⚡ 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/your-org/aurawell.git
cd aurawell

# 2. 后端环境设置
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 环境变量配置
cp env.example .env
# 编辑.env文件，配置以下密钥：
# - DASHSCOPE_API_KEY: 阿里云DashScope API密钥
# - ALIYUN_ACCESS_KEY_ID: 阿里云访问密钥ID
# - ALIYUN_ACCESS_KEY_SECRET: 阿里云访问密钥Secret
# - ENABLE_RAG: true/false (开启/关闭RAG检索)

# 4. 启动本地开发服务
python run_api_server.py
```

### 🌐 前端开发

```bash
cd frontend
npm install
npm run dev  # 开发模式: http://localhost:5175
npm run build  # 生产构建
```

### ☁️ 云端部署

```bash
# 安装Serverless Devs CLI
npm install -g @serverless-devs/s

# 配置阿里云凭证
s config add

# 一键部署到阿里云
s deploy
```

---

## 📊 核心功能模块

### 🎯 健康数据同步
**支持平台**
- Apple Health (HealthKit)
- 华为健康 (Huawei Health)
- 小米运动 (Mi Fitness)
- 薄荷健康 (Bohe Health)

**同步数据**
- 步数、距离、卡路里消耗
- 心率、血压、体重
- 睡眠时长、深睡比例
- 运动类型、运动时长

### 📈 智能健康报告

**AI深度解读**
```
"过去两周深睡时间下降15%，可能与工作强度上升有关，
建议睡前做5分钟深呼吸放松。"
```

**可视化图表**
- 体重趋势折线图
- 运动量柱状图
- 睡眠质量热力图
- 心理状态雷达图

### 🛡️ 数据安全与合规

**传输安全**
- 全链路TLS 1.3加密
- API Gateway统一鉴权
- JWT Token过期管理

**存储安全**
- 敏感字段AES-256加密
- 数据库访问最小权限
- 定期数据备份与恢复

---

## 🔧 开发指南

### 📁 项目结构

```
aurawell/
├── 🏗️ core/                     # 核心组件
│   ├── agent_router.py          # Agent统一路由
│   └── deepseek_client.py       # DeepSeek客户端
├── ⭐ langchain_agent/          # LangChain智能体
│   ├── agent.py                 # 核心Agent实现
│   ├── tools/                   # 工具链
│   │   ├── user_profile_tool.py # 用户档案工具
│   │   ├── calc_metrics_tool.py # 计算工具
│   │   └── search_knowledge_tool.py # 检索工具
│   └── services/                # Agent服务
│       ├── health_advice_service.py # 健康建议服务
│       └── parsers.py           # 输出解析器
├── 🔌 interfaces/               # API接口层
│   └── api_interface.py         # FastAPI接口
├── 📊 models/                   # 数据模型
│   ├── database_models.py       # 数据库模型
│   └── api_models.py            # API模型
├── 🔐 auth/                     # 认证系统
│   └── jwt_auth.py              # JWT认证
├── 🏠 repositories/             # 数据访问层
│   ├── user_repository.py       # 用户数据访问
│   └── family_repository.py     # 家庭数据访问
├── 🩺 integrations/             # 健康平台集成
│   ├── apple_health/            # Apple HealthKit
│   ├── xiaomi_health/           # 小米健康
│   └── huawei_health/           # 华为健康
└── ☁️ deployment/               # 部署配置
    ├── serverless.yml           # Serverless配置
    └── template.yml             # 阿里云资源模板

frontend/                        # Vue.js前端
├── src/
│   ├── components/              # 组件库
│   │   ├── family/              # 家庭管理组件
│   │   ├── health/              # 健康组件
│   │   └── chat/                # 对话组件
│   ├── views/                   # 页面视图
│   │   ├── FamilyDashboard.vue  # 家庭仪表盘
│   │   ├── HealthChat.vue       # AI健康对话
│   │   └── HealthReport.vue     # 健康报告
│   └── stores/                  # Pinia状态管理
│       ├── auth.js              # 认证状态
│       ├── family.js            # 家庭状态
│       └── health.js            # 健康数据状态
```

### 🚀 开发工作流

**团队角色分工**

| 角色 | 职责 | 技术栈 |
|------|------|--------|
| **FE** | 前端开发 | Vue 3 + TypeScript + Pinia |
| **CLOUD** | 云基础设施 | 阿里云FC + API Gateway + RDS |
| **AI** | Agent开发 | LangChain + DeepSeek + RAG |
| **AI+DX** | 数据内容 | 健康知识库 + 测试数据 |

**开发里程碑**

| 阶段 | 周期 | 交付目标 |
|------|------|----------|
| **Phase I** | Week 1-2 | 基础通路打通，WebSocket连接，Mock数据 |
| **Phase II** | Week 3-4 | 核心功能实现，RAG检索，家庭权限 |
| **Phase III** | Week 5-6 | 完善优化，监控告警，性能调优 |

---

## 📋 API接口规范

### 📡 核心端点

| 分类 | 端点 | 方法 | 描述 |
|------|------|------|------|
| **认证** | `/api/v1/auth/login` | POST | 用户登录 |
| **家庭** | `/api/v1/family/members` | GET/POST | 家庭成员管理 |
| **权限** | `/api/v1/family/permissions` | PUT | 权限设置 |
| **对话** | `/api/v1/chat` | WebSocket | AI健康对话 |
| **数据** | `/api/v1/health/sync` | POST | 健康数据同步 |
| **报告** | `/api/v1/reports/generate` | POST | 生成健康报告 |
| **告警** | `/api/v1/alerts/settings` | GET/PUT | 告警设置 |

### 💬 WebSocket消息格式

```javascript
// 发送消息
{
  "text": "帮我制定减重计划",
  "member_id": "user123",
  "history": [
    {"role": "user", "content": "之前的对话"},
    {"role": "assistant", "content": "AI回复"}
  ]
}

// 接收消息
{
  "type": "token",
  "content": "建议您",
  "member_id": "user123"
}
```

---

## 🔍 监控与运维

### 📊 关键监控指标

**性能指标**
- API响应时间P99 < 3s
- WebSocket连接成功率 > 99%
- 函数冷启动时间 < 300ms
- AI推理准确率 > 95%

**业务指标**
- 日活用户数 (DAU)
- 对话完成率
- 健康建议采纳率
- 家庭互动参与度

### 💰 成本优化策略

**免费额度充分利用**
- Function Compute: 150,000 CU·s/月
- DashScope: 100万Token/月
- API Gateway: 100万次调用/月

**按需付费模式**
- 无需预留资源，真正按使用付费
- 自动扩缩容，应对流量高峰
- 冷启动优化，平均300ms启动时间

---

## 🎉 创新特色

### 🔬 技术创新

1. **RAG增强的医学AI** - 权威健康知识 + 深度推理能力
2. **可插拔工具链** - LangChain ReAct模式，自主决策调用工具
3. **流式WebSocket体验** - Token级实时响应，沉浸式交互
4. **Serverless极简架构** - 按需扩容，真正零运维

### 🏠 场景创新

1. **家庭健康协作** - 多用户权限管理，家庭健康互动
2. **主动关怀机制** - AI识别异常，智能推送告警
3. **年轻化社交** - 点赞挑战，游戏化健康管理
4. **跨平台数据融合** - 统一健康数据标准，全场景覆盖

---

## 📚 相关资源

### 📖 文档链接

- [阿里云Function Compute文档](https://help.aliyun.com/product/50980.html)
- [DashScope API文档](https://help.aliyun.com/zh/dashscope/)
- [LangChain官方文档](https://python.langchain.com/)
- [Vue 3官方文档](https://vuejs.org/)

### 🔗 API参考

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **WebSocket测试**: ws://localhost:8000/chat

---

## 🤝 贡献指南

### 🔄 提交规范

```bash
# 功能开发
git commit -m "feat: 添加家庭权限管理功能"

# 问题修复
git commit -m "fix: 修复WebSocket连接断开问题"

# 文档更新
git commit -m "docs: 更新API接口文档"

# 性能优化
git commit -m "perf: 优化RAG检索响应时间"
```

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

**AuraWell** - *让每个家庭都拥有智能健康管家* 💙

[![Star on GitHub](https://img.shields.io/github/stars/your-org/aurawell?style=social)](https://github.com/your-org/aurawell)

</div> 