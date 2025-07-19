<template>
  <Teleport to="body">
    <div
      v-if="isVisible"
      ref="celebrationRef"
      class="fixed inset-0 pointer-events-none z-50 overflow-hidden"
    >
      <!-- 背景遮罩 -->
      <div
        ref="overlayRef"
        class="absolute inset-0 bg-black/20 backdrop-blur-sm"
      ></div>

      <!-- 粒子容器 -->
      <div
        ref="particlesRef"
        class="absolute inset-0"
      ></div>

      <!-- 中心成就显示 -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div
          ref="achievementRef"
          class="bg-white rounded-2xl shadow-2xl p-8 max-w-sm mx-4 text-center transform"
        >
          <div class="mb-4">
            <div
              ref="iconRef"
              class="w-20 h-20 mx-auto rounded-full bg-gradient-to-r from-yellow-400 to-orange-500 flex items-center justify-center mb-4"
            >
              <component :is="achievement.icon" class="w-10 h-10 text-white" />
            </div>
          </div>
          
          <h3
            ref="titleRef"
            class="text-2xl font-bold text-gray-900 mb-2"
          >
            {{ achievement.title }}
          </h3>
          
          <p
            ref="descRef"
            class="text-gray-600 mb-6"
          >
            {{ achievement.description }}
          </p>
          
          <div
            ref="rewardRef"
            class="inline-flex items-center px-4 py-2 bg-primary-50 rounded-lg"
          >
            <span class="text-primary-600 font-medium">+{{ achievement.points }} 健康积分</span>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2">
        <button
          ref="buttonRef"
          @click="dismiss"
          class="px-6 py-3 bg-white rounded-full shadow-lg text-gray-700 font-medium hover:shadow-xl transition-shadow"
        >
          太棒了！
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { gsap } from 'gsap'

const props = defineProps({
  achievement: {
    type: Object,
    required: true,
    default: () => ({
      title: '目标达成！',
      description: '恭喜你完成了今日健康目标',
      icon: 'TrophyOutlined',
      points: 50,
      type: 'daily' // daily, weekly, milestone, special
    })
  },
  autoHide: {
    type: Boolean,
    default: true
  },
  duration: {
    type: Number,
    default: 4000
  }
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
const celebrationRef = ref()
const overlayRef = ref()
const particlesRef = ref()
const achievementRef = ref()
const iconRef = ref()
const titleRef = ref()
const descRef = ref()
const rewardRef = ref()
const buttonRef = ref()

// 粒子系统
const createParticles = () => {
  if (!particlesRef.value) return

  const particleCount = 50
  const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
  
  for (let i = 0; i < particleCount; i++) {
    const particle = document.createElement('div')
    particle.className = 'absolute w-2 h-2 rounded-full pointer-events-none'
    particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)]
    particle.style.left = Math.random() * 100 + '%'
    particle.style.top = Math.random() * 100 + '%'
    
    particlesRef.value.appendChild(particle)
    
    // 粒子动画
    gsap.to(particle, {
      x: (Math.random() - 0.5) * 400,
      y: (Math.random() - 0.5) * 400,
      scale: Math.random() * 2 + 0.5,
      opacity: 0,
      duration: Math.random() * 3 + 2,
      ease: 'power2.out',
      onComplete: () => {
        particle.remove()
      }
    })
  }
}

// 烟花效果
const createFireworks = () => {
  if (!particlesRef.value) return

  const fireworkCount = 3
  
  for (let i = 0; i < fireworkCount; i++) {
    setTimeout(() => {
      const centerX = Math.random() * window.innerWidth
      const centerY = Math.random() * window.innerHeight * 0.6
      
      for (let j = 0; j < 20; j++) {
        const spark = document.createElement('div')
        spark.className = 'absolute w-1 h-1 rounded-full pointer-events-none bg-yellow-400'
        spark.style.left = centerX + 'px'
        spark.style.top = centerY + 'px'
        
        particlesRef.value.appendChild(spark)
        
        const angle = (j / 20) * Math.PI * 2
        const distance = Math.random() * 100 + 50
        
        gsap.to(spark, {
          x: Math.cos(angle) * distance,
          y: Math.sin(angle) * distance,
          opacity: 0,
          duration: 1.5,
          ease: 'power2.out',
          onComplete: () => spark.remove()
        })
      }
    }, i * 500)
  }
}

// 庆祝动画序列
const playCelebration = async () => {
  await nextTick()
  
  if (!celebrationRef.value) return

  const tl = gsap.timeline()

  // 1. 背景淡入
  tl.fromTo(overlayRef.value, 
    { opacity: 0 },
    { opacity: 1, duration: 0.3 }
  )

  // 2. 成就卡片弹入
  tl.fromTo(achievementRef.value,
    { scale: 0.5, opacity: 0, rotateY: -90 },
    { scale: 1, opacity: 1, rotateY: 0, duration: 0.6, ease: 'back.out(1.7)' },
    '-=0.1'
  )

  // 3. 图标旋转放大
  tl.fromTo(iconRef.value,
    { scale: 0, rotation: -180 },
    { scale: 1, rotation: 0, duration: 0.5, ease: 'back.out(1.7)' },
    '-=0.3'
  )

  // 4. 标题打字效果
  tl.fromTo(titleRef.value,
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' },
    '-=0.2'
  )

  // 5. 描述滑入
  tl.fromTo(descRef.value,
    { opacity: 0, y: 15 },
    { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' },
    '-=0.2'
  )

  // 6. 奖励闪烁
  tl.fromTo(rewardRef.value,
    { opacity: 0, scale: 0.8 },
    { opacity: 1, scale: 1, duration: 0.3, ease: 'back.out(1.7)' },
    '-=0.1'
  )
  .to(rewardRef.value, {
    scale: 1.1,
    duration: 0.2,
    yoyo: true,
    repeat: 3,
    ease: 'power2.inOut'
  })

  // 7. 按钮出现
  tl.fromTo(buttonRef.value,
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' },
    '-=0.5'
  )

  // 触发粒子效果
  tl.call(createParticles, [], '-=1.5')
  tl.call(createFireworks, [], '-=1')

  // 自动隐藏
  if (props.autoHide) {
    setTimeout(dismiss, props.duration)
  }
}

// 显示庆祝动画
const show = () => {
  isVisible.value = true
  playCelebration()
}

// 关闭动画
const dismiss = () => {
  if (!celebrationRef.value) return

  gsap.to(celebrationRef.value, {
    opacity: 0,
    scale: 0.95,
    duration: 0.4,
    ease: 'power2.out',
    onComplete: () => {
      isVisible.value = false
      emit('close')
    }
  })
}

// 暴露方法
defineExpose({
  show,
  dismiss
})
</script>

<style scoped>
/* 确保动画流畅 */
.celebration-container {
  will-change: transform, opacity;
}
</style> 