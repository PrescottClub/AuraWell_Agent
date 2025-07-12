<template>
  <div class="p-6 bg-white dark:bg-gray-800/50 rounded-2xl shadow-soft">
    <div class="flex items-start space-x-4">
      <div class="w-12 h-12 rounded-lg bg-gray-200 dark:bg-gray-700 animate-shimmer"></div>
      <div class="flex-1 space-y-3 pt-1">
        <div class="w-1/3 h-4 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
        <div class="w-1/2 h-5 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
      </div>
    </div>
    <div class="mt-6 space-y-3">
      <div class="w-3/4 h-8 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
      <div class="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
    </div>
  </div>
</template>

<script setup>
// 骨架屏不需要任何逻辑，只是视觉占位符
</script>

<style scoped>
/* 🌟 Canva风格Shimmer动画 - 珍珠白粉色光晕扫过 */
.animate-shimmer {
  background: linear-gradient(
    90deg,
    transparent 25%,
    rgba(253, 242, 248, 0.8) 50%, /* Pearl White Pink光晕 */
    transparent 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite ease-in-out;
}



@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 额外的骨架屏动画效果 */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>