<template>
  <div class="loading-indicator" :class="loadingClass">
    <!-- 默认加载动画 -->
    <div v-if="type === 'default'" class="loading-default">
      <div class="spinner"></div>
      <span v-if="text" class="loading-text">{{ text }}</span>
    </div>

    <!-- MCP工具加载动画 -->
    <div v-else-if="type === 'mcp'" class="loading-mcp">
      <div class="mcp-spinner">
        <div class="mcp-circle" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></div>
      </div>
      <span class="loading-text">{{ text || 'AI正在分析中...' }}</span>
    </div>

    <!-- 图表加载动画 -->
    <div v-else-if="type === 'chart'" class="loading-chart">
      <div class="chart-placeholder">
        <div class="chart-bars">
          <div class="bar" v-for="i in 5" :key="i" :style="{ animationDelay: `${i * 0.1}s` }"></div>
        </div>
      </div>
      <span class="loading-text">{{ text || '图表生成中...' }}</span>
    </div>

    <!-- 数据计算加载动画 -->
    <div v-else-if="type === 'calculation'" class="loading-calculation">
      <div class="calculation-spinner">
        <div class="calc-icon">🧮</div>
        <div class="calc-waves">
          <div class="wave" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.2}s` }"></div>
        </div>
      </div>
      <span class="loading-text">{{ text || '数据计算中...' }}</span>
    </div>

    <!-- 搜索研究加载动画 -->
    <div v-else-if="type === 'research'" class="loading-research">
      <div class="research-spinner">
        <div class="research-icon">🔍</div>
        <div class="search-dots">
          <div class="dot" v-for="i in 3" :key="i" :style="{ animationDelay: `${i * 0.3}s` }"></div>
        </div>
      </div>
      <span class="loading-text">{{ text || '搜索科学研究中...' }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'mcp', 'chart', 'calculation', 'research'].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

const loadingClass = computed(() => ({
  [`loading-${props.size}`]: true
}))
</script>

<style scoped>
.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loading-text {
  margin-top: 12px;
  font-size: 14px;
  color: #666;
  text-align: center;
}

/* 尺寸变体 */
.loading-small {
  padding: 10px;
}

.loading-small .loading-text {
  font-size: 12px;
  margin-top: 8px;
}

.loading-large {
  padding: 40px;
}

.loading-large .loading-text {
  font-size: 16px;
  margin-top: 16px;
}

/* 默认加载动画 */
.loading-default {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* MCP工具加载动画 */
.loading-mcp {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mcp-spinner {
  display: flex;
  gap: 8px;
}

.mcp-circle {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: mcpBounce 1.4s ease-in-out infinite both;
}

@keyframes mcpBounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 图表加载动画 */
.loading-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-placeholder {
  width: 120px;
  height: 80px;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: end;
  justify-content: center;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 4px;
  height: 100%;
}

.bar {
  width: 12px;
  background: #1890ff;
  border-radius: 2px;
  animation: chartGrow 1.5s ease-in-out infinite;
}

.bar:nth-child(1) { height: 20%; }
.bar:nth-child(2) { height: 40%; }
.bar:nth-child(3) { height: 60%; }
.bar:nth-child(4) { height: 80%; }
.bar:nth-child(5) { height: 35%; }

@keyframes chartGrow {
  0%, 100% {
    transform: scaleY(1);
    opacity: 0.7;
  }
  50% {
    transform: scaleY(1.3);
    opacity: 1;
  }
}

/* 数据计算加载动画 */
.loading-calculation {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.calculation-spinner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.calc-icon {
  font-size: 32px;
  animation: calcPulse 2s ease-in-out infinite;
}

.calc-waves {
  position: absolute;
  width: 60px;
  height: 60px;
}

.wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid #52c41a;
  border-radius: 50%;
  opacity: 0;
  animation: waveExpand 2s ease-out infinite;
}

@keyframes calcPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes waveExpand {
  0% {
    transform: scale(0.3);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

/* 搜索研究加载动画 */
.loading-research {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.research-spinner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.research-icon {
  font-size: 28px;
  animation: searchRotate 3s linear infinite;
}

.search-dots {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 4px;
  margin-left: 40px;
}

.dot {
  width: 6px;
  height: 6px;
  background: #faad14;
  border-radius: 50%;
  animation: dotBlink 1.5s ease-in-out infinite;
}

@keyframes searchRotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes dotBlink {
  0%, 80%, 100% {
    opacity: 0;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .loading-indicator {
    padding: 16px;
  }
  
  .calc-icon,
  .research-icon {
    font-size: 24px;
  }
  
  .chart-placeholder {
    width: 100px;
    height: 60px;
    padding: 12px;
  }
  
  .bar {
    width: 8px;
  }
}
</style> 