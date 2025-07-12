<template>
  <div class="chat-integration">
    <!-- Quick chat triggers -->
    <div class="quick-chat-triggers">
      <a-button 
        v-for="trigger in quickTriggers" 
        :key="trigger.type"
        type="text" 
        size="small"
        @click="handleQuickChat(trigger)"
        :loading="trigger.loading"
        class="trigger-button"
      >
        <component :is="trigger.icon" />
        {{ trigger.label }}
      </a-button>
    </div>
    
    <!-- Floating chat button -->
    <a-float-button
      v-if="showFloatButton"
      type="primary"
      @click="toggleChatPanel"
      :style="{ right: '24px', bottom: '24px' }"
    >
      <template #icon>
        <MessageOutlined v-if="!chatPanelVisible" />
        <CloseOutlined v-else />
      </template>
    </a-float-button>
    
    <!-- Chat panel -->
    <div 
      v-if="chatPanelVisible" 
      class="chat-panel"
      :class="{ 'panel-expanded': panelExpanded }"
    >
      <div class="panel-header">
        <div class="panel-title">
          <MessageOutlined />
          AI Health Assistant
        </div>
        <div class="panel-controls">
          <a-button 
            type="text" 
            size="small"
            @click="togglePanelSize"
          >
            <ExpandOutlined v-if="!panelExpanded" />
            <CompressOutlined v-else />
          </a-button>
          <a-button 
            type="text" 
            size="small"
            @click="closeChatPanel"
          >
            <CloseOutlined />
          </a-button>
        </div>
      </div>
      
      <div class="panel-content">
        <!-- Context section -->
        <div v-if="currentContext" class="chat-context">
          <div class="context-header">
            <component :is="currentContext.icon" class="context-icon" />
            <div class="context-info">
              <div class="context-title">{{ currentContext.title }}</div>
              <div class="context-desc">{{ currentContext.description }}</div>
            </div>
          </div>
          
          <div v-if="currentContext.data" class="context-data">
            <div class="data-item" v-for="(value, key) in currentContext.data" :key="key">
              <span class="data-label">{{ getDataLabel(key) }}:</span>
              <span class="data-value">{{ formatDataValue(value, key) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Messages list -->
        <div class="messages-container" ref="messagesContainer">
          <div 
            v-for="message in messages" 
            :key="message.id"
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar">
              <UserOutlined v-if="message.role === 'user'" />
              <RobotOutlined v-else />
            </div>
            
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              
              <!-- Message actions -->
              <div v-if="message.role === 'assistant'" class="message-actions">
                <a-button 
                  type="text" 
                  size="small"
                  @click="handleCopyMessage(message)"
                >
                  <CopyOutlined />
                </a-button>
                
                <a-button 
                  type="text" 
                  size="small"
                  @click="handleLikeMessage(message)"
                  :class="{ 'liked': message.liked }"
                >
                  <LikeOutlined />
                </a-button>
                
                <a-dropdown v-if="message.suggestions?.length">
                  <a-button type="text" size="small">
                    <MoreOutlined />
                  </a-button>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item 
                        v-for="suggestion in message.suggestions" 
                        :key="suggestion.action"
                        @click="handleSuggestionAction(suggestion)"
                      >
                        {{ suggestion.label }}
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </div>
              
              <!-- Quick replies -->
              <div v-if="message.quickReplies?.length" class="quick-replies">
                <a-button 
                  v-for="reply in message.quickReplies" 
                  :key="reply.text"
                  size="small"
                  @click="handleQuickReply(reply.text)"
                  class="quick-reply-btn"
                >
                  {{ reply.text }}
                </a-button>
              </div>
            </div>
          </div>
          
          <!-- Typing indicator -->
          <div v-if="isTyping" class="typing-indicator">
            <div class="message-avatar">
              <RobotOutlined />
            </div>
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
        
        <!-- Input area -->
        <div class="input-area">
          <!-- Smart suggestions -->
          <div v-if="smartSuggestions.length" class="smart-suggestions">
            <div class="suggestions-label">Smart suggestions:</div>
            <div class="suggestions-list">
              <a-tag 
                v-for="suggestion in smartSuggestions" 
                :key="suggestion"
                @click="handleSuggestionClick(suggestion)"
                class="suggestion-tag"
              >
                {{ suggestion }}
              </a-tag>
            </div>
          </div>
          
          <!-- Input box -->
          <div class="input-container">
            <a-input
              v-model:value="inputText"
              placeholder="Ask something..."
              @press-enter="handleSendMessage"
              :disabled="isTyping"
              class="message-input"
            />
            
            <a-button 
              type="primary" 
              @click="handleSendMessage"
              :loading="isTyping"
              :disabled="!inputText.trim()"
              class="send-button"
            >
              <SendOutlined />
            </a-button>
          </div>
          
          <!-- Function buttons -->
          <div class="function-buttons">
            <a-button 
              type="text" 
              size="small"
              @click="handleReplanRequest"
              :loading="replanning"
            >
              <EditOutlined />
              Re-plan
            </a-button>
            
            <a-button 
              type="text" 
              size="small"
              @click="handleAdjustPlan"
              :loading="adjusting"
            >
              <SettingOutlined />
              Adjust
            </a-button>
            
            <a-button 
              type="text" 
              size="small"
              @click="handleClearChat"
            >
              <DeleteOutlined />
              Clear
            </a-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { 
  MessageOutlined,
  CloseOutlined,
  ExpandOutlined,
  CompressOutlined,
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  LikeOutlined,
  MoreOutlined,
  SendOutlined,
  EditOutlined,
  SettingOutlined,
  DeleteOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { chatAPI } from '../../mock/api'

const props = defineProps({
  reportId: {
    type: String,
    default: null
  },
  initialContext: {
    type: Object,
    default: null
  },
  showFloatButton: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['context-change', 'interaction'])

const chatPanelVisible = ref(false)
const panelExpanded = ref(false)
const messagesContainer = ref(null)

const isTyping = ref(false)
const inputText = ref('')
const messages = ref([])
const currentContext = ref(null)
const smartSuggestions = ref([])

const replanning = ref(false)
const adjusting = ref(false)

const quickTriggers = ref([
  { type: 'summarize', label: 'Summarize', icon: BarChartOutlined, loading: false },
  { type: 'analyze_trends', label: 'Analyze Trends', icon: LineChartOutlined, loading: false },
  { type: 'compare_periods', label: 'Compare Periods', icon: PieChartOutlined, loading: false }
])

watch(() => props.initialContext, (newContext) => {
  if (newContext) {
    setContext(newContext)
  }
}, { immediate: true })

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const addMessage = (messageData) => {
  messages.value.push({
    ...messageData,
    id: messageData.id || `msg_${Date.now()}`
  })
  scrollToBottom()
}

const handleSendMessage = async () => {
  if (!inputText.value.trim()) return

  const userMessage = {
    role: 'user',
    content: inputText.value,
    timestamp: new Date().toISOString()
  }
  addMessage(userMessage)
  
  const messageContent = inputText.value
  inputText.value = ''
  
  await sendMessage(messageContent)
}

const sendMessage = async (messageContent) => {
  isTyping.value = true
  try {
    const response = await chatAPI.triggerReportChat(props.reportId, {
      query: messageContent,
      context: currentContext.value
    })
    
    if (response.success && response.data.reply) {
      addMessage({
        role: 'assistant',
        content: response.data.reply,
        suggestions: response.data.suggestions,
        quickReplies: response.data.quickReplies,
        timestamp: new Date().toISOString()
      })
      
      if (response.data.context) {
        setContext(response.data.context)
      }
      
      if (response.data.smartSuggestions) {
        smartSuggestions.value = response.data.smartSuggestions
      }
    } else {
      throw new Error('Invalid response from AI assistant')
    }
  } catch (error) {
    addMessage({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.',
      timestamp: new Date().toISOString()
    })
  } finally {
    isTyping.value = false
  }
}

const handleQuickChat = async (trigger) => {
  trigger.loading = true
  await sendMessage(`Please ${trigger.type} the current report.`)
  trigger.loading = false
}

const setContext = (context) => {
  currentContext.value = context
  emit('context-change', context)
}

const toggleChatPanel = () => {
  chatPanelVisible.value = !chatPanelVisible.value
}

const closeChatPanel = () => {
  chatPanelVisible.value = false
}

const togglePanelSize = () => {
  panelExpanded.value = !panelExpanded.value
}

const handleCopyMessage = (msg) => {
  navigator.clipboard.writeText(msg.content)
  message.success('Copied to clipboard')
}

const handleLikeMessage = (msg) => {
  msg.liked = !msg.liked
}

const handleSuggestionAction = (suggestion) => {
  sendMessage(`Regarding my last message, I'd like to ${suggestion.label}.`)
}

const handleQuickReply = (text) => {
  inputText.value = text
  handleSendMessage()
}

const handleSuggestionClick = (suggestion) => {
  inputText.value = suggestion
  handleSendMessage()
}

const handleClearChat = () => {
  messages.value = []
}

const handleReplanRequest = async () => {
  replanning.value = true
  await sendMessage("Based on this, please generate a new health plan.")
  replanning.value = false
}

const handleAdjustPlan = async () => {
  adjusting.value = true
  await sendMessage("Let's adjust the current recommendations.")
  adjusting.value = false
}

const getDataLabel = (key) => {
  const labels = {
    average: 'Average',
    trend: 'Trend',
    comparison: 'Comparison'
  }
  return labels[key] || key
}

const formatDataValue = (value, key) => {
  if (key === 'trend' && typeof value === 'number') {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
  }
  return value
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

</script>

<style scoped>
.chat-integration {
  position: relative;
}

.quick-chat-triggers {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}

.chat-panel {
  position: fixed;
  right: 24px;
  bottom: 88px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 1000;
}

.panel-expanded {
  width: 600px;
  height: 80vh;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.panel-title {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-item.assistant {
  justify-content: flex-start;
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.user .message-content {
  background: #1890ff;
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.message-item.assistant .message-content {
  background: #f0f2f5;
  border-radius: 16px 16px 16px 4px;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  order: 2;
  background: #bae7ff;
}

.message-content {
  padding: 12px;
  max-width: 80%;
}

.message-time {
  font-size: 10px;
  color: #b0b0b0;
  margin-top: 4px;
}

.message-item.user .message-time {
  text-align: right;
  color: rgba(255, 255, 255, 0.7);
}

.input-area {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.input-container {
  display: flex;
  gap: 8px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.typing-dots span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #b0b0b0;
  animation: typing 1s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { opacity: 0.3; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-3px); }
}
</style>
