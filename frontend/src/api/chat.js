import request from '../utils/request'

/**
 * 健康管理聊天API服务
 */
export class HealthChatAPI {
  /**
   * 发送聊天消息
   * @param {string} message - 用户消息
   * @param {string} conversationId - 对话ID
   * @returns {Promise} API响应
   */
  static async sendMessage(message, conversationId = null) {
    try {
      // 使用新的健康聊天API端点
      const response = await request.post('/chat/message', {
        message: message.trim(),
        conversation_id: conversationId,
        context: {
          timestamp: new Date().toISOString(),
          platform: 'web'
        }
      })
      return response
    } catch (error) {
      console.warn('真实API调用失败，使用模拟响应:', error)

      // 模拟AI响应
      return this.getMockResponse(message)
    }
  }

  /**
   * 获取模拟AI响应
   * @param {string} message - 用户消息
   * @returns {Promise} 模拟响应
   */
  static async getMockResponse(message) {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

    const lowerMessage = message.toLowerCase()
    let reply = ''
    let suggestions = []
    let quickReplies = []

    if (lowerMessage.includes('减重') || lowerMessage.includes('减肥') || lowerMessage.includes('瘦身')) {
      reply = `我很高兴帮助您制定减重计划！为了给您最适合的建议，我需要了解一些基本信息：

**📊 基本信息收集：**
• 您目前的身高和体重是多少？
• 您的目标体重是多少？
• 希望在多长时间内达到目标？

**🏃‍♀️ 运动习惯：**
• 您平时有运动习惯吗？
• 喜欢什么类型的运动？
• 每周能安排多少时间运动？

**🥗 饮食偏好：**
• 有没有特殊的饮食限制或过敏？
• 平时的饮食习惯如何？

请告诉我这些信息，我会为您制定个性化的减重方案！`

      suggestions = [
        {
          title: '科学减重原理',
          content: '健康减重的核心是创造热量缺口，即消耗的热量大于摄入的热量。建议每周减重0.5-1公斤。'
        },
        {
          title: '运动建议',
          content: '结合有氧运动和力量训练，有氧运动燃烧脂肪，力量训练保持肌肉量。'
        }
      ]

      quickReplies = [
        { text: '我身高170cm，体重75kg' },
        { text: '我想在3个月内减重10kg' },
        { text: '我平时很少运动' },
        { text: '我没有特殊饮食限制' }
      ]
    } else if (lowerMessage.includes('睡眠') || lowerMessage.includes('失眠') || lowerMessage.includes('睡觉')) {
      reply = `睡眠质量对健康非常重要！让我帮您分析和改善睡眠问题。

**😴 睡眠现状了解：**
• 您通常几点上床睡觉？几点起床？
• 入睡需要多长时间？
• 夜间会醒来几次？
• 早上醒来感觉如何？

**🌙 睡前习惯：**
• 睡前通常做什么？
• 卧室环境如何（温度、光线、噪音）？
• 有使用电子设备的习惯吗？

**☕ 生活习惯：**
• 下午或晚上有喝咖啡、茶的习惯吗？
• 晚餐时间和内容？
• 白天的运动情况？

了解这些信息后，我可以为您提供针对性的睡眠改善建议！`

      suggestions = [
        {
          title: '睡眠卫生原则',
          content: '保持规律作息、创造良好睡眠环境、避免睡前刺激性活动。'
        },
        {
          title: '放松技巧',
          content: '尝试深呼吸、渐进性肌肉放松或冥想来帮助入睡。'
        }
      ]

      quickReplies = [
        { text: '我通常12点睡觉，7点起床' },
        { text: '入睡很困难，要1小时以上' },
        { text: '睡前会看手机' },
        { text: '卧室比较吵闹' }
      ]
    } else if (lowerMessage.includes('运动') || lowerMessage.includes('锻炼') || lowerMessage.includes('健身')) {
      reply = `很棒！运动是健康生活的重要组成部分。让我为您制定合适的运动计划。

**🎯 运动目标：**
• 您的主要运动目标是什么？（减重、增肌、提高体能、缓解压力等）
• 希望通过运动达到什么效果？

**💪 当前状况：**
• 您目前的运动基础如何？
• 有没有运动经验或特长？
• 身体有没有不适或限制？

**⏰ 时间安排：**
• 每周能安排多少时间运动？
• 更喜欢什么时间段运动？
• 在家运动还是去健身房？

**🏃‍♀️ 运动偏好：**
• 喜欢什么类型的运动？
• 更喜欢独自运动还是团体运动？

告诉我这些信息，我会为您推荐最适合的运动方案！`

      suggestions = [
        {
          title: '运动频率建议',
          content: '建议每周至少150分钟中等强度有氧运动，加上2次力量训练。'
        },
        {
          title: '循序渐进原则',
          content: '从低强度开始，逐步增加运动量和强度，避免运动伤害。'
        }
      ]

      quickReplies = [
        { text: '我想减重和提高体能' },
        { text: '我是运动新手' },
        { text: '每周能运动3-4次' },
        { text: '我喜欢跑步和游泳' }
      ]
    } else if (lowerMessage.includes('饮食') || lowerMessage.includes('营养') || lowerMessage.includes('吃')) {
      reply = `营养均衡的饮食是健康的基础！让我帮您制定合适的饮食方案。

**🥗 饮食目标：**
• 您的饮食目标是什么？（减重、增重、维持健康、改善某些症状等）
• 有没有特殊的营养需求？

**🍽️ 当前饮食习惯：**
• 一日三餐的时间和内容？
• 有没有零食或夜宵习惯？
• 平时喝水量如何？

**🚫 饮食限制：**
• 有没有食物过敏或不耐受？
• 有没有宗教或个人饮食限制？
• 不喜欢吃什么食物？

**👨‍🍳 烹饪情况：**
• 平时自己做饭还是外食？
• 烹饪技能如何？
• 有多少时间准备食物？

了解这些后，我可以为您制定个性化的营养方案！`

      suggestions = [
        {
          title: '均衡营养原则',
          content: '确保摄入足够的蛋白质、健康脂肪、复合碳水化合物、维生素和矿物质。'
        },
        {
          title: '饮食时间管理',
          content: '规律进餐，避免暴饮暴食，注意餐前餐后的时间间隔。'
        }
      ]

      quickReplies = [
        { text: '我想通过饮食减重' },
        { text: '我经常外食' },
        { text: '我不喜欢吃蔬菜' },
        { text: '我想学习健康烹饪' }
      ]
    } else {
      reply = `您好！我是AuraWell健康助手，很高兴为您服务！🌟

我可以帮助您：
• 🎯 制定个性化的健康目标和计划
• 💪 提供运动和健身建议
• 🥗 制定营养均衡的饮食方案
• 😴 改善睡眠质量
• 📊 分析健康数据和趋势
• 🧘‍♀️ 建立健康的生活习惯

请告诉我您最关心的健康问题，或者您想要改善的方面，我会为您提供专业的建议和指导！

您可以问我关于减重、运动、饮食、睡眠、压力管理等任何健康相关的问题。`

      quickReplies = [
        { text: '我想制定减重计划' },
        { text: '如何改善睡眠质量？' },
        { text: '请推荐运动方案' },
        { text: '我需要饮食建议' },
        { text: '如何建立健康习惯？' }
      ]
    }

    return {
      data: {
        reply,
        content: reply,
        suggestions,
        quickReplies,
        conversation_id: conversationId || `mock_${Date.now()}`,
        timestamp: new Date().toISOString()
      }
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
      const response = await request.get('/chat/history', {
        params: {
          conversation_id: conversationId,
          limit
        }
      })
      return response
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
        metadata: {
          created_at: new Date().toISOString(),
          platform: 'web'
        }
      })
      return response
    } catch (error) {
      console.warn('创建对话API失败，使用模拟模式:', error)

      // 返回模拟对话
      return {
        data: {
          conversation_id: `mock_conv_${Date.now()}`,
          type: 'health_consultation',
          created_at: new Date().toISOString(),
          title: '健康咨询对话'
        }
      }
    }
  }

  /**
   * 获取用户的对话列表
   * @returns {Promise} 对话列表
   */
  static async getConversations() {
    try {
      const response = await request.get('/chat/conversations')
      return response
    } catch (error) {
      console.warn('获取对话列表API失败，使用模拟数据:', error)

      // 返回模拟对话列表
      return {
        data: {
          conversations: [
            {
              id: 'mock_conv_1',
              title: '减重计划咨询',
              last_message: '我为您制定了个性化的减重方案...',
              date: '今天',
              created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30分钟前
              updated_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
              message_count: 15,
              status: 'active'
            },
            {
              id: 'mock_conv_2',
              title: '睡眠质量改善',
              last_message: '根据您的作息情况，建议...',
              date: '昨天',
              created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1天前
              updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
              message_count: 8,
              status: 'active'
            }
          ]
        }
      }
    }
  }

  /**
   * 删除对话
   * @param {string} conversationId - 对话ID
   * @returns {Promise} 删除结果
   */
  static async deleteConversation(conversationId) {
    try {
      const response = await request.delete(`/chat/conversation/${conversationId}`)
      return response
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
      return response
    } catch (error) {
      console.error('获取健康建议失败:', error)
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
}

export default HealthChatAPI
