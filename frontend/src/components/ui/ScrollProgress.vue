<!--
  AuraWell 滚动进度指示器
  提供优雅的页面滚动进度反馈
-->

<template>
  <div v-if="show" class="scroll-progress-container">
    <!-- 顶部进度条 -->
    <div 
      v-if="type === 'bar'" 
      class="scroll-progress-bar"
      :style="{ 
        transform: `scaleX(${progress / 100})`,
        background: gradientBackground 
      }"
    ></div>

    <!-- 圆形进度指示器 -->
    <div 
      v-else-if="type === 'circle'" 
      class="scroll-progress-circle"
      :class="{ 'scroll-progress-circle--visible': progress > 5 }"
    >
      <svg class="progress-ring" width="60" height="60">
        <circle
          class="progress-ring-background"
          cx="30"
          cy="30"
          r="26"
          fill="transparent"
          stroke="var(--color-border-light)"
          stroke-width="3"
        />
        <circle
          class="progress-ring-progress"
          cx="30"
          cy="30"
          r="26"
          fill="transparent"
          :stroke="circleColor"
          stroke-width="3"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="strokeDashoffset"
          transform="rotate(-90 30 30)"
        />
      </svg>
      
      <!-- 中心图标 -->
      <div class="progress-icon">
        <svg v-if="progress < 100" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
        </svg>
      </div>
    </div>

    <!-- 数字进度指示器 -->
    <div 
      v-else-if="type === 'number'" 
      class="scroll-progress-number"
      :class="{ 'scroll-progress-number--visible': progress > 5 }"
    >
      <div class="progress-percentage">{{ Math.round(progress) }}%</div>
      <div class="progress-label">阅读进度</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'circle', 'number'].includes(value)
  },
  show: {
    type: Boolean,
    default: true
  },
  threshold: {
    type: Number,
    default: 100
  },
  color: {
    type: String,
    default: 'primary'
  },
  gradient: {
    type: Boolean,
    default: true
  }
})

const progress = ref(0)

// 计算属性
const circumference = computed(() => 2 * Math.PI * 26)

const strokeDashoffset = computed(() => {
  return circumference.value - (progress.value / 100) * circumference.value
})

const gradientBackground = computed(() => {
  if (!props.gradient) {
    return `var(--color-${props.color})`
  }
  
  return 'linear-gradient(90deg, var(--color-primary), var(--color-health))'
})

const circleColor = computed(() => {
  if (props.gradient) {
    return 'url(#progressGradient)'
  }
  return `var(--color-${props.color})`
})

// 滚动处理
const updateProgress = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  
  if (scrollHeight <= 0) {
    progress.value = 0
    return
  }
  
  const scrollProgress = (scrollTop / scrollHeight) * 100
  progress.value = Math.min(Math.max(scrollProgress, 0), 100)
}

// 平滑滚动到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 平滑滚动到底部
const scrollToBottom = () => {
  window.scrollTo({
    top: document.documentElement.scrollHeight,
    behavior: 'smooth'
  })
}

// 生命周期
onMounted(() => {
  window.addEventListener('scroll', updateProgress, { passive: true })
  window.addEventListener('resize', updateProgress, { passive: true })
  updateProgress()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
  window.removeEventListener('resize', updateProgress)
})

// 暴露方法给父组件
defineExpose({
  scrollToTop,
  scrollToBottom,
  progress: progress.value
})
</script>

<style scoped>
.scroll-progress-container {
  position: fixed;
  z-index: var(--z-index-fixed);
  pointer-events: none;
}

/* 顶部进度条 */
.scroll-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform-origin: left;
  transition: transform 0.1s ease-out;
  pointer-events: none;
}

/* 圆形进度指示器 */
.scroll-progress-circle {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 60px;
  height: 60px;
  background: var(--color-background);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: auto;
  opacity: 0;
  transform: scale(0.8) translateY(20px);
  transition: all var(--duration-base) var(--ease-out);
}

.scroll-progress-circle--visible {
  opacity: 1;
  transform: scale(1) translateY(0);
}

.scroll-progress-circle:hover {
  transform: scale(1.05) translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.progress-ring {
  position: absolute;
  top: 0;
  left: 0;
  transform: rotate(-90deg);
}

.progress-ring-progress {
  transition: stroke-dashoffset 0.1s ease-out;
}

.progress-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--color-primary);
  transition: all var(--duration-base) var(--ease-out);
}

.scroll-progress-circle:hover .progress-icon {
  transform: translate(-50%, -50%) scale(1.1);
}

/* 数字进度指示器 */
.scroll-progress-number {
  position: fixed;
  bottom: 32px;
  right: 32px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  pointer-events: auto;
  opacity: 0;
  transform: translateY(20px);
  transition: all var(--duration-base) var(--ease-out);
  text-align: center;
  min-width: 80px;
}

.scroll-progress-number--visible {
  opacity: 1;
  transform: translateY(0);
}

.scroll-progress-number:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.progress-percentage {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-primary);
  line-height: 1;
}

.progress-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  line-height: 1;
}

/* 渐变定义 */
.scroll-progress-circle svg defs {
  position: absolute;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .scroll-progress-circle,
  .scroll-progress-number {
    bottom: 20px;
    right: 20px;
  }
  
  .scroll-progress-circle {
    width: 50px;
    height: 50px;
  }
  
  .progress-ring {
    width: 50px;
    height: 50px;
  }
  
  .progress-ring circle {
    cx: 25;
    cy: 25;
    r: 22;
  }
  
  .progress-icon svg {
    width: 16px;
    height: 16px;
  }
}

/* 可访问性 */
@media (prefers-reduced-motion: reduce) {
  .scroll-progress-bar,
  .progress-ring-progress {
    transition: none !important;
  }
  
  .scroll-progress-circle,
  .scroll-progress-number {
    transition: opacity var(--duration-fast) ease !important;
  }
  
  .scroll-progress-circle:hover,
  .scroll-progress-number:hover {
    transform: none !important;
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .scroll-progress-circle,
  .scroll-progress-number {
    border: 2px solid var(--color-text-primary);
  }
  
  .progress-ring-background {
    stroke: var(--color-text-primary);
    stroke-width: 2;
  }
}
</style>
