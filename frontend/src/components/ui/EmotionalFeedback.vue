<!--
  AuraWell 情感化反馈组件
  为健康数据提供有意义的情感化视觉反馈
-->

<template>
  <div class="emotional-feedback" :class="feedbackClasses">
    <!-- 健康状态表情 -->
    <div v-if="type === 'health-emoji'" class="health-emoji-container">
      <div class="emoji-face" :class="emojiClass">
        <div class="emoji-eyes">
          <div class="emoji-eye left"></div>
          <div class="emoji-eye right"></div>
        </div>
        <div class="emoji-mouth" :class="mouthClass"></div>
      </div>
      <div v-if="showLabel" class="emoji-label">{{ statusLabel }}</div>
    </div>

    <!-- 心率波形 -->
    <div v-else-if="type === 'heartbeat'" class="heartbeat-container">
      <svg class="heartbeat-wave" viewBox="0 0 200 60" preserveAspectRatio="none">
        <path
          :d="heartbeatPath"
          fill="none"
          :stroke="heartbeatColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
      <div v-if="showValue" class="heartbeat-value">{{ value }} BPM</div>
    </div>

    <!-- 能量条 -->
    <div v-else-if="type === 'energy-bar'" class="energy-bar-container">
      <div class="energy-bar-background">
        <div 
          class="energy-bar-fill"
          :style="{ 
            width: `${energyPercentage}%`,
            background: energyGradient 
          }"
        >
          <div class="energy-sparkles">
            <div v-for="i in sparkleCount" :key="i" class="sparkle" :style="getSparkleStyle(i)"></div>
          </div>
        </div>
      </div>
      <div v-if="showLabel" class="energy-label">能量值: {{ value }}%</div>
    </div>

    <!-- 睡眠云朵 -->
    <div v-else-if="type === 'sleep-cloud'" class="sleep-cloud-container">
      <div class="cloud-group">
        <div class="cloud cloud-1" :class="{ 'cloud--active': sleepQuality >= 60 }"></div>
        <div class="cloud cloud-2" :class="{ 'cloud--active': sleepQuality >= 80 }"></div>
        <div class="cloud cloud-3" :class="{ 'cloud--active': sleepQuality >= 90 }"></div>
      </div>
      <div class="sleep-stars">
        <div v-for="i in starCount" :key="i" class="star" :style="getStarStyle(i)"></div>
      </div>
      <div v-if="showLabel" class="sleep-label">睡眠质量: {{ sleepQualityText }}</div>
    </div>

    <!-- 步数足迹 -->
    <div v-else-if="type === 'step-trail'" class="step-trail-container">
      <div class="footprint-trail">
        <div v-for="i in footprintCount" :key="i" class="footprint" :style="getFootprintStyle(i)">
          👣
        </div>
      </div>
      <div v-if="showLabel" class="step-label">今日步数: {{ formatNumber(value) }}</div>
    </div>

    <!-- 水分波浪 -->
    <div v-else-if="type === 'hydration-wave'" class="hydration-container">
      <div class="water-container">
        <svg class="water-wave" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path
            :d="wavePath"
            :fill="waveColor"
            opacity="0.8"
          />
          <path
            :d="wavePath2"
            :fill="waveColor"
            opacity="0.6"
          />
        </svg>
      </div>
      <div v-if="showLabel" class="hydration-label">水分摄入: {{ value }}ml</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => [
      'health-emoji', 'heartbeat', 'energy-bar', 
      'sleep-cloud', 'step-trail', 'hydration-wave'
    ].includes(value)
  },
  value: {
    type: [Number, String],
    default: 0
  },
  status: {
    type: String,
    default: 'normal',
    validator: (value) => ['excellent', 'good', 'normal', 'warning', 'danger'].includes(value)
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  showValue: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  }
})

// 动画时间偏移
const animationOffset = ref(0)

// 计算属性
const feedbackClasses = computed(() => [
  `feedback--${props.type}`,
  `feedback--${props.status}`,
  { 'feedback--animated': props.animated }
])

// 健康表情相关
const emojiClass = computed(() => `emoji--${props.status}`)
const mouthClass = computed(() => `mouth--${props.status}`)

const statusLabel = computed(() => {
  const labels = {
    excellent: '优秀',
    good: '良好', 
    normal: '正常',
    warning: '注意',
    danger: '危险'
  }
  return labels[props.status] || '正常'
})

// 心率波形
const heartbeatColor = computed(() => {
  const colors = {
    excellent: 'var(--color-health-excellent)',
    good: 'var(--color-health-good)',
    normal: 'var(--color-health-normal)',
    warning: 'var(--color-health-warning)',
    danger: 'var(--color-health-danger)'
  }
  return colors[props.status] || colors.normal
})

const heartbeatPath = computed(() => {
  const baseY = 30
  const amplitude = props.status === 'danger' ? 20 : props.status === 'excellent' ? 15 : 10
  
  return `M0,${baseY} L40,${baseY} L50,${baseY - amplitude} L60,${baseY + amplitude} L70,${baseY} L200,${baseY}`
})

// 能量条
const energyPercentage = computed(() => Math.min(Math.max(props.value, 0), 100))

const energyGradient = computed(() => {
  if (energyPercentage.value >= 80) {
    return 'linear-gradient(90deg, var(--color-health-excellent), var(--color-health-good))'
  } else if (energyPercentage.value >= 60) {
    return 'linear-gradient(90deg, var(--color-health-good), var(--color-health-normal))'
  } else if (energyPercentage.value >= 40) {
    return 'linear-gradient(90deg, var(--color-health-normal), var(--color-health-warning))'
  } else {
    return 'linear-gradient(90deg, var(--color-health-warning), var(--color-health-danger))'
  }
})

const sparkleCount = computed(() => Math.floor(energyPercentage.value / 20))

// 睡眠质量
const sleepQuality = computed(() => {
  if (typeof props.value === 'number') return props.value
  return 75 // 默认值
})

const sleepQualityText = computed(() => {
  if (sleepQuality.value >= 90) return '极佳'
  if (sleepQuality.value >= 80) return '良好'
  if (sleepQuality.value >= 70) return '一般'
  if (sleepQuality.value >= 60) return '较差'
  return '很差'
})

const starCount = computed(() => Math.floor(sleepQuality.value / 20))

// 步数足迹
const footprintCount = computed(() => Math.min(Math.floor(props.value / 2000), 10))

// 水分波浪
const wavePath = computed(() => {
  const level = 100 - (props.value / 2000) * 100 // 假设2000ml为满值
  const wave = Math.sin(animationOffset.value) * 3
  
  return `M0,${level + wave} Q25,${level + wave - 5} 50,${level + wave} T100,${level + wave} L100,100 L0,100 Z`
})

const wavePath2 = computed(() => {
  const level = 100 - (props.value / 2000) * 100
  const wave = Math.sin(animationOffset.value + Math.PI / 3) * 2
  
  return `M0,${level + wave + 3} Q25,${level + wave - 2} 50,${level + wave + 3} T100,${level + wave + 3} L100,100 L0,100 Z`
})

const waveColor = computed(() => {
  if (props.value >= 1600) return 'var(--color-health-excellent)'
  if (props.value >= 1200) return 'var(--color-health-good)'
  if (props.value >= 800) return 'var(--color-health-normal)'
  if (props.value >= 400) return 'var(--color-health-warning)'
  return 'var(--color-health-danger)'
})

// 工具函数
const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const getSparkleStyle = (index) => {
  return {
    left: `${Math.random() * 80 + 10}%`,
    animationDelay: `${index * 0.2}s`
  }
}

const getStarStyle = (index) => {
  return {
    left: `${Math.random() * 80 + 10}%`,
    top: `${Math.random() * 40 + 10}%`,
    animationDelay: `${index * 0.3}s`
  }
}

const getFootprintStyle = (index) => {
  return {
    left: `${(index / footprintCount.value) * 80 + 10}%`,
    animationDelay: `${index * 0.1}s`,
    transform: `rotate(${(index % 2) * 15 - 7.5}deg)`
  }
}

// 动画循环
onMounted(() => {
  if (props.animated) {
    const animate = () => {
      animationOffset.value += 0.05
      requestAnimationFrame(animate)
    }
    animate()
  }
})
</script>

<style scoped>
.emotional-feedback {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

/* 健康表情 */
.health-emoji-container {
  text-align: center;
}

.emoji-face {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  position: relative;
  transition: all var(--duration-base) var(--ease-out);
}

.emoji--excellent { background: var(--color-health-excellent); }
.emoji--good { background: var(--color-health-good); }
.emoji--normal { background: var(--color-health-normal); }
.emoji--warning { background: var(--color-health-warning); }
.emoji--danger { background: var(--color-health-danger); }

.emoji-eyes {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.emoji-eye {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}

.emoji-mouth {
  position: absolute;
  bottom: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 10px;
  border: 2px solid white;
  border-top: none;
}

.mouth--excellent { border-radius: 0 0 20px 20px; }
.mouth--good { border-radius: 0 0 15px 15px; }
.mouth--normal { border-radius: 0; }
.mouth--warning { border-radius: 15px 15px 0 0; border-top: 2px solid white; border-bottom: none; }
.mouth--danger { border-radius: 20px 20px 0 0; border-top: 2px solid white; border-bottom: none; }

/* 心率波形 */
.heartbeat-container {
  text-align: center;
}

.heartbeat-wave {
  width: 120px;
  height: 40px;
}

/* 能量条 */
.energy-bar-container {
  width: 100%;
  max-width: 200px;
}

.energy-bar-background {
  width: 100%;
  height: 20px;
  background: var(--color-background-surface);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.energy-bar-fill {
  height: 100%;
  border-radius: 10px;
  position: relative;
  transition: width var(--duration-base) var(--ease-out);
}

.energy-sparkles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.sparkle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  animation: sparkle 1.5s infinite ease-in-out;
}

@keyframes sparkle {
  0%, 100% { opacity: 0; transform: scale(0); }
  50% { opacity: 1; transform: scale(1); }
}

/* 睡眠云朵 */
.sleep-cloud-container {
  position: relative;
  width: 120px;
  height: 60px;
}

.cloud-group {
  position: relative;
  width: 100%;
  height: 40px;
}

.cloud {
  position: absolute;
  background: var(--color-neutral-300);
  border-radius: 20px;
  opacity: 0.3;
  transition: all var(--duration-base) var(--ease-out);
}

.cloud--active {
  opacity: 0.8;
  background: var(--color-health-good);
}

.cloud-1 { width: 40px; height: 20px; top: 10px; left: 10px; }
.cloud-2 { width: 50px; height: 25px; top: 5px; left: 35px; }
.cloud-3 { width: 35px; height: 18px; top: 12px; left: 70px; }

.sleep-stars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.star {
  position: absolute;
  color: var(--color-health-excellent);
  animation: twinkle 2s infinite ease-in-out;
}

.star::before {
  content: '✨';
  font-size: 12px;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 步数足迹 */
.step-trail-container {
  width: 100%;
  max-width: 200px;
}

.footprint-trail {
  position: relative;
  height: 30px;
  width: 100%;
}

.footprint {
  position: absolute;
  font-size: 16px;
  opacity: 0;
  animation: footstep 0.5s ease-out forwards;
}

@keyframes footstep {
  0% { opacity: 0; transform: translateY(10px) scale(0.5); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

/* 水分波浪 */
.hydration-container {
  width: 80px;
  text-align: center;
}

.water-container {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--color-border);
  position: relative;
}

.water-wave {
  width: 100%;
  height: 100%;
}

/* 标签样式 */
.emoji-label,
.heartbeat-value,
.energy-label,
.sleep-label,
.step-label,
.hydration-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: center;
  margin-top: 4px;
}

/* 动画效果 */
.feedback--animated .emoji-face {
  animation: pulse 2s infinite ease-in-out;
}

.feedback--animated .heartbeat-wave path {
  animation: heartbeatPulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes heartbeatPulse {
  0%, 100% { stroke-width: 2; }
  50% { stroke-width: 3; }
}

/* 响应式 */
@media (max-width: 768px) {
  .emoji-face {
    width: 50px;
    height: 50px;
  }
  
  .heartbeat-wave {
    width: 100px;
    height: 35px;
  }
}
</style>
