module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  darkMode: 'media', // 根据系统偏好设置，但主要保持浅色主题
  theme: {
    extend: {
      colors: {
        // 核心品牌色 - 灵感源自Gemini Logo的渐变
        gemini: {
          blue: '#4285F4',
          purple: '#8A2BE2', // Updated from report for better contrast
          orange: '#FFA500',
        },
        // 主色调，用于按钮、链接等关键交互
        primary: {
          DEFAULT: '#1a73e8', // Google Blue
          hover: '#185abc',
        },
        // 辅助色，用于次要按钮或背景
        secondary: {
          DEFAULT: '#e8f0fe', // Light blue background for highlights
          hover: '#d2e3fc',
        },
        // 文本颜色
        text: {
          primary: '#202124',   // Near-black for titles
          secondary: '#5f6368', // Dark grey for body text
          disabled: '#80868b',  // Medium grey for subtitles/disabled
        },
        // 背景色
        background: {
          DEFAULT: '#ffffff', // Pure white
          alt: '#f8f9fa',     // Very light grey for cards
        },
        border: {
          DEFAULT: '#dadce0' // Subtle border for cards
        },
        // 功能色
        success: '#1e8e3e',
        warning: '#f9ab00',
        error: '#d93025',
        
        // 保持健康语义色以确保兼容性
        health: {
          excellent: '#30a14f', // 使用Apple绿色
          good: '#84cc16',
          normal: '#f59e0b',
          warning: '#f97316',
          danger: '#d92c2c' // 使用Apple红色
        },
      },
      fontFamily: {
        sans: ['Google Sans', 'Roboto', 'Inter', 'sans-serif'],
      },
      borderRadius: {
        'lg': '8px',
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
      },
      boxShadow: {
        // Remove complex shadows, prefer borders
        'none': 'none',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards',
        'shimmer': 'shimmer 1.5s infinite linear',
        'bounce-in': 'bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'scale-in': 'scaleIn 0.3s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'heart-beat': 'heartBeat 1.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { 'background-position': '-1000px 0' },
          '100%': { 'background-position': '1000px 0' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { 'box-shadow': '0 0 5px rgba(0, 148, 255, 0.2), 0 0 10px rgba(0, 148, 255, 0.2), 0 0 15px rgba(0, 148, 255, 0.2)' },
          '100%': { 'box-shadow': '0 0 10px rgba(0, 148, 255, 0.4), 0 0 20px rgba(0, 148, 255, 0.4), 0 0 30px rgba(0, 148, 255, 0.4)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(1deg)' },
          '75%': { transform: 'rotate(-1deg)' },
        },
        heartBeat: {
          '0%': { transform: 'scale(1)' },
          '14%': { transform: 'scale(1.05)' },
          '28%': { transform: 'scale(1)' },
          '42%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(1)' },
        },
      },
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
        '800': '800ms',
        '1200': '1200ms',
      },
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'elastic': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      backgroundImage: {
        'gemini-gradient': 'linear-gradient(135deg, #8A2BE2 0%, #4A5BF7 50%, #4285F4 100%)',
      },
    }
  },
  plugins: [],
}


