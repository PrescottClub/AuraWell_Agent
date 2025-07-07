<template>
  <div 
    v-motion-bounce-visible="{
      initial: { scale: 0, opacity: 0 },
      visible: { 
        scale: 1, 
        opacity: 1,
        transition: {
          type: 'spring',
          stiffness: 350,
          damping: 20
        }
      }
    }"
    class="loading-indicator" 
    :class="[`size-${size}`, `type-${type}`]"
  >
    <!-- MCP工具加载状态 -->
    <div v-if="type === 'mcp'" class="mcp-loading">
      <div class="loading-icon">
        <div class="mcp-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
      </div>
      <div class="loading-content">
        <div class="loading-title">{{ title || 'MCP 智能助手工作中' }}</div>
        <div class="loading-text">{{ text || '正在调用多个 MCP 服务器进行协同分析...' }}</div>
        <div class="loading-tools" v-if="activeTools && activeTools.length > 0">
          <span 
            v-for="tool in activeTools" 
            :key="tool"
            class="active-tool"
          >
            {{ getToolDisplayName(tool) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 数据分析加载状态 -->
    <div v-else-if="type === 'analysis'" class="analysis-loading">
      <div class="analysis-icon">
        <div class="data-bars">
          <div class="bar" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></div>
        </div>
      </div>
      <div class="loading-content">
        <div class="loading-title">{{ title || '数据分析中' }}</div>
        <div class="loading-text">{{ text || '正在处理您的健康数据，生成个性化分析...' }}</div>
      </div>
    </div>

    <!-- 搜索加载状态 -->
    <div v-else-if="type === 'search'" class="search-loading">
      <div class="search-icon">
        <div class="search-pulse"></div>
      </div>
      <div class="loading-content">
        <div class="loading-title">{{ title || '智能搜索中' }}</div>
        <div class="loading-text">{{ text || '正在搜索最新健康科研信息...' }}</div>
      </div>
    </div>

    <!-- 默认加载状态 -->
    <div v-else class="default-loading">
      <div class="default-spinner"></div>
      <div v-if="text" class="loading-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default', // mcp, analysis, search, default
    validator: (value) => ['mcp', 'analysis', 'search', 'default'].includes(value)
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  activeTools: {
    type: Array,
    default: () => []
  }
})

const getToolDisplayName = (tool) => {
  const toolNames = {
    'database-sqlite': '数据库',
    'calculator': '计算器',
    'quickchart': '图表生成',
    'brave-search': '搜索引擎',
    'memory': '知识图谱',
    'sequential-thinking': '深度分析',
    'weather': '环境数据',
    'filesystem': '文件系统',
    'fetch': '数据抓取',
    'github': '代码仓库',
    'notion': '文档管理',
    'run-python': 'Python执行',
    'time': '时间工具'
  }
  return toolNames[tool] || tool
}
</script>

<style scoped>
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--color-bg-base);
  border-radius: var(--border-radius-card);
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border-color-base);
}

/* 尺寸变体 */
.size-small {
  padding: 12px;
  gap: 12px;
}

.size-large {
  padding: 24px;
  gap: 20px;
}

/* MCP 加载样式 */
.mcp-loading {
  display: flex;
  align-items: center;
  gap: 16px;
}

.loading-icon {
  flex-shrink: 0;
}

.mcp-spinner {
  position: relative;
  width: 40px;
  height: 40px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: mcpSpin 1.2s linear infinite;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.4s;
  transform: scale(0.8);
  border-top-color: theme('colors.gemini.blue');
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.8s;
  transform: scale(0.6);
  border-top-color: theme('colors.gemini.purple');
}

.loading-content {
  flex: 1;
}

.loading-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--color-text-base);
  margin-bottom: 4px;
}

.loading-text {
  font-size: 12px;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.loading-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.active-tool {
  background: var(--color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  animation: toolPulse 2s infinite;
}

/* 数据分析加载样式 */
.analysis-loading {
  display: flex;
  align-items: center;
  gap: 16px;
}

.analysis-icon {
  flex-shrink: 0;
}

.data-bars {
  display: flex;
  align-items: end;
  gap: 3px;
  height: 32px;
}

.bar {
  width: 4px;
  background: linear-gradient(135deg, theme('colors.gemini.blue') 0%, theme('colors.gemini.purple') 100%);
  border-radius: 2px;
  animation: dataBar 1.5s infinite ease-in-out;
}

/* 搜索加载样式 */
.search-loading {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-icon {
  flex-shrink: 0;
}

.search-pulse {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: searchPulse 1.5s infinite;
}

/* 默认加载样式 */
.default-loading {
  display: flex;
  align-items: center;
  gap: 12px;
}

.default-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color-base);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 动画定义 */
@keyframes mcpSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes toolPulse {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(0.95);
  }
}

@keyframes dataBar {
  0%, 100% { 
    height: 8px; 
    opacity: 0.6; 
  }
  50% { 
    height: 24px; 
    opacity: 1; 
  }
}

@keyframes searchPulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 小尺寸调整 */
.size-small .mcp-spinner {
  width: 24px;
  height: 24px;
}

.size-small .loading-title {
  font-size: 12px;
}

.size-small .loading-text {
  font-size: 11px;
}

.size-small .data-bars {
  height: 20px;
}

.size-small .search-pulse {
  width: 20px;
  height: 20px;
}

/* 大尺寸调整 */
.size-large .mcp-spinner {
  width: 48px;
  height: 48px;
}

.size-large .loading-title {
  font-size: 16px;
}

.size-large .loading-text {
  font-size: 14px;
}

.size-large .data-bars {
  height: 40px;
}

.size-large .search-pulse {
  width: 40px;
  height: 40px;
}

/* 深色模式优化 */
.dark .loading-indicator {
  background: var(--color-bg-muted);
  border-color: var(--border-color-muted);
}

.dark .active-tool {
  background: theme('colors.gemini.purple');
}

/* 响应式优化 */
@media (max-width: 640px) {
  .loading-indicator {
    padding: 16px;
    gap: 12px;
  }

  .loading-tools {
    gap: 4px;
  }

  .active-tool {
    font-size: 9px;
    padding: 1px 6px;
  }
}
</style>