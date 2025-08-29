/**
 * AuraWell Design Tokens 工具函数
 *
 * 提供便捷的函数来访问和使用设计令牌
 */

import type {
  HealthStatus,
  ButtonVariant,
  SpacingSize,
  BorderRadiusSize,
} from '@/types/design-tokens';

/**
 * 获取CSS变量值
 * @param variableName CSS变量名（不包含--前缀）
 * @returns CSS变量值
 */
export function getCSSVariable(variableName: string): string {
  if (typeof window === 'undefined') {
    return `var(--${variableName})`;
  }

  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(`--${variableName}`)
    .trim();

  return value || `var(--${variableName})`;
}

/**
 * 获取颜色值
 * @param colorPath 颜色路径，如 'primary', 'text-primary', 'health-excellent'
 * @returns 颜色值
 */
export function getColor(colorPath: string): string {
  const normalizedPath = colorPath.replace(/\./g, '-');
  return getCSSVariable(`color-${normalizedPath}`);
}

/**
 * 获取间距值
 * @param size 间距大小
 * @returns 间距值
 */
export function getSpacing(size: SpacingSize): string {
  return getCSSVariable(`spacing-${size}`);
}

/**
 * 获取圆角值
 * @param size 圆角大小
 * @returns 圆角值
 */
export function getBorderRadius(size: BorderRadiusSize): string {
  return getCSSVariable(`border-radius-${size}`);
}

/**
 * 获取健康状态对应的颜色
 * @param status 健康状态
 * @returns 颜色值
 */
export function getHealthColor(status: HealthStatus): string {
  return getCSSVariable(`color-health-${status}`);
}

/**
 * 获取按钮变体对应的CSS类名
 * @param variant 按钮变体
 * @returns CSS类名
 */
export function getButtonClasses(variant: ButtonVariant): string {
  return `aura-btn aura-btn--${variant}`;
}

/**
 * 获取文字样式类名
 * @param type 文字类型
 * @param size 文字大小（可选）
 * @returns CSS类名
 */
export function getTextClasses(
  type: 'heading' | 'body' | 'caption' | 'metric',
  size?: string
): string {
  if (type === 'metric') {
    return size ? `text-metric-${size}` : 'text-metric';
  }

  if (size) {
    return `text-${type}-${size}`;
  }

  return `text-${type}`;
}

/**
 * 获取卡片样式类名
 * @param variant 卡片变体
 * @returns CSS类名
 */
export function getCardClasses(variant?: 'elevated' | 'health'): string {
  const baseClass = 'aura-card';

  if (!variant) {
    return baseClass;
  }

  if (variant === 'health') {
    return `${baseClass} health-metric-card`;
  }

  return `${baseClass} ${baseClass}--${variant}`;
}

/**
 * 获取健康指标卡片的样式类名
 * @param status 健康状态
 * @returns CSS类名
 */
export function getHealthCardClasses(status: HealthStatus): string {
  return `health-metric-card health-metric-card--${status}`;
}

/**
 * 生成响应式间距类名
 * @param spacing 间距配置
 * @returns CSS类名
 */
export function getResponsiveSpacing(spacing: {
  default: SpacingSize;
  sm?: SpacingSize;
  md?: SpacingSize;
  lg?: SpacingSize;
}): string {
  let classes = `p-${spacing.default}`;

  if (spacing.sm) classes += ` sm:p-${spacing.sm}`;
  if (spacing.md) classes += ` md:p-${spacing.md}`;
  if (spacing.lg) classes += ` lg:p-${spacing.lg}`;

  return classes;
}

/**
 * 设计令牌常量
 */
export const DESIGN_TOKENS = {
  // 颜色
  COLORS: {
    PRIMARY: 'var(--color-primary)',
    PRIMARY_HOVER: 'var(--color-primary-hover)',
    HEALTH: 'var(--color-health)',
    ACCENT: 'var(--color-accent)',
    SUCCESS: 'var(--color-success)',
    WARNING: 'var(--color-warning)',
    ERROR: 'var(--color-error)',
    INFO: 'var(--color-info)',

    TEXT: {
      PRIMARY: 'var(--color-text-primary)',
      SECONDARY: 'var(--color-text-secondary)',
      MUTED: 'var(--color-text-muted)',
      DISABLED: 'var(--color-text-disabled)',
    },

    BACKGROUND: {
      DEFAULT: 'var(--color-background)',
      ALT: 'var(--color-background-alt)',
      SURFACE: 'var(--color-background-surface)',
      ELEVATED: 'var(--color-background-elevated)',
    },

    BORDER: {
      LIGHT: 'var(--color-border-light)',
      DEFAULT: 'var(--color-border)',
      STRONG: 'var(--color-border-strong)',
    },
  },

  // 间距
  SPACING: {
    XS: 'var(--spacing-2)',
    SM: 'var(--spacing-3)',
    MD: 'var(--spacing-4)',
    LG: 'var(--spacing-6)',
    XL: 'var(--spacing-8)',
    XXL: 'var(--spacing-12)',
  },

  // 圆角
  BORDER_RADIUS: {
    SM: 'var(--border-radius-sm)',
    MD: 'var(--border-radius-md)',
    LG: 'var(--border-radius-lg)',
    XL: 'var(--border-radius-xl)',
  },

  // 字体
  FONT: {
    FAMILY: {
      SANS: 'var(--font-family-sans)',
      MONO: 'var(--font-family-mono)',
    },
    SIZE: {
      XS: 'var(--font-size-xs)',
      SM: 'var(--font-size-sm)',
      BASE: 'var(--font-size-base)',
      LG: 'var(--font-size-lg)',
      XL: 'var(--font-size-xl)',
      XXL: 'var(--font-size-2xl)',
    },
    WEIGHT: {
      NORMAL: 'var(--font-weight-normal)',
      MEDIUM: 'var(--font-weight-medium)',
      SEMIBOLD: 'var(--font-weight-semibold)',
      BOLD: 'var(--font-weight-bold)',
    },
  },

  // 动画
  ANIMATION: {
    DURATION: {
      FAST: 'var(--duration-fast)',
      BASE: 'var(--duration-base)',
      SLOW: 'var(--duration-slow)',
      SLOWER: 'var(--duration-slower)',
    },
    EASE: {
      IN: 'var(--ease-in)',
      OUT: 'var(--ease-out)',
      IN_OUT: 'var(--ease-in-out)',
    },
  },

  // 阴影
  SHADOW: {
    NONE: 'var(--shadow-none)',
    SM: 'var(--shadow-sm)',
    BASE: 'var(--shadow-base)',
    MD: 'var(--shadow-md)',
    LG: 'var(--shadow-lg)',
  },

  // Z-index
  Z_INDEX: {
    DROPDOWN: 'var(--z-index-dropdown)',
    STICKY: 'var(--z-index-sticky)',
    FIXED: 'var(--z-index-fixed)',
    MODAL_BACKDROP: 'var(--z-index-modal-backdrop)',
    MODAL: 'var(--z-index-modal)',
    POPOVER: 'var(--z-index-popover)',
    TOOLTIP: 'var(--z-index-tooltip)',
  },
} as const;

/**
 * 健康状态映射
 */
export const HEALTH_STATUS_MAP = {
  excellent: {
    color: 'var(--color-health-excellent)',
    label: '优秀',
    icon: '🟢',
  },
  good: {
    color: 'var(--color-health-good)',
    label: '良好',
    icon: '🟡',
  },
  normal: {
    color: 'var(--color-health-normal)',
    label: '正常',
    icon: '🟠',
  },
  warning: {
    color: 'var(--color-health-warning)',
    label: '注意',
    icon: '🟠',
  },
  danger: {
    color: 'var(--color-health-danger)',
    label: '危险',
    icon: '🔴',
  },
} as const;

/**
 * 验证健康状态
 * @param status 状态值
 * @returns 是否为有效的健康状态
 */
export function isValidHealthStatus(status: string): status is HealthStatus {
  return status in HEALTH_STATUS_MAP;
}

/**
 * 获取健康状态信息
 * @param status 健康状态
 * @returns 状态信息对象
 */
export function getHealthStatusInfo(status: HealthStatus) {
  return HEALTH_STATUS_MAP[status];
}
