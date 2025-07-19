/**
 * Store 相关类型定义
 */

import type { UserProfile, Family, FamilyMember, HealthReport, HealthPlan, ChatMessage } from './api'

// 认证Store类型
export interface AuthState {
  token: string;
  tokenType: string;
  expiresIn: string;
  expiresAt: string;
  isValidating: boolean;
  lastValidation: number;
}

export interface AuthStore extends AuthState {
  // 计算属性
  isAuthenticated: boolean;
  isTokenExpired: boolean;
  timeUntilExpiry: number;
  
  // 方法
  setToken: (token: string, tokenType?: string, expiresIn?: number) => void;
  clearToken: () => void;
  getAuthHeader: () => Record<string, string>;
  validateToken: () => Promise<boolean>;
  performAutoLogin: () => Promise<boolean>;
  ensureAuthenticated: () => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
  logout: () => Promise<void>;
}

// 用户Store类型
export interface UserState {
  userProfile: Partial<UserProfile>;
  loading: boolean;
  error: string | null;
}

export interface UserStore extends UserState {
  // 计算属性
  isProfileComplete: boolean;
  displayName: string;
  
  // 方法
  fetchUserProfile: () => Promise<void>;
  updateUserProfile: (profile: Partial<UserProfile>) => Promise<void>;
  uploadAvatar: (file: File) => Promise<string>;
  clearUserData: () => void;
}

// 家庭Store类型
export interface FamilyState {
  currentFamily: Family | null;
  familyMembers: FamilyMember[];
  userFamilies: Family[];
  loading: boolean;
  error: string | null;
}

export interface FamilyStore extends FamilyState {
  // 计算属性
  isInFamily: boolean;
  isAdmin: boolean;
  isOwner: boolean;
  memberCount: number;
  
  // 方法
  fetchUserFamilies: () => Promise<void>;
  fetchFamilyMembers: (familyId: string) => Promise<void>;
  createFamily: (familyData: Partial<Family>) => Promise<Family>;
  joinFamily: (invitationCode: string) => Promise<void>;
  leaveFamily: (familyId: string) => Promise<void>;
  inviteMember: (familyId: string, email: string, role: string) => Promise<void>;
  removeMember: (familyId: string, memberId: string) => Promise<void>;
  updateMemberRole: (familyId: string, memberId: string, role: string) => Promise<void>;
  setCurrentFamily: (family: Family) => void;
  clearFamilyData: () => void;
}

// 健康Store类型
export interface HealthState {
  healthReports: HealthReport[];
  currentReport: HealthReport | null;
  healthMetrics: Record<string, any>;
  loading: boolean;
  error: string | null;
}

export interface HealthStore extends HealthState {
  // 计算属性
  latestReport: HealthReport | null;
  healthScore: number;
  healthTrend: 'up' | 'down' | 'stable';
  
  // 方法
  fetchHealthReports: () => Promise<void>;
  fetchHealthReport: (reportId: string) => Promise<void>;
  generateHealthReport: (type: string, period: any) => Promise<HealthReport>;
  fetchHealthMetrics: (timeRange: string) => Promise<void>;
  addHealthMetric: (metric: any) => Promise<void>;
  clearHealthData: () => void;
}

// 健康计划Store类型
export interface HealthPlanState {
  healthPlans: HealthPlan[];
  currentPlan: HealthPlan | null;
  planModules: Record<string, any>;
  loading: boolean;
  error: string | null;
}

export interface HealthPlanStore extends HealthPlanState {
  // 计算属性
  activePlans: HealthPlan[];
  completedPlans: HealthPlan[];
  planProgress: number;
  
  // 方法
  fetchHealthPlans: () => Promise<void>;
  fetchHealthPlan: (planId: string) => Promise<void>;
  createHealthPlan: (planData: Partial<HealthPlan>) => Promise<HealthPlan>;
  updateHealthPlan: (planId: string, updates: Partial<HealthPlan>) => Promise<void>;
  deleteHealthPlan: (planId: string) => Promise<void>;
  startPlan: (planId: string) => Promise<void>;
  pausePlan: (planId: string) => Promise<void>;
  completePlan: (planId: string) => Promise<void>;
  updatePlanProgress: (planId: string, progress: number) => Promise<void>;
  setCurrentPlan: (plan: HealthPlan) => void;
  clearPlanData: () => void;
}

// 聊天Store类型
export interface ChatState {
  conversations: any[];
  currentConversation: any | null;
  messages: ChatMessage[];
  loading: boolean;
  isTyping: boolean;
  error: string | null;
}

export interface ChatStore extends ChatState {
  // 计算属性
  hasConversations: boolean;
  messageCount: number;
  
  // 方法
  fetchConversations: () => Promise<void>;
  fetchMessages: (conversationId: string) => Promise<void>;
  sendMessage: (content: string, conversationId?: string) => Promise<void>;
  createConversation: (title?: string) => Promise<any>;
  deleteConversation: (conversationId: string) => Promise<void>;
  clearCurrentConversation: () => void;
  setTyping: (isTyping: boolean) => void;
  performRAGSearch: (query: string) => Promise<any>;
  clearChatData: () => void;
}

// 应用设置Store类型
export interface AppState {
  theme: 'light' | 'dark' | 'auto';
  language: 'zh' | 'en';
  sidebarCollapsed: boolean;
  notifications: any[];
  loading: boolean;
}

export interface AppStore extends AppState {
  // 计算属性
  isDark: boolean;
  unreadNotifications: number;
  
  // 方法
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  setLanguage: (language: 'zh' | 'en') => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  fetchNotifications: () => Promise<void>;
  markNotificationRead: (notificationId: string) => Promise<void>;
  clearNotifications: () => void;
  addNotification: (notification: any) => void;
}

// 根Store类型
export interface RootStore {
  auth: AuthStore;
  user: UserStore;
  family: FamilyStore;
  health: HealthStore;
  healthPlan: HealthPlanStore;
  chat: ChatStore;
  app: AppStore;
}

// Store操作类型
export type StoreAction<T = any> = (...args: any[]) => Promise<T> | T;
export type StoreGetter<T = any> = () => T;
export type StoreMutation<T = any> = (state: any, payload?: T) => void;

// 异步操作状态类型
export interface AsyncState {
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;
}

// 分页状态类型
export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
}

// 过滤状态类型
export interface FilterState {
  keyword: string;
  filters: Record<string, any>;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

// 缓存状态类型
export interface CacheState<T = any> {
  data: T | null;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

// Store插件类型
export interface StorePlugin {
  install: (store: any) => void;
}

// 持久化配置类型
export interface PersistConfig {
  key: string;
  storage: Storage;
  paths?: string[];
  beforeRestore?: (context: any) => void;
  afterRestore?: (context: any) => void;
}
