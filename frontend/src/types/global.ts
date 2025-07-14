/**
 * 全局类型定义
 */

// 全局常量类型
export type Environment = 'development' | 'production' | 'test';
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

// 路由相关类型
export interface RouteConfig {
  path: string;
  name: string;
  component: any;
  meta?: RouteMeta;
  children?: RouteConfig[];
  redirect?: string;
  alias?: string | string[];
  beforeEnter?: (to: any, from: any, next: any) => void;
}

export interface RouteMeta {
  title?: string;
  requiresAuth?: boolean;
  roles?: string[];
  icon?: string;
  hidden?: boolean;
  keepAlive?: boolean;
  breadcrumb?: boolean;
}

// 菜单类型
export interface MenuItem {
  key: string;
  label: string;
  icon?: string;
  path?: string;
  children?: MenuItem[];
  disabled?: boolean;
  hidden?: boolean;
  badge?: number | string;
}

// 面包屑类型
export interface BreadcrumbItem {
  title: string;
  path?: string;
  icon?: string;
}

// 主题类型
export interface ThemeConfig {
  primaryColor: string;
  borderRadius: number;
  componentSize: 'small' | 'middle' | 'large';
  wireframe: boolean;
}

// 国际化类型
export interface I18nConfig {
  locale: string;
  fallbackLocale: string;
  messages: Record<string, any>;
}

// 环境变量类型
export interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_APP_API_BASE_URL: string;
  readonly VITE_APP_ENV: Environment;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_ENABLE_MOCK: string;
  readonly VITE_SENTRY_DSN: string;
}

export interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// 工具类型
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type Recordable<T = any> = Record<string, T>;
export type ReadonlyRecordable<T = any> = Readonly<Record<string, T>>;
export type Indexable<T = any> = { [key: string]: T };
export type DeepPartial<T> = { [P in keyof T]?: DeepPartial<T[P]> };
export type TimeoutHandle = ReturnType<typeof setTimeout>;
export type IntervalHandle = ReturnType<typeof setInterval>;

// 函数类型
export type Fn<T = any, R = T> = (...arg: T[]) => R;
export type PromiseFn<T = any, R = T> = (...arg: T[]) => Promise<R>;
export type AnyFunction = (...args: any[]) => any;
export type AnyPromiseFunction = (...args: any[]) => Promise<any>;

// 事件类型
export type EventHandler<T = Event> = (event: T) => void;
export type KeyboardEventHandler = EventHandler<KeyboardEvent>;
export type MouseEventHandler = EventHandler<MouseEvent>;
export type ChangeEventHandler = EventHandler<Event>;
export type InputEventHandler = EventHandler<InputEvent>;

// 组件实例类型
export type ComponentRef<T = any> = T | null;
export type ElRef<T extends HTMLElement = HTMLDivElement> = Nullable<T>;

// 表单相关类型
export interface FormRule {
  required?: boolean;
  message?: string;
  trigger?: string | string[];
  min?: number;
  max?: number;
  pattern?: RegExp;
  validator?: (rule: any, value: any, callback: any) => void;
}

export type FormRules = Record<string, FormRule | FormRule[]>;

// 表格相关类型
export interface TableRowSelection {
  type?: 'checkbox' | 'radio';
  selectedRowKeys?: string[] | number[];
  onChange?: (selectedRowKeys: string[] | number[], selectedRows: any[]) => void;
  onSelect?: (record: any, selected: boolean, selectedRows: any[], nativeEvent: Event) => void;
  onSelectAll?: (selected: boolean, selectedRows: any[], changeRows: any[]) => void;
}

// 分页类型
export interface PaginationConfig {
  current?: number;
  pageSize?: number;
  total?: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => string;
  onChange?: (page: number, pageSize: number) => void;
  onShowSizeChange?: (current: number, size: number) => void;
}

// 上传类型
export interface UploadFile {
  uid: string;
  name: string;
  status?: 'uploading' | 'done' | 'error' | 'removed';
  response?: any;
  linkProps?: any;
  xhr?: any;
  url?: string;
  preview?: string;
  originFileObj?: File;
  file?: File | Blob;
  percent?: number;
  thumbUrl?: string;
  size?: number;
  type?: string;
}

// 树形数据类型
export interface TreeNode {
  key: string | number;
  title: string;
  children?: TreeNode[];
  disabled?: boolean;
  disableCheckbox?: boolean;
  selectable?: boolean;
  checkable?: boolean;
  icon?: any;
  isLeaf?: boolean;
  [key: string]: any;
}

// 选择器选项类型
export interface SelectOption {
  label: string;
  value: string | number;
  disabled?: boolean;
  children?: SelectOption[];
  [key: string]: any;
}

// 图表数据类型
export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

export interface ChartSeries {
  name: string;
  type: string;
  data: ChartDataPoint[] | number[];
  [key: string]: any;
}

// 性能监控类型
export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
}

export interface PerformanceEntry {
  name: string;
  entryType: string;
  startTime: number;
  duration: number;
}

// 错误处理类型
export interface ErrorInfo {
  message: string;
  stack?: string;
  componentStack?: string;
  errorBoundary?: string;
  errorBoundaryStack?: string;
}

// WebSocket类型
export interface WebSocketConfig {
  url: string;
  protocols?: string | string[];
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeat?: boolean;
  heartbeatInterval?: number;
}

// 缓存类型
export interface CacheItem<T = any> {
  key: string;
  value: T;
  timestamp: number;
  ttl?: number;
}

// 存储类型
export interface StorageConfig {
  prefix?: string;
  expire?: number;
  isEncrypt?: boolean;
}

// 请求拦截器类型
export interface RequestInterceptor {
  onFulfilled?: (config: any) => any;
  onRejected?: (error: any) => any;
}

export interface ResponseInterceptor {
  onFulfilled?: (response: any) => any;
  onRejected?: (error: any) => any;
}

// 插件类型
export interface PluginConfig {
  name: string;
  version: string;
  install: (app: any, options?: any) => void;
  options?: any;
}

// 全局声明
declare global {
  interface Window {
    __POWERED_BY_QIANKUN__?: boolean;
    __INJECTED_PUBLIC_PATH_BY_QIANKUN__?: string;
    __APP_INFO__?: {
      pkg: {
        name: string;
        version: string;
        dependencies: Recordable<string>;
        devDependencies: Recordable<string>;
      };
      lastBuildTime: string;
    };
  }
}
