<template>
  <div class="health-chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="agent-info">
          <a-avatar :size="48" :style="{ backgroundColor: '#52c41a' }">
            <template #icon>
              <robot-outlined />
            </template>
          </a-avatar>
          <div class="agent-details">
            <h3>AuraWell 健康助手</h3>
            <p>您的专属健康管理顾问，随时为您提供个性化建议</p>
          </div>
        </div>
        <div class="chat-actions">
          <a-button type="text" @click="showConversationHistory = true">
            <template #icon><history-outlined /></template>
            历史对话
          </a-button>
          <a-button type="text" @click="clearCurrentChat">
            <template #icon><clear-outlined /></template>
            清空对话
          </a-button>
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-section">
        <div class="welcome-message">
          <h2>👋 欢迎使用 AuraWell 健康助手</h2>
          <p>我是您的专属健康管理顾问，可以帮助您：</p>
          <ul>
            <li>🎯 制定个性化的健康目标</li>
            <li>📊 分析您的健康数据</li>
            <li>💪 提供运动和饮食建议</li>
            <li>😴 改善睡眠质量</li>
            <li>🧘 建立健康的生活习惯</li>
          </ul>
          <p>请告诉我您的健康目标或当前遇到的问题，让我们开始您的健康之旅吧！</p>
        </div>
        
        <!-- 快速开始建议 -->
        <div class="quick-start-suggestions">
          <h4>💡 快速开始</h4>
          <div class="suggestion-buttons">
            <a-button 
              v-for="suggestion in quickStartSuggestions" 
              :key="suggestion"
              type="default"
              class="suggestion-btn"
              @click="sendQuickMessage(suggestion)"
            >
              {{ suggestion }}
            </a-button>
          </div>
        </div>
      </div>

      <!-- 聊天消息列表 -->
      <div v-for="message in messages" :key="message.id">
        <ChatMessage 
          :message="message"
          @quick-reply="handleQuickReply"
          @suggestion-action="handleSuggestionAction"
        />
      </div>

      <!-- 打字指示器 -->
      <TypingIndicator :visible="isTyping" />
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <!-- RAG功能提示 -->
      <div class="rag-tip" v-if="!messages.length">
        <a-alert
          message="💡 智能检索功能"
          description="输入 /rag 您的问题 可以搜索相关医学文档，例如：/rag 高血压的饮食建议"
          type="info"
          show-icon
          closable
          class="rag-alert"
        />
      </div>

      <div class="input-container">
        <a-input
          v-model:value="inputMessage"
          placeholder="请输入您的健康问题或需求..."
          :disabled="isTyping || isRAGLoading"
          @press-enter="sendMessage"
          class="message-input"
          :maxlength="500"
          show-count
        />
        <a-button
          type="primary"
          :loading="isTyping || isRAGLoading"
          :disabled="!inputMessage.trim()"
          @click="sendMessage"
          class="send-button"
        >
          <template #icon><send-outlined /></template>
          {{ isRAGLoading ? '检索中...' : '发送' }}
        </a-button>
      </div>

      <!-- 输入提示 -->
      <div class="input-hints">
        <span class="hint-text">💡 提示：您可以询问关于运动、饮食、睡眠、健康目标等任何问题，或使用 /rag 指令进行文档检索</span>
      </div>
    </div>

    <!-- 对话历史抽屉 -->
    <a-drawer
      v-model:open="showConversationHistory"
      title="对话历史"
      placement="right"
      :width="400"
    >
      <div class="conversation-history">
        <a-list
          :data-source="conversationHistory"
          :loading="loadingHistory"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta
                :title="item.title"
                :description="item.lastMessage"
              >
                <template #avatar>
                  <a-avatar :style="{ backgroundColor: '#1890ff' }">
                    {{ item.date }}
                  </a-avatar>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a @click="loadConversation(item.id)">加载</a>
                <a @click="deleteConversation(item.id)" style="color: #ff4d4f">删除</a>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { message as antMessage } from 'ant-design-vue'
import {
  RobotOutlined,
  SendOutlined,
  HistoryOutlined,
  ClearOutlined
} from '@ant-design/icons-vue'

import ChatMessage from '../../components/chat/ChatMessage.vue'
import TypingIndicator from '../../components/chat/TypingIndicator.vue'
import HealthChatAPI from '../../api/chat.js'
import { UserAPI } from '../../api/user.js'
import { useAuthStore } from '../../stores/auth.js'
import { useChatStore } from '../../stores/chat.js'
import request from '../../utils/request.js'

// 使用stores
const { user } = useAuthStore()
const { performRAGSearch, isRAGLoading, ragError, ragStatus } = useChatStore()

// 响应式数据
const inputMessage = ref('')
const messages = ref([])
const isTyping = ref(false)
const messagesContainer = ref(null)
const showConversationHistory = ref(false)
const conversationHistory = ref([])
const loadingHistory = ref(false)
const currentConversationId = ref(null)

// 快速开始建议
const quickStartSuggestions = ref([
  '我想制定一个减重计划',
  '如何改善我的睡眠质量？',
  '请帮我分析我的运动数据',
  '我需要营养饮食建议',
  '如何建立健康的作息习惯？',
  '/rag 高血压的饮食建议',
  '/rag 糖尿病的运动指导'
])

// 🚀 生命周期钩子 - 优化的初始化流程
onMounted(async () => {
  console.log('🎯 HealthChat 组件开始初始化...')
  
  try {
    // 🔑 第一步：严格的认证检查（必须成功后才能继续）
    console.log('🔍 第一步：执行认证检查...')
    await ensureAuthenticated()
    console.log('✅ 认证检查完成')
    
    // 🚀 第二步：初始化聊天功能（仅在认证成功后执行）
    console.log('🔍 第二步：初始化聊天功能...')
    await initializeChat()
    console.log('✅ 聊天功能初始化完成')
    
    // 🚀 第三步：加载历史对话（仅在聊天初始化成功后执行）
    console.log('🔍 第三步：加载历史对话...')
    await loadConversationHistory()
    console.log('✅ 历史对话加载完成')
    
    console.log('🎉 HealthChat 初始化全部完成！')
    
  } catch (error) {
    console.error('❌ HealthChat 初始化失败:', error)
    
    // 初始化失败时的容错处理
    antMessage.error('页面初始化失败，请稍后重试')
    
    // 如果是认证相关错误，不再重复处理（ensureAuthenticated已处理）
    // 如果是其他错误，显示友好提示
    if (!error.message?.includes('认证') && !error.message?.includes('Token')) {
      setTimeout(() => {
        window.location.reload()
      }, 3000)
    }
  }
})

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 🔧 简化认证逻辑 - 使用统一的认证状态管理
const ensureAuthenticated = async () => {
  try {
    const authStore = useAuthStore()

    // 使用统一的认证检查方法
    const isAuthenticated = await authStore.ensureAuthenticated()

    if (isAuthenticated) {
      console.log('✅ 用户认证成功')
      return true
    } else {
      console.warn('⚠️ 用户认证失败')
      antMessage.error('认证失败，请刷新页面重试')
      return false
    }
  } catch (error) {
    console.error('❌ 认证检查异常:', error)
    antMessage.error('认证异常，请刷新页面重试')
    return false
  }
}

// 🔧 自动登录逻辑已移至统一认证状态管理中

const initializeChat = async () => {
  try {
    // 创建新对话
    const response = await HealthChatAPI.createConversation()
    if (response.conversation_id || response.data?.conversation_id) {
      currentConversationId.value = response.conversation_id || response.data.conversation_id
    }
  } catch (error) {
    console.error('初始化聊天失败:', error)
    // 使用本地生成的对话ID
    currentConversationId.value = `local_${Date.now()}`
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return

  const messageText = inputMessage.value.trim()

  // 检查是否是RAG指令
  if (messageText.startsWith('/rag ')) {
    await handleRAGCommand(messageText)
    return
  }

  const userMessage = {
    id: Date.now(),
    sender: 'user',
    content: messageText,
    timestamp: new Date().toISOString()
  }

  // 添加用户消息
  messages.value.push(userMessage)
  inputMessage.value = ''

  // 显示打字指示器
  isTyping.value = true

  try {
    // 发送消息到后端
    const response = await HealthChatAPI.sendMessage(messageText, currentConversationId.value)

    // 模拟延迟以显示打字效果
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 添加AI回复
    const aiMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      content: response.reply || response.data?.reply || response.data?.content || '抱歉，我现在无法处理您的请求，请稍后再试。',
      timestamp: new Date().toISOString(),
      suggestions: response.suggestions || response.data?.suggestions || [],
      quickReplies: response.quick_replies || response.data?.quickReplies || []
    }

    messages.value.push(aiMessage)
  } catch (error) {
    console.error('发送消息失败:', error)

    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      content: '抱歉，我现在遇到了一些技术问题。请稍后再试，或者尝试重新描述您的问题。',
      timestamp: new Date().toISOString()
    }

    messages.value.push(errorMessage)
    antMessage.error('发送消息失败，请检查网络连接')
  } finally {
    isTyping.value = false
  }
}

// 处理RAG指令
const handleRAGCommand = async (command) => {
  const query = command.replace('/rag ', '').trim()

  if (!query) {
    const helpMessage = {
      id: Date.now(),
      sender: 'agent',
      type: 'help',
      content: '使用方法：/rag 您的查询内容\n例如：/rag 高血压的饮食建议',
      timestamp: new Date().toISOString()
    }
    messages.value.push(helpMessage)
    inputMessage.value = ''
    return
  }

  // 添加用户RAG查询消息
  const userMessage = {
    id: Date.now(),
    sender: 'user',
    type: 'rag_query',
    content: `🔍 RAG检索: ${query}`,
    timestamp: new Date().toISOString()
  }
  messages.value.push(userMessage)
  inputMessage.value = ''

  // 执行RAG检索
  try {
    await performRAGSearch(query, 3)
  } catch (error) {
    console.error('RAG检索失败:', error)
  }
}

const sendQuickMessage = (suggestionText) => {
  inputMessage.value = suggestionText
  sendMessage()
}

const handleQuickReply = (reply) => {
  inputMessage.value = reply.text || reply
  sendMessage()
}

const handleSuggestionAction = (action) => {
  console.log('处理建议操作:', action)
  // 这里可以根据action类型执行不同的操作
  // 比如跳转到特定页面、打开模态框等
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const clearCurrentChat = () => {
  messages.value = []
  antMessage.success('对话已清空')
}

const loadConversationHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await HealthChatAPI.getConversations()
    conversationHistory.value = response.conversations || response.data?.conversations || response.data || []
  } catch (error) {
    console.error('加载对话历史失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

const loadConversation = async (conversationId) => {
  try {
    const response = await HealthChatAPI.getConversationHistory(conversationId)
    messages.value = response.data || []
    currentConversationId.value = conversationId
    showConversationHistory.value = false
    antMessage.success('对话已加载')
  } catch (error) {
    console.error('加载对话失败:', error)
    antMessage.error('加载对话失败')
  }
}

const deleteConversation = async (conversationId) => {
  try {
    await HealthChatAPI.deleteConversation(conversationId)
    await loadConversationHistory()
    antMessage.success('对话已删除')
  } catch (error) {
    console.error('删除对话失败:', error)
    antMessage.error('删除对话失败')
  }
}
</script>

<style scoped>
.health-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.agent-details h3 {
  margin: 0;
  font-size: 18px;
  color: #262626;
}

.agent-details p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #8c8c8c;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.welcome-section {
  padding: 0 24px;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.welcome-message {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.welcome-message h2 {
  color: #52c41a;
  margin-bottom: 16px;
}

.welcome-message ul {
  text-align: left;
  max-width: 400px;
  margin: 16px auto;
}

.welcome-message li {
  margin: 8px 0;
  color: #595959;
}

.quick-start-suggestions {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.quick-start-suggestions h4 {
  margin-bottom: 16px;
  color: #262626;
}

.suggestion-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggestion-btn {
  border-radius: 20px;
  border: 1px solid #d9d9d9;
  transition: all 0.3s;
}

.suggestion-btn:hover {
  border-color: #52c41a;
  color: #52c41a;
}

.chat-input-area {
  background: white;
  border-top: 1px solid #e8e8e8;
  padding: 16px 24px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.input-container {
  display: flex;
  gap: 12px;
  max-width: 1200px;
  margin: 0 auto;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  border-radius: 20px;
}

.send-button {
  border-radius: 20px;
  height: 40px;
  padding: 0 20px;
}

.input-hints {
  margin-top: 8px;
  text-align: center;
}

.hint-text {
  font-size: 12px;
  color: #8c8c8c;
}

/* RAG功能提示样式 */
.rag-tip {
  margin-bottom: 12px;
}

.rag-alert {
  border-radius: 8px;
  font-size: 12px;
}

.conversation-history {
  height: 100%;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .chat-messages {
    padding: 16px 0;
  }

  .welcome-section {
    padding: 0 16px;
  }

  .welcome-message {
    padding: 24px 20px;
  }

  .suggestion-buttons {
    flex-direction: column;
  }

  .chat-input-area {
    padding: 12px 16px;
  }

  .input-container {
    flex-direction: column;
    gap: 8px;
  }

  .send-button {
    width: 100%;
  }
}
</style>
