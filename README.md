# AuraWell - 超个性化健康生活方式编排AI Agent

## 项目简介

AuraWell是一个基于AI驱动的个性化健康管理平台，整合用户健身目标、日常作息、饮食偏好、工作日程及社交活动，提供智能化的健康建议与习惯养成支持。

## 核心特性

### 🤖 智能AI引擎
- **DeepSeek R1模型**: 先进的推理能力，提供个性化健康建议
- **MCP工具集成**: 13个智能化MCP服务器自动协作
- **多模态数据分析**: 整合健康数据、用户行为、环境因素

### 🏥 健康数据集成
- **薄荷健康API**: 营养数据和饮食管理
- **小米健康API**: 运动数据和生理指标
- **苹果HealthKit**: iOS设备健康数据同步
- **通用健康API**: 支持多种健康设备

### 👨‍👩‍👧‍👦 家庭健康管理
- **多成员管理**: 支持家庭成员健康档案
- **互动挑战**: 家庭健康目标和竞赛
- **智能提醒**: 基于家庭作息的个性化提醒

### 📊 数据可视化
- **健康仪表盘**: 实时健康指标监控
- **趋势分析**: 长期健康数据趋势
- **科学依据**: 基于权威研究的建议支撑

## 技术架构

### 后端
- **框架**: Python FastAPI
- **数据库**: SQLAlchemy + SQLite
- **AI引擎**: DeepSeek API
- **数据模型**: Pydantic

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件**: Ant Design Vue
- **图表**: ECharts + QuickChart
- **样式**: Tailwind CSS

### 智能工具栈
- **MCP服务器**: 13个专业化工具服务
- **数据分析**: Calculator + Sequential-thinking
- **信息检索**: Brave-search + Memory
- **可视化**: QuickChart + ECharts

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- SQLite 3

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/AuraWell_Agent.git
cd AuraWell_Agent
```

2. **后端设置**
```bash
# 创建虚拟环境
python -m venv aurawell_env
source aurawell_env/bin/activate  # Windows: aurawell_env\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入API密钥
```

3. **前端设置**
```bash
cd frontend
npm install
```

4. **启动服务**

后端服务：
```bash
# 在项目根目录
python -m src.aurawell.main
```

前端服务：
```bash
# 在frontend目录
npm run dev
```

访问 `http://localhost:5173` 体验AuraWell健康助手

## 核心功能

### 🎯 个性化健康规划
- 基于用户画像的定制化健康计划
- 智能目标设定和进度跟踪
- 动态计划调整和优化建议

### 💬 智能健康对话
- 自然语言健康咨询
- 基于科学研究的建议
- 实时数据分析和可视化

### 📈 健康数据分析
- 多维度健康指标监控
- 趋势预测和风险评估
- 个性化洞察报告

### 🔬 科学依据支撑
- 权威医学研究引用
- 可信度评估系统
- 实时信息验证

## API文档

项目提供完整的RESTful API接口：

- **用户管理**: `/api/users/`
- **健康数据**: `/api/health/`
- **AI对话**: `/api/chat/`
- **家庭管理**: `/api/family/`

详细API文档请访问: `http://localhost:8000/docs`

## 数据安全

AuraWell严格遵循数据保护标准：

- **加密存储**: 敏感健康数据端到端加密
- **隐私保护**: 遵循GDPR和HIPAA标准
- **访问控制**: 基于角色的权限管理
- **审计日志**: 完整的数据访问记录

## 部署

### Docker部署
```bash
# 构建镜像
docker build -t aurawell .

# 运行容器
docker run -p 8000:8000 -p 5173:5173 aurawell
```

### 云端部署
支持部署到主流云平台：
- AWS (Lambda + RDS)
- 阿里云 (ECS + RDS)
- 腾讯云 (CVM + CDB)

## 贡献指南

欢迎社区贡献！请查看以下指南：

1. Fork项目仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add some amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系我们

- **项目主页**: https://github.com/your-username/AuraWell_Agent
- **问题反馈**: https://github.com/your-username/AuraWell_Agent/issues
- **邮箱**: aurawell@example.com

---

**让AI助力每个人都拥有更健康的生活方式** 🌟
