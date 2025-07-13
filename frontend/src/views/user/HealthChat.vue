<template>
  <div class="h-full flex flex-col bg-background">
    <!-- 主聊天界面 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 消息列表 -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-6">
        <!-- 欢迎信息 -->
        <div v-if="messages.length === 0" class="welcome-message text-center">
          <div class="inline-block p-4 bg-secondary rounded-2xl mb-4">
              <svg class="w-10 h-10 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8.625 9.75a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375m-13.5 3.01c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.184-4.183a1.14 1.14 0 01.778-.332 48.294 48.294 0 005.83-.498c1.585-.233 2.708-1.626 2.708-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
              </svg>
          </div>
          <h2 class="text-2xl font-bold text-text-primary">AuraWell 健康助手</h2>
          <p class="text-text-secondary mt-2">我可以帮助您分析健康数据、制定计划、获取建议等。</p>
        </div>
        
        <ChatMessage 
          v-for="msg in messages" 
          :key="msg.id" 
          :message="msg"
        />
        <TypingIndicator v-if="isTyping" />
      </div>

      <!-- 底部输入区域 -->
      <div class="p-4 bg-white border-t border-border">
        <!-- 快速建议 -->
        <div class="flex items-center space-x-2 mb-3 overflow-x-auto pb-2">
            <button 
                v-for="suggestion in quickStartSuggestions" 
                :key="suggestion"
                @click="sendQuickSuggestion(suggestion)"
                class="px-4 py-2 text-sm font-medium text-primary bg-secondary rounded-full whitespace-nowrap hover:bg-primary/20 transition-colors"
            >
                {{ suggestion }}
            </button>
        </div>

        <!-- 输入框和发送按钮 -->
        <div class="relative">
          <CommandPalette
            ref="commandPaletteRef"
            :visible="showCommandPalette"
            :commands="availableCommands"
            :filter="commandFilter"
            @select="onCommandSelect"
          />
          <textarea
            v-model="inputMessage"
            @input="handleInput"
            @keydown="handleKeyDown"
            placeholder="输入 / 获取命令提示..."
            class="w-full py-3 pl-4 pr-28 text-base bg-background-alt border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
            rows="1"
            ref="inputArea"
          ></textarea>
          <button 
            @click="sendMessage"
            :disabled="!inputMessage.trim() || isTyping"
            class="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-primary text-white hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- 历史记录侧边栏 (可选) -->
    <aside v-if="showConversationHistory" class="w-80 bg-background-alt border-l border-border p-4">
      <h3 class="text-lg font-semibold text-text-primary mb-4">对话历史</h3>
      <!-- 历史记录列表 -->
    </aside>
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
import { PaperAirplaneIcon } from '@heroicons/vue/24/solid'

import ChatMessage from '../../components/chat/ChatMessage.vue'
import TypingIndicator from '../../components/chat/TypingIndicator.vue'
import CommandPalette from '../../components/chat/CommandPalette.vue'
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
const inputArea = ref(null)
const commandPaletteRef = ref(null)
const showCommandPalette = ref(false)
const commandFilter = ref('')
const messageHistory = ref([])
let historyIndex = -1

// 快速开始建议
const quickStartSuggestions = ref([
  '帮我制定一个减脂计划',
  '如何改善我的睡眠质量？',
  '分析我最近的运动数据'
])

const availableCommands = ref([
    { name: '/rag', description: '使用RAG知识库进行搜索' },
    { name: '/clear', description: '清除当前对话' },
    { name: '/help', description: '显示帮助信息' },
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

watch(inputMessage, () => {
    nextTick(() => {
        const el = inputArea.value;
        if (el) {
            el.style.height = 'auto';
            el.style.height = (el.scrollHeight) + 'px';
        }
    });
});

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
  const messageText = inputMessage.value.trim();

  // Handle commands
  if (messageText.startsWith('/')) {
    const [command] = messageText.split(' ');
    switch (command) {
      case '/clear':
        messages.value = [];
        antMessage.success('对话已清除');
        inputMessage.value = '';
        return;
      case '/help':
        messages.value.push({
          id: Date.now(),
          sender: 'assistant',
          content: '可用命令: /rag [查询], /clear, /help',
          timestamp: new Date().toISOString()
        });
        inputMessage.value = '';
        return;
      case '/rag':
        // RAG command is handled below
        break;
      default:
        antMessage.error(`未知命令: ${command}`);
        inputMessage.value = '';
        return;
    }
  }

  messageHistory.value.push(messageText);
  historyIndex = messageHistory.value.length;

  // 检查是否是RAG指令
  if (messageText.startsWith('/rag ')) {
    await handleRAGCommand(messageText)
    return
  }

  // 🔐 发送消息前确保认证状态
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    console.warn('⚠️ 用户未认证，尝试重新认证...')
    const isAuthenticated = await authStore.ensureAuthenticated()
    if (!isAuthenticated) {
      antMessage.error('认证失败，请刷新页面重试')
      return
    }
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
    console.log('📤 发送消息到AI引擎:', messageText)

    // 发送消息到后端
    const response = await HealthChatAPI.sendMessage(messageText, currentConversationId.value)

    console.log('📥 收到AI回复:', response)

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
    console.log('✅ 消息发送成功')
  } catch (error) {
    console.error('发送消息失败:', error)

    // 检查是否是认证错误
    if (error.response?.status === 401) {
      console.warn('🔐 认证失败，清除token并提示重新登录')
      authStore.clearToken()
      antMessage.error('认证已过期，请刷新页面重新登录')
    } else {
      // 添加错误消息
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'agent',
        content: '抱歉，我现在遇到了一些技术问题。请稍后再试，或者尝试重新描述您的问题。',
        timestamp: new Date().toISOString()
      }

      messages.value.push(errorMessage)
      antMessage.error('发送消息失败，请检查网络连接')
    }
  } finally {
    isTyping.value = false
    nextTick(() => {
        const el = inputArea.value;
        if (el) {
            el.style.height = 'auto';
        }
    });
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

  // 显示加载状态
  isTyping.value = true
  scrollToBottom()

  try {
    // 直接发送RAG命令到后端，让后端处理RAG逻辑
    const response = await HealthChatAPI.sendMessage(command, currentConversationId.value)

    // 添加AI回复，包含RAG结果
    const aiMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      content: response.reply || response.data?.reply || response.data?.content || '抱歉，RAG检索失败。',
      timestamp: new Date().toISOString(),
      type: 'rag_response',
      ragResults: response.data?.rag_results || [],
      ragQuery: query,
      ragCount: response.data?.rag_count || 0
    }

    messages.value.push(aiMessage)

  } catch (error) {
    console.error('RAG检索失败:', error)

    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      sender: 'agent',
      type: 'error',
      content: `RAG检索失败: ${error.message || '未知错误'}`,
      timestamp: new Date().toISOString()
    }
    messages.value.push(errorMessage)
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

const handleInput = (e) => {
    const text = e.target.value;
    if (text.startsWith('/')) {
        showCommandPalette.value = true;
        commandFilter.value = text;
    } else {
        showCommandPalette.value = false;
    }
}

const handleKeyDown = (e) => {
    if (showCommandPalette.value) {
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                commandPaletteRef.value?.onArrowUp();
                break;
            case 'ArrowDown':
                e.preventDefault();
                commandPaletteRef.value?.onArrowDown();
                break;
            case 'Enter':
                e.preventDefault();
                commandPaletteRef.value?.onEnter();
                break;
            case 'Escape':
                showCommandPalette.value = false;
                break;
        }
    } else if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    } else if (e.key === 'ArrowUp' && !inputMessage.value) {
        if (historyIndex > 0) {
            historyIndex--;
            inputMessage.value = messageHistory.value[historyIndex];
        }
    } else if (e.key === 'ArrowDown' && !inputMessage.value) {
        if (historyIndex < messageHistory.value.length - 1) {
            historyIndex++;
            inputMessage.value = messageHistory.value[historyIndex];
        } else {
            historyIndex = messageHistory.value.length;
            inputMessage.value = '';
        }
    }
}

const onCommandSelect = (command) => {
    inputMessage.value = command + ' ';
    showCommandPalette.value = false;
    nextTick(() => {
        inputArea.value?.focus();
    });
}

const sendQuickSuggestion = (suggestion) => {
    inputMessage.value = suggestion;
    sendMessage();
};

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
/* 聊天页面样式使用新的aura设计系统 */

/* 聊天输入区域的阴影，使其悬浮 */
.chat-input-area {
  box-shadow: 0 -4px 20px rgba(0,0,0,0.04);
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
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 32px;
  border: 1px solid #e2e8f0;
}

.welcome-message h2 {
  color: #1f2937;
  margin-bottom: 16px;
  font-weight: 700;
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
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.quick-start-suggestions h4 {
  margin-bottom: 20px;
  color: #1f2937;
  font-weight: 600;
}

.suggestion-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggestion-btn {
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
  background: white;
  color: #64748b;
}

.suggestion-btn:hover {
  background: linear-gradient(120deg, #a0e9ff, #a1c4fd, #c2e9fb);
  border-color: transparent;
  color: #1f2937;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(160, 233, 255, 0.25);
}

.chat-input-area {
  background: white;
  border-top: 1px solid #e2e8f0;
  padding: 24px 32px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
  border-radius: 16px 16px 0 0;
}

.input-container {
  display: flex;
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.message-input:focus {
  border-color: #a0e9ff;
  box-shadow: 0 0 0 3px rgba(160, 233, 255, 0.1);
}

.send-button {
  border-radius: 12px;
  height: 44px;
  padding: 0 24px;
  font-weight: 600;
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
  margin-bottom: 16px;
}

.rag-alert {
  border-radius: 12px;
  font-size: 13px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
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
    padding: 16px 20px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .chat-messages {
    padding: 20px 0;
  }

  .welcome-section {
    padding: 0 20px;
  }

  .welcome-message {
    padding: 32px 24px;
  }

  .suggestion-buttons {
    flex-direction: column;
  }

  .chat-input-area {
    padding: 20px 24px;
  }

  .input-container {
    flex-direction: column;
    gap: 12px;
  }

  .send-button {
    width: 100%;
    height: 48px;
  }
}
</style>
