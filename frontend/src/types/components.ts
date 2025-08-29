/**
 * 组件相关类型定义
 */

import type { Component } from 'vue';

// 基础组件Props类型
export interface BaseComponentProps {
  class?: string;
  style?: string | Record<string, any>;
  id?: string;
}

// 按钮组件类型
export interface ButtonProps extends BaseComponentProps {
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'text';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: Component | string;
  block?: boolean;
  ghost?: boolean;
  danger?: boolean;
}

// 输入框组件类型
export interface InputProps extends BaseComponentProps {
  modelValue?: string | number;
  type?: 'text' | 'password' | 'email' | 'number' | 'tel' | 'url';
  placeholder?: string;
  disabled?: boolean;
  readonly?: boolean;
  maxlength?: number;
  showCount?: boolean;
  clearable?: boolean;
  size?: 'small' | 'medium' | 'large';
  prefix?: Component | string;
  suffix?: Component | string;
}

// 卡片组件类型
export interface CardProps extends BaseComponentProps {
  title?: string;
  extra?: Component | string;
  bordered?: boolean;
  hoverable?: boolean;
  loading?: boolean;
  size?: 'small' | 'default';
  bodyStyle?: Record<string, any>;
  headStyle?: Record<string, any>;
}

// 表格组件类型
export interface TableColumn {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sorter?: boolean | ((a: any, b: any) => number);
  filters?: Array<{ text: string; value: any }>;
  render?: (value: any, record: any, index: number) => any;
  fixed?: 'left' | 'right';
}

export interface TableProps extends BaseComponentProps {
  columns: TableColumn[];
  dataSource: any[];
  loading?: boolean;
  pagination?: boolean | object;
  rowKey?: string | ((record: any) => string);
  rowSelection?: object;
  scroll?: { x?: number | string; y?: number | string };
  size?: 'small' | 'middle' | 'large';
}

// 模态框组件类型
export interface ModalProps extends BaseComponentProps {
  open?: boolean;
  title?: string;
  width?: number | string;
  centered?: boolean;
  closable?: boolean;
  maskClosable?: boolean;
  keyboard?: boolean;
  footer?: Component | string | null;
  confirmLoading?: boolean;
  destroyOnClose?: boolean;
  forceRender?: boolean;
}

// 表单组件类型
export interface FormItemProps extends BaseComponentProps {
  label?: string;
  name?: string;
  rules?: any[];
  required?: boolean;
  help?: string;
  validateStatus?: 'success' | 'warning' | 'error' | 'validating';
  hasFeedback?: boolean;
  labelCol?: object;
  wrapperCol?: object;
}

export interface FormProps extends BaseComponentProps {
  model?: object;
  rules?: Record<string, any>;
  layout?: 'horizontal' | 'vertical' | 'inline';
  labelCol?: object;
  wrapperCol?: object;
  colon?: boolean;
  hideRequiredMark?: boolean;
  validateOnRuleChange?: boolean;
  scrollToFirstError?: boolean;
}

// 图表组件类型
export interface ChartProps extends BaseComponentProps {
  option: any;
  loading?: boolean;
  theme?: string | object;
  initOpts?: object;
  autoresize?: boolean;
  notMerge?: boolean;
  lazyUpdate?: boolean;
  silent?: boolean;
}

// 健康卡片组件类型
export interface HealthCardProps extends BaseComponentProps {
  title: string;
  category: string;
  value: number | string;
  unit?: string;
  icon: Component | string | (() => Component);
  trend?: number;
  trendPeriod?: string;
  status?: string;
  showChart?: boolean;
  chartData?: number[];
}

// 聊天消息组件类型
export interface ChatMessageProps extends BaseComponentProps {
  message: {
    id: string;
    content: string;
    type: 'user' | 'assistant' | 'system';
    timestamp: string;
    avatar?: string;
    username?: string;
  };
  showAvatar?: boolean;
  showTime?: boolean;
  maxWidth?: number | string;
}

// 虚拟滚动组件类型
export interface VirtualScrollProps extends BaseComponentProps {
  items: any[];
  itemHeight: number;
  containerHeight: number;
  buffer?: number;
  renderItem: (item: any, index: number) => any;
  keyField?: string;
}

// 骨架屏组件类型
export interface SkeletonProps extends BaseComponentProps {
  loading?: boolean;
  active?: boolean;
  avatar?: boolean | object;
  paragraph?: boolean | object;
  title?: boolean | object;
  round?: boolean;
}

// 空状态组件类型
export interface EmptyProps extends BaseComponentProps {
  description?: string;
  image?: string | Component;
  imageStyle?: Record<string, any>;
}

// 加载组件类型
export interface LoadingProps extends BaseComponentProps {
  spinning?: boolean;
  size?: 'small' | 'default' | 'large';
  tip?: string;
  delay?: number;
  indicator?: Component;
}

// 分页组件类型
export interface PaginationProps extends BaseComponentProps {
  current?: number;
  total: number;
  pageSize?: number;
  pageSizeOptions?: string[];
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => string;
  size?: 'small' | 'default';
  simple?: boolean;
  hideOnSinglePage?: boolean;
}

// 标签页组件类型
export interface TabPane {
  key: string;
  tab: string;
  disabled?: boolean;
  closable?: boolean;
  forceRender?: boolean;
}

export interface TabsProps extends BaseComponentProps {
  activeKey?: string;
  defaultActiveKey?: string;
  type?: 'line' | 'card' | 'editable-card';
  size?: 'small' | 'default' | 'large';
  position?: 'top' | 'right' | 'bottom' | 'left';
  tabBarGutter?: number;
  hideAdd?: boolean;
  centered?: boolean;
}

// 步骤条组件类型
export interface StepItem {
  title: string;
  description?: string;
  icon?: Component | string;
  status?: 'wait' | 'process' | 'finish' | 'error';
  disabled?: boolean;
}

export interface StepsProps extends BaseComponentProps {
  current?: number;
  direction?: 'horizontal' | 'vertical';
  size?: 'small' | 'default';
  status?: 'wait' | 'process' | 'finish' | 'error';
  progressDot?: boolean | Component;
  items: StepItem[];
}

// 事件类型
export interface ComponentEvents {
  onClick?: (event: MouseEvent) => void;
  onChange?: (value: any) => void;
  onInput?: (value: any) => void;
  onFocus?: (event: FocusEvent) => void;
  onBlur?: (event: FocusEvent) => void;
  onSubmit?: (values: any) => void;
  onReset?: () => void;
  onCancel?: () => void;
  onOk?: () => void;
}
