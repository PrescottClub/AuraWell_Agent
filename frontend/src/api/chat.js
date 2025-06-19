// 🔥 天启行动：连接真实AI引擎
import request from '../utils/request.js'

/**
 * 健康管理聊天API服务 - 真实版本
 */
export class HealthChatAPI {
  /**
   * 发送聊天消息到真实AI引擎
   * @param {string} message - 用户消息
   * @param {string} conversationId - 对话ID
   * @returns {Promise} API响应
   */
  static async sendMessage(message, conversationId = null) {
    try {
      // 🚀 真实API调用：连接后端AI引擎
      const response = await request.post('/chat/message', {
        message: message,
        conversation_id: conversationId,
        // 移除user_id，让后端从认证token中获取
        family_member_id: null
      })

      return {
        data: {
          reply: response.reply,
          content: response.reply,
          conversation_id: response.conversation_id,
          timestamp: response.timestamp || new Date().toISOString(),
          suggestions: response.suggestions || [],
          quickReplies: response.quick_replies || []
        }
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      console.error('错误详情:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        method: error.config?.method
      })
      throw error
    }
  }

  /**
   * 获取对话历史
   * @param {string} conversationId - 对话ID
   * @param {number} limit - 消息数量限制
   * @returns {Promise} 对话历史
   */
  static async getConversationHistory(conversationId, limit = 50) {
    try {
      const response = await request.get(`/chat/conversations/${conversationId}/messages`, {
        params: { limit }
      })
      return {
        data: {
          messages: response.messages || [],
          conversation_id: conversationId,
          total_count: response.total_count || 0
        }
      }
    } catch (error) {
      console.error('获取对话历史失败:', error)
      throw error
    }
  }

  /**
   * 创建新对话
   * @returns {Promise} 新对话信息
   */
  static async createConversation() {
    try {
      const response = await request.post('/chat/conversation', {
        type: 'health_consultation',
        title: '健康咨询对话'
      })
      return {
        data: {
          conversation_id: response.conversation_id,
          type: response.type,
          created_at: response.created_at,
          title: response.title
        }
      }
    } catch (error) {
      console.error('创建对话失败:', error)
      throw error
    }
  }

  /**
   * 获取用户的对话列表
   * @returns {Promise} 对话列表
   */
  static async getConversations() {
    try {
      const response = await request.get('/chat/conversations')
      return {
        data: {
          conversations: response.conversations || []
        }
      }
    } catch (error) {
      console.error('获取对话列表失败:', error)
      throw error
    }
  }

  /**
   * 删除对话
   * @param {string} conversationId - 对话ID
   * @returns {Promise} 删除结果
   */
  static async deleteConversation(conversationId) {
    try {
      const response = await request.delete(`/chat/conversations/${conversationId}`)
      return {
        success: true,
        message: '对话删除成功',
        data: response.data,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('删除对话失败:', error)
      throw error
    }
  }

  /**
   * 获取健康建议模板
   * @returns {Promise} 建议模板列表
   */
  static async getHealthSuggestions() {
    try {
      const response = await request.get('/chat/suggestions')
      return {
        data: response.suggestions || [
          "我想制定一个减重计划",
          "如何改善我的睡眠质量？",
          "请帮我分析我的运动数据",
          "我需要营养饮食建议",
          "如何建立健康的作息习惯？"
        ]
      }
    } catch (error) {
      console.error('获取健康建议失败:', error)
      // 返回默认建议
      return {
        data: [
          "我想制定一个减重计划",
          "如何改善我的睡眠质量？",
          "请帮我分析我的运动数据",
          "我需要营养饮食建议",
          "如何建立健康的作息习惯？"
        ]
      }
    }
  }

  /**
   * RAG文档检索
   * @param {string} query - 用户查询
   * @param {number} k - 返回文档数量
   * @returns {Promise} RAG检索结果
   */
  static async retrieveRAGDocuments(query, k = 3) {
    try {
      const response = await request.post('/rag/retrieve', {
        user_query: query,
        k: k
      })

      return {
        success: true,
        data: {
          documents: response.documents || [],
          query: query,
          total_count: response.total_count || 0,
          retrieval_time: response.retrieval_time || 0,
          timestamp: new Date().toISOString()
        }
      }
    } catch (error) {
      console.error('RAG检索失败:', error)

      // 处理不同类型的错误
      if (error.response?.status === 503) {
        throw new Error('RAG服务暂时不可用，请检查配置或稍后再试')
      } else if (error.response?.status === 401) {
        throw new Error('认证失败，请重新登录')
      } else if (error.response?.status === 400) {
        throw new Error('查询参数无效，请检查输入')
      } else {
        throw new Error('RAG检索服务异常，请稍后再试')
      }
    }
  }

  /**
   * 获取RAG服务状态
   * @returns {Promise} RAG服务状态
   */
  static async getRAGStatus() {
    try {
      const response = await request.get('/rag/status')
      return {
        success: true,
        data: response
      }
    } catch (error) {
      console.error('获取RAG状态失败:', error)
      throw error
    }
  }

  /**
   * 格式化日期
   * @param {string} dateString - 日期字符串
   * @returns {string} 格式化后的日期
   */
  static formatDate(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    if (days < 30) return `${Math.floor(days / 7)}周前`
    return date.toLocaleDateString('zh-CN')
  }
}

// 🎯 默认导出
export default HealthChatAPI
