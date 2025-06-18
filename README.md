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

## 🎯 项目核心特色

### 🤖 **13个MCP智能服务器自动协作**
AuraWell基于MCP (Model Context Protocol) 架构，集成了13个专业化的智能服务器，实现真正的AI自动化健康管理：

- **🧠 推理引擎**: `sequential-thinking` - 深度推理分析用户健康状况
- **📊 数据分析**: `database-sqlite` + `calculator` - 智能健康数据分析和指标计算  
- **📈 可视化**: `quickchart` - 自动生成健康趋势图表
- **🔍 智能搜索**: `brave-search` + `fetch` - 获取最新健康科学研究
- **🧭 记忆系统**: `memory` - 构建用户健康画像知识图谱
- **⚡ 代码执行**: `run-python` - 执行复杂健康算法
- **🌤️ 环境感知**: `weather` - 基于天气的运动建议
- **📁 文档管理**: `filesystem` + `github` + `notion` - 健康档案管理
- **🎨 设计协作**: `figma` - UI/UX设计资源获取
- **⏰ 时间管理**: `time` - 智能健康提醒调度

### 🏥 **真正个性化的健康建议**
- **全方位健康分析**: 营养、运动、睡眠、心理、体重管理五大维度
- **AI深度推理**: 基于DeepSeek-R1模型，具备复杂健康推理能力
- **数据驱动决策**: 自动分析历史数据，识别健康模式和风险
- **科学研究支撑**: 实时获取最新医学研究，确保建议的科学性

### 👨‍👩‍👧‍👦 **家庭健康协作管理**
- **多成员管理**: 一个账号管理全家健康，支持不同权限角色
- **智能权限控制**: Owner/Manager/Viewer三级权限，保护隐私
- **家庭健康报告**: AI自动生成家庭健康周报月报
- **互动激励系统**: 健康挑战、排行榜、成就系统

---

## 🏗️ 技术架构现状

### 🔧 **核心技术栈**
```
🌐 前端层: Vue 3 + TypeScript + Tailwind CSS
    ↓ WebSocket实时通信
📡 API网关: FastAPI + WebSocket + JWT认证
    ↓ MCP协议通信
🤖 AI引擎: DeepSeek-R1 + 13个MCP智能服务器
    ↓ 数据层访问
🗄️ 数据层: SQLite + 用户健康画像 + 知识图谱
```

### 🎯 **MCP智能自动化系统**
当用户发起健康咨询时，系统会自动触发相应的工具链：

**健康数据分析链**:
```
用户询问"我的健康状况如何？" 
  ↓ 自动触发
1. database-sqlite → 查询历史健康数据
2. calculator → 计算BMI、基础代谢等指标
3. sequential-thinking → 深度分析健康趋势
4. quickchart → 生成可视化健康仪表盘
5. memory → 更新用户健康画像
```

**营养优化建议链**:
```
用户询问"如何改善饮食？"
  ↓ 自动触发  
1. brave-search → 搜索最新营养科学研究
2. memory → 获取用户饮食偏好和历史
3. calculator → 计算个人营养需求
4. sequential-thinking → 个性化营养方案推理
5. quickchart → 生成营养摄入分析图
```

## 📊 **已实现的核心功能模块**

### 🔐 **用户认证与家庭管理**
- ✅ JWT Token认证系统
- ✅ 家庭创建、邀请、权限管理
- ✅ 多成员切换和数据隔离
- ✅ 操作审计日志

### 🤖 **AI智能对话系统**
- ✅ WebSocket实时流式对话
- ✅ 上下文记忆和会话管理
- ✅ 五维度健康建议输出（营养/运动/体重/睡眠/心理）
- ✅ 自动工具选择和链式调用

### 📈 **健康数据管理**
- ✅ 用户健康档案管理
- ✅ 健康目标设定和跟踪
- ✅ 智能健康报告生成
- ✅ 数据可视化图表自动生成

### 📱 **前端用户界面**
- ✅ 响应式现代化UI设计
- ✅ 实时聊天界面（支持流式输出）
- ✅ 家庭成员管理界面
- ✅ 健康数据仪表盘
- ✅ 健康计划制定和追踪

---

## 🚀 已实现的AI智能化特性

### 🧠 **自动推理分析**
基于`sequential-thinking` MCP服务器，AuraWell能够：
- 分析用户健康数据的深层关联
- 识别生活习惯对健康的潜在影响
- 推理最适合的健康改善策略
- 预测健康趋势和潜在风险

### 📊 **自动数据可视化**
基于`quickchart` MCP服务器，系统自动生成：
- 体重变化趋势图
- 运动量统计柱状图
- 营养摄入雷达图
- 睡眠质量热力图
- 健康指标仪表盘

### 🔍 **实时健康信息研究**
基于`brave-search` + `fetch` MCP服务器：
- 自动搜索最新健康科学研究
- 验证健康建议的科学依据
- 获取权威营养和运动指导
- 跟踪健康领域最新发展

### 🧭 **智能记忆系统**
基于`memory` MCP服务器，构建用户健康知识图谱：
- 记录用户健康偏好和历史
- 构建个性化健康画像
- 跟踪健康改善进展
- 积累家庭健康知识

---

## 💡 核心功能演示

### 🗣️ **AI健康对话示例**

```
👤 用户: "我最近总是失眠，压力也很大，该怎么办？"

🤖 AuraWell: [自动触发分析链]
📋 正在分析您的情况...
   ├─ 🔍 搜索最新睡眠研究 (brave-search)
   ├─ 📊 计算您的压力指数 (calculator)  
   ├─ 🧠 深度分析影响因素 (sequential-thinking)
   └─ 📈 生成睡眠改善方案 (memory + quickchart)

🍎 **饮食调整建议**
• 睡前3小时避免咖啡因：咖啡、茶、巧克力
• 增加富含色氨酸食物：牛奶、香蕉、燕麦、火鸡肉
• 晚餐控制在7分饱，避免重口味刺激性食物
• 睡前1小时可饮用洋甘菊茶，有助放松

🏃‍♂️ **运动改善方案**
• 每天下午15:00-17:00进行30分钟有氧运动
• 睡前2小时做15分钟瑜伽或深度拉伸
• 避免睡前4小时剧烈运动，会提高体温影响睡眠
• 推荐：散步、太极、游泳等低强度运动

😴 **睡眠环境优化**
• 卧室温度保持18-22°C，湿度50-60%
• 使用遮光窗帘，营造暗环境促进褪黑素分泌
• 建立固定作息：22:30上床，6:30起床
• 睡前1小时关闭电子设备，可听轻音乐

🧘‍♀️ **压力管理技巧**
• 4-7-8呼吸法：吸气4秒，憋气7秒，呼气8秒
• 每天记录3件感恩的事情，培养积极心态
• 工作时设置番茄钟，每25分钟休息5分钟
• 学习渐进式肌肉放松法，缓解身体紧张

⚖️ **体重监测**
• 压力会导致皮质醇分泌增加，可能影响体重
• 建议每周同一时间测量体重，记录变化
• 避免压力性进食，选择健康零食如坚果、水果

📊 **个性化7天改善计划** [自动生成图表]
我已为您制定了详细的改善方案，预计2-3周可看到明显效果。
需要我为您设置每日提醒吗？
```

### 📊 **智能健康报告示例**

```
📈 张家健康周报 (2025年6月9日-15日)

👨‍👩‍👧‍👦 **家庭健康概览**
┌─────────────────────────────────────────┐
│ 成员      │ 健康评分 │ 主要表现    │ 需关注 │
├─────────────────────────────────────────┤
│ 张先生    │   85分   │ 运动达标✅  │ 血压略高⚠️│
│ 李女士    │   78分   │ 睡眠改善✅  │ 运动不足⚠️│
│ 小明      │   92分   │ 成长正常✅  │     -    │
│ 小丽      │   76分   │ 营养均衡✅  │ 屏幕时间长⚠️│
└─────────────────────────────────────────┘

🏆 **本周健康亮点**
• 全家平均步数10,847步，比上周增加18% 📈
• 李女士连续7天达到8小时睡眠目标 🎯
• 小明身高增长0.8cm，发育指标优秀 📏
• 张先生减重0.5kg，朝目标稳步前进 ⚖️

⚠️ **需要重点关注**
• 张先生血压略有升高(138/89)，建议减盐限酒
• 小丽每日屏幕时间6.2小时，影响户外活动
• 李女士运动量仅达标准的60%，需增加活动

📋 **下周改善建议**
• 全家周末安排3小时户外活动(天气预报：晴朗☀️)
• 张先生预约体检，监测血压变化趋势
• 李女士可尝试瑜伽或游泳，每周3次
• 小丽限制屏幕时间，增加阅读和运动时间

📊 [自动生成趋势图表]
体重变化图 | 运动量对比 | 睡眠质量分析 | 营养摄入评估
```

---

## 🚀 快速开始

### 📋 **系统要求**
- Python 3.11+
- Node.js 18+
- Git
- DeepSeek API Key

### ⚡ **5分钟启动指南**

```bash
# 1. 克隆项目
git clone https://github.com/your-org/AuraWell_Agent.git
cd AuraWell_Agent

# 2. 后端环境配置
pip install -r requirements.txt
cp env.example .env
# 编辑 .env 文件，添加 DEEPSEEK_API_KEY

# 3. 启动后端服务
cd src
python -m aurawell.main

# 4. 启动前端开发服务器
cd ../frontend  
npm install
npm run dev

# 5. 访问应用
# 前端界面: http://localhost:5174
# API文档: http://localhost:8000/docs
# WebSocket: ws://localhost:8000/ws/chat/{user_id}
```

### 🔧 **MCP服务器配置**
项目已预配置13个MCP服务器，只需运行自动配置脚本：

```bash
# Windows PowerShell
./scripts/start_mcp_env.ps1

# 或者手动配置
python scripts/mcp_auto_setup.py
```

### 🧪 **快速体验功能**

```bash
# 1. 创建测试用户和家庭
curl -X POST "http://localhost:8000/api/v1/family" \
  -H "Authorization: Bearer demo-test-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "测试家庭", "description": "快速体验AuraWell功能"}'

# 2. 获取AI健康建议  
curl -X POST "http://localhost:8000/api/v1/health/advice/comprehensive" \
  -H "Authorization: Bearer demo-test-token" \
  -H "Content-Type: application/json" \
  -d '{"goal_type": "general_health", "special_requirements": "改善睡眠质量"}'

# 3. WebSocket实时对话测试
# 使用浏览器访问前端界面，体验AI实时对话功能
```

---

## 📁 项目结构详解

```
AuraWell_Agent/
├── 🎨 frontend/                    # Vue 3前端应用
│   ├── src/
│   │   ├── 🗣️ components/chat/     # AI对话组件  
│   │   ├── 👨‍👩‍👧‍👦 components/family/  # 家庭管理组件
│   │   ├── 📊 components/charts/   # 健康数据可视化
│   │   ├── 🏥 views/user/          # 用户功能页面
│   │   └── 📡 stores/              # 状态管理
│   └── 🎯 package.json
├── 🤖 src/aurawell/               # Python后端核心
│   ├── 🧠 agent/                  # MCP工具注册和健康助手
│   │   ├── health_tools.py        # 13个MCP工具封装
│   │   └── tools_registry.py      # 智能工具选择器
│   ├── 🌐 interfaces/             # API和WebSocket接口
│   │   ├── api_interface.py       # REST API路由
│   │   └── websocket_interface.py # 实时对话接口
│   ├── 🏠 services/               # 业务逻辑服务
│   │   ├── family_service.py      # 家庭管理逻辑
│   │   ├── chat_service.py        # AI对话服务
│   │   └── dashboard_service.py   # 健康仪表盘
│   ├── 📊 models/                 # 数据模型定义
│   │   ├── family_models.py       # 家庭数据模型
│   │   ├── health_data_model.py   # 健康数据模型
│   │   └── chat_models.py         # 对话数据模型
│   ├── 🗄️ database/               # 数据库层
│   │   ├── models.py              # SQLAlchemy模型
│   │   └── connection.py          # 数据库连接管理
│   ├── 🔧 core/                   # 核心组件
│   │   ├── orchestrator_v2.py     # MCP编排器
│   │   └── deepseek_client.py     # AI模型客户端
│   └── ⚙️ config/                 # 配置管理
│       ├── settings.py            # 应用配置
│       └── health_constants.py    # 健康常量定义
├── 🛠️ scripts/                    # 自动化脚本
│   ├── mcp_auto_setup.py         # MCP服务器自动配置
│   └── start_mcp_env.ps1         # Windows启动脚本
└── 📋 requirements.txt            # Python依赖
```

---

## 🛡️ 数据安全与合规

### 🔐 **安全特性**
- **JWT认证**: 无状态Token认证，支持自动刷新
- **权限控制**: 基于角色的细粒度权限管理
- **数据加密**: 敏感健康数据AES-256加密存储
- **API限流**: 智能防护，防止恶意请求
- **审计日志**: 完整的操作记录和追踪

### 📊 **数据隐私保护**
- **最小权限原则**: 用户只能访问被授权的家庭成员数据
- **数据匿名化**: 统计分析时自动去除个人标识信息
- **本地化部署**: 支持私有化部署，数据不出门
- **GDPR兼容**: 符合欧盟通用数据保护条例

### 🏥 **医疗伦理边界**
- **建议非诊断**: 明确声明AI建议仅供参考，不能替代专业医疗
- **多源验证**: 通过多个权威来源验证健康建议的科学性
- **透明推理**: 使用sequential-thinking展示AI建议的推理过程
- **用户自主**: 强调最终决定权在用户，提供选择而非强制

---

## 🌟 系统技术亮点

### ⚡ **极致性能优化**
- **并行MCP调用**: 多个工具同时执行，响应速度提升3-5倍
- **智能缓存**: 健康数据和AI响应智能缓存，减少重复计算
- **流式输出**: WebSocket流式传输，AI回复逐字显示
- **异步处理**: 全异步架构，支持高并发访问

### 🔄 **智能自适应**
- **动态工具选择**: 根据用户问题自动选择最适合的MCP工具组合
- **上下文感知**: 基于对话历史和用户画像提供个性化建议
- **学习优化**: 根据用户反馈持续优化建议质量
- **故障自愈**: 工具调用失败时自动切换备用方案

### 📈 **可扩展架构**
- **模块化设计**: 新功能可独立开发和部署
- **插件化MCP**: 新的健康工具可轻松集成
- **微服务就绪**: 支持容器化部署和水平扩展
- **API优先**: 完整的REST API，方便第三方集成

---

## 🔮 未来发展方向

### 🎯 **即将上线功能**
- 🔜 **移动端APP**: React Native跨平台移动应用
- 🔜 **健康设备集成**: Apple Health、华为健康、小米健康等
- 🔜 **AI语音交互**: 语音输入和AI语音回复
- 🔜 **智能提醒系统**: 基于用户作息的个性化健康提醒

### 🚀 **技术演进规划**  
- **多模态AI**: 支持图像识别（食物拍照营养分析）
- **联邦学习**: 在保护隐私的前提下，利用群体数据优化AI
- **边缘计算**: 本地AI推理，降低延迟提升隐私保护
- **区块链验证**: 健康数据真实性验证和激励机制

---

## 🤝 开源社区

### 💡 **贡献指南**
欢迎参与AuraWell的开发和改进：

```bash
# 1. Fork项目到您的GitHub
# 2. 克隆到本地
git clone https://github.com/yourusername/AuraWell_Agent.git

# 3. 创建功能分支
git checkout -b feature/awesome-feature

# 4. 提交代码
git commit -m "feat: 添加超棒的新功能"

# 5. 推送并创建Pull Request
git push origin feature/awesome-feature
```

### 📖 **学习资源**
- **MCP官方文档**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **DeepSeek API**: [DeepSeek开发者平台](https://platform.deepseek.com/)
- **FastAPI文档**: [FastAPI官方指南](https://fastapi.tiangolo.com/)
- **Vue 3指南**: [Vue.js官方文档](https://vuejs.org/)

### 💬 **技术交流**
- 🐛 [报告Bug](https://github.com/your-org/AuraWell_Agent/issues)
- 💡 [功能建议](https://github.com/your-org/AuraWell_Agent/discussions)
- 📧 [技术支持](mailto:tech@aurawell.ai)
- 💬 [开发者QQ群](qq://群号)

---

<div align="center">

### 🎯 **智能化健康管理的未来，从AuraWell开始**

**让每个家庭都拥有专属的AI健康顾问** 💙

基于13个MCP智能服务器，AuraWell提供真正个性化的健康生活方式编排，让健康管理变得简单、智能、有趣。

[⭐ 给项目点星](https://github.com/your-org/AuraWell_Agent) • [🚀 立即体验](http://localhost:5174) • [📖 查看API文档](http://localhost:8000/docs)

*"健康是1，其他都是0。让AuraWell的AI智能守护您和家人的健康。"*

**MIT开源协议 | 持续更新中 | Made with ❤️ in China**

</div>
