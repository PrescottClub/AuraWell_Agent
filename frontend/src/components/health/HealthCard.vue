<template>
  <div
    ref="cardRef"
    class="aura-card group flex flex-col h-full cursor-pointer"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @click="handleClick"
  >
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 rounded-xl bg-background-surface border border-border flex items-center justify-center transition-all duration-200 group-hover:scale-105">
          <component :is="icon" class="w-6 h-6 text-primary transition-colors duration-200" />
        </div>
        <div>
          <p class="text-caption">{{ category }}</p>
          <h3 class="text-heading-4">{{ title }}</h3>
        </div>
      </div>
      <div class="w-8 h-8 flex items-center justify-center rounded-full text-text-muted/0 group-hover:text-text-muted transition-all duration-200 group-hover:rotate-12">
        <RightOutlined class="w-5 h-5" />
      </div>
    </div>

    <!-- 主数据显示 -->
    <div class="flex-1 flex flex-col justify-center my-4">
      <div class="mb-2">
        <span class="text-metric-large metric-value">{{ value }}</span>
        <span class="text-body-large text-text-secondary ml-1.5">{{ unit }}</span>
      </div>

      <!-- 趋势指示器 -->
      <div v-if="trend" class="flex items-center">
        <div
          :class="[
            'flex items-center space-x-1.5 text-sm font-medium',
            trendColorClass
          ]"
        >
          <component :is="trendIcon" class="w-4 h-4" />
          <span>{{ Math.abs(trend) }}% vs {{ trendPeriod || '上月' }}</span>
        </div>
      </div>
    </div>

    <!-- 迷你图表区域（可选） -->
    <div v-if="showChart" class="mt-auto h-16 bg-background-elevated rounded-lg p-2 border border-border-light">
       <div class="w-full h-full rounded flex items-end">
        <div v-for="(bar, index) in chartData" :key="index"
             class="flex-1 bg-primary/20 rounded-t-sm mx-px transition-colors duration-200 ease-out group-hover:bg-primary/30"
             :style="{ height: bar + '%' }">
        </div>
      </div>
    </div>

    <!-- 底部状态 -->
    <div v-if="status" class="mt-4 pt-4 border-t border-border-light">
      <div class="flex items-center space-x-2.5">
        <div
          :class="[
            'w-2.5 h-2.5 rounded-full',
            statusColorClass
          ]"
        ></div>
        <span class="text-body-small">{{ status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  RightOutlined
} from '@ant-design/icons-vue'
import { useMicroInteractions } from '@/composables/useMicroInteractions'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  category: {
    type: String,
    default: ''
  },
  value: {
    type: [String, Number],
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  icon: {
    type: [String, Object],
    required: true
  },
  trend: {
    type: Number,
    default: null
  },
  trendPeriod: {
    type: String,
    default: '上月'
  },
  status: {
    type: String,
    default: null
  },
  showChart: {
    type: Boolean,
    default: false
  },
  chartData: {
    type: Array,
    default: () => [20, 45, 30, 60, 80, 45, 70]
  }
})

// 趋势颜色计算
const trendColorClass = computed(() => {
  if (props.trend > 0) {
    return 'text-success'
  } else if (props.trend < 0) {
    return 'text-error'
  }
  return 'text-text-secondary'
})

// 趋势图标
const trendIcon = computed(() => {
  return props.trend > 0 ? ArrowUpOutlined : ArrowDownOutlined
})

// 状态颜色计算
const statusColorClass = computed(() => {
  if (!props.status) return ''
  
  const status = props.status.toLowerCase()
  if (status.includes('优秀') || status.includes('良好') || status.includes('正常') || status.includes('目标达成')) {
    return 'bg-success'
  } else if (status.includes('注意') || status.includes('偏高') || status.includes('偏低') || status.includes('接近目标')) {
    return 'bg-warning'
  } else if (status.includes('异常') || status.includes('危险') || status.includes('需要改善') || status.includes('需要努力')) {
    return 'bg-error'
  }
  return 'bg-primary'
})

// 微交互
const cardRef = ref()
const { cardHover, cardLeave, rippleEffect, animateNumber } = useMicroInteractions()

const handleMouseEnter = () => {
  if (cardRef.value) {
    cardHover(cardRef.value)
  }
}

const handleMouseLeave = () => {
  if (cardRef.value) {
    cardLeave(cardRef.value)
  }
}

const handleClick = (event) => {
  if (cardRef.value) {
    rippleEffect(cardRef.value, event)
  }
}

// 数值动画
onMounted(() => {
  if (cardRef.value && typeof props.value === 'number') {
    const valueElement = cardRef.value.querySelector('.metric-value')
    if (valueElement) {
      animateNumber(valueElement, 0, props.value, {
        duration: 800,
        delay: 200
      })
    }
  }
})
</script>

<style scoped>
/* No custom styles needed, relying purely on Tailwind utility classes for a clean look */
</style> 