# AuraWell 🌟 - 智能家庭健康管理AI助手

<div align="center">

![AuraWell](https://img.shields.io/badge/AuraWell-Family%20Health%20AI-4A90E2?style=for-the-badge&logo=heart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-Reasoner-FF6B6B?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Framework-00D4AA?style=for-the-badge&logo=chainlink&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-009688?style=for-the-badge&logo=fastapi&logoColor=white)

**让每个家庭都拥有专属的AI健康顾问**

*基于LangChain框架，为家庭提供个性化健康建议、成员管理和智能报告生成*

[🚀 立即体验](#快速开始) • [💡 功能演示](#功能演示) • [🏠 家庭管理](#家庭健康管理) • [🤖 AI对话](#ai健康对话)

</div>

---

## 🎯 AuraWell能为您做什么？

### 👨‍👩‍👧‍👦 **一个账号，管理全家健康**
- 邀请家庭成员加入，设置不同权限角色
- 父母可以查看孩子的健康数据，配偶互相关心
- 长辈健康异常时，及时通知子女

### 🤖 **24/7 专业AI健康顾问**
- 基于DeepSeek推理模型，提供科学的健康建议
- 结合家庭成员的具体情况，给出个性化方案
- 支持营养、运动、睡眠、心理健康等全方位咨询

### 📊 **智能健康报告生成**
- AI自动分析家庭成员健康趋势
- 生成易懂的图表和专业解读
- 发现潜在健康风险，提前预警

### 🏆 **家庭健康互动**
- 家庭成员健康数据排行榜
- 设置健康挑战，全家一起参与
- 健康目标达成庆祝和鼓励

---

## 💡 功能演示

### 🗣️ **AI健康对话示例**

```
👤 用户: "我最近总是失眠，而且工作压力很大，该怎么办？"

🤖 AuraWell:
📋 **问题分析**
根据您描述的失眠和工作压力问题，这是现代人常见的健康困扰。让我为您制定一个综合改善方案。

🍎 **饮食建议**
• 睡前2小时避免咖啡因摄入
• 晚餐增加富含色氨酸的食物：牛奶、香蕉、燕麦
• 减少精制糖分，稳定血糖波动

🏃‍♂️ **运动建议**
• 每天下午进行30分钟中等强度运动
• 睡前1小时做10分钟瑜伽或拉伸
• 避免睡前3小时剧烈运动

😴 **睡眠优化**
• 建立固定作息：每晚10:30上床，早上6:30起床
• 卧室温度保持18-22°C，使用遮光窗帘
• 睡前30分钟放下电子设备，可以听轻音乐

🧘‍♀️ **压力管理**
• 学习4-7-8呼吸法：吸气4秒，憋气7秒，呼气8秒
• 每天记录3件感恩的事情
• 工作间隙每2小时休息10分钟

⚖️ **体重管理**
• 压力会影响皮质醇分泌，建议监测体重变化
• 保持规律饮食，避免压力性暴饮暴食

需要我为您制定详细的7天改善计划吗？
```

### 📊 **家庭健康报告示例**

```
📈 张家健康周报 (2025年6月9日-15日)

👨‍👩‍👧‍👦 家庭成员概况
• 爸爸张先生：体重稳定，运动量达标 ✅
• 妈妈李女士：睡眠质量改善，需增加运动 ⚠️
• 女儿小张：成长发育正常，营养均衡 ✅
• 儿子小李：运动时间不足，建议增加户外活动 ⚠️

🏆 本周亮点
• 全家平均步数比上周增加15%
• 李女士连续7天达到8小时睡眠目标
• 小张的身高增长了0.5cm

⚠️ 需要关注
• 张先生血压略有升高，建议减少盐分摄入
• 小李的屏幕时间超标，影响户外运动时间

📋 下周建议
• 全家周末安排2小时户外活动
• 李女士可以尝试瑜伽课程
• 张先生预约体检，监测血压变化
```

---

## 🏠 家庭健康管理

### 👨‍👩‍👧‍👦 **如何创建和管理家庭**

**第一步：创建家庭**
```bash
# 使用API创建家庭
POST /api/v1/family
{
  "name": "张家大院",
  "description": "我们是相亲相爱的一家人"
}
```

**第二步：邀请家庭成员**
```bash
# 邀请配偶
POST /api/v1/family/{family_id}/invite
{
  "email": "wife@example.com",
  "role": "MANAGER",
  "custom_message": "亲爱的，加入我们的健康管理吧！"
}

# 邀请孩子
POST /api/v1/family/{family_id}/invite
{
  "email": "child@example.com",
  "role": "VIEWER",
  "custom_message": "宝贝，让我们一起变得更健康！"
}
```

### 🔐 **家庭权限说明**

| 角色 | 能做什么 | 典型场景 |
|------|----------|----------|
| **👑 Owner (家长)** | • 查看所有成员数据<br>• 邀请/移除成员<br>• 设置权限<br>• 接收所有健康告警 | 父母管理整个家庭健康 |
| **👥 Manager (配偶)** | • 查看指定成员数据<br>• 设置健康目标<br>• 接收相关告警 | 夫妻互相关心，共同照顾孩子 |
| **👤 Viewer (成员)** | • 查看自己的数据<br>• 获取个人健康建议<br>• 参与家庭挑战 | 孩子或长辈使用个人功能 |

### 🎯 **家庭互动功能**

**健康排行榜**
- 步数排行：看看谁是今天的"步数王"
- 睡眠质量：比比谁的睡眠最规律
- 运动时长：全家一起动起来

**健康挑战赛**
- 设置家庭目标：比如"全家每天走8000步"
- 进度追踪：实时查看每个人的完成情况
- 达成庆祝：目标完成后的家庭奖励

---

## 🤖 AI健康对话

### 💬 **如何与AI对话**

**WebSocket实时对话**
```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat/user123?token=demo-test-token');

// 发送健康咨询
ws.send(JSON.stringify({
  "type": "health_chat",
  "data": {
    "message": "我想减肥，但是工作很忙，有什么简单有效的方法吗？"
  },
  "active_member_id": "user123"
}));

// 接收AI回复（流式输出）
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'chat_stream') {
    // 实时显示AI回复的每个字符
    displayToken(data.delta);
  }
};
```

### 🧠 **AI的专业能力**

**🍎 营养饮食**
- 根据身高体重计算每日热量需求
- 推荐适合的饮食搭配和食谱
- 分析营养摄入是否均衡

**🏃‍♂️ 运动健身**
- 基于体质和目标制定运动计划
- 推荐适合的运动类型和强度
- 监测运动效果和进度

**😴 睡眠管理**
- 分析睡眠质量和作息规律
- 提供改善睡眠的具体建议
- 制定个性化的睡眠计划

**🧘‍♀️ 心理健康**
- 识别压力和情绪问题
- 提供放松和减压的方法
- 建议心理调节技巧

**⚖️ 体重管理**
- 科学的减重/增重策略
- 监测体重变化趋势
- 调整饮食和运动计划

### 🔍 **AI如何给出专业建议**

1. **用户画像分析** - 综合年龄、性别、身高体重、活动水平等信息
2. **健康数据解读** - 分析历史数据，发现健康趋势和问题
3. **知识库检索** - 从权威医学文献中查找相关建议
4. **个性化定制** - 结合个人情况，生成专属的健康方案
5. **持续优化** - 根据执行效果，动态调整建议内容

### 💬 五模块结构化输出

- 🍎 **饮食营养** - 个性化营养需求计算
- 🏃‍♂️ **运动健身** - 基于体质的运动计划
- ⚖️ **体重管理** - 科学减重/增重策略
- 😴 **睡眠优化** - 睡眠质量改善建议
- 🧘‍♀️ **心理健康** - 压力管理和情绪调节

---

## 🔧 技术特色

### 🚀 **为什么选择AuraWell？**

**🤖 真正智能的AI对话**
- 基于DeepSeek Reasoner，具备复杂推理和多轮对话能力
- LangChain框架支持，实现工具调用和记忆管理
- RAG知识库加持，结合权威医学文献给出科学建议
- 五模块结构化输出，覆盖营养、运动、睡眠、心理、体重管理

**⚡ 极致的用户体验**
- WebSocket实时对话，流式输出逐字显示
- 自动重连机制，网络断开无感知恢复
- 多用户并发支持，家庭成员同时使用
- 响应式设计，支持桌面和移动设备

**🏠 专为家庭设计**
- 细粒度权限控制 (Owner/Manager/Viewer)
- 家庭成员数据隔离和隐私保护
- 健康排行榜和挑战赛，增强家庭互动
- 异常健康状态自动告警通知

**🛡️ 企业级稳定性**
- 完善的错误处理和自动重试机制
- 详细的操作日志和安全审计追踪
- API限流保护和DDoS防护
- 数据加密存储和传输安全保障

**🔌 先进的技术架构**
- MCP协议支持，13个智能化服务器协作
- 微服务架构，支持水平扩展
- 异步处理，高并发性能优化
- 多数据库支持，灵活的部署选择

**📚 专业的知识体系**
- 权威医学文献知识库
- 中文健康内容优化
- 持续更新的医学研究成果
- 个性化健康建议生成

### 🏗️ **核心技术架构**

```
🌐 前端界面 (React + TypeScript)
    ↓
📡 WebSocket实时通信 + REST API
    ↓
🛡️ 认证中间件 (JWT + 权限控制)
    ↓
🤖 LangChain AI Agent + 🔄 Agent Router
    ↓
📚 RAG知识库 (ChromaDB + 向量检索) + 🧠 DeepSeek推理引擎
    ↓
🔌 MCP协议层 (13个智能化MCP服务器)
    ↓
🗄️ 数据库层 (SQLAlchemy + PostgreSQL/SQLite)
    ↓
🔗 健康平台集成 (小米健康 + 薄荷健康 + Apple Health)
```

**技术亮点**
- **LangChain框架** - 业界领先的AI Agent开发框架，支持工具调用和记忆管理
- **DeepSeek Reasoner** - 国产顶级推理模型，具备复杂推理能力
- **RAG知识库** - ChromaDB向量数据库 + Sentence Transformers，提供专业医学知识检索
- **MCP协议支持** - 13个智能化MCP服务器自动协作，实现复杂健康管理任务
- **FastAPI** - 高性能Python Web框架，支持异步处理和自动API文档生成
- **WebSocket** - 实时双向通信，支持流式AI对话和自动重连
- **SQLAlchemy** - 企业级数据库ORM，支持多数据库和异步操作
- **家庭权限系统** - 基于角色的细粒度权限控制，保护家庭成员隐私

---

## 🚀 快速开始

### 📋 环境要求

**基础环境**
- Python 3.11+ (推荐 3.12)
- 数据库 (PostgreSQL 推荐 / SQLite 开发)
- DeepSeek API Key

**可选组件**
- ChromaDB (RAG知识库)
- Redis (缓存和会话管理)
- Docker (容器化部署)

### ⚡ 5分钟快速体验

```bash
# 1. 克隆项目
git clone https://github.com/your-org/aurawell.git
cd aurawell

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp env.example .env
# 编辑 .env 文件，添加必要配置：
# DEEPSEEK_API_KEY=your_deepseek_api_key
# DATABASE_URL=sqlite:///aurawell.db  # 开发环境
# JWT_SECRET_KEY=your_jwt_secret_key

# 4. 初始化数据库
python -c "from src.aurawell.database import get_database_manager; import asyncio; asyncio.run(get_database_manager().initialize_database())"

# 5. 启动服务
python run_api_server.py

# 6. 访问服务
# http://localhost:8000/docs - Swagger API文档
# http://localhost:8000/redoc - ReDoc API文档
# ws://localhost:8000/ws/chat/{user_id}?token=demo-test-token - WebSocket对话
```

### 🔧 **详细配置说明**

**环境变量配置 (.env)**
```bash
# AI服务配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/aurawell  # 生产环境
# DATABASE_URL=sqlite:///aurawell.db  # 开发环境

# 认证配置
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# RAG配置 (可选)
CHROMA_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# MCP配置 (可选)
MCP_SERVER_PORT=8001
MCP_WEBSOCKET_URL=ws://localhost:8001

# 健康平台API (可选)
XIAOMI_HEALTH_API_KEY=your_xiaomi_api_key
BOHE_HEALTH_API_KEY=your_bohe_api_key

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/aurawell.log
```

### 🌐 **功能测试**

**API接口测试**
```bash
# 创建家庭
curl -X POST "http://localhost:8000/api/v1/family" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-test-token" \
  -d '{"name": "我的家庭", "description": "健康生活从今天开始"}'

# 获取健康建议
curl -X POST "http://localhost:8000/api/v1/health/advice/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-test-token" \
  -d '{"goal_type": "general_health", "duration_weeks": 4, "special_requirements": "如何改善睡眠质量？"}'

# WebSocket连接测试
wscat -c "ws://localhost:8000/ws/chat/test_user?token=demo-test-token"
```

### 🌐 **前端开发**

```bash
cd frontend
npm install
npm run dev  # 开发模式: http://localhost:5175
npm run build  # 生产构建
npm run preview  # 预览构建结果
```

**前端技术栈**
- React 18 + TypeScript
- Vite 构建工具
- Tailwind CSS 样式框架
- WebSocket 实时通信
- Chart.js 数据可视化

### ☁️ **部署选项**

**Docker部署**
```bash
# 构建镜像
docker build -t aurawell:latest .

# 运行容器
docker run -d \
  --name aurawell \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY=your_key \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  aurawell:latest
```

**云端部署**
```bash
# 阿里云Serverless部署
npm install -g @serverless-devs/s
s config add  # 配置阿里云凭证
s deploy      # 一键部署

# AWS Lambda部署
pip install chalice
chalice deploy

# 腾讯云SCF部署
pip install scf
scf deploy
```

---

## 📊 核心功能模块

### 🤖 **LangChain AI智能体**
**核心能力**
- **智能对话** - 基于DeepSeek Reasoner的自然语言理解和生成
- **工具调用** - 动态调用健康分析、家庭管理等专业工具
- **记忆管理** - 维护长期对话历史和用户偏好
- **意图识别** - 准确理解用户健康咨询需求

**五模块结构化输出**
- 🍎 **饮食营养** - 个性化营养需求计算和食谱推荐
- 🏃‍♂️ **运动健身** - 基于体质的运动计划制定
- ⚖️ **体重管理** - 科学减重/增重策略
- 😴 **睡眠优化** - 睡眠质量改善建议
- 🧘‍♀️ **心理健康** - 压力管理和情绪调节

### 📚 **RAG知识库系统**
**知识来源**
- 权威医学文献和指南
- 营养学专业资料
- 运动科学研究成果
- 心理健康专业知识

**技术实现**
- **ChromaDB向量数据库** - 高效的向量存储和检索
- **Sentence Transformers** - 中文医学文本向量化
- **FAISS索引** - 快速相似性搜索
- **知识更新机制** - 定期更新最新医学研究

### 🔌 **MCP协议支持**
**13个智能化MCP服务器**
- 健康数据分析服务器
- 营养计算服务器
- 运动计划生成服务器
- 睡眠质量评估服务器
- 心理健康评估服务器
- 家庭权限管理服务器
- 报告生成服务器
- 数据同步服务器
- 通知推送服务器
- 成就系统服务器
- 数据可视化服务器
- 安全审计服务器
- 系统监控服务器

### 🏠 **家庭健康管理**
**权限控制系统**
- **Owner (家长)** - 全权管理，查看所有成员数据
- **Manager (配偶)** - 管理指定成员，设置健康目标
- **Viewer (成员)** - 查看个人数据，参与家庭活动

**家庭互动功能**
- 健康数据排行榜 (步数、睡眠、运动)
- 家庭健康挑战赛
- 成员健康状态监控
- 异常情况自动告警

### 🎯 **健康数据同步**
**支持平台**
- 小米健康 (Mi Health) - 完整API集成
- 薄荷健康 (Bohe Health) - 营养数据同步
- Apple Health (HealthKit) - iOS设备数据
- 华为健康 (Huawei Health) - 华为设备数据

**同步数据类型**
- **活动数据** - 步数、距离、卡路里消耗、运动类型
- **生理指标** - 心率、血压、体重、体脂率
- **睡眠数据** - 睡眠时长、深睡比例、睡眠质量
- **营养数据** - 饮食记录、营养摄入、热量统计

### 📈 **智能健康报告**
**AI深度分析**
```
"过去两周深睡时间下降15%，可能与工作强度上升有关。
建议：睡前做5分钟深呼吸放松，调整晚餐时间至19:00前，
减少睡前2小时的屏幕时间。预计1周内睡眠质量可改善20%。"
```

**可视化图表**
- 体重趋势折线图 - 长期体重变化分析
- 运动量柱状图 - 每日/周/月运动统计
- 睡眠质量热力图 - 睡眠模式可视化
- 心理状态雷达图 - 多维度心理健康评估
- 营养摄入饼图 - 营养结构分析

### 💬 **WebSocket实时通信**
**技术特性**
- **流式AI对话** - 逐字显示AI回复，无需等待
- **自动重连机制** - 网络断开自动恢复连接
- **多用户并发** - 支持大量用户同时在线
- **消息确认机制** - 确保消息可靠传输

**支持的消息类型**
- 健康咨询对话 (health_chat)
- 一般聊天对话 (general_chat)
- 家庭成员切换 (switch_member)
- 系统状态更新 (status_update)

### 🛡️ **数据安全与合规**
**传输安全**
- 全链路TLS 1.3加密
- WebSocket安全连接 (WSS)
- API Gateway统一鉴权
- JWT Token过期管理

**存储安全**
- 敏感字段AES-256加密
- 数据库访问最小权限原则
- 定期数据备份与恢复
- 审计日志完整记录

**隐私保护**
- 家庭成员数据隔离
- 细粒度权限控制
- 数据匿名化处理
- GDPR合规设计

---

## 🔧 开发指南

### 📁 **项目结构一览**

```
AuraWell_Agent/
├── 📁 src/aurawell/                 # 主要源代码目录
│   ├── 🤖 langchain_agent/          # LangChain AI智能体核心
│   │   ├── agent.py                 # 主要的AI对话逻辑和工具调用
│   │   ├── tools/                   # AI可以使用的工具集
│   │   │   ├── adapter.py               # 工具适配器
│   │   │   ├── health_advice_tool.py    # 健康建议生成工具
│   │   │   ├── family_tools.py          # 家庭管理工具
│   │   │   └── health_tools.py          # 健康数据分析工具
│   │   ├── services/                # 健康建议生成服务
│   │   │   ├── health_advice_service.py # 核心健康建议服务
│   │   │   └── parsers.py               # 五模块结构化解析器
│   │   ├── memory/                  # 对话记忆管理
│   │   │   └── conversation_memory.py   # 对话历史存储
│   │   └── templates/               # 提示词模板
│   │       └── health_advice_prompt.template # 健康建议提示词模板
│   ├── 🤖 agent/                    # 传统Agent系统 (兼容性保留)
│   │   ├── health_tools.py          # 健康工具集合
│   │   ├── health_tools_helpers.py  # 健康工具辅助函数
│   │   └── tools_registry.py        # 工具注册表
│   ├── 📚 rag/                      # RAG知识库系统
│   │   └── __init__.py              # RAG模块初始化
│   ├── 🔌 mcp/                      # MCP协议支持
│   │   └── __init__.py              # MCP模块初始化
│   ├── 🏠 services/                 # 业务功能服务层
│   │   ├── family_service.py        # 家庭管理服务
│   │   ├── dashboard_service.py     # 健康仪表盘服务
│   │   ├── report_service.py        # 报告生成服务
│   │   ├── chat_service.py          # 对话管理服务
│   │   ├── database_service.py      # 数据库操作服务
│   │   └── data_sanitization_service.py # 数据清理服务
│   ├── 🔌 interfaces/               # 对外接口层
│   │   ├── api_interface.py         # REST API接口
│   │   ├── websocket_interface.py   # WebSocket实时通信
│   │   └── cli_interface.py         # 命令行接口
│   ├── 🛡️ auth/                     # 认证授权系统
│   │   └── jwt_auth.py              # JWT认证实现
│   ├── 🔄 middleware/               # 中间件层
│   │   ├── cors_middleware.py       # 跨域处理
│   │   ├── error_handler.py         # 错误处理中间件
│   │   └── rate_limiter.py          # API限流中间件
│   ├── 📊 models/                   # 数据模型层
│   │   ├── family_models.py         # 家庭相关数据模型
│   │   ├── health_data_model.py     # 健康数据模型
│   │   ├── user_profile.py          # 用户档案模型
│   │   ├── api_models.py            # API请求响应模型
│   │   ├── chat_models.py           # 对话数据模型
│   │   ├── dashboard_models.py      # 仪表盘数据模型
│   │   ├── enums.py                 # 枚举定义
│   │   └── error_codes.py           # 错误代码定义
│   ├── 🗄️ database/                 # 数据库层
│   │   ├── connection.py            # 数据库连接管理
│   │   ├── models.py                # SQLAlchemy数据库模型
│   │   ├── base.py                  # 数据库基类
│   │   ├── migrations.py            # 数据库迁移
│   │   └── db_init_checker.py       # 数据库初始化检查
│   ├── 📦 repositories/             # 数据访问层
│   │   ├── base.py                  # 仓库基类
│   │   ├── user_repository.py       # 用户数据仓库
│   │   ├── health_data_repository.py # 健康数据仓库
│   │   ├── family_repository.py     # 家庭数据仓库
│   │   ├── chat_repository.py       # 对话数据仓库
│   │   ├── achievement_repository.py # 成就数据仓库
│   │   └── health_plan_repository.py # 健康计划仓库
│   ├── 🔗 integrations/             # 外部平台集成
│   │   ├── xiaomi_health_client.py  # 小米健康API集成
│   │   ├── bohe_health_client.py    # 薄荷健康API集成
│   │   ├── apple_health_client.py   # Apple Health集成
│   │   └── generic_health_api_client.py # 通用健康API客户端
│   ├── 🎮 gamification/             # 游戏化系统
│   │   └── achievement_system.py    # 成就系统
│   ├── 💬 conversation/             # 对话管理
│   │   ├── memory_manager.py        # 记忆管理器
│   │   └── session_manager.py       # 会话管理器
│   ├── ⚙️ config/                   # 配置管理
│   │   ├── settings.py              # 应用配置
│   │   ├── health_constants.py      # 健康常量定义
│   │   └── logging_config.py        # 日志配置
│   ├── 🔧 core/                     # 核心组件
│   │   ├── agent_router.py          # 智能Agent路由
│   │   ├── deepseek_client.py       # DeepSeek AI客户端
│   │   ├── orchestrator_v2.py       # 系统协调器
│   │   ├── permissions.py           # 权限管理
│   │   └── exceptions.py            # 异常定义
│   ├── 🛠️ utils/                    # 工具函数
│   │   ├── health_calculations.py   # 健康指标计算
│   │   ├── data_validation.py       # 数据验证
│   │   ├── async_tasks.py           # 异步任务管理
│   │   ├── cache.py                 # 缓存工具
│   │   ├── date_utils.py            # 日期工具
│   │   └── encryption_utils.py      # 加密工具
│   └── main.py                      # 应用入口文件
├── 🌐 frontend/                     # 前端项目目录 (Vue 3 + Vite)
│   ├── src/                         # 前端源代码
│   │   ├── App.vue                  # 主应用组件
│   │   ├── main.js                  # 应用入口文件
│   │   ├── style.css                # 全局样式
│   │   ├── api/                     # API接口层
│   │   │   ├── chat.js              # 聊天API接口
│   │   │   ├── healthPlan.js        # 健康计划API接口
│   │   │   └── user.js              # 用户API接口
│   │   ├── components/              # 可复用组件
│   │   │   ├── GlobalHeader.vue     # 全局头部组件
│   │   │   ├── chat/                # 聊天相关组件
│   │   │   └── health/              # 健康相关组件
│   │   ├── layout/                  # 布局组件
│   │   │   ├── AdminLayout.vue      # 管理员布局
│   │   │   └── BasicLayout.vue      # 基础布局
│   │   ├── router/                  # 路由配置
│   │   │   └── index.js             # 路由定义
│   │   ├── stores/                  # 状态管理 (Pinia)
│   │   │   ├── auth.js              # 认证状态
│   │   │   ├── chat.js              # 聊天状态
│   │   │   ├── health.js            # 健康数据状态
│   │   │   ├── healthPlan.js        # 健康计划状态
│   │   │   └── user.js              # 用户状态
│   │   ├── utils/                   # 工具函数
│   │   │   ├── healthPlanUtils.js   # 健康计划工具
│   │   │   └── request.js           # HTTP请求工具
│   │   └── views/                   # 页面组件
│   │       ├── Login.vue            # 登录页面
│   │       ├── Register.vue         # 注册页面
│   │       ├── admin/               # 管理员页面
│   │       └── user/                # 用户页面
│   ├── public/                      # 静态资源
│   │   └── vite.svg                 # Vite图标
│   ├── node_modules/                # 前端依赖包
│   ├── package.json                 # 前端依赖配置
│   ├── package-lock.json            # 依赖锁定文件
│   ├── vite.config.js               # Vite构建配置
│   ├── tailwind.config.js           # Tailwind CSS配置
│   ├── postcss.config.js            # PostCSS配置
│   ├── index.html                   # HTML入口文件
│   └── README.md                    # 前端项目说明
├── 📚 docs/                         # 项目文档
│   ├── API.md                       # API接口文档
│   ├── ARCHITECTURE_SUMMARY.md      # 架构总结文档
│   ├── DEPLOYMENT.md                # 部署指南
│   ├── FASTAPI_IMPLEMENTATION.md    # FastAPI实现文档
│   ├── VERSION_MANAGEMENT.md        # 版本管理文档
│   ├── development_roadmap.md       # 开发路线图
│   ├── family_architecture.md       # 家庭架构文档
│   ├── tools_contract.md            # 工具契约文档
│   └── reports/                     # 报告文档
│       ├── AURAWELL_FAMILY_AGENT_AUDIT_REPORT.md      # 家庭代理审计报告
│       └── FAMILY_AGENT_AUDIT_COMPLETION_REPORT.md    # 家庭代理审计完成报告
├── 🧪 tests/                        # 测试文件
│   ├── test_health_constants.py     # 健康常量测试
│   ├── __pycache__/                 # Python缓存文件
│   └── README.md                    # 测试说明文档
├── 🚀 scripts/                      # 部署和工具脚本
│   ├── __init__.py                  # Python包初始化
│   ├── mcp_auto_setup.py            # MCP自动设置脚本
│   ├── deploy_mcp_config.ps1        # MCP部署配置
│   ├── start_mcp_env.ps1            # MCP环境启动
│   └── release.py                   # 发布脚本
├── ☁️ deployment/                   # 部署配置
│   └── serverless.yml              # Serverless部署配置
├── 📝 logs/                         # 日志文件
│   ├── aurawell.log                 # 应用日志
│   └── aurawell_errors.log          # 错误日志
├── 📋 requirements.txt              # Python依赖配置
├── 🔧 run_api_server.py             # API服务器启动脚本
├── ⚙️ env.example                   # 环境变量配置示例
├── 📖 README.md                     # 项目说明文档
├── 📄 CHANGELOG.md                  # 版本更新日志
├── 📋 AURAWELL_DEVELOPMENT_GUIDE.md # 开发指南
└── 🗄️ aurawell.db*                  # SQLite数据库文件 (开发环境)
```

### 🎯 **开发进展**

**✅ 已完成功能**
- **LangChain AI智能体** - 基于DeepSeek的智能健康顾问，支持工具调用和记忆管理
- **家庭管理系统** - 完整的多用户权限控制和成员管理功能
- **WebSocket实时通信** - 流式AI对话体验，支持自动重连和并发处理
- **健康数据集成** - 小米健康、薄荷健康等平台的数据同步
- **智能健康报告** - AI生成个性化健康分析和可视化图表
- **RAG知识库** - ChromaDB向量数据库和医学知识检索系统
- **MCP协议支持** - 13个智能化MCP服务器自动协作
- **数据安全系统** - 企业级权限控制、JWT认证和审计日志
- **FastAPI后端** - 完整的REST API和自动文档生成
- **数据库层** - SQLAlchemy ORM，支持PostgreSQL和SQLite

**🔄 开发中功能**
- **前端界面** - Vue 3 + TypeScript + Ant Design Vue用户界面开发
- **高级分析** - 更复杂的健康趋势分析和预测
- **移动端适配** - 响应式设计和PWA支持

**📋 计划中功能**
- **机器学习模型** - 个性化健康预测模型
- **更多健康平台** - 华为健康、Apple Health等集成
- **智能提醒系统** - 基于AI的个性化健康提醒
- **社交功能** - 家庭健康社区和分享功能

---

## 📋 如何集成AuraWell

### 🔌 **主要API接口**

**创建家庭**
```bash
POST /api/v1/family
{
  "name": "我的家庭",
  "description": "健康生活从今天开始"
}
```

**邀请家庭成员**
```bash
POST /api/v1/family/{family_id}/invite
{
  "email": "family@example.com",
  "role": "MANAGER"
}
```

**获取健康建议**
```bash
POST /api/v1/health/advice/comprehensive
{
  "goal_type": "weight_loss",
  "duration_weeks": 4,
  "special_requirements": "如何改善睡眠质量？"
}
```

**生成健康报告**
```bash
GET /api/v1/family/{family_id}/report?members=user1,user2&start_date=2025-06-01&end_date=2025-06-15
```

### 💬 **WebSocket实时对话**

```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat/user123?token=demo-test-token');

// 发送健康咨询
ws.send(JSON.stringify({
  "type": "health_chat",
  "data": {
    "message": "我想减肥，有什么建议吗？"
  },
  "active_member_id": "user123"
}));

// 接收AI回复
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'chat_stream') {
    console.log('AI回复:', data.delta);
  }
};
```

### 📖 **完整API文档**

启动服务后，访问以下地址查看完整的API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛡️ 安全与稳定性

### 🔒 **数据安全保障**
- **权限控制** - 基于角色的细粒度权限管理
- **数据加密** - 敏感信息加密存储和传输
- **审计日志** - 完整的操作记录和追踪
- **API限流** - 防止恶意请求和系统过载

### 📊 **系统稳定性**
- **错误重试** - 自动重试机制，提高成功率
- **健康检查** - 实时监控系统状态
- **优雅降级** - 部分功能异常时保证核心功能可用
- **负载均衡** - 支持水平扩展，应对高并发

---

## 🌟 为什么选择AuraWell？

### 💡 **解决真实痛点**
- **家庭健康管理难** - 一个平台管理全家健康，不再各自为战
- **专业建议获取难** - 24/7 AI健康顾问，随时获得专业建议
- **健康数据分散** - 统一的健康数据管理和分析
- **缺乏互动激励** - 家庭成员互相鼓励，让健康管理更有趣

### 🚀 **技术优势**
- **国产AI模型** - 基于DeepSeek，理解中文语境和中国人健康习惯
- **企业级架构** - 稳定可靠，支持大规模用户使用
- **开源透明** - 代码开源，可自由定制和部署
- **持续更新** - 活跃的开发团队，持续优化和新功能开发

---

## 🤝 加入我们

### 🔄 **贡献代码**
```bash
# Fork项目 → 创建分支 → 提交代码 → 发起PR
git checkout -b feature/your-feature
git commit -m "feat: 添加新功能"
git push origin feature/your-feature
```

### 💬 **反馈建议**
- 🐛 [报告Bug](https://github.com/your-org/aurawell/issues)
- 💡 [功能建议](https://github.com/your-org/aurawell/discussions)
- 📧 [联系我们](mailto:team@aurawell.com)

### 📖 **学习资源**
- [LangChain官方文档](https://python.langchain.com/)
- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议，欢迎自由使用和修改。

---

<div align="center">

### 🎯 **让健康管理变得简单有趣**

**AuraWell** - *每个家庭都值得拥有的AI健康助手* 💙

[⭐ 给我们一个Star](https://github.com/your-org/aurawell) • [🚀 立即体验](http://demo.aurawell.com) • [📖 查看文档](https://docs.aurawell.com)

*"健康是1，其他都是0。让AuraWell守护您和家人的健康。"*

</div>
