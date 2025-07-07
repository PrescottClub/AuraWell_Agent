/**
 * Mock API服务层
 * 模拟真实API的响应格式和行为
 */

import { mockData, mockUtils } from './index'

// Mock API基础类
class MockAPI {
  constructor(baseDelay = 300) {
    this.baseDelay = baseDelay
  }

  // 模拟网络延迟
  async delay(ms = this.baseDelay) {
    await mockUtils.delay(ms)
  }

  // 模拟API响应
  createResponse(data, success = true, message = '') {
    return mockUtils.createResponse(data, success, message)
  }

  // 模拟错误响应
  createErrorResponse(message, code = 400) {
    return {
      success: false,
      message,
      error: {
        code,
        details: message
      },
      timestamp: new Date().toISOString()
    }
  }

  // 模拟认证检查
  checkAuth() {
    if (!mockData.authToken || !mockData.currentUser) {
      throw new Error('未授权访问')
    }
    return true
  }
}

// 用户认证API
export class AuthAPI extends MockAPI {
  // 用户登录
  async login(credentials) {
    await this.delay()
    
    const { username } = credentials
    
    // 模拟登录验证 - 支持多种测试账户
    const validCredentials = [
      { username: 'demo_user', password: 'password' },
      { username: 'test_user', password: 'test_password' },
      { username: 'admin', password: 'admin123' }
    ]

    const isValidLogin = validCredentials.some(cred =>
      cred.username === username && cred.password === credentials.password
    )

    if (isValidLogin) {
      const user = mockData.users[0]
      mockData.currentUser = user
      mockData.authToken = 'mock_jwt_token_' + Date.now()

      return this.createResponse({
        access_token: mockData.authToken,
        token_type: 'Bearer',
        expires_in: 3600,
        user
      }, true, '登录成功')
    } else {
      throw new Error('用户名或密码错误')
    }
  }

  // 用户注册
  async register(userData) {
    await this.delay()
    
    const { username, email, full_name } = userData
    
    // 检查用户是否已存在
    const existingUser = mockData.users.find(u => u.username === username || u.email === email)
    if (existingUser) {
      throw new Error('用户名或邮箱已存在')
    }
    
    // 创建新用户
    const newUser = {
      user_id: mockUtils.generateId('user'),
      username,
      email,
      full_name,
      phone: '',
      date_of_birth: '',
      gender: '',
      height: 0,
      weight: 0,
      avatar: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    mockData.users.push(newUser)
    mockData.currentUser = newUser
    mockData.authToken = 'mock_jwt_token_' + Date.now()
    
    return this.createResponse({
      user: newUser,
      token: mockData.authToken,
      expires_in: 3600
    }, true, '注册成功')
  }

  // 获取当前用户信息
  async getCurrentUser() {
    await this.delay(100)
    this.checkAuth()
    
    return this.createResponse(mockData.currentUser)
  }

  // 更新用户信息
  async updateProfile(profileData) {
    await this.delay()
    this.checkAuth()
    
    Object.assign(mockData.currentUser, {
      ...profileData,
      updated_at: new Date().toISOString()
    })
    
    return this.createResponse(mockData.currentUser, true, '个人信息更新成功')
  }

  // 用户登出
  async logout() {
    await this.delay(100)
    
    mockData.currentUser = null
    mockData.authToken = null
    
    return this.createResponse(null, true, '登出成功')
  }
}

// 健康计划API
export class HealthPlanAPI extends MockAPI {
  // 获取用户健康计划列表
  async getUserHealthPlans(params = {}) {
    await this.delay()
    this.checkAuth()
    
    const { page = 1, pageSize = 10, status } = params
    let plans = mockData.healthPlans.filter(plan => plan.user_id === mockData.currentUser.user_id)
    
    if (status) {
      plans = plans.filter(plan => plan.status === status)
    }
    
    return mockUtils.createPaginatedResponse(plans, page, pageSize)
  }

  // 获取健康计划详情
  async getHealthPlan(planId) {
    await this.delay()
    this.checkAuth()
    
    const plan = mockUtils.findById(mockData.healthPlans, planId, 'plan_id')
    if (!plan) {
      throw new Error('健康计划不存在')
    }
    
    return this.createResponse(plan)
  }

  // 创建健康计划
  async createHealthPlan(planData) {
    await this.delay(800) // 模拟AI生成时间
    this.checkAuth()
    
    const newPlan = {
      plan_id: mockUtils.generateId('plan'),
      user_id: mockData.currentUser.user_id,
      ...planData,
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      recommendations: [
        {
          category: 'diet',
          title: '饮食建议',
          content: '基于您的目标和身体状况，建议采用均衡饮食方案...',
          priority: 'high'
        },
        {
          category: 'exercise',
          title: '运动计划',
          content: '建议每周进行3-4次中等强度运动...',
          priority: 'high'
        },
        {
          category: 'lifestyle',
          title: '生活方式',
          content: '保持规律作息，充足睡眠...',
          priority: 'medium'
        }
      ]
    }
    
    mockData.healthPlans.push(newPlan)
    
    return this.createResponse(newPlan, true, '健康计划创建成功')
  }

  // 更新健康计划
  async updateHealthPlan(planId, updateData) {
    await this.delay()
    this.checkAuth()
    
    const planIndex = mockData.healthPlans.findIndex(plan => plan.plan_id === planId)
    if (planIndex === -1) {
      throw new Error('健康计划不存在')
    }
    
    Object.assign(mockData.healthPlans[planIndex], {
      ...updateData,
      updated_at: new Date().toISOString()
    })
    
    return this.createResponse(mockData.healthPlans[planIndex], true, '健康计划更新成功')
  }

  // 删除健康计划
  async deleteHealthPlan(planId) {
    await this.delay()
    this.checkAuth()
    
    const planIndex = mockData.healthPlans.findIndex(plan => plan.plan_id === planId)
    if (planIndex === -1) {
      throw new Error('健康计划不存在')
    }
    
    mockData.healthPlans.splice(planIndex, 1)
    
    return this.createResponse(null, true, '健康计划删除成功')
  }
}

// 健康咨询API
export class ChatAPI extends MockAPI {
  // 获取聊天会话列表
  async getChatSessions(params = {}) {
    await this.delay()
    this.checkAuth()
    
    const { page = 1, pageSize = 10 } = params
    const sessions = mockData.chatSessions.filter(session => session.user_id === mockData.currentUser.user_id)
    
    return mockUtils.createPaginatedResponse(sessions, page, pageSize)
  }

  // 获取聊天会话详情
  async getChatSession(sessionId) {
    await this.delay()
    this.checkAuth()
    
    const session = mockUtils.findById(mockData.chatSessions, sessionId, 'session_id')
    if (!session) {
      throw new Error('聊天会话不存在')
    }
    
    return this.createResponse(session)
  }

  // 创建新的聊天会话
  async createChatSession(title = '新的咨询') {
    await this.delay()
    this.checkAuth()
    
    const newSession = {
      session_id: mockUtils.generateId('session'),
      user_id: mockData.currentUser.user_id,
      title,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      messages: []
    }
    
    mockData.chatSessions.push(newSession)
    
    return this.createResponse(newSession, true, '聊天会话创建成功')
  }

  // 发送消息
  async sendMessage(sessionId, content) {
    await this.delay(600) // 模拟AI响应时间
    this.checkAuth()
    
    const session = mockUtils.findById(mockData.chatSessions, sessionId, 'session_id')
    if (!session) {
      throw new Error('聊天会话不存在')
    }
    
    // 添加用户消息
    const userMessage = {
      message_id: mockUtils.generateId('msg'),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    }
    session.messages.push(userMessage)
    
    // 模拟AI回复
    const aiResponse = this.generateAIResponse()
    const aiMessage = {
      message_id: mockUtils.generateId('msg'),
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date().toISOString()
    }
    session.messages.push(aiMessage)
    
    session.updated_at = new Date().toISOString()
    
    return this.createResponse({
      userMessage,
      aiMessage
    })
  }

  // 生成AI回复（简单模拟）
  generateAIResponse() {
    const responses = [
      '感谢您的咨询！基于您提供的信息，我建议您...',
      '这是一个很好的问题。根据健康管理的最佳实践...',
      '我理解您的关注。让我为您分析一下这个情况...',
      '根据您的描述，我建议您采取以下措施...'
    ]
    
    return responses[Math.floor(Math.random() * responses.length)] + 
           '\n\n如果您需要更详细的建议，请告诉我更多关于您的具体情况。'
  }
}

// 家庭管理API
export class FamilyAPI extends MockAPI {
  // 获取用户家庭列表
  async getUserFamilies() {
    await this.delay()
    this.checkAuth()

    const families = mockData.families.filter(family => {
      return mockData.familyMembers.some(member =>
        member.family_id === family.family_id &&
        member.user_id === mockData.currentUser.user_id
      )
    })

    return this.createResponse({ families })
  }

  // 获取家庭详情
  async getFamilyInfo(familyId) {
    await this.delay()
    this.checkAuth()

    const family = mockUtils.findById(mockData.families, familyId, 'family_id')
    if (!family) {
      throw new Error('家庭不存在')
    }

    return this.createResponse(family)
  }

  // 创建家庭
  async createFamily(familyData) {
    await this.delay()
    this.checkAuth()

    const newFamily = {
      family_id: mockUtils.generateId('family'),
      family_name: familyData.family_name,
      description: familyData.description || '',
      admin_id: mockData.currentUser.user_id,
      created_at: new Date().toISOString(),
      member_count: 1
    }

    mockData.families.push(newFamily)

    // 添加创建者为家庭成员
    const newMember = {
      member_id: mockUtils.generateId('member'),
      family_id: newFamily.family_id,
      user_id: mockData.currentUser.user_id,
      display_name: mockData.currentUser.full_name || '我',
      role: 'Owner',
      avatar: mockData.currentUser.avatar,
      is_current_user: true,
      joined_at: new Date().toISOString(),
      status: 'active'
    }

    mockData.familyMembers.push(newMember)
    mockData.activeMember = newMember

    return this.createResponse(newFamily, true, '家庭创建成功')
  }

  // 获取家庭成员列表
  async getFamilyMembers(familyId) {
    await this.delay()
    this.checkAuth()

    const members = mockData.familyMembers.filter(member => member.family_id === familyId)

    return this.createResponse({ members })
  }

  // 获取家庭权限
  async getFamilyPermissions(familyId) {
    await this.delay()
    this.checkAuth()

    const member = mockData.familyMembers.find(m =>
      m.family_id === familyId && m.user_id === mockData.currentUser.user_id
    )

    if (!member) {
      throw new Error('您不是该家庭的成员')
    }

    const permissions = this.getRolePermissions(member.role)

    return this.createResponse({
      role: member.role,
      permissions
    })
  }

  // 切换活跃成员
  async switchActiveMember(data) {
    await this.delay(100)
    this.checkAuth()

    const { member_id } = data
    const member = mockUtils.findById(mockData.familyMembers, member_id, 'member_id')

    if (!member) {
      throw new Error('成员不存在')
    }

    mockData.activeMember = member

    return this.createResponse(member, true, '活跃成员切换成功')
  }

  // 获取家庭健康报告
  async getFamilyHealthReport(familyId) {
    await this.delay()
    this.checkAuth()

    const mockReport = {
      summary: {
        total_steps: 25000,
        avg_sleep_hours: 7.5,
        active_members: mockData.familyMembers.filter(m => m.family_id === familyId).length,
        weekly_challenges: 3
      },
      trends: {
        steps: [8000, 9500, 7200, 10000, 8800, 9200, 11000],
        sleep: [7.2, 7.8, 6.9, 8.1, 7.5, 7.3, 8.0]
      }
    }

    return this.createResponse(mockReport)
  }

  // 获取家庭排行榜
  async getFamilyLeaderboard(familyId) {
    await this.delay()
    this.checkAuth()

    const members = mockData.familyMembers.filter(m => m.family_id === familyId)
    const leaderboard = members.map(member => ({
      ...member,
      value: Math.floor(Math.random() * 10000) + 5000,
      likes_count: Math.floor(Math.random() * 10),
      liked_by_current_user: false
    }))

    return this.createResponse({ leaderboard })
  }

  // 获取家庭挑战
  async getFamilyChallenges(familyId) {
    await this.delay()
    this.checkAuth()

    const challenges = mockData.familyChallenges.filter(c => c.family_id === familyId)

    return this.createResponse({ challenges })
  }

  // 创建家庭挑战
  async createFamilyChallenge(familyId, challengeData) {
    await this.delay()
    this.checkAuth()

    const newChallenge = {
      challenge_id: mockUtils.generateId('challenge'),
      family_id: familyId,
      ...challengeData,
      status: 'active',
      current_value: 0,
      progress_percentage: 0,
      start_date: new Date().toISOString(),
      end_date: new Date(Date.now() + challengeData.duration_days * 24 * 60 * 60 * 1000).toISOString(),
      participants_count: challengeData.participants?.length || 0,
      participants: challengeData.participants || []
    }

    mockData.familyChallenges.push(newChallenge)

    return this.createResponse(newChallenge, true, '家庭挑战创建成功')
  }

  // 为成员点赞
  async likeMember() {
    await this.delay(200)
    this.checkAuth()

    return this.createResponse(null, true, '点赞成功')
  }

  // 获取健康告警列表
  async getHealthAlerts(familyId) {
    await this.delay()
    this.checkAuth()

    const alerts = mockData.healthAlerts.filter(alert => alert.family_id === familyId)

    return this.createResponse({ alerts })
  }

  // 获取角色权限
  getRolePermissions(role) {
    const permissions = {
      'Owner': ['invite_members', 'manage_members', 'view_all_data', 'set_alerts', 'create_challenges', 'export_reports'],
      'Manager': ['invite_members', 'view_all_data', 'set_alerts', 'create_challenges'],
      'Member': ['view_own_data', 'participate_challenges']
    }

    return permissions[role] || permissions['Member']
  }
}

// 健康报告API
export class HealthReportAPI extends MockAPI {
  // 获取健康报告列表
  async getHealthReports(params = {}) {
    await this.delay()
    this.checkAuth()

    const { page = 1, pageSize = 10, report_type } = params
    let reports = mockData.healthReports.filter(report => report.user_id === mockData.currentUser.user_id)

    if (report_type) {
      reports = reports.filter(report => report.report_type === report_type)
    }

    return mockUtils.createPaginatedResponse(reports, page, pageSize)
  }

  // 获取健康报告详情
  async getHealthReport(reportId) {
    await this.delay()
    this.checkAuth()

    const report = mockUtils.findById(mockData.healthReports, reportId, 'report_id')
    if (!report) {
      throw new Error('健康报告不存在')
    }

    return this.createResponse(report)
  }

  // 生成健康报告
  async generateHealthReport(params = {}) {
    await this.delay(1500) // 模拟报告生成时间
    this.checkAuth()

    const { report_type = 'weekly', start_date, end_date } = params

    // 生成新的健康报告
    const newReport = {
      report_id: mockUtils.generateId('report'),
      user_id: mockData.currentUser.user_id,
      title: this.generateReportTitle(report_type, start_date),
      report_type,
      period: {
        start_date: start_date || this.getDefaultStartDate(report_type),
        end_date: end_date || new Date().toISOString()
      },
      status: 'completed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...this.generateMockReportData(report_type)
    }

    mockData.healthReports.push(newReport)

    return this.createResponse(newReport, true, '健康报告生成成功')
  }

  // 获取健康指标时间序列数据
  async getHealthMetricsTimeSeries(params = {}) {
    await this.delay()
    this.checkAuth()

    const { metric_type, start_date, end_date, interval = 'daily' } = params

    // 模拟时间序列数据
    const timeSeriesData = this.generateTimeSeriesData(metric_type, start_date, end_date, interval)

    return this.createResponse({
      metric_type,
      interval,
      data: timeSeriesData,
      summary: this.calculateMetricSummary(timeSeriesData)
    })
  }

  // 获取健康洞察分析
  async getHealthInsights(params = {}) {
    await this.delay(800)
    this.checkAuth()

    const { category } = params

    // 模拟AI生成的健康洞察
    const insights = this.generateHealthInsights(category)

    return this.createResponse({
      insights,
      generated_at: new Date().toISOString(),
      confidence_score: 0.87
    })
  }

  // 触发报告对话
  async triggerReportChat(reportId, chartData) {
    await this.delay(600)
    this.checkAuth()

    // 创建新的聊天会话
    const chatSession = await chatAPI.createChatSession(`关于${chartData.metric}的分析讨论`)

    // 生成基于图表数据的初始消息
    const initialMessage = this.generateChartAnalysisMessage(chartData)

    // 发送初始分析消息
    const chatResponse = await chatAPI.sendMessage(chatSession.data.session_id, initialMessage)

    return this.createResponse({
      session_id: chatSession.data.session_id,
      initial_analysis: chatResponse.data.aiMessage.content,
      chart_context: chartData
    })
  }

  // 生成报告标题
  generateReportTitle(reportType, startDate) {
    const date = new Date(startDate || Date.now())
    const year = date.getFullYear()
    const month = date.getMonth() + 1

    switch (reportType) {
      case 'weekly':
        return `${year}年第${Math.ceil(month * 4.33)}周健康周报`
      case 'monthly':
        return `${year}年${month}月健康月报`
      case 'quarterly':
        return `${year}年第${Math.ceil(month / 3)}季度健康季报`
      default:
        return `${year}年健康报告`
    }
  }

  // 获取默认开始日期
  getDefaultStartDate(reportType) {
    const today = new Date();
    switch (reportType) {
      case 'weekly': {
        const d = new Date(today);
        d.setDate(d.getDate() - 7);
        return d;
      }
      case 'monthly': {
        const d = new Date(today);
        d.setMonth(d.getMonth() - 1);
        return d;
      }
      case 'quarterly': {
        const d = new Date(today);
        d.setMonth(d.getMonth() - 3);
        return d;
      }
      default:
        return today;
    }
  }

  // 生成模拟报告数据
  generateMockReportData(reportType) {
    // 这里返回基础的模拟数据结构
    return {
      metrics: {
        weight: {
          current: 68.5 + (Math.random() - 0.5) * 2,
          previous: 70.0,
          change: -1.5 + (Math.random() - 0.5),
          trend: 'decreasing'
        },
        exercise: {
          total_sessions: Math.floor(Math.random() * 10) + 15,
          total_duration: Math.floor(Math.random() * 300) + 900
        },
        sleep: {
          avg_duration: 7.0 + Math.random(),
          avg_quality_score: Math.floor(Math.random() * 20) + 70
        }
      },
      health_score: {
        overall: Math.floor(Math.random() * 20) + 75,
        improvement: Math.floor(Math.random() * 10) + 1
      },
      insights: this.generateHealthInsights('general', reportType)
    }
  }

  // 生成时间序列数据
  generateTimeSeriesData(metricType, startDate, endDate, interval) {
    const data = []
    const start = new Date(startDate || Date.now() - 30 * 24 * 60 * 60 * 1000)
    const end = new Date(endDate || Date.now())

    let current = new Date(start)
    while (current <= end) {
      data.push({
        date: current.toISOString().split('T')[0],
        value: this.generateMetricValue(metricType)
      })

      // 根据间隔增加时间
      if (interval === 'daily') {
        current.setDate(current.getDate() + 1)
      } else if (interval === 'weekly') {
        current.setDate(current.getDate() + 7)
      }
    }

    return data
  }

  // 生成指标值
  generateMetricValue(metricType) {
    switch (metricType) {
      case 'weight':
        return 68 + Math.random() * 4
      case 'exercise_duration':
        return Math.floor(Math.random() * 60) + 30
      case 'sleep_duration':
        return 6.5 + Math.random() * 2
      case 'mood_score':
        return Math.floor(Math.random() * 4) + 6
      default:
        return Math.random() * 100
    }
  }

  // 计算指标摘要
  calculateMetricSummary(data) {
    if (!data.length) return {}

    const values = data.map(d => d.value)
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((a, b) => a + b, 0) / values.length,
      trend: values[values.length - 1] > values[0] ? 'increasing' : 'decreasing'
    }
  }

  // 生成健康洞察
  generateHealthInsights(category) {
    const insights = [
      {
        insight_id: mockUtils.generateId('insight'),
        category: category || 'general',
        title: '数据趋势分析',
        content: '基于您最近的健康数据，我们发现了一些值得关注的趋势...',
        severity: 'info',
        confidence: 0.85,
        recommendations: [
          '建议保持当前的健康习惯',
          '可以适当调整运动强度',
          '注意饮食营养均衡'
        ]
      }
    ]

    return insights
  }

  // 生成图表分析消息
  generateChartAnalysisMessage(chartData) {
    const { metric, trend, value, period } = chartData

    return `我注意到您在${period}期间的${metric}数据显示${trend}趋势，当前值为${value}。让我为您分析一下这个趋势的可能原因和改进建议。`
  }
}

// 创建API实例
export const authAPI = new AuthAPI()
export const healthPlanAPI = new HealthPlanAPI()
export const chatAPI = new ChatAPI()
export const familyAPI = new FamilyAPI()
export const healthReportAPI = new HealthReportAPI()

export default {
  authAPI,
  healthPlanAPI,
  chatAPI,
  familyAPI,
  healthReportAPI
}
