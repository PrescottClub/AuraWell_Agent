# AuraWell Health Assistant API Documentation

## Overview

AuraWell Health Assistant API v1.0.0 is a comprehensive RESTful API for personalized health lifestyle orchestration. The API provides endpoints for user authentication, health data management, AI-powered chat consultations, family health management, and gamified health tracking.

## Base URL

```
http://127.0.0.1:8000
```

## Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Obtain a token by calling the `/api/v1/auth/login` endpoint.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": boolean,
  "status": "success|error|warning",
  "message": "string",
  "data": object,
  "timestamp": "ISO8601",
  "request_id": "uuid"
}
```

## Error Handling

Error responses include additional fields:

```json
{
  "success": false,
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {},
  "timestamp": "ISO8601",
  "request_id": "uuid"
}
```

## API Endpoints

### 🔐 Authentication

#### POST /api/v1/auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "password": "string (6-128 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

**Error Codes:**
- `INVALID_CREDENTIALS`: Invalid username or password
- `INTERNAL_SERVER_ERROR`: Authentication service error

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-50 chars, alphanumeric + underscore)",
  "email": "string (valid email format)",
  "password": "string (6-128 chars)",
  "health_data": {} // optional initial health data
}
```

**Response:**
```json
{
  "success": true,
  "status": "success",
  "message": "User registered successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

**Validation Rules:**
- Username: lowercase, alphanumeric + underscore only
- Email: valid email format, normalized to lowercase
- Password: no leading/trailing whitespace

### 💬 Chat & Conversations

#### POST /api/v1/chat
Process chat message and return AI response using agent router.

**Request Body:**
```json
{
  "message": "string (1-1000 chars)",
  "conversation_id": "string (optional)",
  "context": {} // optional context data
}
```

**Response:**
```json
{
  "success": true,
  "status": "success",
  "message": "Chat response generated",
  "reply": "AI response text",
  "user_id": "string",
  "conversation_id": "string",
  "tools_used": ["tool1", "tool2"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### POST /api/v1/chat/conversation
Create a new conversation.

**Request Body:**
```json
{
  "type": "string (default: health_consultation)",
  "metadata": {} // optional metadata
}
```

**Response:**
```json
{
  "conversation_id": "string",
  "type": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "title": "string",
  "status": "active"
}
```

#### GET /api/v1/chat/conversations
Get list of user conversations.

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "id": "string",
      "title": "string",
      "last_message": "string",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "message_count": 0,
      "status": "active"
    }
  ]
}
```

#### POST /api/v1/chat/message
Send enhanced health chat message with AI suggestions.

**Request Body:**
```json
{
  "message": "string (1-2000 chars)",
  "conversation_id": "string (optional)",
  "context": {} // optional context
}
```

**Response:**
```json
{
  "success": true,
  "reply": "AI response",
  "conversation_id": "string",
  "message_id": "string",
  "timestamp": "2024-01-01T00:00:00Z",
  "suggestions": [
    {
      "title": "string",
      "content": "string",
      "action": "string",
      "action_text": "string"
    }
  ],
  "quick_replies": [
    {"text": "string"}
  ]
}
```

#### GET /api/v1/chat/history
Get chat history for a conversation.

**Query Parameters:**
- `conversation_id`: string (required)
- `limit`: integer (1-100, default: 50)
- `offset`: integer (≥0, default: 0)

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": "string",
      "sender": "user|agent",
      "content": "string",
      "timestamp": "2024-01-01T00:00:00Z",
      "suggestions": [],
      "quick_replies": []
    }
  ],
  "total": 0,
  "has_more": false
}
```

#### DELETE /api/v1/chat/conversation/{conversation_id}
Delete a conversation.

**Response:**
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

#### GET /api/v1/chat/suggestions
Get health suggestion templates for quick access.

**Response:**
```json
{
  "success": true,
  "suggestions": [
    "How can I improve my sleep quality?",
    "What's a good workout routine for beginners?",
    "How many calories should I eat per day?"
  ]
}
```

### 👤 User Profile

#### GET /api/v1/user/profile
Get user profile information.

**Response:**
```json
{
  "success": true,
  "user_id": "string",
  "display_name": "string",
  "email": "string",
  "age": 25,
  "gender": "male|female|other",
  "height_cm": 175.0,
  "weight_kg": 70.0,
  "activity_level": "sedentary|lightly_active|moderately_active|very_active|extremely_active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/v1/user/profile
Update user profile information.

**Request Body:**
```json
{
  "display_name": "string (1-100 chars, optional)",
  "email": "string (valid email, optional)",
  "age": "integer (13-120, optional)",
  "gender": "male|female|other (optional)",
  "height_cm": "float (50-300, optional)",
  "weight_kg": "float (20-500, optional)",
  "activity_level": "sedentary|lightly_active|moderately_active|very_active|extremely_active (optional)"
}
```

**Validation Rules:**
- Display name: no HTML/script characters
- Email: normalized to lowercase
- BMI validation: height + weight combination must result in realistic BMI (10-60)
- Age: minimum 13 years old

### 🏥 Health Data

#### GET /api/v1/health/summary
Get health summary for specified period.

**Query Parameters:**
- `days`: integer (default: 7) - Number of days to include in summary

**Response:**
```json
{
  "success": true,
  "period_days": 7,
  "activity_summary": {
    "total_steps": 50000,
    "avg_daily_steps": 7142,
    "total_calories": 2100,
    "avg_daily_calories": 300,
    "active_days": 5
  },
  "sleep_summary": {
    "total_hours": 49.5,
    "avg_daily_hours": 7.07,
    "quality_score": 85,
    "nights_tracked": 7
  },
  "achievements": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "points": 100,
      "completed": true,
      "completed_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/v1/health/activity
Get activity data.

**Query Parameters:**
- `start_date`: string (ISO date, optional)
- `end_date`: string (ISO date, optional)
- `limit`: integer (1-100, default: 30)

**Response:**
```json
{
  "success": true,
  "activities": [
    {
      "date": "2024-01-01",
      "steps": 8000,
      "calories_burned": 350,
      "distance_km": 6.4,
      "active_minutes": 45
    }
  ],
  "total_records": 30
}
```

#### GET /api/v1/health/sleep
Get sleep data.

**Query Parameters:**
- `start_date`: string (ISO date, optional)
- `end_date`: string (ISO date, optional)
- `limit`: integer (1-100, default: 30)

**Response:**
```json
{
  "success": true,
  "sleep_sessions": [
    {
      "date": "2024-01-01",
      "bedtime": "23:00:00",
      "wake_time": "07:00:00",
      "duration_hours": 8.0,
      "quality_score": 85,
      "deep_sleep_hours": 2.5,
      "rem_sleep_hours": 1.5
    }
  ],
  "total_records": 30
}
```

### 🎯 Health Goals

#### POST /api/v1/health/goals
Create a new health goal.

**Request Body:**
```json
{
  "goal_type": "weight_loss|weight_gain|fitness|nutrition|sleep|steps",
  "target_value": "float (>0)",
  "target_unit": "string (1-20 chars)",
  "target_date": "date (optional, ISO format)",
  "description": "string (max 500 chars, optional)"
}
```

**Response:**
```json
{
  "success": true,
  "goal_id": "string",
  "goal_type": "string",
  "target_value": 10000.0,
  "target_unit": "steps",
  "current_value": 0.0,
  "progress_percentage": 0.0,
  "target_date": "2024-12-31",
  "description": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Validation Rules:**
- Goal type: must be one of the predefined types
- Target value: must be positive, with reasonable limits per goal type
- Target date: cannot be in the past, max 2 years in future
- Steps goal: max 100,000 per day
- Sleep goal: max 12 hours
- Weight change: max 100 kg

#### GET /api/v1/health/goals
Get list of health goals.

**Query Parameters:**
- `goal_type`: string (optional filter)
- `status`: string (optional filter: active, completed, paused)
- `limit`: integer (1-100, default: 20)
- `offset`: integer (≥0, default: 0)

**Response:**
```json
{
  "success": true,
  "goals": [
    {
      "goal_id": "string",
      "goal_type": "steps",
      "target_value": 10000.0,
      "target_unit": "steps",
      "current_value": 7500.0,
      "progress_percentage": 75.0,
      "target_date": "2024-12-31",
      "description": "Daily steps goal",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 5,
  "has_more": false
}
```

### 🏃‍♂️ Health Plans

#### GET /api/v1/health-plan/plans
Get list of user's health plans.

**Query Parameters:**
- `status`: string (optional: active, completed, paused)
- `plan_type`: string (optional filter)
- `limit`: integer (1-100, default: 20)
- `offset`: integer (≥0, default: 0)

**Response:**
```json
{
  "success": true,
  "plans": [
    {
      "plan_id": "string",
      "title": "Comprehensive Health Plan",
      "description": "A complete health improvement plan",
      "plan_type": "comprehensive",
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "modules": [
        {
          "module_type": "diet",
          "title": "Nutrition Plan",
          "content": "Detailed nutrition recommendations",
          "status": "active"
        }
      ]
    }
  ],
  "total": 3,
  "has_more": false
}
```

#### POST /api/v1/health-plan/generate
Generate a new health plan using AI.

**Request Body:**
```json
{
  "plan_type": "comprehensive|diet|exercise|sleep|mental_health",
  "user_goals": ["weight_loss", "fitness_improvement"],
  "preferences": {
    "dietary_restrictions": ["vegetarian"],
    "exercise_preferences": ["cardio", "strength"],
    "time_availability": "30_minutes_daily"
  },
  "health_conditions": ["none"],
  "duration_weeks": 12
}
```

**Response:**
```json
{
  "success": true,
  "plan_id": "string",
  "title": "Generated Health Plan",
  "description": "AI-generated personalized health plan",
  "plan_type": "comprehensive",
  "status": "active",
  "duration_weeks": 12,
  "modules": [
    {
      "module_type": "diet",
      "title": "Nutrition Module",
      "content": "Detailed nutrition plan...",
      "recommendations": ["Eat 5 servings of vegetables daily"],
      "status": "active"
    },
    {
      "module_type": "exercise",
      "title": "Exercise Module",
      "content": "Workout routine...",
      "recommendations": ["30 minutes cardio 3x per week"],
      "status": "active"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/health-plan/plans/{plan_id}
Get specific health plan details.

#### PUT /api/v1/health-plan/plans/{plan_id}
Update health plan.

#### DELETE /api/v1/health-plan/plans/{plan_id}
Delete a health plan.

#### GET /api/v1/health-plan/plans/{plan_id}/export
Export health plan to PDF or other formats.

#### POST /api/v1/health-plan/plans/{plan_id}/feedback
Save user feedback for a health plan.

#### GET /api/v1/health-plan/plans/{plan_id}/progress
Get health plan progress details.

#### PUT /api/v1/health-plan/plans/{plan_id}/progress
Update health plan progress.

### 🤖 Health Advice

#### POST /api/v1/health/advice/comprehensive
Generate comprehensive health advice covering all five modules.

**Request Body:**
```json
{
  "user_goals": ["weight_loss", "fitness_improvement"],
  "health_data": {
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "activity_level": "moderately_active"
  },
  "preferences": {
    "dietary_restrictions": ["vegetarian"],
    "exercise_preferences": ["cardio"],
    "time_availability": "30_minutes_daily"
  },
  "health_conditions": ["none"]
}
```

**Response:**
```json
{
  "success": true,
  "advice_id": "string",
  "modules": {
    "diet": {
      "title": "Nutrition Recommendations",
      "content": "Detailed dietary advice...",
      "recommendations": ["Eat 5 servings of vegetables daily"],
      "meal_suggestions": ["Breakfast: Oatmeal with berries"]
    },
    "exercise": {
      "title": "Exercise Plan",
      "content": "Workout routine...",
      "recommendations": ["30 minutes cardio 3x per week"],
      "workout_suggestions": ["Monday: 30min jog"]
    },
    "weight": {
      "title": "Weight Management",
      "content": "Weight management strategy...",
      "recommendations": ["Track daily weight"],
      "target_weight": 65
    },
    "sleep": {
      "title": "Sleep Optimization",
      "content": "Sleep improvement tips...",
      "recommendations": ["Maintain consistent sleep schedule"],
      "target_hours": 8
    },
    "mental_health": {
      "title": "Mental Wellness",
      "content": "Mental health strategies...",
      "recommendations": ["Practice daily meditation"],
      "stress_management": ["Deep breathing exercises"]
    }
  },
  "generated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/v1/health/advice/quick
Generate quick health advice for a specific topic.

**Query Parameters:**
- `topic`: string (required) - The health topic to get advice about

**Response:**
```json
{
  "success": true,
  "topic": "sleep_improvement",
  "advice": "To improve sleep quality, maintain a consistent sleep schedule...",
  "quick_tips": [
    "Go to bed at the same time every night",
    "Avoid screens 1 hour before bedtime",
    "Keep your bedroom cool and dark"
  ]
}
```

### 👨‍👩‍👧‍👦 Family Management

#### POST /api/v1/family
Create a new family.

**Request Body:**
```json
{
  "family_name": "string (required)",
  "description": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "family_id": "string",
  "family_name": "string",
  "description": "string",
  "admin_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "member_count": 1
}
```

#### GET /api/v1/family/{family_id}
Get family information.

**Response:**
```json
{
  "success": true,
  "family_id": "string",
  "family_name": "string",
  "description": "string",
  "admin_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "member_count": 3,
  "members": [
    {
      "user_id": "string",
      "display_name": "string",
      "role": "admin|member",
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/v1/family
Get user's families.

**Response:**
```json
{
  "success": true,
  "families": [
    {
      "family_id": "string",
      "family_name": "string",
      "role": "admin|member",
      "member_count": 3,
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /api/v1/family/{family_id}/invite
Invite a member to the family.

**Request Body:**
```json
{
  "email": "string (required)",
  "role": "member (default)"
}
```

**Response:**
```json
{
  "success": true,
  "invitation_id": "string",
  "email": "string",
  "family_id": "string",
  "expires_at": "2024-01-01T00:00:00Z"
}
```

#### POST /api/v1/family/invitation/accept
Accept a family invitation.

**Request Body:**
```json
{
  "invitation_token": "string (required)"
}
```

#### POST /api/v1/family/invitation/decline
Decline a family invitation.

#### GET /api/v1/family/{family_id}/members
Get family members.

#### GET /api/v1/family/{family_id}/permissions
Get family permissions for current user.

#### POST /api/v1/family/switch-member
Switch active family member context.

**Request Body:**
```json
{
  "target_member_id": "string (required)"
}
```

### 🏆 Achievements

#### GET /api/v1/achievements
Get user achievements.

**Response:**
```json
{
  "success": true,
  "message": "Achievements retrieved successfully",
  "achievements": [
    {
      "id": "string",
      "title": "First Steps",
      "description": "Complete your first 1000 steps",
      "category": "activity",
      "points": 100,
      "completed": true,
      "completed_at": "2024-01-01T00:00:00Z",
      "progress": 100,
      "requirements": {
        "steps": 1000
      }
    }
  ],
  "total_points": 500,
  "completed_count": 5,
  "in_progress_count": 3
}
```

### 📊 Health Reports

#### GET /api/v1/family/{family_id}/report
Generate family health report.

**Query Parameters:**
- `period`: string (weekly, monthly, quarterly, default: monthly)
- `format`: string (json, pdf, default: json)

**Response:**
```json
{
  "success": true,
  "family_id": "string",
  "report_period": "monthly",
  "generated_at": "2024-01-01T00:00:00Z",
  "summary": {
    "total_members": 3,
    "active_members": 2,
    "total_activities": 150,
    "avg_daily_steps": 8500
  },
  "member_reports": [
    {
      "user_id": "string",
      "display_name": "string",
      "activity_summary": {
        "total_steps": 25000,
        "avg_daily_steps": 8333,
        "active_days": 20
      },
      "achievements": 5,
      "health_score": 85
    }
  ]
}
```

#### GET /api/v1/family/{family_id}/leaderboard
Get family leaderboard.

**Query Parameters:**
- `metric`: string (steps, calories, sleep_hours, default: steps)
- `period`: string (daily, weekly, monthly, default: weekly)

**Response:**
```json
{
  "success": true,
  "metric": "steps",
  "period": "weekly",
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "string",
      "display_name": "string",
      "value": 50000,
      "unit": "steps"
    }
  ]
}
```

#### GET /api/v1/family/{family_id}/challenges
Get family challenges.

**Response:**
```json
{
  "success": true,
  "challenges": [
    {
      "challenge_id": "string",
      "title": "Weekly Steps Challenge",
      "description": "Reach 70,000 steps as a family",
      "type": "steps",
      "target_value": 70000,
      "current_value": 45000,
      "progress_percentage": 64.3,
      "start_date": "2024-01-01",
      "end_date": "2024-01-07",
      "status": "active",
      "participants": 3
    }
  ]
}
```

#### POST /api/v1/family/{family_id}/challenges
Create a family challenge.

**Request Body:**
```json
{
  "title": "string (required)",
  "description": "string (optional)",
  "type": "steps|calories|sleep_hours|active_days",
  "target_value": "float (required)",
  "duration_days": "integer (1-365, required)",
  "start_date": "date (optional, default: today)"
}
```

### 🔧 System Endpoints

#### GET /api/v1/health
System health check endpoint.

**Response:**
```json
{
  "success": true,
  "message": "AuraWell API is healthy and running",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/system/performance
Get system performance metrics.

**Response:**
```json
{
  "success": true,
  "message": "Performance metrics retrieved successfully",
  "data": {
    "cache_hit_rate": 85.5,
    "slow_endpoints": [
      {
        "endpoint": "POST /api/v1/health/advice/comprehensive",
        "avg_response_time": 1.2
      }
    ],
    "cache_stats": {
      "hits": 1500,
      "misses": 250,
      "total_requests": 1750
    },
    "cache_enabled": true,
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### GET /
Root endpoint with API information.

**Response:**
```json
{
  "success": true,
  "message": "Welcome to AuraWell Health Assistant API v1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

API requests are rate limited. Check response headers for current limits:

- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

## Filtering and Sorting

Many endpoints support filtering and sorting:

**Query Parameters:**
- `sort_by`: Field to sort by
- `sort_order`: `asc` or `desc`
- Various filter parameters specific to each endpoint

## WebSocket Support

Real-time features are available via WebSocket connections at:

```
ws://127.0.0.1:8000/ws
```

## Performance Headers

All responses include performance monitoring headers:

- `X-Process-Time`: Request processing time in seconds
- `X-Request-ID`: Unique request identifier for tracking

## Security Features

- JWT-based authentication
- CORS configuration for cross-origin requests
- Request validation and sanitization
- Rate limiting to prevent abuse
- Comprehensive error handling

## SDK and Client Libraries

Official client libraries are available for:

- JavaScript/TypeScript
- Python
- Swift (iOS)
- Kotlin (Android)

## Support

For API support and documentation updates:

- GitHub Issues: https://github.com/PrescottClub/AuraWell_Agent/issues
- API Documentation: http://127.0.0.1:8000/docs
- Email: support@aurawell.com
