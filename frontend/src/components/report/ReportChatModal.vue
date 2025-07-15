<template>
  <a-modal
    :open="visible"
    title="AI健康分析对话"
    width="800px"
    :footer="null"
    @cancel="handleClose"
  >
    <div class="chat-container">
      <div class="chat-context" v-if="context">
        <div class="context-title">讨论主题: {{ context.title }}</div>
        <div class="context-desc">{{ context.description }}</div>
      </div>
      
      <div class="chat-messages">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="chat-message"
          :class="message.role"
        >
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div class="chat-input">
        <a-input
          v-model="chatInput"
          placeholder="输入您的问题或想法..."
          @press-enter="sendMessage"
          :disabled="loading"
        />
        <a-button 
          type="primary" 
          @click="sendMessage"
          :loading="loading"
        >
          发送
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, watch } from 'vue';
import { message } from 'ant-design-vue';
import { chatAPI } from '../../mock/api';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  context: {
    type: Object,
    default: null,
  },
  sessionId: {
    type: String,
    default: null,
  }
});

const emit = defineEmits(['update:visible', 'close', 'sent']);

const messages = ref([]);
const chatInput = ref('');
const loading = ref(false);
const internalSessionId = ref(props.sessionId);

watch(() => props.sessionId, (newVal) => {
  internalSessionId.value = newVal;
  if (newVal) {
    // Optionally fetch history when session changes
    messages.value = []; 
  }
});

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
}

const handleClose = () => {
  emit('update:visible', false);
  emit('close');
};

const sendMessage = async () => {
  if (!chatInput.value.trim()) return;
  if (!internalSessionId.value) {
    message.error('无法确定对话会话，请重试。');
    return;
  }

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: chatInput.value,
    timestamp: Date.now(),
  };
  messages.value.push(userMessage);
  emit('sent', userMessage);

  const currentInput = chatInput.value;
  chatInput.value = '';
  loading.value = true;

  try {
    const response = await chatAPI.sendMessage({
      session_id: internalSessionId.value,
      message: currentInput,
    });
    
    if (response.success && response.data) {
      const agentMessage = {
        id: response.data.message_id,
        role: 'agent',
        content: response.data.content,
        timestamp: response.data.timestamp,
      };
      messages.value.push(agentMessage);
    } else {
      throw new Error(response.message || 'AI响应失败');
    }
  } catch (error) {
    message.error(error.message || '发送消息失败');
    // Restore input on failure
    chatInput.value = currentInput;
    // remove the user message that failed
    messages.value.pop();
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 60vh;
}
.chat-context {
  padding: 12px;
  background-color: #f0f2f5;
  border-radius: 8px;
  margin-bottom: 16px;
}
.context-title {
  font-weight: bold;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 16px;
}
.chat-message {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
}
.chat-message.user {
  align-items: flex-end;
}
.chat-message.agent {
  align-items: flex-start;
}
.message-content {
  padding: 8px 12px;
  border-radius: 12px;
  max-width: 70%;
}
.chat-message.user .message-content {
  background-color: #1890ff;
  color: white;
}
.chat-message.agent .message-content {
  background-color: #f0f0f0;
}
.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.chat-input {
  display: flex;
  gap: 8px;
}
</style> 