<template>
  <span 
    ref="numberRef"
    :class="className"
    class="animated-number"
  >
    {{ displayValue }}
  </span>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  value: {
    type: Number,
    required: true
  },
  className: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 1.2
  },
  delay: {
    type: Number,
    default: 0
  },
  precision: {
    type: Number,
    default: 0
  },
  easing: {
    type: String,
    default: 'power2.out'
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  separator: {
    type: String,
    default: ','
  }
})

const numberRef = ref()
const displayValue = ref(0)
const currentValue = ref(0)

const formatNumber = (num) => {
  const fixed = num.toFixed(props.precision)
  const parts = fixed.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, props.separator)
  return props.prefix + parts.join('.') + props.suffix
}

const animateToValue = (targetValue) => {
  if (!numberRef.value) return

  // 创建高性能数值动画
  gsap.to(currentValue, {
    value: targetValue,
    duration: props.duration,
    delay: props.delay,
    ease: props.easing,
    onUpdate: () => {
      displayValue.value = formatNumber(currentValue.value)
    },
    // 添加微妙的缩放效果
    onStart: () => {
      gsap.fromTo(numberRef.value, 
        { scale: 0.95 },
        { scale: 1, duration: 0.3, ease: 'back.out(1.7)' }
      )
    }
  })
}

// 监听数值变化
watch(() => props.value, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    animateToValue(newValue)
  }
}, { immediate: false })

onMounted(async () => {
  await nextTick()
  // 初始化动画
  currentValue.value = 0
  displayValue.value = formatNumber(0)
  animateToValue(props.value)
})
</script>

<style scoped>
.animated-number {
  display: inline-block;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}

.animated-number:hover {
  color: theme('colors.primary.600');
  transform: scale(1.02);
  transition: all 0.2s ease;
}
</style> 