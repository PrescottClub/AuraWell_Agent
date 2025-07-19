<!--
  AuraWell 加载状态组件
  提供多种专业的加载动画和骨架屏效果
-->

<template>
  <div class="loading-container">
    <!-- 基础加载点 -->
    <div v-if="type === 'dots'" class="loading-dots">
      <div></div>
      <div></div>
      <div></div>
    </div>

    <!-- 脉冲加载 -->
    <div v-else-if="type === 'pulse'" class="loading-pulse">
      <div class="pulse-circle"></div>
    </div>

    <!-- 健康心跳动画 -->
    <div v-else-if="type === 'heartbeat'" class="loading-heartbeat">
      <svg class="heartbeat-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
      </svg>
    </div>

    <!-- 数据流动画 -->
    <div v-else-if="type === 'dataflow'" class="loading-dataflow">
      <div class="dataflow-line"></div>
      <div class="dataflow-line" style="animation-delay: 0.2s;"></div>
      <div class="dataflow-line" style="animation-delay: 0.4s;"></div>
    </div>

    <!-- 旋转加载 -->
    <div v-else-if="type === 'spinner'" class="loading-spinner">
      <div class="spinner-ring"></div>
    </div>

    <!-- 骨架屏 - 卡片 -->
    <div v-else-if="type === 'skeleton-card'" class="skeleton-card">
      <div class="skeleton skeleton-avatar"></div>
      <div class="skeleton-content">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text"></div>
        <div class="skeleton skeleton-text short"></div>
      </div>
    </div>

    <!-- 骨架屏 - 列表 -->
    <div v-else-if="type === 'skeleton-list'" class="skeleton-list">
      <div v-for="i in count" :key="i" class="skeleton-list-item">
        <div class="skeleton skeleton-avatar small"></div>
        <div class="skeleton-content">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-text"></div>
        </div>
      </div>
    </div>

    <!-- 骨架屏 - 图表 -->
    <div v-else-if="type === 'skeleton-chart'" class="skeleton-chart">
      <div class="skeleton-chart-header">
        <div class="skeleton skeleton-title"></div>
        <div class="skeleton skeleton-text short"></div>
      </div>
      <div class="skeleton-chart-body">
        <div class="skeleton-bars">
          <div v-for="i in 6" :key="i" class="skeleton-bar" :style="{ height: `${Math.random() * 60 + 20}%` }"></div>
        </div>
      </div>
    </div>

    <!-- 加载文字 -->
    <div v-if="text && type !== 'skeleton-card' && type !== 'skeleton-list' && type !== 'skeleton-chart'" class="loading-text">
      {{ text }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'dots',
    validator: (value) => [
      'dots', 'pulse', 'heartbeat', 'dataflow', 'spinner',
      'skeleton-card', 'skeleton-list', 'skeleton-chart'
    ].includes(value)
  },
  text: {
    type: String,
    default: ''
  },
  count: {
    type: Number,
    default: 3
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

/* 基础加载点 */
.loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.loading-dots > div {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: loadingPulse 1.4s infinite ease-in-out both;
}

.loading-dots > div:nth-child(1) { animation-delay: -0.32s; }
.loading-dots > div:nth-child(2) { animation-delay: -0.16s; }
.loading-dots > div:nth-child(3) { animation-delay: 0s; }

@keyframes loadingPulse {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 脉冲加载 */
.loading-pulse {
  position: relative;
  width: 40px;
  height: 40px;
}

.pulse-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: var(--color-primary);
  animation: pulseScale 1.5s infinite ease-in-out;
}

.pulse-circle::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: var(--color-primary);
  opacity: 0.6;
  animation: pulseScale 1.5s infinite ease-in-out;
  animation-delay: -0.4s;
}

@keyframes pulseScale {
  0%, 100% {
    transform: scale(0);
    opacity: 1;
  }
  50% {
    transform: scale(1);
    opacity: 0;
  }
}

/* 健康心跳动画 */
.loading-heartbeat {
  color: var(--color-health);
}

.heartbeat-icon {
  width: 32px;
  height: 32px;
  animation: heartbeat 1.5s infinite ease-in-out;
}

@keyframes heartbeat {
  0%, 100% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.2);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.2);
  }
  70% {
    transform: scale(1);
  }
}

/* 数据流动画 */
.loading-dataflow {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 60px;
}

.dataflow-line {
  height: 3px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-primary),
    transparent
  );
  animation: dataFlow 2s infinite ease-in-out;
}

@keyframes dataFlow {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 旋转加载 */
.loading-spinner {
  width: 32px;
  height: 32px;
}

.spinner-ring {
  width: 100%;
  height: 100%;
  border: 3px solid var(--color-border-light);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 骨架屏基础样式 */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-neutral-200) 25%,
    var(--color-neutral-100) 50%,
    var(--color-neutral-200) 75%
  );
  background-size: 200% 100%;
  animation: skeletonLoading 1.5s infinite ease-in-out;
  border-radius: 4px;
}

@keyframes skeletonLoading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 骨架屏 - 卡片 */
.skeleton-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  width: 100%;
  max-width: 400px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-avatar.small {
  width: 32px;
  height: 32px;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-title {
  height: 20px;
  width: 60%;
}

.skeleton-text {
  height: 16px;
  width: 100%;
}

.skeleton-text.short {
  width: 40%;
}

/* 骨架屏 - 列表 */
.skeleton-list {
  width: 100%;
  max-width: 400px;
}

.skeleton-list-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.skeleton-list-item:last-child {
  border-bottom: none;
}

/* 骨架屏 - 图表 */
.skeleton-chart {
  width: 100%;
  max-width: 500px;
  padding: 16px;
}

.skeleton-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.skeleton-chart-body {
  height: 200px;
  display: flex;
  align-items: end;
  justify-content: center;
}

.skeleton-bars {
  display: flex;
  align-items: end;
  gap: 8px;
  height: 100%;
  width: 80%;
}

.skeleton-bar {
  flex: 1;
  background: var(--color-neutral-200);
  border-radius: 2px;
  animation: skeletonLoading 1.5s infinite ease-in-out;
}

/* 加载文字 */
.loading-text {
  color: var(--color-text-secondary);
  font-size: 14px;
  text-align: center;
}

/* 尺寸变体 */
.loading-container.small .loading-dots > div {
  width: 6px;
  height: 6px;
}

.loading-container.small .heartbeat-icon {
  width: 24px;
  height: 24px;
}

.loading-container.large .loading-dots > div {
  width: 12px;
  height: 12px;
}

.loading-container.large .heartbeat-icon {
  width: 48px;
  height: 48px;
}
</style>
