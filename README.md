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
- 基于DeepSeek Reasoner，具备复杂推理能力
- 不是简单的问答，而是能理解上下文的深度对话
- 结合医学知识库，给出科学可信的建议

**⚡ 极致的用户体验**
- WebSocket实时对话，像聊天一样自然
- 流式输出，AI回复逐字显示，无需等待
- 自动重连，网络断开也不影响使用

**🏠 专为家庭设计**
- 一个账号管理全家健康
- 灵活的权限控制，保护隐私
- 家庭互动功能，让健康管理更有趣

**🛡️ 企业级稳定性**
- 完善的错误处理和重试机制
- 详细的操作日志和审计追踪
- API限流保护，防止滥用

### 🏗️ **核心技术架构**

```
🌐 用户界面
    ↓
📡 WebSocket实时通信
    ↓
🤖 LangChain AI Agent
    ↓
🧠 DeepSeek推理引擎 + 📚 医学知识库
    ↓
🗄️ 数据库 (用户数据 + 健康记录)
```

**技术亮点**
- **LangChain框架** - 业界领先的AI Agent开发框架
- **DeepSeek Reasoner** - 国产顶级推理模型
- **FastAPI** - 高性能Python Web框架
- **WebSocket** - 实时双向通信
- **SQLAlchemy** - 企业级数据库ORM

---

## 🚀 快速开始

### 📋 环境要求

- Python 3.11+
- 数据库 (PostgreSQL/MySQL)
- DeepSeek API Key

### ⚡ 5分钟快速体验

```bash
# 1. 克隆项目
git clone https://github.com/your-org/aurawell.git
cd aurawell

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的 DeepSeek API Key

# 4. 启动服务
python run_api_server.py

# 5. 打开浏览器访问
# http://localhost:8000/docs - API文档
# ws://localhost:8000/ws/chat/{user_id} - WebSocket对话
```

### 🌐 在线体验

如果你想直接体验功能，可以使用我们的在线演示：

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

### 📁 **项目结构一览**

```
src/aurawell/
├── 🤖 langchain_agent/          # AI智能体核心
│   ├── agent.py                 # 主要的AI对话逻辑
│   ├── tools/                   # AI可以使用的工具
│   └── services/                # 健康建议生成服务
├── 🏠 services/                 # 业务功能
│   ├── family_service.py        # 家庭管理
│   ├── dashboard_service.py     # 健康仪表盘
│   └── report_service.py        # 报告生成
├── 🔌 interfaces/               # 对外接口
│   ├── api_interface.py         # REST API
│   └── websocket_interface.py   # 实时对话
├── 📊 models/                   # 数据模型
│   ├── family_models.py         # 家庭相关数据
│   └── health_models.py         # 健康相关数据
├── ⚙️ config/                   # 配置管理
│   ├── settings.py              # 应用配置
│   └── health_constants.py      # 健康常量
└── 🔧 core/                     # 核心组件
    ├── agent_router.py          # 智能路由
    └── deepseek_client.py       # AI客户端
```

### 👥 **开发团队**

| 成员 | 角色 | 主要贡献 |
|------|------|----------|
| **Terence** | 项目负责人 | 架构设计、核心功能开发 |
| **wizardG7777777** | 后端开发 | 用户意图识别、对话管理、测试 |
| **Young** | 前端开发 | 用户界面、交互体验 |

### 🎯 **开发进展**

- ✅ **核心AI对话** - 基于LangChain的智能健康顾问
- ✅ **家庭管理** - 多用户权限控制和成员管理
- ✅ **实时通信** - WebSocket流式对话体验
- ✅ **健康报告** - AI生成个性化健康分析
- ✅ **数据安全** - 企业级权限控制和审计日志
- 🔄 **前端界面** - 用户友好的Web界面开发中

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