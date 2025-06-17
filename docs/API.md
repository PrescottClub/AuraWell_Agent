# AuraWell API 文档

## 📋 概述

AuraWell API v1.0.0 提供完整的健康管理功能，包括用户认证、健康数据管理、AI健康咨询、健康计划生成、家庭健康管理等核心服务。

**Base URL**: `http://127.0.0.1:8000/api/v1`

## 📚 交互式文档

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json
- **English Documentation**: [API_EN.md](./API_EN.md)

## 🆕 最新更新 (v1.0.0)

- ✅ 新增家庭健康管理功能
- ✅ 增强的AI健康建议系统
- ✅ 健康计划生成和管理
- ✅ 成就系统和游戏化功能
- ✅ WebSocket实时通信支持
- ✅ 性能监控和缓存优化
- ✅ 速率限制和安全增强

## 🔐 认证

所有需要认证的API都使用JWT Bearer Token认证。

### 获取Token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "test_user",
  "password": "test_password"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 使用Token

在请求头中添加Authorization字段：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 👤 用户管理

### 用户注册

```http
POST /auth/register
Content-Type: application/json

{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "health_data": {
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "activity_level": "moderately_active"
  }
}
```

### 获取用户档案

```http
GET /user/profile
Authorization: Bearer <token>
```

### 更新用户档案

```http
PUT /user/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "display_name": "用户昵称",
  "age": 26,
  "height_cm": 175.0,
  "weight_kg": 72.0
}
```

## 🏥 健康数据管理

### 获取健康数据

```http
GET /user/health-data
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "message": "Health data retrieved successfully",
  "user_id": "user_123",
  "age": 25,
  "gender": "male",
  "height": 175.0,
  "weight": 70.0,
  "activity_level": "moderately_active",
  "bmi": 22.9,
  "bmi_category": "正常"
}
```

### 更新健康数据

```http
PUT /user/health-data
Authorization: Bearer <token>
Content-Type: application/json

{
  "age": 26,
  "height": 175.0,
  "weight": 72.0,
  "activity_level": "very_active"
}
```

## 🎯 健康目标管理

### 获取健康目标

```http
GET /user/health-goals
Authorization: Bearer <token>
```

### 创建健康目标

```http
POST /user/health-goals
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "减重目标",
  "description": "在3个月内减重5公斤",
  "type": "weight_loss",
  "target_value": 5.0,
  "current_value": 0.0,
  "unit": "kg",
  "target_date": "2024-12-31",
  "status": "active"
}
```

## 📋 健康计划管理

### 获取健康计划列表

```http
GET /health-plan/plans
Authorization: Bearer <token>
```

### 生成个性化健康计划

```http
POST /health-plan/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "goals": ["减重", "增强体质"],
  "modules": ["diet", "exercise", "weight"],
  "duration_days": 30,
  "user_preferences": {
    "dietary_restrictions": ["无"],
    "exercise_preference": "中等强度"
  }
}
```

**响应**:
```json
{
  "success": true,
  "message": "Health plan generated successfully",
  "plan": {
    "plan_id": "plan_user_123_001",
    "title": "30天个性化健康计划",
    "description": "基于您的目标：减重, 增强体质",
    "modules": [
      {
        "module_type": "diet",
        "title": "个性化饮食计划",
        "description": "根据您的目标和偏好定制的营养计划",
        "content": {
          "daily_calories": 2000,
          "goals": ["减重", "增强体质"],
          "recommendations": ["多吃蔬菜水果", "控制碳水化合物摄入"]
        },
        "duration_days": 30
      }
    ],
    "duration_days": 30,
    "status": "active",
    "progress": 0.0
  },
  "recommendations": [
    "建议每天记录您的进展",
    "保持计划的一致性很重要"
  ]
}
```

### 获取特定健康计划

```http
GET /health-plan/plans/{plan_id}
Authorization: Bearer <token>
```

## 🤖 AI健康咨询

### 发送消息

```http
POST /chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "我想了解如何制定健康的饮食计划"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "reply": "我是您的健康助手！关于制定健康饮食计划，我建议您...",
  "conversation_id": "conv_123",
  "timestamp": "2024-06-12T16:51:11.052086"
}
```

### 获取对话历史

```http
GET /chat/conversations
Authorization: Bearer <token>
```

## 📊 健康数据查询

### 健康数据汇总

```http
GET /health/summary
Authorization: Bearer <token>
```

### 活动数据

```http
GET /health/activity
Authorization: Bearer <token>
```

### 睡眠数据

```http
GET /health/sleep
Authorization: Bearer <token>
```

## 🏆 成就系统

### 获取用户成就

```http
GET /achievements
Authorization: Bearer <token>
```

## 🔍 系统监控

### 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-06-12T16:51:11.052086",
  "version": "1.0.0"
}
```

## 📝 错误处理

所有API错误都遵循统一的错误格式：

```json
{
  "success": false,
  "status": "error",
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  },
  "timestamp": "2024-06-12T16:51:11.052086",
  "request_id": "req_123"
}
```

### 常见错误码

- `401` - 未授权，需要登录
- `403` - 禁止访问，权限不足
- `404` - 资源不存在
- `422` - 数据验证失败
- `500` - 服务器内部错误

## 🧪 测试

使用提供的测试脚本验证API功能：

```bash
python test_api_endpoints.py
```

## 📚 更多信息

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub**: https://github.com/PrescottClub/AuraWell_Agent
