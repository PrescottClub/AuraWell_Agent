module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  darkMode: 'class', // 改为class模式，但主要使用浅色主题
  theme: {
    extend: {
      colors: {
        // 专业健康科技色彩系统 - 基于Oura Ring风格
        // 主色调 - 深邃专业，体现信任感
        primary: {
          50: '#e6f3ff',
          100: '#cce7ff',
          200: '#99cfff',
          300: '#66b7ff',
          400: '#339fff',
          500: '#1a365d',  // 主色：深邃海军蓝
          600: '#152b4a',
          700: '#102037',
          800: '#0b1524',
          900: '#060a11',
          DEFAULT: '#1a365d',
          hover: '#152b4a',
        },

        // 健康色 - 深绿色，确保在浅色背景上可读
        health: {
          50: '#e8f5e8',
          100: '#c8e6c8',
          200: '#a5d6a5',
          300: '#81c784',
          400: '#66bb6a',
          500: '#2d7d32',  // 健康色：深绿色
          600: '#2e7d32',
          700: '#1b5e20',
          800: '#1b5e20',
          900: '#0d4f14',
          excellent: '#2d7d32', // 优秀：深绿色
          good: '#388e3c',      // 良好：中绿色
          normal: '#fbc02d',    // 正常：深黄色
          warning: '#f57c00',   // 警告：深橙色
          danger: '#c62828',    // 危险：深红色
        },

        // 强调色 - 深橙色，用于重要提醒
        accent: {
          50: '#fff3e0',
          100: '#ffe0b2',
          200: '#ffcc80',
          300: '#ffb74d',
          400: '#ffa726',
          500: '#d84315',  // 强调色：深橙色
          600: '#bf360c',
          700: '#a6300c',
          800: '#8d2a0a',
          900: '#742408',
          DEFAULT: '#d84315',
          hover: '#bf360c',
        },

        // 中性色系 - 浅色主题优先
        neutral: {
          50: '#ffffff',    // 纯白色
          100: '#f8f9fa',   // 极浅灰
          200: '#f1f3f4',   // 浅灰
          300: '#e9ecef',   // 轻边框
          400: '#dee2e6',   // 边框
          500: '#6c757d',   // 辅助文字
          600: '#495057',   // 次要文字
          700: '#343a40',   // 主要文字
          800: '#212529',   // 深黑色
          900: '#000000',   // 纯黑色
        },

        // 语义化颜色 - 确保对比度
        text: {
          primary: '#212529',   // 主文字：深黑色 (对比度 16.0:1)
          secondary: '#495057', // 次文字：深灰色 (对比度 9.5:1)
          muted: '#6c757d',     // 辅助文字：中灰色 (对比度 5.8:1)
          disabled: '#adb5bd',  // 禁用文字：浅灰色
        },

        // 背景色系 - 浅色为主
        background: {
          DEFAULT: '#ffffff',   // 主背景：纯白色
          alt: '#f8f9fa',      // 次背景：极浅灰
          surface: '#f1f3f4',  // 卡片背景：浅灰
          elevated: '#ffffff', // 悬浮背景：纯白色
        },

        // 边框色系
        border: {
          light: '#e9ecef',    // 轻边框：更浅灰色
          DEFAULT: '#dee2e6',  // 默认边框：浅灰色
          strong: '#adb5bd',   // 强边框：中灰色
        },

        // 功能色 - 深色确保可读性
        success: '#2d7d32',   // 成功：深绿色
        warning: '#f57c00',   // 警告：深橙色
        error: '#c62828',     // 错误：深红色
        info: '#1976d2',      // 信息：深蓝色
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'monospace'],
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1.2' }],
        '6xl': ['3.75rem', { lineHeight: '1.1' }],
      },

      borderRadius: {
        'sm': '4px',
        'DEFAULT': '8px',
        'md': '8px',
        'lg': '12px',
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
        'full': '9999px',
      },

      boxShadow: {
        // 简化阴影系统，优先使用边框
        'none': 'none',
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'DEFAULT': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        // 移除复杂的发光效果
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        // 简化动画系统，保持专业感
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'slide-up': 'slideUp 0.3s ease-out forwards',
        'slide-down': 'slideDown 0.3s ease-out forwards',
        'shimmer': 'shimmer 1.5s infinite linear',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce': 'bounce 1s infinite',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { 'background-position': '-200% 0' },
          '100%': { 'background-position': '200% 0' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        bounce: {
          '0%, 100%': {
            transform: 'translateY(-25%)',
            'animation-timing-function': 'cubic-bezier(0.8, 0, 1, 1)',
          },
          '50%': {
            transform: 'translateY(0)',
            'animation-timing-function': 'cubic-bezier(0, 0, 0.2, 1)',
          },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      transitionDuration: {
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
        '700': '700ms',
        '1000': '1000ms',
      },
      transitionTimingFunction: {
        'in': 'cubic-bezier(0.4, 0, 1, 1)',
        'out': 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      // 移除渐变背景，使用纯色
      backgroundImage: {
        'none': 'none',
      },
    }
  },
  plugins: [],
}


