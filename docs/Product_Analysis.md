# AuraWell 产品分析（基于代码库实现）

> 面向投资人、技术团队与业务团队的专业产品分析文档（v2.1）。本文严格基于仓库实现进行撰写，引用了真实文件/端点/依赖，并在撰写时完成了关键准确性校验。

---

## 一、项目概述

### 1.1 核心定位与价值主张
- AuraWell 是“超个性化健康生活方式编排”AI 助手，目标是将用户健康画像（基础信息、活动、睡眠、营养等）与家庭关系整合为可执行、可追踪的健康计划。
- 核心价值：
  - 使用大模型推理（DeepSeek 系列）+ 工具编排（MCP）+ 健康计算工具集，产出可解释、可验证、有证据链支撑的结构化健康建议与日常行动清单。
  - 支持家庭协作、成就与激励机制，形成高频、长期、可复访的使用闭环。

### 1.2 目标用户与使用场景
- 个人健康管理者：体重/体脂管理、运动处方、睡眠优化、压力管理、饮食结构调整。
- 家庭健康管理者：统一管理家庭成员健康档案、权限与提醒，关怀老人与儿童的健康风险。
- 企业/保险等 B 端场景：员工健康福利、随访与合规报表、健康风险评估与干预建议。

### 1.3 独特卖点与竞争优势
- AI 原生能力：DeepSeek + LangChain + MCP 工具链，具备强推理、强自动化执行能力。
- 家庭协作差异化：多成员、权限、互动与成就系统，区别于“单人健康 App”。
- 循证与可解释：内置健康计算工具与 RAG 文档检索，提供解释与引用，提升可信度。
- 交付友好：完善的前端性能优化、移动端适配与文档体系，支持快速推广与二次开发。

---

## 二、问题与解决方案

### 2.1 用户痛点
- 建议“泛化/不连续/不可执行”，难以坚持；
- 家庭协作缺失，难以形成外部激励；
- 缺乏证据链与可信度支撑；
- 跨平台健康数据难以统一与利用。

### 2.2 市场方案不足
- 传统健康记录类：强记录弱推理；
- 通用 AI 聊天：强对话弱结构化与落地执行；
- 家庭场景、激励链路、证据引用普遍缺失。

### 2.3 我们的方案
- 强推理 + 强结构化：将饮食/运动/体重/睡眠/心理“五区段”建议结构化输出并可追踪执行；
- 工具编排：通过 MCP 工具链将建议转化为可执行动作（提醒、计算、图表、数据查询等）；
- 循证与可解释：RAG 文档检索与健康计算兜底，提供可验证的参考；
- 家庭协作与成就：用互动、排行榜与挑战提升留存与复访。

---

## 三、技术架构与开发方式

### 3.1 前端技术栈与合理性
- 技术选型：Vue 3 + Vite + Pinia + Ant Design Vue + ECharts + I18n（`frontend/package.json`）。
- 统一请求层：`frontend/src/utils/request.js` 使用 Axios，自动注入 `Authorization`，开发模式下自动注入测试 Token；聊天接口设置 60s 超时，兼容多种响应格式。
- 组件与场景：聊天组件、报告对话、图表（折线/雷达/热力）、加载与骨架屏、响应式与动画体系齐备；移动端与桌面端已验证。

参考：
- Axios 认证与超时（节选） `frontend/src/utils/request.js`
- 健康聊天 API（前端） `frontend/src/api/chat.js`
- 可视化组件 `frontend/src/components/charts/*`

### 3.2 后端架构与数据库
- 技术选型：FastAPI + Async SQLAlchemy（`requirements.txt`、`src/aurawell/database/*`）。
- 启动入口：`src/aurawell/main.py` 以 `uvicorn` 启动 `src.aurawell.interfaces.api_interface:app`。
- 数据库：默认 SQLite（开发），支持 PostgreSQL（生产），统一异步会话与连接池策略（`src/aurawell/database/connection.py`）。
- 认证与安全：JWT + 黑名单检查 + CORS + TrustedHost + 结构化异常处理；开发模式支持测试 Token 便于联调（`src/aurawell/core/auth_middleware.py`）。

### 3.3 关键功能模块
- 聊天与健康建议：`src/aurawell/services/chat_service.py` 与 `src/aurawell/langchain_agent/services/health_advice_service.py`；
  - 健康计算：BMI/BMR/TDEE/目标卡路里等（`src/aurawell/utils/health_calculations.py`）。
  - 五区段建议解析器：`langchain_agent/services/health_advice_service.py`（FiveSectionParser）。
- 家庭与互动：家庭模型、权限、邀请、互动统计与健康提醒（`src/aurawell/database/family_*` 与对应服务/仓库类）。
- 计划与报告：健康计划模板/进度/反馈；报告模块含 AI 总结与对话解释。
- 数据接入：苹果/小米/薄荷健康 API 客户端与扩展点（`src/aurawell/integrations/*`）。

### 3.4 AI 集成方案
- DeepSeek 客户端：OpenAI 兼容协议访问，支持工具调用与用量统计；优先 `deepseek-v3`/`deepseek-r1`（`src/aurawell/core/deepseek_client.py`）。
- LangChain：通过 `ChatOpenAI` 的 `openai_api_base` 指定兼容端点，模型名由环境变量注入（`src/aurawell/langchain_agent/agent.py`）。
- WebSocket：已纳入 `interfaces/websocket_interface.py` 路由，支持流式聊天能力（前后端留有扩展点）。
- 模型回退与可用性：AI 模型测试总结与回退服务在位（`docs/AI_MODELS_TEST_SUMMARY.md`、`src/aurawell/services/model_fallback_service.py`）。

### 3.5 开发流程与商业考量
- 环境与脚本：`.env` 模板、Nginx 配置、启动脚本（Windows/Mac）与部署文档完备；
- 面向可维护与成本控制：OpenAI 兼容协议便于多供应商切换；工具链可按需裁剪；前端组件与性能优化已到位；测试脚本覆盖登录/聊天/MCP/AI 模型可用性等关键链路。

---

## 四、功能特性分析

### 4.1 核心功能清单与业务价值
- AI 健康对话与结构化建议：围绕五大模块（饮食/运动/体重/睡眠/心理）提供个性化建议，支持上下文与结构化执行；
- 健康数据整合与可视化：多维图表（折线、雷达、热力、柱状）、趋势与异常；
- 健康计划（模板/进度/反馈）与 AI 报告（报告内嵌 AI 对话解释与追问）；
- 家庭成员/权限/邀请、互动点赞与健康提醒、成就与排行榜；
- 第三方平台接入扩展点，利于后续统一画像与干预。

### 4.2 用户体验亮点
- 统一的现代化视觉与交互（Gemini 风格、微交互、动效、移动端适配）；
- 聊天体验完善：Typing 指示、建议/快捷回复、错误兜底与超时设置；
- 性能与稳定性：前端性能监控、按需加载与优化；后端结构化日志与异常收敛。

### 4.3 数据安全与隐私
- JWT 鉴权与黑名单、CORS 与 TrustedHost、速率限制与异常处理；
- 环境变量集中化与安全配置（安全 Cookie/CSRF/Sentry/日志切分与备份/请求限流）。

---

## 五、市场定位

### 5.1 竞品差异化
- 相比“记录/可视化型”健康应用：AuraWell 更强推理与计划编排，能够输出可执行的结构化方案并跟踪进展；
- 相比“通用聊天大模型”：AuraWell 具备健康域知识、健康计算与家庭/计划/报告等业务模型，闭环更完整；
- 循证与可解释：RAG 检索与健康计算，提升建议可信与合规友好度。

### 5.2 商业模式与盈利点
- B2C 订阅：基础免费 + 高级（更强模型、家庭版、报告导出、跨平台数据同步）。
- B2B/B2B2C：保险/雇主健康福利/医疗机构随访；白标、SDK/API 接入与管理后台。
- 增值服务：家庭健康挑战、定制营养/运动方案、个性化报告、设备联动等。

### 5.3 路线图建议
- 3 个月：流式对话全面落地、模型回退策略完善、RAG 证据链可视化、平台 OAuth 接入、家庭互动玩法；
- 6 个月：Apple/Xiaomi/薄荷等深度整合、执行闭环（打卡/提醒/周报）、A/B 实验与指标库；
- 12 个月：企业/保险试点、合规与隐私体系地区化、匿名化群体洞察与个性化微调。

---

## 六、关键准确性与代码对应（已核验）

- 后端启动：`src/aurawell/main.py` 使用 `uvicorn` 运行 `src.aurawell.interfaces.api_interface:app`；
- 聊天端点（前端兼容）：`POST /api/v1/chat/message` 定义于 `src/aurawell/interfaces/api_interface.py`，与前端 `frontend/src/api/chat.js` 一致；
- Axios 拦截与超时：`frontend/src/utils/request.js` 已实现认证头注入与 60s 聊天超时；
- DeepSeek 客户端：`src/aurawell/core/deepseek_client.py` 以 OpenAI 兼容协议访问，支持工具调用；
- LangChain 接入：`src/aurawell/langchain_agent/agent.py` 通过 `openai_api_base` 指向兼容端点；
- 数据库：默认 SQLite，支持 PostgreSQL（`src/aurawell/database/connection.py`）。

> 以上所有点已对照源代码逐条核验，如后续代码变更，请同步维护本文档对应章节。

---

## 附录
- 依赖清单（节选）：`requirements.txt`（FastAPI、SQLAlchemy、openai、langchain、redis、alembic、dashvector、mcp 等）。
- 文档参考：`docs/AI_MODELS_TEST_SUMMARY.md`、`docs/README_AI_TESTS.md`、`docs/DEPLOYMENT_README.md`。
- 配置参考：`.env.example` 与 `README.md` 的环境变量示例与部署指引。
