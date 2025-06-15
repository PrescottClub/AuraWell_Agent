# AuraWell 工具链接口契约 v2.0

## 概述
定义三大核心工具的标准化接口，确保AI Agent能够可靠地调用和处理返回数据。

## 工具1：UserProfileLookup

### 接口定义
```python
async def user_profile_lookup(user_id: str) -> UserProfileResponse
```

### 输入参数
| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| user_id | str | ✅ | 用户唯一标识符 |

### 返回字段
```json
{
  "status": "success|error",
  "data": {
    "user_id": "string",
    "age": "integer",
    "gender": "male|female|other", 
    "height_cm": "float",
    "weight_kg": "float",
    "activity_level": "sedentary|light|moderate|active|very_active",
    "health_goals": ["weight_loss", "muscle_gain", "general_fitness"],
    "medical_conditions": ["diabetes", "hypertension"],
    "dietary_restrictions": ["vegetarian", "gluten_free"],
    "last_updated": "ISO8601_timestamp"
  },
  "error_code": "USER_NOT_FOUND|DATABASE_ERROR|null",
  "message": "string"
}
```

### 错误码
- `USER_NOT_FOUND`: 用户不存在
- `DATABASE_ERROR`: 数据库连接失败
- `PERMISSION_DENIED`: 权限不足

## 工具2：CalcMetrics

### 接口定义
```python
def calc_metrics(height_cm: float, weight_kg: float, age: int, gender: str, activity_level: str) -> MetricsResponse
```

### 输入参数
| 参数名 | 类型 | 必需 | 描述 | 取值范围 |
|--------|------|------|------|----------|
| height_cm | float | ✅ | 身高(厘米) | 100-250 |
| weight_kg | float | ✅ | 体重(公斤) | 30-300 |
| age | int | ✅ | 年龄(岁) | 1-120 |
| gender | str | ✅ | 性别 | "male", "female" |
| activity_level | str | ✅ | 活动水平 | 见UserProfile定义 |

### 返回字段
```json
{
  "status": "success|error",
  "data": {
    "bmi": "float",
    "bmi_category": "underweight|normal|overweight|obese",
    "bmr": "float",
    "tdee": "float", 
    "ideal_weight_range": [55.0, 65.0],
    "body_fat_estimate": "float|null",
    "muscle_mass_estimate": "float|null",
    "calorie_goal": {
      "maintain": "float",
      "lose_weight": "float", 
      "gain_weight": "float"
    }
  },
  "error_code": "INVALID_INPUT|CALCULATION_ERROR|null",
  "message": "string"
}
```

### 错误码
- `INVALID_INPUT`: 输入参数超出合理范围
- `CALCULATION_ERROR`: 计算过程出错

## 工具3：SearchKnowledge

### 接口定义
```python
async def search_knowledge(query: str, domain: str = "general", max_results: int = 5) -> KnowledgeResponse
```

### 输入参数
| 参数名 | 类型 | 必需 | 描述 | 取值范围 |
|--------|------|------|------|----------|
| query | str | ✅ | 搜索查询词 | 1-200字符 |
| domain | str | ❌ | 知识领域 | "nutrition", "exercise", "sleep", "mental", "general" |
| max_results | int | ❌ | 最大结果数 | 1-20，默认5 |

### 返回字段
```json
{
  "status": "success|error", 
  "data": {
    "query": "string",
    "domain": "string",
    "results": [
      {
        "title": "string",
        "content": "string",
        "source": "string",
        "confidence_score": "float",
        "last_updated": "ISO8601_timestamp",
        "tags": ["tag1", "tag2"]
      }
    ],
    "total_count": "integer",
    "search_time_ms": "integer"
  },
  "error_code": "QUERY_TOO_SHORT|DOMAIN_INVALID|SERVICE_UNAVAILABLE|null",
  "message": "string"
}
```

### 错误码
- `QUERY_TOO_SHORT`: 查询词少于1个字符
- `DOMAIN_INVALID`: 知识领域不存在
- `SERVICE_UNAVAILABLE`: 搜索服务不可用

## 统一错误处理

### 超时设置
- UserProfileLookup: 5秒
- CalcMetrics: 2秒（本地计算）
- SearchKnowledge: 10秒

### 重试策略
- 网络错误：最多重试3次，指数退避
- 服务错误：不重试，直接返回错误
- 超时错误：重试1次

### 日志要求
所有工具调用必须记录：
- 调用时间和用时
- 输入参数（脱敏处理）
- 返回状态和错误码
- 用户ID（用于问题追踪） 