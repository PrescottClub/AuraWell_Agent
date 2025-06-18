# AuraWell 感官系统自检报告 - 第三阶段
## 🎯 前端-后端通信链路诊断

### 📊 扫描统计
- **前端API调用**: 80 个
- **后端API端点**: 57 个
- **通信正常 (Green Zone)**: 47 个
- **通信异常 (Red Zone)**: 33 个
- **孤立端点**: 39 个

## ✅ Green Zone - 通信正常
前端调用与后端实现完全匹配的接口：

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/members** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/permissions** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/switch-member** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/leaderboard** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/members** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/permissions** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/switch-member** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/leaderboard** 🔍 模糊匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\api\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/auth/register** 🎯 精确匹配
  - 前端: frontend\src\api\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/auth/login** 🎯 精确匹配
  - 前端: frontend\src\api\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/profile** 🔍 模糊匹配
  - 前端: frontend\src\api\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/profile** 🔍 模糊匹配
  - 前端: frontend\src\api\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/chat** 🎯 精确匹配
  - 前端: frontend\src\stores\chat.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/chat/message** 🎯 精确匹配
  - 前端: frontend\src\stores\chat.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/chat/conversations** 🔍 模糊匹配
  - 前端: frontend\src\stores\chat.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/chat/history** 🔍 模糊匹配
  - 前端: frontend\src\stores\chat.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/chat/conversation/{id}** 🔍 模糊匹配
  - 前端: frontend\src\stores\chat.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}** 🔍 模糊匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/members** 🔍 模糊匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/permissions** 🔍 模糊匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/invite** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/switch-member** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/leaderboard** 🔍 模糊匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/{id}/challenges** 🎯 精确匹配
  - 前端: frontend\src\stores\family.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/profile** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/profile** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-data** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-data** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-goals** 🎯 精确匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-goals** 🎯 精确匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-goals/{id}** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/user/health-goals/{id}** 🔍 模糊匹配
  - 前端: frontend\src\stores\user.js
  - 后端: src\aurawell\interfaces\api_interface.py

## 🚨 Red Zone - 通信异常
前端试图调用但后端不存在的接口：

- **POST /api/v1/family/{id}/health-report** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: mockFamilyAPI
  - 方法: getFamilyHealthReport

- **POST /api/v1/family/members/{id}/like** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: mockFamilyAPI
  - 方法: likeMember

- **POST /api/v1/family/{id}/health-alerts** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: mockFamilyAPI
  - 方法: getHealthAlerts

- **POST /api/v1/family/{id}/health-report** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: Family
  - 方法: getFamilyHealthReport

- **POST /api/v1/family/members/{id}/like** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: Family
  - 方法: likeMember

- **POST /api/v1/family/{id}/health-alerts** ❌
  - 文件: frontend\src\api\family.js
  - 类型: mock_call
  - API类: Family
  - 方法: getHealthAlerts

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: createHealthPlan

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: getUserHealthPlans

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: getHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: updateHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: deleteHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: getHealthPlan

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: mockHealthPlanAPI
  - 方法: createHealthPlan

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: createHealthPlan

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: getUserHealthPlans

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: getHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: updateHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: deleteHealthPlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: getHealthPlan

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\api\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlan
  - 方法: createHealthPlan

- **POST /api/v1/auth/logout** ❌
  - 文件: frontend\src\api\user.js
  - 类型: mock_call
  - API类: authAPI
  - 方法: logout

- **POST /api/v1/family/{id}/health-report** ❌
  - 文件: frontend\src\stores\family.js
  - 类型: mock_call
  - API类: familyAPI
  - 方法: getFamilyHealthReport

- **POST /api/v1/family/{id}/health-alerts** ❌
  - 文件: frontend\src\stores\family.js
  - 类型: mock_call
  - API类: familyAPI
  - 方法: getHealthAlerts

- **POST /api/v1/health/plans** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: getPlans

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: getPlanDetail

- **POST /api/v1/health/plans/generate** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: generatePlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: updatePlan

- **POST /api/v1/health/plans/{id}** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: deletePlan

- **POST /api/v1/health/plans/{id}/export** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: exportPlan

- **POST /api/v1/health/plans/{id}/progress** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: getPlanProgress

- **POST /api/v1/health/plans/{id}/progress** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: updatePlanProgress

- **POST /api/v1/health/plans/templates** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: getPlanTemplates

- **POST /api/v1/health/plans/from-template** ❌
  - 文件: frontend\src\stores\healthPlan.js
  - 类型: mock_call
  - API类: HealthPlanAPI
  - 方法: createFromTemplate

## 🔍 孤立端点
后端存在但前端未调用的接口：

- **POST /api/v1/health/advice/comprehensive**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/health/advice/quick**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/family/{family_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/family**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/invitation/accept**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/family/invitation/decline**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/chat/conversations/{conversation_id}/messages**
  - 文件: src\aurawell\interfaces\api_interface.py

- **DELETE /api/v1/chat/conversation/{conversation_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/chat/suggestions**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/user/profile**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/user/profile/frontend**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/user/profile/frontend**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/summary**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/summary/frontend**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/health/goals**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/goals**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/goals/paginated**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/user/health-data**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/user/health-goals/{goal_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **DELETE /api/v1/user/health-goals/{goal_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health-plan/plans**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/health-plan/generate**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health-plan/plans/{plan_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/health-plan/plans/{plan_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **DELETE /api/v1/health-plan/plans/{plan_id}**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health-plan/plans/{plan_id}/export**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/health-plan/plans/{plan_id}/feedback**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health-plan/plans/{plan_id}/progress**
  - 文件: src\aurawell\interfaces\api_interface.py

- **PUT /api/v1/health-plan/plans/{plan_id}/progress**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health-plan/templates**
  - 文件: src\aurawell\interfaces\api_interface.py

- **POST /api/v1/health-plan/templates/{template_id}/create**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/achievements**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/activity**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health/sleep**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/family/{family_id}/report**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/family/{family_id}/challenges**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/health**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /api/v1/system/performance**
  - 文件: src\aurawell\interfaces\api_interface.py

- **GET /**
  - 文件: src\aurawell\interfaces\api_interface.py

## 🎯 核心功能可用性确认
- **健康聊天**: ✅ 可用
- **健康计划**: ❌ 不可用 (缺失: /api/v1/health/plans, /api/v1/health/advice)
- **家庭挑战**: ❌ 不可用 (缺失: /api/v1/family/{id}/challenges)
- **用户认证**: ✅ 可用
- **用户档案**: ✅ 可用

## 📋 诊断结论
⚠️ **发现 33 个通信异常**，需要修复Red Zone中的问题。
📊 **API覆盖率**: 58.8% (47/80)