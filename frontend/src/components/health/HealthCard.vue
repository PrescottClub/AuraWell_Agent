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
      <div class="mb-2" data-animate="value">
        <AnimatedNumber 
          :value="typeof value === 'number' ? value : parseInt(value.toString().replace(/,/g, '')) || 0"
          :precision="getPrecision(value)"
          class-name="text-metric-large"
          :duration="1.2"
          :delay="0.2"
        />
        <span class="text-body-large text-text-secondary ml-1.5">{{ unit }}</span>
      </div>

      <!-- 趋势指示器 -->
      <div v-if="trend" class="flex items-center">
        <div
          :class="[
            'flex items-center space-x-1.5 text-sm font-medium trend-indicator',
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
import { useDataTransition } from '@/composables/useDataTransition'
import { useGestures } from '@/composables/useGestures'
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  category: {
    type: String,
    required: true
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
    type: [String, Object, Function],
    required: true,
    validator: (value) => {
      // 允许字符串、Vue组件对象或Vue组件函数
      return typeof value === 'string' ||
             typeof value === 'function' ||
             (typeof value === 'object' && value !== null)
    }
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

// 微交互和手势
const cardRef = ref()
const { cardHover, cardLeave, rippleEffect } = useMicroInteractions()
const { pulseOnUpdate, animateTrend, refreshCardData } = useDataTransition()
const { bindGestures } = useGestures()

// 数值精度计算
const getPrecision = (val) => {
  if (typeof val === 'number') {
    return val % 1 === 0 ? 0 : 1
  }
  return 0
}

const handleMouseEnter = () => {
  if (cardRef.value) {
    cardHover(cardRef.value)
    // 数据脉冲效果
    const valueElement = cardRef.value.querySelector('[data-animate="value"]')
    if (valueElement) {
      pulseOnUpdate(valueElement, { scale: 1.02, duration: 0.2 })
    }
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
    // 数据刷新动画
    refreshCardData(cardRef.value)
  }
}

// 组件挂载和手势绑定
onMounted(() => {
  if (cardRef.value) {
    // 绑定手势交互
    const cleanup = bindGestures(cardRef.value, {
      onLongPress: (element) => {
        // 长按显示详细数据
        refreshCardData(element, { duration: 0.6 })
      },
      onSwipe: (element, gesture) => {
        // 滑动切换数据视图
        console.log('Card swiped:', gesture.direction)
      },
      onDoubleTap: (element) => {
        // 双击刷新数据
        refreshCardData(element)
      }
    })

    // 趋势动画
    if (props.trend && props.trend !== 0) {
      const trendElement = cardRef.value.querySelector('.trend-indicator')
      if (trendElement) {
        setTimeout(() => {
          animateTrend(trendElement, props.trend)
        }, 600)
      }
    }

    // 清理函数
    return cleanup
  }
})
</script>

<style scoped>
/* No custom styles needed, relying purely on Tailwind utility classes for a clean look */
</style> 