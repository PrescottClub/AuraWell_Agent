import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import HealthChatAPI from '../api/chat.js';

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref([]);
  const currentConversationId = ref(null);
  const messages = ref([]);
  const isTyping = ref(false);
  const isLoading = ref(false);
  const userProfile = ref(null);

  // RAG相关状态
  const ragResults = ref([]);
  const isRAGLoading = ref(false);
  const ragError = ref(null);
  const ragStatus = ref(null);

  // 计算属性
  const currentConversation = computed(() => {
    return conversations.value.find(
      conv => conv.id === currentConversationId.value
    );
  });

  const hasActiveConversation = computed(() => {
    return currentConversationId.value !== null;
  });

  const messageCount = computed(() => {
    return messages.value.length;
  });

  // 操作方法
  const createNewConversation = async () => {
    try {
      isLoading.value = true;
      const response = await HealthChatAPI.createConversation();

      if (response.data) {
        const newConversation = {
          id: response.data.conversation_id,
          title: '新的健康咨询',
          createdAt: new Date().toISOString(),
          lastMessage: '',
          messageCount: 0,
        };

        conversations.value.unshift(newConversation);
        currentConversationId.value = newConversation.id;
        messages.value = [];

        return newConversation;
      }
    } catch (error) {
      console.error('创建对话失败:', error);
      // 创建本地对话
      const localConversation = {
        id: `local_${Date.now()}`,
        title: '新的健康咨询',
        createdAt: new Date().toISOString(),
        lastMessage: '',
        messageCount: 0,
        isLocal: true,
      };

      conversations.value.unshift(localConversation);
      currentConversationId.value = localConversation.id;
      messages.value = [];

      return localConversation;
    } finally {
      isLoading.value = false;
    }
  };

  const sendMessage = async messageText => {
    if (!messageText.trim() || isTyping.value) return null;

    // 创建用户消息
    const userMessage = {
      id: `msg_${Date.now()}`,
      sender: 'user',
      content: messageText.trim(),
      timestamp: new Date().toISOString(),
    };

    // 添加到消息列表
    messages.value.push(userMessage);

    // 设置打字状态
    isTyping.value = true;

    try {
      // 发送到后端
      const response = await HealthChatAPI.sendMessage(
        messageText,
        currentConversationId.value
      );

      // 创建AI回复消息
      const aiMessage = {
        id: `msg_${Date.now() + 1}`,
        sender: 'agent',
        content:
          response.data?.reply ||
          response.data?.content ||
          '抱歉，我现在无法处理您的请求。',
        timestamp: new Date().toISOString(),
        suggestions: response.data?.suggestions || [],
        quickReplies: response.data?.quickReplies || [],
      };

      // 添加AI回复
      messages.value.push(aiMessage);

      // 更新对话信息
      updateConversationLastMessage(aiMessage.content);

      return aiMessage;
    } catch (error) {
      console.error('发送消息失败:', error);

      // 添加错误消息
      const errorMessage = {
        id: `msg_${Date.now() + 1}`,
        sender: 'agent',
        content: '抱歉，我现在遇到了一些技术问题。请稍后再试。',
        timestamp: new Date().toISOString(),
      };

      messages.value.push(errorMessage);
      return errorMessage;
    } finally {
      isTyping.value = false;
    }
  };

  const loadConversations = async () => {
    try {
      isLoading.value = true;
      const response = await HealthChatAPI.getConversations();
      conversations.value = response.data || [];
    } catch (error) {
      console.error('加载对话列表失败:', error);
    } finally {
      isLoading.value = false;
    }
  };

  const loadConversationMessages = async conversationId => {
    try {
      isLoading.value = true;
      const response =
        await HealthChatAPI.getConversationHistory(conversationId);
      messages.value = response.data || [];
      currentConversationId.value = conversationId;
    } catch (error) {
      console.error('加载对话消息失败:', error);
      messages.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  const deleteConversation = async conversationId => {
    try {
      await HealthChatAPI.deleteConversation(conversationId);

      // 从本地列表中移除
      const index = conversations.value.findIndex(
        conv => conv.id === conversationId
      );
      if (index > -1) {
        conversations.value.splice(index, 1);
      }

      // 如果删除的是当前对话，清空消息
      if (currentConversationId.value === conversationId) {
        currentConversationId.value = null;
        messages.value = [];
      }

      return true;
    } catch (error) {
      console.error('删除对话失败:', error);
      return false;
    }
  };

  const clearCurrentConversation = () => {
    messages.value = [];
  };

  const updateConversationLastMessage = lastMessage => {
    const conversation = conversations.value.find(
      conv => conv.id === currentConversationId.value
    );

    if (conversation) {
      conversation.lastMessage =
        lastMessage.substring(0, 50) + (lastMessage.length > 50 ? '...' : '');
      conversation.messageCount = messages.value.length;
      conversation.updatedAt = new Date().toISOString();
    }
  };

  const setUserProfile = profile => {
    userProfile.value = profile;
  };

  const performRAGSearch = async (query, k = 3) => {
    try {
      isRAGLoading.value = true;
      ragError.value = null;

      const response = await HealthChatAPI.retrieveRAGDocuments(query, k);

      if (response.success) {
        ragResults.value = response.data.documents;

        // 创建RAG结果消息
        const ragMessage = {
          id: `rag_${Date.now()}`,
          sender: 'agent',
          type: 'rag_results',
          content: `为您找到 ${response.data.documents.length} 条相关文档：`,
          ragResults: response.data.documents,
          query: query,
          timestamp: new Date().toISOString(),
        };

        messages.value.push(ragMessage);
        return ragMessage;
      }
    } catch (error) {
      console.error('RAG检索失败:', error);
      ragError.value = error.message;

      // 添加错误消息
      const errorMessage = {
        id: `rag_error_${Date.now()}`,
        sender: 'agent',
        type: 'error',
        content: `RAG检索失败: ${error.message}`,
        timestamp: new Date().toISOString(),
      };

      messages.value.push(errorMessage);
      return errorMessage;
    } finally {
      isRAGLoading.value = false;
    }
  };

  const checkRAGStatus = async () => {
    try {
      const response = await HealthChatAPI.getRAGStatus();
      ragStatus.value = response.data;
      return response.data;
    } catch (error) {
      console.error('获取RAG状态失败:', error);
      ragStatus.value = { service_ready: false, error: error.message };
      return ragStatus.value;
    }
  };

  const clearRAGResults = () => {
    ragResults.value = [];
    ragError.value = null;
  };

  const resetStore = () => {
    conversations.value = [];
    currentConversationId.value = null;
    messages.value = [];
    isTyping.value = false;
    isLoading.value = false;
    userProfile.value = null;

    // 重置RAG状态
    ragResults.value = [];
    isRAGLoading.value = false;
    ragError.value = null;
    ragStatus.value = null;
  };

  return {
    // 状态
    conversations,
    currentConversationId,
    messages,
    isTyping,
    isLoading,
    userProfile,

    // RAG状态
    ragResults,
    isRAGLoading,
    ragError,
    ragStatus,

    // 计算属性
    currentConversation,
    hasActiveConversation,
    messageCount,

    // 方法
    createNewConversation,
    sendMessage,
    loadConversations,
    loadConversationMessages,
    deleteConversation,
    clearCurrentConversation,
    updateConversationLastMessage,
    setUserProfile,
    resetStore,

    // RAG方法
    performRAGSearch,
    checkRAGStatus,
    clearRAGResults,
  };
});
