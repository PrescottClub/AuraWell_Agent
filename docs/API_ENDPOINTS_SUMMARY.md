# AuraWell API Endpoints Summary

## Quick Reference

This document provides a quick reference for all available API endpoints in AuraWell Health Assistant API v1.0.0.

## Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login` | User login | ❌ |
| POST | `/api/v1/auth/register` | User registration | ❌ |

## Chat & Conversation Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/chat` | Process chat message | ✅ |
| POST | `/api/v1/chat/conversation` | Create conversation | ✅ |
| GET | `/api/v1/chat/conversations` | List conversations | ✅ |
| POST | `/api/v1/chat/message` | Send health chat message | ✅ |
| GET | `/api/v1/chat/history` | Get chat history | ✅ |
| DELETE | `/api/v1/chat/conversation/{id}` | Delete conversation | ✅ |
| GET | `/api/v1/chat/suggestions` | Get health suggestions | ✅ |

## User Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/user/profile` | Get user profile | ✅ |
| PUT | `/api/v1/user/profile` | Update user profile | ✅ |
| GET | `/api/v1/user/health-data` | Get health data | ✅ |
| PUT | `/api/v1/user/health-data` | Update health data | ✅ |
| GET | `/api/v1/user/health-goals` | Get health goals | ✅ |
| POST | `/api/v1/user/health-goals` | Create health goal | ✅ |

## Health Data Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/health/summary` | Get health summary | ✅ |
| GET | `/api/v1/health/activity` | Get activity data | ✅ |
| GET | `/api/v1/health/sleep` | Get sleep data | ✅ |
| POST | `/api/v1/health/goals` | Create health goal | ✅ |
| GET | `/api/v1/health/goals` | List health goals | ✅ |
| GET | `/api/v1/health/goals/paginated` | Get paginated goals | ✅ |

## Health Plans Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/health-plan/plans` | List health plans | ✅ |
| POST | `/api/v1/health-plan/generate` | Generate health plan | ✅ |
| GET | `/api/v1/health-plan/plans/{id}` | Get plan details | ✅ |
| PUT | `/api/v1/health-plan/plans/{id}` | Update health plan | ✅ |
| DELETE | `/api/v1/health-plan/plans/{id}` | Delete health plan | ✅ |
| GET | `/api/v1/health-plan/plans/{id}/export` | Export health plan | ✅ |
| POST | `/api/v1/health-plan/plans/{id}/feedback` | Save plan feedback | ✅ |
| GET | `/api/v1/health-plan/plans/{id}/progress` | Get plan progress | ✅ |
| PUT | `/api/v1/health-plan/plans/{id}/progress` | Update plan progress | ✅ |
| GET | `/api/v1/health-plan/templates` | Get plan templates | ✅ |
| POST | `/api/v1/health-plan/templates/{id}/create` | Create from template | ✅ |

## Health Advice Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/health/advice/comprehensive` | Generate comprehensive advice | ✅ |
| POST | `/api/v1/health/advice/quick` | Generate quick advice | ✅ |

## Family Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/family` | Create family | ✅ |
| GET | `/api/v1/family/{id}` | Get family info | ✅ |
| GET | `/api/v1/family` | List user families | ✅ |
| POST | `/api/v1/family/{id}/invite` | Invite family member | ✅ |
| POST | `/api/v1/family/invitation/accept` | Accept invitation | ✅ |
| POST | `/api/v1/family/invitation/decline` | Decline invitation | ✅ |
| GET | `/api/v1/family/{id}/members` | Get family members | ✅ |
| GET | `/api/v1/family/{id}/permissions` | Get family permissions | ✅ |
| POST | `/api/v1/family/switch-member` | Switch active member | ✅ |

## Family Dashboard Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/family/{id}/report` | Generate family report | ✅ |
| GET | `/api/v1/family/{id}/leaderboard` | Get family leaderboard | ✅ |
| GET | `/api/v1/family/{id}/challenges` | Get family challenges | ✅ |
| POST | `/api/v1/family/{id}/challenges` | Create family challenge | ✅ |

## Achievements Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/achievements` | Get user achievements | ✅ |

## System Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/health` | System health check | ❌ |
| GET | `/api/v1/system/performance` | Get performance metrics | ❌ |
| GET | `/` | Root endpoint | ❌ |

## Response Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Common Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Items per page (1-100) | 20 |
| `offset` | integer | Items to skip (≥0) | 0 |
| `page` | integer | Page number (≥1) | 1 |
| `page_size` | integer | Page size (1-100) | 20 |
| `sort_by` | string | Field to sort by | varies |
| `sort_order` | string | Sort order (asc/desc) | desc |
| `start_date` | string | Start date (ISO format) | - |
| `end_date` | string | End date (ISO format) | - |

## Authentication Header

```
Authorization: Bearer <jwt_token>
```

## Content Type

```
Content-Type: application/json
```

## Rate Limiting Headers

- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

## Performance Headers

- `X-Process-Time`: Request processing time
- `X-Request-ID`: Unique request identifier

## WebSocket Endpoint

```
ws://127.0.0.1:8000/ws
```

## Documentation Links

- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Detailed API Documentation**: [API_EN.md](./API_EN.md)
- **Chinese Documentation**: [API.md](./API.md)
