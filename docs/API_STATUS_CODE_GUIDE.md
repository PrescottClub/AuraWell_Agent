# AuraWell API状态码标准化指南

## 🎯 概述
本指南定义了AuraWell API中HTTP状态码的标准化使用规范，确保前后端开发的一致性。

## 📋 状态码标准

### 🔐 认证与授权 (Authentication & Authorization)

#### 401 UNAUTHORIZED - 身份验证失败
**使用场景：**
- JWT token无效或过期
- 认证头缺失或格式错误  
- 登录凭据错误

**实现方式：**
```python
from fastapi import status
from ..middleware.error_handler import AuthenticationException

# 推荐方式
raise AuthenticationException("Invalid token")

# 或者使用FastAPI状态码常量
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail="Authentication failed"
)
```

#### 403 FORBIDDEN - 权限不足
**使用场景：**
- 用户已认证但无权访问资源
- 家庭成员权限不足
- API访问权限限制

**实现方式：**
```python
from ..middleware.error_handler import AuthorizationException

raise AuthorizationException("Insufficient permissions")
```

### 📝 客户端错误 (Client Errors)

#### 400 BAD REQUEST - 请求格式错误
**使用场景：**
- 请求参数格式错误
- 必需参数缺失
- 业务逻辑约束违反

#### 404 NOT FOUND - 资源不存在  
**使用场景：**
- 请求的资源不存在
- 用户ID不存在
- 健康计划不存在

**实现方式：**
```python
from ..middleware.error_handler import NotFoundException

raise NotFoundException("Health plan not found", "health_plan", plan_id)
```

#### 422 UNPROCESSABLE ENTITY - 输入验证失败
**使用场景：**
- Pydantic模型验证失败
- 数据类型错误
- 字段约束违反

**实现方式：**
```python
from ..middleware.error_handler import ValidationException

raise ValidationException("Invalid email format", field="email")
```

### 🖥️ 服务器错误 (Server Errors)

#### 500 INTERNAL SERVER ERROR - 服务器内部错误
**使用场景：**
- 未捕获的程序异常
- 数据库连接失败
- 系统配置错误

#### 502 BAD GATEWAY - 外部服务错误
**使用场景：**
- DeepSeek API调用失败
- 健康数据API连接失败
- 第三方服务不可用

**实现方式：**
```python
from ..middleware.error_handler import ExternalServiceException

raise ExternalServiceException("DeepSeek API unavailable", "deepseek")
```

## 🚀 最佳实践

### 1. 使用标准化异常类
❌ **不推荐：**
```python
raise HTTPException(status_code=401, detail="Token invalid")
```

✅ **推荐：**
```python
raise AuthenticationException("Token invalid")
```

### 2. 状态码常量
❌ **不推荐：**
```python
raise HTTPException(status_code=404, detail="Not found")
```

✅ **推荐：**
```python
from fastapi import status
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
```

### 3. 一致的错误响应格式
所有API错误都应返回标准化的错误响应格式：
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "details": {},
  "timestamp": "2024-12-28T10:00:00Z"
}
```

## 🔧 实施检查清单

- [ ] 所有认证失败使用401
- [ ] 所有权限不足使用403  
- [ ] 所有资源不存在使用404
- [ ] 所有验证失败使用422
- [ ] 所有外部服务错误使用502
- [ ] 使用FastAPI status常量
- [ ] 优先使用AuraWell异常类
- [ ] 错误响应格式统一

## 📊 状态码映射表

| HTTP状态码 | 使用场景 | AuraWell异常类 | ErrorCode |
|-----------|----------|---------------|-----------|
| 400 | 请求错误 | AuraWellException | INVALID_INPUT |
| 401 | 认证失败 | AuthenticationException | UNAUTHORIZED |
| 403 | 权限不足 | AuthorizationException | FORBIDDEN |
| 404 | 资源不存在 | NotFoundException | USER_NOT_FOUND |
| 422 | 验证失败 | ValidationException | INVALID_INPUT |
| 429 | 请求过频 | - | RATE_LIMIT_EXCEEDED |
| 500 | 服务器错误 | - | INTERNAL_SERVER_ERROR |
| 502 | 外部服务错误 | ExternalServiceException | EXTERNAL_API_ERROR |
| 503 | 服务不可用 | - | SERVICE_UNAVAILABLE |

---
**更新时间：** 2024-12-28  
**版本：** 1.0  
**Phase：** 2 BONUS Task
