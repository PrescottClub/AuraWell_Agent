/**
 * 类型定义统一导出
 */

// API相关类型
export type {
  ApiResponse,
  PaginatedResponse,
  User,
  UserProfile,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  HealthMetric,
  HealthReport,
  Family,
  FamilyMember,
  FamilyInvitation,
  ChatMessage,
  ChatConversation,
  HealthPlan,
  PlanModule,
  ApiError,
  RequestConfig,
  FileUpload,
  Notification,
  UserSettings
} from './api'

// 组件相关类型
export type {
  BaseComponentProps,
  ButtonProps,
  InputProps,
  CardProps,
  TableColumn,
  TableProps,
  ModalProps,
  FormItemProps,
  FormProps,
  ChartProps,
  HealthCardProps,
  ChatMessageProps,
  VirtualScrollProps,
  SkeletonProps,
  EmptyProps,
  LoadingProps,
  PaginationProps,
  TabPane,
  TabsProps,
  StepItem,
  StepsProps,
  ComponentEvents
} from './components'

// Store相关类型
export type {
  AuthState,
  AuthStore,
  UserState,
  UserStore,
  FamilyState,
  FamilyStore,
  HealthState,
  HealthStore,
  HealthPlanState,
  HealthPlanStore,
  ChatState,
  ChatStore,
  AppState,
  AppStore,
  RootStore,
  StoreAction,
  StoreGetter,
  StoreMutation,
  AsyncState,
  PaginationState,
  FilterState,
  CacheState,
  StorePlugin,
  PersistConfig
} from './store'

// 设计令牌相关类型
export type {
  ColorTokens,
  TypographyTokens,
  SpacingTokens,
  BorderRadiusTokens,
  ShadowTokens,
  AnimationTokens,
  ZIndexTokens,
  BreakpointTokens,
  ComponentTokens,
  DesignTokens,
  HealthStatus,
  ButtonVariant,
  TextSize,
  SpacingSize,
  BorderRadiusSize,
  DesignTokenUtils
} from './design-tokens'

// 全局类型
export type {
  Environment,
  LogLevel,
  RouteConfig,
  RouteMeta,
  MenuItem,
  BreadcrumbItem,
  ThemeConfig,
  I18nConfig,
  ImportMetaEnv,
  ImportMeta,
  Nullable,
  Optional,
  Recordable,
  ReadonlyRecordable,
  Indexable,
  DeepPartial,
  TimeoutHandle,
  IntervalHandle,
  Fn,
  PromiseFn,
  AnyFunction,
  AnyPromiseFunction,
  EventHandler,
  KeyboardEventHandler,
  MouseEventHandler,
  ChangeEventHandler,
  InputEventHandler,
  ComponentRef,
  ElRef,
  FormRule,
  FormRules,
  TableRowSelection,
  PaginationConfig,
  UploadFile,
  TreeNode,
  SelectOption,
  ChartDataPoint,
  ChartSeries,
  PerformanceMetric,
  PerformanceEntry,
  ErrorInfo,
  WebSocketConfig,
  CacheItem,
  StorageConfig,
  RequestInterceptor,
  ResponseInterceptor,
  PluginConfig
} from './global'

// 常量导出
export {
  HEALTH_STATUSES,
  BUTTON_VARIANTS,
  TEXT_SIZES
} from './design-tokens'

// 导入需要的类型用于类型守卫
import type {
  User,
  HealthReport,
  Family,
  ChatMessage,
  ApiResponse,
  PaginatedResponse
} from './api'
import type { PaginationState } from './store'

// 类型守卫函数
export const isUser = (obj: any): obj is User => {
  return obj && typeof obj.user_id === 'string' && typeof obj.username === 'string'
}

export const isHealthReport = (obj: any): obj is HealthReport => {
  return obj && typeof obj.report_id === 'string' && typeof obj.report_type === 'string'
}

export const isFamily = (obj: any): obj is Family => {
  return obj && typeof obj.family_id === 'string' && typeof obj.family_name === 'string'
}

export const isChatMessage = (obj: any): obj is ChatMessage => {
  return obj && typeof obj.message_id === 'string' && typeof obj.content === 'string'
}

export const isApiResponse = <T>(obj: any): obj is ApiResponse<T> => {
  return obj && typeof obj.success === 'boolean'
}

// 工具类型函数
export const createApiResponse = <T>(
  success: boolean,
  data?: T,
  message?: string,
  error?: string
): ApiResponse<T> => ({
  success,
  data,
  message,
  error,
  timestamp: new Date().toISOString()
})

export const createPaginatedResponse = <T>(
  data: T[],
  pagination: PaginationState
): PaginatedResponse<T> => ({
  success: true,
  data,
  pagination: {
    page: pagination.page,
    pageSize: pagination.pageSize,
    total: pagination.total,
    totalPages: Math.ceil(pagination.total / pagination.pageSize)
  },
  timestamp: new Date().toISOString()
})

// 枚举类型
export enum UserRole {
  OWNER = 'Owner',
  ADMIN = 'Admin',
  MEMBER = 'Member'
}

export enum HealthMetricType {
  STEPS = 'steps',
  WEIGHT = 'weight',
  BLOOD_PRESSURE = 'blood_pressure',
  HEART_RATE = 'heart_rate',
  SLEEP = 'sleep',
  CALORIES = 'calories'
}

export enum ReportType {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly'
}

export enum ReportStatus {
  GENERATING = 'generating',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export enum MessageType {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

export enum PlanStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  PAUSED = 'paused'
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error'
}
