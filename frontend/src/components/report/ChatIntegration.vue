<template>
  <div class="chat-integration">
    <!-- 快速对话触发器 -->
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
    
    <!-- 浮动聊天按钮 -->
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
    
    <!-- 侧边聊天面板 -->
    <div 
      v-if="chatPanelVisible" 
      class="chat-panel"
      :class="{ 'panel-expanded': panelExpanded }"
    >
      <div class="panel-header">
        <div class="panel-title">
          <MessageOutlined />
          AI健康助手
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
        <!-- 对话上下文 -->
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
        
        <!-- 消息列表 -->
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
              
              <!-- 消息操作 -->
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
              
              <!-- 快速回复 -->
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
          
          <!-- 加载指示器 -->
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
        
        <!-- 输入区域 -->
        <div class="input-area">
          <!-- 智能建议 -->
          <div v-if="smartSuggestions.length" class="smart-suggestions">
            <div class="suggestions-label">智能建议:</div>
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
          
          <!-- 输入框 -->
          <div class="input-container">
            <a-input
              v-model:value="inputText"
              placeholder="输入您的问题或想法..."
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
          
          <!-- 功能按钮 -->
          <div class="function-buttons">
            <a-button 
              type="text" 
              size="small"
              @click="handleReplanRequest"
              :loading="replanning"
            >
              <EditOutlined />
              重新规划
            </a-button>
            
            <a-button 
              type="text" 
              size="small"
              @click="handleAdjustPlan"
              :loading="adjusting"
            >
              <SettingOutlined />
              微调方案
            </a-button>
            
            <a-button 
              type="text" 
              size="small"
              @click="handleClearChat"
            >
              <DeleteOutlined />
              清空对话
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
  RadarChartOutlined,
  HeatMapOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { chatAPI, healthPlanAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  reportData: {
    type: Object,
    default: () => ({})
  },
  showFloatButton: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['chat-started', 'plan-updated', 'context-changed'])

// 响应式数据
const chatPanelVisible = ref(false)
const panelExpanded = ref(false)
const messages = ref([])
const inputText = ref('')
const isTyping = ref(false)
const currentContext = ref(null)
const currentSessionId = ref(null)
const messagesContainer = ref(null)
const replanning = ref(false)
const adjusting = ref(false)

// 快速触发器
const quickTriggers = ref([
  {
    type: 'trend_analysis',
    label: '趋势分析',
    icon: LineChartOutlined,
    loading: false
  },
  {
    type: 'data_insight',
    label: '数据洞察',
    icon: BarChartOutlined,
    loading: false
  },
  {
    type: 'health_advice',
    label: '健康建议',
    icon: RadarChartOutlined,
    loading: false
  },
  {
    type: 'pattern_analysis',
    label: '模式分析',
    icon: HeatMapOutlined,
    loading: false
  }
])

// 智能建议
const smartSuggestions = computed(() => {
  if (!currentContext.value) {
    return ['我想了解我的健康状况', '如何改善睡眠质量？', '制定运动计划']
  }
  
  const contextType = currentContext.value.type
  const suggestions = {
    chart_analysis: ['这个趋势说明什么？', '如何改善这个指标？', '设定新的目标'],
    insight_discussion: ['这个建议可行吗？', '有其他方案吗？', '如何开始执行？'],
    plan_adjustment: ['调整运动强度', '修改饮食计划', '设置提醒']
  }
  
  return suggestions[contextType] || []
})

// 方法
const toggleChatPanel = () => {
  chatPanelVisible.value = !chatPanelVisible.value
  if (chatPanelVisible.value && messages.value.length === 0) {
    // 发送欢迎消息
    addWelcomeMessage()
  }
}

const closeChatPanel = () => {
  chatPanelVisible.value = false
}

const togglePanelSize = () => {
  panelExpanded.value = !panelExpanded.value
}

const addWelcomeMessage = () => {
  const welcomeMessage = {
    id: Date.now(),
    role: 'assistant',
    content: '您好！我是您的AI健康助手。我可以帮您分析健康数据、解读报告内容、调整健康计划。有什么我可以帮助您的吗？',
    timestamp: new Date().toISOString(),
    quickReplies: [
      { text: '分析我的健康趋势' },
      { text: '解读报告内容' },
      { text: '调整健康计划' }
    ]
  }
  
  messages.value.push(welcomeMessage)
  scrollToBottom()
}

const handleQuickChat = async (trigger) => {
  trigger.loading = true
  
  try {
    // 设置对话上下文
    const context = {
      type: trigger.type,
      title: trigger.label,
      description: getContextDescription(trigger.type),
      icon: trigger.icon,
      data: getContextData(trigger.type)
    }
    
    setContext(context)
    
    // 打开聊天面板
    if (!chatPanelVisible.value) {
      chatPanelVisible.value = true
    }
    
    // 发送初始分析消息
    const initialMessage = generateInitialMessage(trigger.type)
    await sendMessage(initialMessage, false)
    
  } catch (error) {
    console.error('快速对话启动失败:', error)
    message.error('启动对话失败')
  } finally {
    trigger.loading = false
  }
}

const setContext = (context) => {
  currentContext.value = context
  emit('context-changed', context)
}

const getContextDescription = (type) => {
  const descriptions = {
    trend_analysis: '分析您的健康数据变化趋势',
    data_insight: '深度解读您的健康数据',
    health_advice: '基于数据提供个性化建议',
    pattern_analysis: '分析您的健康行为模式'
  }
  return descriptions[type] || '健康数据分析'
}

const getContextData = (type) => {
  // 根据类型返回相关的上下文数据
  const reportMetrics = props.reportData.metrics || {}
  
  switch (type) {
    case 'trend_analysis':
      return {
        weight_change: reportMetrics.weight?.change || 0,
        exercise_trend: reportMetrics.exercise?.trend || 'stable',
        sleep_avg: reportMetrics.sleep?.avg_duration || 0
      }
    case 'data_insight':
      return {
        health_score: props.reportData.health_score?.overall || 0,
        improvement: props.reportData.health_score?.improvement || 0
      }
    default:
      return null
  }
}

const generateInitialMessage = (type) => {
  const messages = {
    trend_analysis: '我来为您分析最近的健康数据趋势。从您的数据来看...',
    data_insight: '让我为您深度解读这些健康数据的含义...',
    health_advice: '基于您的健康数据，我为您准备了一些个性化建议...',
    pattern_analysis: '我发现了您健康行为中的一些有趣模式...'
  }
  return messages[type] || '让我们开始分析您的健康数据。'
}

const handleSendMessage = async () => {
  if (!inputText.value.trim()) return
  
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: inputText.value,
    timestamp: new Date().toISOString()
  }
  
  messages.value.push(userMessage)
  const messageContent = inputText.value
  inputText.value = ''
  
  await sendMessage(messageContent, true)
}

const sendMessage = async (content, isUserMessage = true) => {
  if (!isUserMessage) {
    // 直接添加AI消息
    const aiMessage = {
      id: Date.now(),
      role: 'assistant',
      content,
      timestamp: new Date().toISOString(),
      suggestions: generateSuggestions(content),
      quickReplies: generateQuickReplies(content)
    }
    
    messages.value.push(aiMessage)
    scrollToBottom()
    return
  }
  
  isTyping.value = true
  scrollToBottom()
  
  try {
    // 创建或使用现有会话
    if (!currentSessionId.value) {
      const session = await chatAPI.createChatSession('健康报告分析')
      currentSessionId.value = session.data.session_id
    }
    
    const response = await chatAPI.sendMessage(content, currentSessionId.value)
    
    const aiMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: response.data.content,
      timestamp: new Date().toISOString(),
      suggestions: response.data.suggestions || [],
      quickReplies: response.data.quickReplies || []
    }
    
    messages.value.push(aiMessage)
    
  } catch (error) {
    console.error('发送消息失败:', error)
    message.error('发送消息失败')
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const handleQuickReply = (text) => {
  inputText.value = text
  handleSendMessage()
}

const handleSuggestionClick = (suggestion) => {
  inputText.value = suggestion
  handleSendMessage()
}

const handleCopyMessage = (msg) => {
  navigator.clipboard.writeText(msg.content)
  message.success('消息已复制')
}

const handleLikeMessage = (msg) => {
  msg.liked = !msg.liked
  message.success(msg.liked ? '感谢您的反馈' : '反馈已取消')
}

const handleSuggestionAction = (suggestion) => {
  // 处理建议操作
  console.log('执行建议:', suggestion)
}

const handleReplanRequest = async () => {
  replanning.value = true
  
  try {
    const replanMessage = '我想重新制定我的健康计划，请基于当前的数据和目标为我生成新的方案。'
    await sendMessage(replanMessage, false)
    
    // 模拟重新规划过程
    setTimeout(async () => {
      const planMessage = '好的，我正在为您重新制定健康计划。基于您最近的数据表现和健康目标，我建议...'
      await sendMessage(planMessage, false)
      
      emit('plan-updated', { type: 'replan', context: currentContext.value })
    }, 1000)
    
  } catch (error) {
    console.error('重新规划失败:', error)
    message.error('重新规划失败')
  } finally {
    replanning.value = false
  }
}

const handleAdjustPlan = async () => {
  adjusting.value = true
  
  try {
    const adjustMessage = '让我为您微调当前的健康方案，保持主要框架不变，只优化具体的执行细节。'
    await sendMessage(adjustMessage, false)
    
    emit('plan-updated', { type: 'adjust', context: currentContext.value })
    
  } catch (error) {
    console.error('方案调整失败:', error)
    message.error('方案调整失败')
  } finally {
    adjusting.value = false
  }
}

const handleClearChat = () => {
  messages.value = []
  currentContext.value = null
  currentSessionId.value = null
  addWelcomeMessage()
}

const generateSuggestions = (content) => {
  // 基于消息内容生成操作建议
  return [
    { action: 'create_plan', label: '创建计划' },
    { action: 'set_reminder', label: '设置提醒' },
    { action: 'view_details', label: '查看详情' }
  ]
}

const generateQuickReplies = (content) => {
  // 基于消息内容生成快速回复
  if (content.includes('建议')) {
    return [
      { text: '这个建议很好' },
      { text: '有其他方案吗？' },
      { text: '如何开始执行？' }
    ]
  }
  return []
}

const getDataLabel = (key) => {
  const labels = {
    weight_change: '体重变化',
    exercise_trend: '运动趋势',
    sleep_avg: '平均睡眠',
    health_score: '健康评分',
    improvement: '改善程度'
  }
  return labels[key] || key
}

const formatDataValue = (value, key) => {
  if (typeof value === 'number') {
    if (key.includes('weight')) return value.toFixed(1) + 'kg'
    if (key.includes('sleep')) return value.toFixed(1) + '小时'
    if (key.includes('score')) return value + '分'
    return value.toString()
  }
  return value
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听器
watch(chatPanelVisible, (visible) => {
  if (visible) {
    emit('chat-started')
  }
})

// 暴露方法给父组件
defineExpose({
  startChat: (context) => {
    setContext(context)
    if (!chatPanelVisible.value) {
      toggleChatPanel()
    }
  },
  sendMessage: (content) => {
    sendMessage(content, false)
  }
})
</script>

<style scoped>
.chat-integration {
  position: relative;
}

.quick-chat-triggers {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.trigger-button {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.trigger-button:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.chat-panel {
  position: fixed;
  right: 24px;
  bottom: 80px;
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transition: all 0.3s ease;
}

.panel-expanded {
  width: 600px;
  height: 700px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  border-radius: 12px 12px 0 0;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.panel-controls {
  display: flex;
  gap: 4px;
}

.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-context {
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #f0f0f0;
}

.context-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.context-icon {
  color: #1890ff;
  font-size: 16px;
}

.context-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.context-desc {
  font-size: 12px;
  color: #8c8c8c;
}

.context-data {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.data-item {
  font-size: 12px;
}

.data-label {
  color: #8c8c8c;
}

.data-value {
  color: #262626;
  font-weight: 600;
  margin-left: 4px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-item {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: #1890ff;
  color: white;
}

.message-content {
  flex: 1;
  max-width: calc(100% - 40px);
}

.message-text {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-item.user .message-text {
  background: #1890ff;
  color: white;
}

.message-time {
  font-size: 11px;
  color: #8c8c8c;
  margin-top: 4px;
  text-align: right;
}

.message-item.user .message-time {
  text-align: left;
}

.message-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

.message-actions .ant-btn.liked {
  color: #1890ff;
}

.quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.quick-reply-btn {
  font-size: 12px;
  height: 24px;
  padding: 0 8px;
  border-radius: 12px;
}

.typing-indicator {
  display: flex;
  gap: 8px;
  align-items: center;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 12px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #8c8c8c;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
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

.input-area {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
}

.smart-suggestions {
  margin-bottom: 12px;
}

.suggestions-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 6px;
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suggestion-tag {
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.suggestion-tag:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}

.input-container {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.message-input {
  flex: 1;
}

.send-button {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.function-buttons {
  display: flex;
  justify-content: space-between;
}

.function-buttons .ant-btn {
  font-size: 12px;
  padding: 0 8px;
  height: 28px;
}
</style>
