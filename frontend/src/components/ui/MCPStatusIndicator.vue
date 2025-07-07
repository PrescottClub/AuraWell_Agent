<template>
  <div 
    v-motion-slide-right="{
      initial: { x: -50, opacity: 0 },
      visible: { 
        x: 0, 
        opacity: 1,
        transition: {
          delay: 200,
          duration: 500
        }
      }
    }"
    class="mcp-status-indicator"
    :class="[`status-${status}`, `size-${size}`]"
  >
    <!-- MCP 服务器状态图标 -->
    <div class="mcp-icon-container">
      <div class="mcp-main-icon">
        <div class="server-icon">
          <div class="server-rack"></div>
          <div class="server-rack"></div>
          <div class="server-rack"></div>
        </div>
      </div>
      
      <!-- 连接线动画 -->
      <div class="connection-lines">
        <div class="line line-1"></div>
        <div class="line line-2"></div>
        <div class="line line-3"></div>
      </div>
      
      <!-- 状态指示灯 -->
      <PulsingDot 
        :theme="statusTheme" 
        :size="size === 'large' ? 'lg' : 'md'"
        class="status-dot"
      />
    </div>
    
    <!-- 状态文本 -->
    <div class="status-content">
      <div class="status-title">
        {{ title }}
      </div>
      <div class="status-description">
        {{ description }}
      </div>
      
      <!-- MCP 工具列表 -->
      <div v-if="mcpTools.length > 0" class="mcp-tools">
        <div 
          v-for="(tool, index) in mcpTools"
          :key="tool.name"
          v-motion-fade-visible="{
            initial: { opacity: 0, y: 10 },
            visible: { 
              opacity: 1, 
              y: 0,
              transition: {
                delay: 100 * index,
                duration: 300
              }
            }
          }"
          class="tool-item"
          :class="{ 'tool-active': tool.active }"
        >
          <div class="tool-icon">{{ tool.icon }}</div>
          <span class="tool-name">{{ tool.name }}</span>
          <div class="tool-status">
            <div v-if="tool.active" class="status-spinner"></div>
            <div v-else-if="tool.completed" class="status-check">✓</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import PulsingDot from './PulsingDot.vue'
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'idle',
    validator: (value) => ['idle', 'connecting', 'active', 'error', 'success'].includes(value)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  title: {
    type: String,
    default: 'MCP 智能助手'
  },
  description: {
    type: String,
    default: '多服务器协同工作中...'
  },
  mcpTools: {
    type: Array,
    default: () => []
  }
})

const statusTheme = computed(() => {
  const themeMap = {
    idle: 'primary',
    connecting: 'warning',
    active: 'primary',
    error: 'danger',
    success: 'success'
  }
  return themeMap[props.status] || 'primary'
})
</script>

<style scoped>
.mcp-status-indicator {
  @apply flex items-start space-x-4 p-4 bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700;
}

.mcp-icon-container {
  @apply relative flex-shrink-0;
}

.mcp-main-icon {
  @apply relative;
}

.server-icon {
  @apply w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex flex-col justify-center items-center space-y-1 p-2;
}

.server-rack {
  @apply w-full h-1 bg-white/30 rounded-sm;
  animation: serverActivity 2s ease-in-out infinite;
}

.server-rack:nth-child(2) {
  animation-delay: 0.3s;
}

.server-rack:nth-child(3) {
  animation-delay: 0.6s;
}

.connection-lines {
  @apply absolute -right-2 top-1/2 transform -translate-y-1/2;
}

.line {
  @apply w-6 h-0.5 bg-gradient-to-r from-blue-500 to-transparent rounded-full mb-1;
  animation: dataFlow 1.5s ease-in-out infinite;
}

.line-2 {
  animation-delay: 0.2s;
}

.line-3 {
  animation-delay: 0.4s;
}

.status-dot {
  @apply absolute -top-1 -right-1;
}

.status-content {
  @apply flex-1 min-w-0;
}

.status-title {
  @apply font-semibold text-gray-900 dark:text-white text-sm;
}

.status-description {
  @apply text-xs text-gray-600 dark:text-gray-400 mt-1;
}

.mcp-tools {
  @apply mt-3 space-y-2;
}

.tool-item {
  @apply flex items-center space-x-2 text-xs px-2 py-1 rounded-lg bg-gray-50 dark:bg-gray-700/50 transition-all duration-200;
}

.tool-item.tool-active {
  @apply bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700;
}

.tool-icon {
  @apply text-sm;
}

.tool-name {
  @apply flex-1 text-gray-700 dark:text-gray-300;
}

.tool-status {
  @apply flex items-center;
}

.status-spinner {
  @apply w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin;
}

.status-check {
  @apply text-green-500 font-bold;
}

/* 不同状态的样式 */
.status-connecting .server-icon {
  @apply animate-pulse;
}

.status-active .server-icon {
  animation: glow 2s ease-in-out infinite alternate;
}

.status-error .server-icon {
  @apply from-red-500 to-red-600;
}

.status-success .server-icon {
  @apply from-green-500 to-green-600;
}

/* 尺寸变体 */
.size-small {
  @apply p-3;
}

.size-small .server-icon {
  @apply w-8 h-8;
}

.size-large {
  @apply p-6;
}

.size-large .server-icon {
  @apply w-16 h-16;
}

@keyframes serverActivity {
  0%, 100% {
    opacity: 0.3;
    transform: scaleX(0.8);
  }
  50% {
    opacity: 1;
    transform: scaleX(1);
  }
}

@keyframes dataFlow {
  0% {
    opacity: 0;
    transform: translateX(-10px);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateX(10px);
  }
}

@keyframes glow {
  0% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.8), 0 0 30px rgba(59, 130, 246, 0.4);
  }
}
</style>