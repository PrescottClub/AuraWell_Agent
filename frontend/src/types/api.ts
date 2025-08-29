/**
 * API 相关类型定义
 */

// 基础API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp?: string;
}

// 分页响应类型
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
}

// 用户相关类型
export interface User {
  user_id: string;
  username: string;
  email: string;
  display_name?: string;
  avatar?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface UserProfile extends User {
  age?: number;
  gender?: 'male' | 'female' | 'other';
  height?: number;
  weight?: number;
  health_goals?: string[];
  preferences?: Record<string, any>;
}

// 认证相关类型
export interface LoginRequest {
  username: string;
  password: string;
  remember?: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  display_name?: string;
}

// 健康数据类型
export interface HealthMetric {
  metric_id: string;
  user_id: string;
  metric_type:
    | 'steps'
    | 'weight'
    | 'blood_pressure'
    | 'heart_rate'
    | 'sleep'
    | 'calories';
  value: number;
  unit: string;
  recorded_at: string;
  source?: string;
}

export interface HealthReport {
  report_id: string;
  user_id: string;
  title: string;
  report_type: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  status: 'generating' | 'completed' | 'failed';
  score?: number;
  summary?: string;
  insights?: string[];
  recommendations?: string[];
  data?: Record<string, any>;
  generated_at: string;
  period_start: string;
  period_end: string;
}

// 家庭相关类型
export interface Family {
  family_id: string;
  family_name: string;
  description?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  member_count: number;
}

export interface FamilyMember {
  member_id: string;
  family_id: string;
  user_id: string;
  role: 'Owner' | 'Admin' | 'Member';
  display_name: string;
  avatar?: string;
  joined_at: string;
  is_active: boolean;
}

export interface FamilyInvitation {
  invitation_id: string;
  family_id: string;
  email: string;
  role: 'Admin' | 'Member';
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  invited_by: string;
  invited_at: string;
  expires_at: string;
}

// 聊天相关类型
export interface ChatMessage {
  message_id: string;
  conversation_id?: string;
  user_id: string;
  content: string;
  message_type: 'user' | 'assistant' | 'system';
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatConversation {
  conversation_id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: ChatMessage;
}

// 健康计划类型
export interface HealthPlan {
  plan_id: string;
  user_id: string;
  title: string;
  description?: string;
  goals: string[];
  modules: ('diet' | 'exercise' | 'sleep' | 'mental_health')[];
  duration_days: number;
  status: 'draft' | 'active' | 'completed' | 'paused';
  progress?: number;
  created_at: string;
  updated_at: string;
  start_date?: string;
  end_date?: string;
}

export interface PlanModule {
  module_id: string;
  plan_id: string;
  module_type: 'diet' | 'exercise' | 'sleep' | 'mental_health';
  title: string;
  content: Record<string, any>;
  order: number;
  is_completed: boolean;
}

// 错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// 请求配置类型
export interface RequestConfig {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
}

// 文件上传类型
export interface FileUpload {
  file: File;
  progress?: number;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  url?: string;
  error?: string;
}

// 通知类型
export interface Notification {
  notification_id: string;
  user_id: string;
  title: string;
  content: string;
  type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

// 设置类型
export interface UserSettings {
  user_id: string;
  language: 'zh' | 'en';
  timezone: string;
  theme: 'light' | 'dark' | 'auto';
  notifications: {
    email: boolean;
    push: boolean;
    health_reminders: boolean;
    family_updates: boolean;
  };
  privacy: {
    profile_visibility: 'public' | 'family' | 'private';
    health_data_sharing: boolean;
  };
  updated_at: string;
}
