<template>
  <div 
    ref="containerRef"
    :class="[
      'optimized-image-container',
      { 'loading': isLoading, 'error': hasError }
    ]"
    :style="containerStyle"
  >
    <!-- 占位符 -->
    <div 
      v-if="isLoading && placeholder"
      class="image-placeholder"
      :style="placeholderStyle"
    >
      <div class="placeholder-content">
        <div class="placeholder-skeleton"></div>
      </div>
    </div>

    <!-- 实际图片 -->
    <img
      v-show="!isLoading && !hasError"
      ref="imageRef"
      :src="optimizedSrc"
      :alt="alt"
      :loading="lazy ? 'lazy' : 'eager'"
      :decoding="async ? 'async' : 'sync'"
      :sizes="sizes"
      :srcset="srcset"
      :class="imageClass"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
    />

    <!-- 错误状态 -->
    <div 
      v-if="hasError"
      class="image-error"
      :style="errorStyle"
    >
      <div class="error-content">
        <svg class="error-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
        </svg>
        <span class="error-text">{{ errorText || '图片加载失败' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

// Props定义
const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  width: {
    type: [Number, String],
    default: 'auto'
  },
  height: {
    type: [Number, String],
    default: 'auto'
  },
  lazy: {
    type: Boolean,
    default: true
  },
  async: {
    type: Boolean,
    default: true
  },
  placeholder: {
    type: Boolean,
    default: true
  },
  quality: {
    type: Number,
    default: 80,
    validator: (value) => value >= 1 && value <= 100
  },
  format: {
    type: String,
    default: 'auto',
    validator: (value) => ['auto', 'webp', 'avif', 'jpg', 'png'].includes(value)
  },
  sizes: {
    type: String,
    default: ''
  },
  breakpoints: {
    type: Array,
    default: () => [320, 640, 960, 1280, 1920]
  },
  errorText: {
    type: String,
    default: ''
  },
  objectFit: {
    type: String,
    default: 'cover',
    validator: (value) => ['fill', 'contain', 'cover', 'none', 'scale-down'].includes(value)
  }
})

// 响应式数据
const containerRef = ref(null)
const imageRef = ref(null)
const isLoading = ref(true)
const hasError = ref(false)
const observer = ref(null)

// 计算属性
const containerStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  position: 'relative',
  overflow: 'hidden'
}))

const placeholderStyle = computed(() => ({
  width: '100%',
  height: '100%',
  position: 'absolute',
  top: 0,
  left: 0,
  backgroundColor: '#f5f5f5',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
}))

const errorStyle = computed(() => ({
  width: '100%',
  height: '100%',
  position: 'absolute',
  top: 0,
  left: 0,
  backgroundColor: '#fafafa',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#999'
}))

const imageClass = computed(() => [
  'optimized-image',
  `object-${props.objectFit}`
])

const imageStyle = computed(() => ({
  width: '100%',
  height: '100%',
  objectFit: props.objectFit
}))

// 检测浏览器支持的图片格式
const getSupportedFormat = () => {
  if (props.format !== 'auto') return props.format
  
  // 检测WebP支持
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  const webpSupported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
  
  if (webpSupported) return 'webp'
  return 'jpg'
}

// 生成优化后的图片URL
const optimizedSrc = computed(() => {
  if (!props.src) return ''
  
  const format = getSupportedFormat()
  const url = new URL(props.src, window.location.origin)
  
  // 添加优化参数（假设后端支持）
  url.searchParams.set('format', format)
  url.searchParams.set('quality', props.quality.toString())
  
  // 根据容器大小设置宽度
  if (containerRef.value) {
    const containerWidth = containerRef.value.offsetWidth
    if (containerWidth > 0) {
      url.searchParams.set('width', Math.ceil(containerWidth * window.devicePixelRatio).toString())
    }
  }
  
  return url.toString()
})

// 生成srcset
const srcset = computed(() => {
  if (!props.src || !props.breakpoints.length) return ''
  
  const format = getSupportedFormat()
  return props.breakpoints
    .map(width => {
      const url = new URL(props.src, window.location.origin)
      url.searchParams.set('format', format)
      url.searchParams.set('quality', props.quality.toString())
      url.searchParams.set('width', width.toString())
      return `${url.toString()} ${width}w`
    })
    .join(', ')
})

// 事件处理
const handleLoad = () => {
  isLoading.value = false
  hasError.value = false
}

const handleError = () => {
  isLoading.value = false
  hasError.value = true
}

// 懒加载观察器
const setupIntersectionObserver = () => {
  if (!props.lazy || !containerRef.value) return
  
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // 图片进入视口，开始加载
          observer.value?.unobserve(entry.target)
        }
      })
    },
    {
      rootMargin: '50px'
    }
  )
  
  observer.value.observe(containerRef.value)
}

// 生命周期
onMounted(() => {
  if (props.lazy) {
    setupIntersectionObserver()
  }
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})

// 监听src变化
watch(() => props.src, () => {
  isLoading.value = true
  hasError.value = false
})
</script>

<style scoped>
.optimized-image-container {
  display: inline-block;
  border-radius: 8px;
  overflow: hidden;
}

.optimized-image {
  transition: opacity 0.3s ease;
}

.image-placeholder {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

.placeholder-skeleton {
  width: 60%;
  height: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
}

.image-error .error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.error-icon {
  width: 24px;
  height: 24px;
  opacity: 0.5;
}

.error-text {
  font-size: 12px;
  opacity: 0.7;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.object-fill { object-fit: fill; }
.object-contain { object-fit: contain; }
.object-cover { object-fit: cover; }
.object-none { object-fit: none; }
.object-scale-down { object-fit: scale-down; }
</style>
