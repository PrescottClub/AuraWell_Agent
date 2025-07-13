/**
 * AuraWell Design Tokens TypeScript 定义
 * 
 * 这个文件提供了设计令牌的TypeScript类型定义，
 * 确保在JavaScript/TypeScript代码中使用设计令牌时的类型安全
 */

// 颜色系统类型
export interface ColorTokens {
  // 主色调
  primary: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
    DEFAULT: string;
    hover: string;
  };
  
  // 健康色
  health: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
    DEFAULT: string;
    excellent: string;
    good: string;
    normal: string;
    warning: string;
    danger: string;
  };
  
  // 强调色
  accent: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
    DEFAULT: string;
    hover: string;
  };
  
  // 中性色
  neutral: {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  };
  
  // 语义化颜色
  text: {
    primary: string;
    secondary: string;
    muted: string;
    disabled: string;
  };
  
  // 背景色
  background: {
    DEFAULT: string;
    alt: string;
    surface: string;
    elevated: string;
  };
  
  // 边框色
  border: {
    light: string;
    DEFAULT: string;
    strong: string;
  };
  
  // 功能色
  success: string;
  warning: string;
  error: string;
  info: string;
}

// 字体系统类型
export interface TypographyTokens {
  fontFamily: {
    sans: string;
    mono: string;
  };
  
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
    '4xl': string;
    '5xl': string;
  };
  
  fontWeight: {
    normal: number;
    medium: number;
    semibold: number;
    bold: number;
  };
  
  lineHeight: {
    tight: number;
    normal: number;
    relaxed: number;
  };
}

// 间距系统类型
export interface SpacingTokens {
  0: string;
  1: string;
  2: string;
  3: string;
  4: string;
  5: string;
  6: string;
  8: string;
  10: string;
  12: string;
  16: string;
  20: string;
  24: string;
}

// 圆角系统类型
export interface BorderRadiusTokens {
  none: string;
  sm: string;
  base: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
  '3xl': string;
  full: string;
}

// 阴影系统类型
export interface ShadowTokens {
  none: string;
  sm: string;
  base: string;
  md: string;
  lg: string;
}

// 动画系统类型
export interface AnimationTokens {
  duration: {
    fast: string;
    base: string;
    slow: string;
    slower: string;
  };
  
  ease: {
    in: string;
    out: string;
    inOut: string;
  };
}

// Z-index 系统类型
export interface ZIndexTokens {
  dropdown: number;
  sticky: number;
  fixed: number;
  modalBackdrop: number;
  modal: number;
  popover: number;
  tooltip: number;
}

// 断点系统类型
export interface BreakpointTokens {
  sm: string;
  md: string;
  lg: string;
  xl: string;
  '2xl': string;
}

// 组件特定令牌类型
export interface ComponentTokens {
  card: {
    padding: string;
    borderRadius: string;
    borderWidth: string;
    borderColor: string;
    background: string;
  };
  
  button: {
    paddingX: string;
    paddingY: string;
    borderRadius: string;
    fontWeight: string;
  };
  
  input: {
    paddingX: string;
    paddingY: string;
    borderRadius: string;
    borderWidth: string;
    borderColor: string;
  };
}

// 完整的设计令牌类型
export interface DesignTokens {
  colors: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  borderRadius: BorderRadiusTokens;
  shadow: ShadowTokens;
  animation: AnimationTokens;
  zIndex: ZIndexTokens;
  breakpoints: BreakpointTokens;
  components: ComponentTokens;
}

// 健康状态类型
export type HealthStatus = 'excellent' | 'good' | 'normal' | 'warning' | 'danger';

// 按钮变体类型
export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error';

// 文字大小类型
export type TextSize = 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl';

// 间距大小类型
export type SpacingSize = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '8' | '10' | '12' | '16' | '20' | '24';

// 圆角大小类型
export type BorderRadiusSize = 'none' | 'sm' | 'base' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | 'full';

// 工具函数类型
export interface DesignTokenUtils {
  getColor: (path: string) => string;
  getSpacing: (size: SpacingSize) => string;
  getBorderRadius: (size: BorderRadiusSize) => string;
  getHealthColor: (status: HealthStatus) => string;
  getButtonClasses: (variant: ButtonVariant) => string;
}

// 导出常量
export const HEALTH_STATUSES: HealthStatus[] = ['excellent', 'good', 'normal', 'warning', 'danger'];
export const BUTTON_VARIANTS: ButtonVariant[] = ['primary', 'secondary', 'success', 'warning', 'error'];
export const TEXT_SIZES: TextSize[] = ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl'];
