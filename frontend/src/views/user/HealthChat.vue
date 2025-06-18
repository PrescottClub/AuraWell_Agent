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
      <div class="input-container">
        <a-input
          v-model:value="inputMessage"
          placeholder="请输入您的健康问题或需求..."
          :disabled="isTyping"
          @press-enter="sendMessage"
          class="message-input"
          :maxlength="500"
          show-count
        />
        <a-button 
          type="primary" 
          :loading="isTyping"
          :disabled="!inputMessage.trim()"
          @click="sendMessage"
          class="send-button"
        >
          <template #icon><send-outlined /></template>
          发送
        </a-button>
      </div>
      
      <!-- 输入提示 -->
      <div class="input-hints">
        <span class="hint-text">💡 提示：您可以询问关于运动、饮食、睡眠、健康目标等任何问题</span>
        <span class="hint-text">🔍 输入 "/rag" 开头可以使用RAG文档检索功能</span>
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
import { useAuthStore } from '../../stores/auth.js'
import request from '../../utils/request.js'

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
  '如何建立健康的作息习惯？'
])

// 生命周期
onMounted(async () => {
  await ensureAuthenticated()
  await initializeChat()
  await loadConversationHistory()
})

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 方法
const ensureAuthenticated = async () => {
  try {
    const authStore = useAuthStore()

    // 检查是否已有token
    if (authStore.token) {
      console.log('用户已认证')
      return
    }

    // 自动登录（用于演示）
    console.log('正在自动登录...')
    const response = await request.post('/auth/login', {
      username: 'test_user',
      password: 'test_password'
    })

    if (response.data) {
      authStore.setToken(
        response.data.access_token,
        response.data.token_type,
        response.data.expires_in
      )
      console.log('自动登录成功')
    }
  } catch (error) {
    console.error('认证失败:', error)
    antMessage.error('认证失败，请刷新页面重试')
  }
}

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

  const userMessage = {
    id: Date.now(),
    sender: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString()
  }

  // 添加用户消息
  messages.value.push(userMessage)
  const messageText = inputMessage.value.trim()
  inputMessage.value = ''

  // 显示打字指示器
  isTyping.value = true

  try {
    // 🔍 检查是否为RAG查询
    if (messageText.startsWith('/rag ')) {
      await handleRAGQuery(messageText.substring(5).trim())
    } else {
      // 普通聊天消息
      await handleNormalChat(messageText)
    }
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

// RAG查询处理函数
const handleRAGQuery = async (query) => {
  try {
    console.log('🔍 执行RAG查询:', query)

    // 调用RAG API
    const response = await HealthChatAPI.retrieveRAGDocuments(query, 3)

    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 构造RAG响应消息
    let content = `🔍 **RAG文档检索结果**\n\n`
    content += `**查询**: ${query}\n`
    content += `**找到文档**: ${response.data.total_found} 个\n\n`

    if (response.data.results && response.data.results.length > 0) {
      content += `**相关文档**:\n`
      response.data.results.forEach((doc, index) => {
        content += `${index + 1}. ${doc}\n\n`
      })
    } else {
      content += `抱歉，没有找到与"${query}"相关的文档。`
    }

    const aiMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      content: content,
      timestamp: new Date().toISOString(),
      type: 'rag_result'
    }

    messages.value.push(aiMessage)
    antMessage.success(`RAG检索完成，找到 ${response.data.total_found} 个相关文档`)

  } catch (error) {
    console.error('RAG查询失败:', error)

    const errorMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      content: `🔍 **RAG检索失败**\n\n抱歉，RAG文档检索服务暂时不可用。\n\n错误信息: ${error.message || '未知错误'}`,
      timestamp: new Date().toISOString(),
      type: 'rag_error'
    }

    messages.value.push(errorMessage)
    antMessage.error('RAG检索失败')
  }
}

// 普通聊天处理函数
const handleNormalChat = async (messageText) => {
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
