<template>
  <div 
    ref="emptyStateRef"
    class="empty-state-container flex flex-col items-center justify-center py-16 px-8 text-center"
  >
    <!-- 动画图标 -->
    <div 
      ref="iconRef"
      class="relative mb-6"
    >
      <div class="w-24 h-24 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <component 
          :is="icon" 
          ref="iconInnerRef"
          class="w-12 h-12 text-gray-400"
        />
      </div>
      
      <!-- 装饰性粒子 -->
      <div 
        ref="particleRef1"
        class="absolute -top-2 -right-2 w-3 h-3 rounded-full bg-primary-300 opacity-60"
      ></div>
      <div 
        ref="particleRef2"
        class="absolute -bottom-2 -left-2 w-2 h-2 rounded-full bg-primary-400 opacity-40"
      ></div>
      <div 
        ref="particleRef3"
        class="absolute top-1 -left-4 w-1.5 h-1.5 rounded-full bg-primary-500 opacity-80"
      ></div>
    </div>

    <!-- 标题 -->
    <h3 
      ref="titleRef"
      class="text-xl font-semibold text-gray-900 mb-3"
    >
      {{ title }}
    </h3>

    <!-- 描述 -->
    <p 
      ref="descRef"
      class="text-gray-600 mb-8 max-w-md leading-relaxed"
    >
      {{ description }}
    </p>

    <!-- 行动按钮 -->
    <div 
      ref="actionRef"
      class="flex flex-col sm:flex-row gap-4"
    >
      <button
        v-if="primaryAction"
        @click="$emit('primaryAction')"
        class="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200 focus-ring"
      >
        {{ primaryAction }}
      </button>
      
      <button
        v-if="secondaryAction"
        @click="$emit('secondaryAction')"
        class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors duration-200 focus-ring"
      >
        {{ secondaryAction }}
      </button>
    </div>

    <!-- 提示信息 -->
    <div 
      v-if="showTips"
      ref="tipsRef"
      class="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100"
    >
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <div class="w-5 h-5 rounded-full bg-blue-200 flex items-center justify-center">
            <span class="text-blue-600 text-xs">💡</span>
          </div>
        </div>
        <div class="text-sm text-blue-800">
          <p class="font-medium mb-1">小贴士</p>
          <p>{{ tips }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  icon: {
    type: [String, Object, Function],
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  primaryAction: {
    type: String,
    default: null
  },
  secondaryAction: {
    type: String,
    default: null
  },
  tips: {
    type: String,
    default: null
  },
  showTips: {
    type: Boolean,
    default: false
  },
  autoPlay: {
    type: Boolean,
    default: true
  }
})

defineEmits(['primaryAction', 'secondaryAction'])

const emptyStateRef = ref()
const iconRef = ref()
const iconInnerRef = ref()
const particleRef1 = ref()
const particleRef2 = ref()
const particleRef3 = ref()
const titleRef = ref()
const descRef = ref()
const actionRef = ref()
const tipsRef = ref()

// 粒子浮动动画
const createParticleAnimation = () => {
  const particles = [particleRef1, particleRef2, particleRef3]
  
  particles.forEach((particle, index) => {
    if (particle.value) {
      gsap.to(particle.value, {
        y: Math.random() * 20 - 10,
        x: Math.random() * 20 - 10,
        duration: 2 + index * 0.5,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        delay: index * 0.3
      })
      
      gsap.to(particle.value, {
        opacity: 0.2 + Math.random() * 0.6,
        duration: 1.5,
        ease: 'sine.inOut',
        yoyo: true,
        repeat: -1,
        delay: index * 0.2
      })
    }
  })
}

// 图标呼吸动画
const createIconAnimation = () => {
  if (iconInnerRef.value) {
    gsap.to(iconInnerRef.value, {
      scale: 1.1,
      duration: 2,
      ease: 'sine.inOut',
      yoyo: true,
      repeat: -1
    })
  }
  
  if (iconRef.value) {
    gsap.to(iconRef.value, {
      rotateY: 5,
      duration: 4,
      ease: 'sine.inOut',
      yoyo: true,
      repeat: -1
    })
  }
}

// 入场动画
const playEntranceAnimation = async () => {
  await nextTick()
  
  if (!emptyStateRef.value) return

  const tl = gsap.timeline()

  // 设置初始状态
  gsap.set([iconRef.value, titleRef.value, descRef.value, actionRef.value, tipsRef.value], {
    opacity: 0,
    y: 30
  })

  // 1. 图标放大入场
  tl.fromTo(iconRef.value,
    { opacity: 0, scale: 0.5, y: 50 },
    { 
      opacity: 1, 
      scale: 1, 
      y: 0, 
      duration: 0.8, 
      ease: 'back.out(1.7)' 
    }
  )

  // 2. 标题滑入
  tl.to(titleRef.value, {
    opacity: 1,
    y: 0,
    duration: 0.6,
    ease: 'power2.out'
  }, '-=0.4')

  // 3. 描述淡入
  tl.to(descRef.value, {
    opacity: 1,
    y: 0,
    duration: 0.6,
    ease: 'power2.out'
  }, '-=0.3')

  // 4. 按钮弹入
  tl.to(actionRef.value, {
    opacity: 1,
    y: 0,
    duration: 0.5,
    ease: 'back.out(1.7)'
  }, '-=0.2')

  // 5. 提示信息滑入
  if (tipsRef.value) {
    tl.to(tipsRef.value, {
      opacity: 1,
      y: 0,
      duration: 0.5,
      ease: 'power2.out'
    }, '-=0.2')
  }

  // 启动循环动画
  tl.call(() => {
    createParticleAnimation()
    createIconAnimation()
  })
}

// 悬浮提示动画
const showHoverHint = () => {
  if (iconRef.value) {
    gsap.to(iconRef.value, {
      scale: 1.05,
      duration: 0.3,
      ease: 'power2.out',
      yoyo: true,
      repeat: 1
    })
  }
}

// 暴露方法
defineExpose({
  playEntranceAnimation,
  showHoverHint
})

onMounted(() => {
  if (props.autoPlay) {
    playEntranceAnimation()
  }
})
</script>

<style scoped>
.empty-state-container {
  min-height: 400px;
}

.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  border-color: theme('colors.blue.500');
}

/* 确保动画流畅 */
.empty-state-container * {
  will-change: transform, opacity;
}
</style> 