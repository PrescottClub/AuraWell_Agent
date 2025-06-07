# AuraWell 健康助手 API 接口文档

## 📋 目录
- [项目概述](#项目概述)
- [快速开始](#快速开始)
- [认证与授权](#认证与授权)
- [核心API接口](#核心api接口)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [SDK使用示例](#sdk使用示例)
- [部署指南](#部署指南)

## 🎯 项目概述

AuraWell是一个超个性化健康生活方式编排AI Agent，集成了多个健康平台数据，提供AI驱动的健康分析和个性化建议。

### 核心功能
- 🤖 **AI健康分析**: 基于DeepSeek AI的智能健康数据分析
- 📊 **多平台集成**: 支持小米健康、薄荷健康、苹果健康等平台
- 🎯 **个性化计划**: 动态生成个性化健康计划和建议
- 🏆 **游戏化系统**: 成就系统和激励机制
- 💬 **对话式交互**: 自然语言健康咨询

### 技术栈
- **后端**: Python 3.8+, FastAPI, Pydantic
- **AI引擎**: DeepSeek API
- **前端**: Vue.js 3, Vite
- **数据处理**: Pandas, NumPy

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+ (前端开发)
- DeepSeek API Key

### 安装与配置

1. **克隆项目**
```bash
git clone https://github.com/PrescottClub/AuraWell_Agent.git
cd AuraWell_Agent
```

2. **安装后端依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp env.example .env
# 编辑.env文件，添加必要的API密钥
```

4. **启动开发服务器**
```bash
# 启动后端API服务 (计划中)
python -m aurawell.interfaces.api_interface

# 启动前端开发服务器
cd frontend
npm install
npm run dev
```

### 基础使用示例

```python
from aurawell.core.orchestrator_v2 import AuraWellOrchestrator
from aurawell.models.user_profile import UserProfile

# 初始化编排器
orchestrator = AuraWellOrchestrator()

# 创建用户档案
user_profile = {
    "user_id": "user_001",
    "age": 28,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "daily_steps_goal": 10000
}

# 分析健康数据
insights = orchestrator.analyze_user_health_data(user_profile)

# 创建健康计划
health_plan = orchestrator.create_personalized_health_plan(user_profile)
```

## 🔐 认证与授权

### API密钥配置

AuraWell使用多种API密钥进行第三方服务集成：

```bash
# 必需配置
DEEPSEEK_API_KEY=your_deepseek_api_key

# 健康平台配置 (可选)
XIAOMI_HEALTH_API_KEY=your_xiaomi_api_key
XIAOMI_HEALTH_CLIENT_ID=your_xiaomi_client_id
XIAOMI_HEALTH_CLIENT_SECRET=your_xiaomi_client_secret

BOHE_HEALTH_API_KEY=your_bohe_api_key
BOHE_HEALTH_CLIENT_ID=your_bohe_client_id

APPLE_HEALTH_CLIENT_ID=your_apple_health_client_id
APPLE_HEALTH_CLIENT_SECRET=your_apple_health_client_secret
```

### OAuth 2.0 流程

健康平台集成使用标准OAuth 2.0流程：

1. **授权请求**: 重定向用户到健康平台授权页面
2. **授权码获取**: 用户授权后获取授权码
3. **访问令牌交换**: 使用授权码换取访问令牌
4. **API调用**: 使用访问令牌调用健康平台API

## 📡 核心API接口

### 1. 健康数据分析

#### POST /api/v1/health/analyze
分析用户健康数据并生成洞察

**请求参数:**
```json
{
  "user_id": "string",
  "user_profile": {
    "age": 28,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "daily_steps_goal": 10000
  },
  "activity_data": [
    {
      "date": "2025-01-15",
      "steps": 8500,
      "distance_meters": 6800,
      "active_calories": 320,
      "active_minutes": 45
    }
  ],
  "sleep_data": [
    {
      "start_time_utc": "2025-01-14T23:30:00Z",
      "end_time_utc": "2025-01-15T07:00:00Z",
      "total_duration_seconds": 27000,
      "deep_sleep_seconds": 8100,
      "light_sleep_seconds": 16200,
      "rem_sleep_seconds": 2700
    }
  ],
  "nutrition_data": [
    {
      "timestamp_utc": "2025-01-15T12:00:00Z",
      "meal_type": "lunch",
      "food_name": "鸡胸肉沙拉",
      "calories": 450,
      "protein_grams": 35,
      "carbs_grams": 20,
      "fat_grams": 15
    }
  ]
}
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "insights": [
      {
        "insight_id": "activity_low_user_001_1705123456",
        "insight_type": "ACTIVITY_PATTERN",
        "priority": "MEDIUM",
        "title": "步数目标完成度较低",
        "description": "最近平均每日步数为 8500 步，仅达到目标的 85.0%",
        "recommendations": [
          "尝试在日常生活中增加更多步行机会",
          "设置每小时提醒，进行短暂的步行",
          "选择楼梯而不是电梯"
        ],
        "data_points": {
          "avg_steps": 8500,
          "goal_steps": 10000,
          "achievement_percentage": 85.0
        },
        "confidence_score": 0.9,
        "generated_at": "2025-01-15T10:30:00Z"
      }
    ],
    "summary": {
      "total_insights": 3,
      "high_priority_count": 0,
      "medium_priority_count": 2,
      "low_priority_count": 1
    }
  }
}
```

### 2. 个性化健康计划

#### POST /api/v1/health/plan
创建个性化健康计划

**请求参数:**
```json
{
  "user_id": "string",
  "user_profile": {
    "age": 28,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "daily_steps_goal": 10000,
    "sleep_duration_goal_hours": 8.0
  },
  "user_preferences": {
    "preferred_workout_time": "morning",
    "fitness_level": "intermediate",
    "health_goals": ["weight_loss", "better_sleep"],
    "dietary_restrictions": ["vegetarian"]
  },
  "recent_insights": [
    {
      "insight_type": "ACTIVITY_PATTERN",
      "priority": "MEDIUM",
      "title": "步数目标完成度较低"
    }
  ]
}
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "plan_id": "plan_user_001_1705123456",
    "user_id": "user_001",
    "title": "AI个性化健康计划",
    "description": "基于您的健康数据和目标制定的30天个性化计划",
    "goals": [
      {
        "type": "daily_steps",
        "target": 10000,
        "current_avg": 8500,
        "improvement_needed": "17.6%"
      },
      {
        "type": "sleep_hours",
        "target": 8.0,
        "current_avg": 7.2,
        "improvement_needed": "0.8 hours"
      }
    ],
    "daily_recommendations": [
      {
        "time": "morning",
        "title": "晨间运动",
        "activity": "快走或慢跑",
        "duration": 30,
        "calories_target": 200
      },
      {
        "time": "evening",
        "title": "放松活动",
        "activity": "瑜伽或冥想",
        "duration": 15,
        "benefits": ["改善睡眠质量", "减少压力"]
      }
    ],
    "weekly_targets": {
      "exercise_sessions": 3,
      "meditation_sessions": 5,
      "step_goal_achievement": "90%"
    },
    "created_at": "2025-01-15T10:30:00Z",
    "valid_until": "2025-02-14T10:30:00Z"
  }
}
```

### 3. 每日建议

#### GET /api/v1/health/recommendations/{user_id}
获取用户每日健康建议

**路径参数:**
- `user_id`: 用户ID

**查询参数:**
- `date`: 目标日期 (可选, 默认今天)
- `timezone`: 时区 (可选, 默认UTC)

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "user_id": "user_001",
    "date": "2025-01-15",
    "recommendations": [
      {
        "id": "rec_001",
        "type": "activity",
        "title": "增加步行活动",
        "description": "今天已完成6000步，距离目标还差4000步",
        "action": "尝试步行去附近的咖啡店",
        "estimated_time": 20,
        "priority": "medium"
      },
      {
        "id": "rec_002",
        "type": "nutrition",
        "title": "补充蛋白质",
        "description": "今日蛋白质摄入偏低",
        "action": "晚餐添加鸡胸肉或豆腐",
        "estimated_calories": 150,
        "priority": "low"
      }
    ],
    "daily_summary": {
      "steps_progress": "60%",
      "sleep_quality": "good",
      "nutrition_balance": "needs_improvement"
    }
  }
}
```

### 4. 健康平台数据同步

#### POST /api/v1/integrations/sync
同步健康平台数据

**请求参数:**
```json
{
  "user_id": "string",
  "platform": "xiaomi|apple|bohe",
  "data_types": ["activity", "sleep", "nutrition"],
  "date_range": {
    "start_date": "2025-01-08",
    "end_date": "2025-01-15"
  }
}
```

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "sync_id": "sync_001_1705123456",
    "user_id": "user_001",
    "platform": "xiaomi",
    "synced_data_types": ["activity", "sleep"],
    "records_synced": {
      "activity": 7,
      "sleep": 6,
      "nutrition": 0
    },
    "sync_status": "completed",
    "last_sync_time": "2025-01-15T10:30:00Z",
    "next_sync_time": "2025-01-16T10:30:00Z"
  }
}
```

### 5. 游戏化系统

#### GET /api/v1/gamification/achievements/{user_id}
获取用户成就

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "user_id": "user_001",
    "total_points": 1250,
    "level": 5,
    "achievements": [
      {
        "achievement_id": "step_master_7day",
        "title": "步行达人",
        "description": "连续7天完成步数目标",
        "icon": "🚶‍♂️",
        "points": 100,
        "unlocked_at": "2025-01-10T08:00:00Z",
        "category": "activity"
      },
      {
        "achievement_id": "early_bird",
        "title": "早起鸟",
        "description": "连续5天在7点前起床",
        "icon": "🌅",
        "points": 75,
        "unlocked_at": "2025-01-12T06:30:00Z",
        "category": "sleep"
      }
    ],
    "progress": [
      {
        "achievement_id": "nutrition_balance_30day",
        "title": "营养均衡大师",
        "description": "30天内保持营养均衡",
        "current_progress": 15,
        "target": 30,
        "progress_percentage": 50
      }
    ]
  }
}
```

### 6. 用户档案管理

#### GET /api/v1/users/{user_id}/profile
获取用户档案

**响应示例:**
```json
{
  "status": "success",
  "data": {
    "user_id": "user_001",
    "display_name": "张小明",
    "age": 28,
    "gender": "male",
    "height_cm": 175,
    "weight_kg": 75,
    "activity_level": "MODERATELY_ACTIVE",
    "daily_steps_goal": 10000,
    "sleep_duration_goal_hours": 8.0,
    "created_at": "2025-01-01T00:00:00Z",
    "last_updated": "2025-01-15T10:30:00Z",
    "health_summary": {
      "avg_daily_steps": 8500,
      "avg_sleep_hours": 7.2,
      "avg_daily_calories": 2100,
      "bmi": 24.5,
      "bmi_category": "normal"
    }
  }
}
```

#### PUT /api/v1/users/{user_id}/profile
更新用户档案

**请求参数:**
```json
{
  "display_name": "张小明",
  "age": 29,
  "weight_kg": 73,
  "daily_steps_goal": 12000,
  "sleep_duration_goal_hours": 8.5
}
```

## 📊 数据模型

### 核心数据结构

#### UserProfile (用户档案)
```python
{
  "user_id": "string",
  "display_name": "string",
  "age": "integer",
  "gender": "male|female|other",
  "height_cm": "float",
  "weight_kg": "float",
  "activity_level": "SEDENTARY|LIGHTLY_ACTIVE|MODERATELY_ACTIVE|VERY_ACTIVE|EXTREMELY_ACTIVE",
  "daily_steps_goal": "integer",
  "sleep_duration_goal_hours": "float",
  "created_at": "datetime",
  "last_updated": "datetime"
}
```

#### UnifiedActivitySummary (活动数据)
```python
{
  "date": "YYYY-MM-DD",
  "steps": "integer",
  "distance_meters": "float",
  "active_calories": "float",
  "total_calories": "float",
  "active_minutes": "integer",
  "source_platform": "XIAOMI|APPLE|BOHE|MANUAL",
  "data_quality": "HIGH|MEDIUM|LOW|UNKNOWN",
  "recorded_at": "datetime"
}
```

#### UnifiedSleepSession (睡眠数据)
```python
{
  "start_time_utc": "datetime",
  "end_time_utc": "datetime",
  "total_duration_seconds": "integer",
  "deep_sleep_seconds": "integer",
  "light_sleep_seconds": "integer",
  "rem_sleep_seconds": "integer",
  "awake_seconds": "integer",
  "sleep_efficiency": "float",
  "source_platform": "XIAOMI|APPLE|BOHE|MANUAL",
  "data_quality": "HIGH|MEDIUM|LOW|UNKNOWN",
  "recorded_at": "datetime"
}
```

#### NutritionEntry (营养数据)
```python
{
  "timestamp_utc": "datetime",
  "meal_type": "breakfast|lunch|dinner|snack",
  "food_name": "string",
  "calories": "float",
  "protein_grams": "float",
  "carbs_grams": "float",
  "fat_grams": "float",
  "fiber_grams": "float",
  "serving_size": "string",
  "source_platform": "XIAOMI|APPLE|BOHE|MANUAL",
  "data_quality": "HIGH|MEDIUM|LOW|UNKNOWN",
  "recorded_at": "datetime"
}
```
