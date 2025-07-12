<template>
  <div 
    v-motion-bounce-visible
    class="pulse-container"
    :class="[`size-${size}`, `theme-${theme}`]"
  >
    <div class="pulse-dot">
      <div class="pulse-ring"></div>
      <div class="pulse-ring ring-2"></div>
      <div class="pulse-ring ring-3"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  theme: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger'].includes(value)
  }
})
</script>

<style scoped>
.pulse-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.pulse-dot {
  position: relative;
  border-radius: 50%;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.pulse-ring.ring-2 {
  animation-delay: 0.3s;
}

.pulse-ring.ring-3 {
  animation-delay: 0.6s;
}

/* 尺寸变体 */
.size-sm .pulse-dot,
.size-sm .pulse-ring {
  @apply w-2 h-2;
}

.size-md .pulse-dot,
.size-md .pulse-ring {
  @apply w-3 h-3;
}

.size-lg .pulse-dot,
.size-lg .pulse-ring {
  @apply w-4 h-4;
}

/* 主题变体 */
.theme-primary .pulse-dot {
  background-image: linear-gradient(135deg, #e0e7ff, #a78bfa, #8b5cf6, #6366f1);
}

.theme-primary .pulse-ring {
  border: 2px solid #6366f1;
}

.theme-success .pulse-dot {
  @apply bg-emerald-500;
}

.theme-success .pulse-ring {
  border: 2px solid theme('colors.emerald.500');
}

.theme-warning .pulse-dot {
  @apply bg-amber-500;
}

.theme-warning .pulse-ring {
  border: 2px solid theme('colors.amber.500');
}

.theme-danger .pulse-dot {
  @apply bg-red-500;
}

.theme-danger .pulse-ring {
  border: 2px solid theme('colors.red.500');
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(0.9);
    opacity: 1;
  }
  70% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(2.2);
    opacity: 0;
  }
}
</style>