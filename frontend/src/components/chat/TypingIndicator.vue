<template>
  <div 
    v-if="visible"
    v-motion-bounce-visible="{
      initial: { scale: 0, opacity: 0 },
      visible: { 
        scale: 1, 
        opacity: 1,
        transition: {
          type: 'spring',
          stiffness: 400,
          damping: 15
        }
      }
    }"
    class="typing-indicator"
  >
    <div class="message-container">
      <!-- AI助手头像 -->
      <div class="avatar-container">
        <a-avatar 
          :size="44" 
          :style="{ 
            background: 'linear-gradient(135deg, var(--color-primary) 0%, theme(\\\'colors.primary.600\\\') 100%)',
            boxShadow: 'var(--shadow-card)',
            fontWeight: '600'
          }"
        >
          AI
        </a-avatar>
      </div>
      
      <!-- 打字动画 -->
      <div class="typing-content">
        <div 
          v-motion-fade-visible="{
            initial: { opacity: 0, scale: 0.9 },
            visible: { 
              opacity: 1, 
              scale: 1,
              transition: {
                delay: 200,
                duration: 300
              }
            }
          }"
          class="typing-bubble"
        >
          <div 
            v-motion-pop="{
              initial: { scale: 0 },
              visible: { 
                scale: 1,
                transition: {
                  type: 'spring',
                  stiffness: 300,
                  delay: 400
                }
              }
            }"
            class="typing-dots"
          >
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div class="typing-text">{{ typingText }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  customText: {
    type: String,
    default: ''
  }
})

const typingText = ref('')
const typingTexts = [
  'AuraWell 正在思考...',
  '正在分析您的健康数据...',
  '正在为您制定个性化建议...',
  '正在查找相关健康信息...',
  '正在生成健康方案...'
]

let textInterval = null

onMounted(() => {
  if (props.customText) {
    typingText.value = props.customText
  } else {
    // 随机显示不同的打字文本
    let currentIndex = 0
    typingText.value = typingTexts[currentIndex]
    
    textInterval = setInterval(() => {
      currentIndex = (currentIndex + 1) % typingTexts.length
      typingText.value = typingTexts[currentIndex]
    }, 2000)
  }
})

onUnmounted(() => {
  if (textInterval) {
    clearInterval(textInterval)
  }
})
</script>

<style scoped>
.typing-indicator {
  margin-bottom: 16px;
  padding: 0 16px;
  animation: fadeIn 0.3s ease-in;
}

.message-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.avatar-container {
  flex-shrink: 0;
}

.typing-content {
  flex: 1;
  max-width: 70%;
}

.typing-bubble {
  background: var(--color-bg-muted);
  padding: 16px 20px;
  border-radius: var(--border-radius-card);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 24px;
  transition: all 0.3s ease;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: theme('colors.primary.500');
  box-shadow: 0 2px 4px rgba(26, 54, 93, 0.2);
  animation: typing 1.6s infinite cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

.dot:nth-child(3) {
  animation-delay: 0s;
}

.typing-text {
  font-size: 13px;
  color: var(--color-text-muted);
  font-style: italic;
  font-weight: 500;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
