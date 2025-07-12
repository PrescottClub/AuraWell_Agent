// src/composables/useTheme.js - 强制禁用深色模式
import { ref } from 'vue';

// 导出一个可复用的组合式函数 - 硬编码为浅色模式
export function useTheme() {
  const isDark = ref(false); // 硬编码为 false，永远不启用深色模式

  const toggleTheme = () => {
    console.log("Dark mode is temporarily disabled.");
  };

  // 确保 DOM 始终处于浅色模式
  document.documentElement.classList.remove('dark');

  return {
    isDark,
    toggleTheme,
  };
}
