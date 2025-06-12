<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-container">
      <!-- 头像 -->
      <div class="avatar-container">
        <a-avatar :size="40" :src="avatarSrc" :style="avatarStyle">
          {{ avatarText }}
        </a-avatar>
      </div>
      
      <!-- 消息内容 -->
      <div class="message-content">
        <!-- 发送者名称和时间 -->
        <div class="message-header">
          <span class="sender-name">{{ senderName }}</span>
          <span class="message-time">{{ formattedTime }}</span>
        </div>
        
        <!-- 消息文本 -->
        <div class="message-text" v-html="formattedMessage"></div>
        
        <!-- 健康建议卡片 -->
        <div v-if="message.suggestions && message.suggestions.length > 0" class="suggestions-container">
          <h4>💡 个性化建议</h4>
          <div class="suggestion-cards">
            <a-card 
              v-for="(suggestion, index) in message.suggestions" 
              :key="index"
              size="small"
              class="suggestion-card"
            >
              <template #title>
                <span class="suggestion-title">{{ suggestion.title }}</span>
              </template>
              <p class="suggestion-content">{{ suggestion.content }}</p>
              <div v-if="suggestion.action" class="suggestion-action">
                <a-button type="link" size="small" @click="handleSuggestionAction(suggestion.action)">
                  {{ suggestion.actionText || '了解更多' }}
                </a-button>
              </div>
            </a-card>
          </div>
        </div>
        
        <!-- 快速回复按钮 -->
        <div v-if="message.quickReplies && message.quickReplies.length > 0" class="quick-replies">
          <a-button 
            v-for="(reply, index) in message.quickReplies" 
            :key="index"
            size="small"
            type="default"
            class="quick-reply-btn"
            @click="handleQuickReply(reply)"
          >
            {{ reply.text }}
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserOutlined, RobotOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['quick-reply', 'suggestion-action'])

// 计算属性
const messageClass = computed(() => ({
  'user-message': props.message.sender === 'user',
  'agent-message': props.message.sender === 'agent'
}))

const senderName = computed(() => {
  return props.message.sender === 'user' ? '我' : 'AuraWell 健康助手'
})

const avatarSrc = computed(() => {
  return props.message.sender === 'user' ? null : '/logo.png'
})

const avatarText = computed(() => {
  return props.message.sender === 'user' ? '我' : 'AI'
})

const avatarStyle = computed(() => ({
  backgroundColor: props.message.sender === 'user' ? '#1890ff' : '#52c41a'
}))

const formattedTime = computed(() => {
  const date = new Date(props.message.timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

const formattedMessage = computed(() => {
  let text = props.message.content || props.message.text || ''
  
  // 简单的markdown渲染
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>')
  text = text.replace(/\n/g, '<br>')
  
  return text
})

// 事件处理
const handleQuickReply = (reply) => {
  emit('quick-reply', reply)
}

const handleSuggestionAction = (action) => {
  emit('suggestion-action', action)
}
</script>

<style scoped>
.chat-message {
  margin-bottom: 16px;
  padding: 0 16px;
}

.message-container {
  display: flex;
  gap: 12px;
}

.user-message .message-container {
  flex-direction: row-reverse;
}

.avatar-container {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #666;
}

.user-message .message-header {
  justify-content: flex-end;
}

.sender-name {
  font-weight: 500;
}

.message-time {
  color: #999;
}

.message-text {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
}

.user-message .message-text {
  background: #1890ff;
  color: white;
}

.suggestions-container {
  margin-top: 12px;
}

.suggestions-container h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #52c41a;
}

.suggestion-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-card {
  border-left: 3px solid #52c41a;
}

.suggestion-title {
  font-size: 13px;
  font-weight: 500;
}

.suggestion-content {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.suggestion-action {
  margin-top: 8px;
}

.quick-replies {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-reply-btn {
  border-radius: 16px;
  font-size: 12px;
}

.user-message .quick-replies {
  justify-content: flex-end;
}
</style>
