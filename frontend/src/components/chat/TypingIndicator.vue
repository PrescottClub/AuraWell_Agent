<template>
  <div class="typing-indicator" v-if="visible">
    <div class="message-container">
      <!-- AI助手头像 -->
      <div class="avatar-container">
        <a-avatar :size="40" :style="{ backgroundColor: '#52c41a' }">
          AI
        </a-avatar>
      </div>
      
      <!-- 打字动画 -->
      <div class="typing-content">
        <div class="typing-bubble">
          <div class="typing-dots">
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
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 20px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #52c41a;
  animation: typing 1.4s infinite ease-in-out;
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
  font-size: 12px;
  color: #666;
  font-style: italic;
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
