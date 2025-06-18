/**
 * Mock数据管理系统
 * 提供统一的Mock数据存储、管理和API模拟功能
 */

import { ref, reactive } from 'vue'

// Mock数据存储
export const mockData = reactive({
  // 用户数据
  users: [
    {
      user_id: 'user_001',
      username: 'demo_user',
      email: 'demo@aurawell.com',
      full_name: '演示用户',
      phone: '13800138000',
      date_of_birth: '1990-01-01',
      gender: 'male',
      height: 175,
      weight: 70,
      avatar: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-06-17T00:00:00Z'
    }
  ],

  // 当前登录用户
  currentUser: null,

  // JWT Token
  authToken: null,

  // 健康计划数据
  healthPlans: [
    {
      plan_id: 'plan_001',
      user_id: 'user_001',
      title: '个性化减重计划',
      description: '基于您的身体状况和目标，为您制定的专属减重方案',
      plan_type: 'weight_loss',
      status: 'active',
      target_weight: 65,
      current_weight: 70,
      duration_weeks: 12,
      created_at: '2024-06-01T00:00:00Z',
      updated_at: '2024-06-17T00:00:00Z',
      recommendations: [
        {
          category: 'diet',
          title: '饮食建议',
          content: '每日控制热量摄入在1500-1800卡路里，增加蛋白质摄入，减少精制碳水化合物。',
          priority: 'high'
        },
        {
          category: 'exercise',
          title: '运动计划',
          content: '每周进行3-4次有氧运动，每次30-45分钟，结合力量训练。',
          priority: 'high'
        },
        {
          category: 'lifestyle',
          title: '生活方式',
          content: '保证每晚7-8小时睡眠，减少压力，定期监测体重变化。',
          priority: 'medium'
        }
      ]
    },
    {
      plan_id: 'plan_002',
      user_id: 'user_001',
      title: '心血管健康改善计划',
      description: '针对心血管健康的综合改善方案',
      plan_type: 'cardiovascular',
      status: 'completed',
      created_at: '2024-05-01T00:00:00Z',
      updated_at: '2024-05-30T00:00:00Z',
      recommendations: [
        {
          category: 'diet',
          title: '心脏友好饮食',
          content: '增加Omega-3脂肪酸摄入，减少饱和脂肪，多吃蔬菜水果。',
          priority: 'high'
        }
      ]
    }
  ],

  // 聊天对话数据
  chatSessions: [
    {
      session_id: 'session_001',
      user_id: 'user_001',
      title: '关于减重的咨询',
      created_at: '2024-06-17T10:00:00Z',
      updated_at: '2024-06-17T10:30:00Z',
      messages: [
        {
          message_id: 'msg_001',
          role: 'user',
          content: '我想制定一个减重计划，目前体重70kg，目标是65kg',
          timestamp: '2024-06-17T10:00:00Z'
        },
        {
          message_id: 'msg_002',
          role: 'assistant',
          content: '很好的目标！减重5kg是一个合理且可实现的目标。让我为您分析一下您的情况并制定个性化方案。\n\n首先，我需要了解一些基本信息：\n1. 您的身高是多少？\n2. 您目前的运动习惯如何？\n3. 您希望在多长时间内达到目标？\n\n基于健康减重的原则，建议每周减重0.5-1kg，这样您大约需要5-10周的时间来达到目标。',
          timestamp: '2024-06-17T10:01:00Z'
        },
        {
          message_id: 'msg_003',
          role: 'user',
          content: '我身高175cm，平时很少运动，希望在3个月内达到目标',
          timestamp: '2024-06-17T10:05:00Z'
        },
        {
          message_id: 'msg_004',
          role: 'assistant',
          content: '根据您的信息，我为您制定了一个3个月的减重计划：\n\n**目标分析：**\n- 当前BMI：22.9（正常范围）\n- 目标BMI：21.2（理想范围）\n- 减重目标：5kg/12周 = 约0.4kg/周\n\n**饮食建议：**\n- 每日热量控制在1600-1800卡路里\n- 蛋白质：每公斤体重1.2-1.6g\n- 多吃蔬菜、瘦肉、鱼类\n- 减少精制糖和加工食品\n\n**运动计划：**\n- 第1-4周：每周3次快走，每次30分钟\n- 第5-8周：增加到每周4次，加入轻度力量训练\n- 第9-12周：有氧+力量训练结合\n\n您觉得这个计划如何？需要我详细解释某个部分吗？',
          timestamp: '2024-06-17T10:10:00Z'
        }
      ]
    }
  ],

  // 家庭数据
  families: [
    {
      family_id: 'family_001',
      family_name: '张家大院',
      description: '我们是一个热爱健康生活的家庭',
      admin_id: 'user_001',
      created_at: '2024-01-01T00:00:00Z',
      member_count: 4
    }
  ],

  // 家庭成员数据
  familyMembers: [
    {
      member_id: 'member_001',
      family_id: 'family_001',
      user_id: 'user_001',
      display_name: '爸爸',
      role: 'Owner',
      avatar: null,
      is_current_user: true,
      joined_at: '2024-01-01T00:00:00Z',
      status: 'active'
    },
    {
      member_id: 'member_002',
      family_id: 'family_001',
      user_id: 'user_002',
      display_name: '妈妈',
      role: 'Manager',
      avatar: null,
      is_current_user: false,
      joined_at: '2024-01-02T00:00:00Z',
      status: 'active'
    },
    {
      member_id: 'member_003',
      family_id: 'family_001',
      user_id: 'user_003',
      display_name: '小明',
      role: 'Member',
      avatar: null,
      is_current_user: false,
      joined_at: '2024-01-03T00:00:00Z',
      status: 'active'
    },
    {
      member_id: 'member_004',
      family_id: 'family_001',
      user_id: 'user_004',
      display_name: '小红',
      role: 'Member',
      avatar: null,
      is_current_user: false,
      joined_at: '2024-01-04T00:00:00Z',
      status: 'active'
    }
  ],

  // 当前活跃成员
  activeMember: null,

  // 家庭挑战数据
  familyChallenges: [
    {
      challenge_id: 'challenge_001',
      family_id: 'family_001',
      title: '家庭步数挑战',
      description: '本周目标：每人每天走10000步',
      type: 'steps',
      status: 'active',
      target_value: 10000,
      current_value: 7500,
      progress_percentage: 75,
      start_date: '2024-06-17T00:00:00Z',
      end_date: '2024-06-24T00:00:00Z',
      participants_count: 4,
      participants: ['member_001', 'member_002', 'member_003', 'member_004']
    }
  ],

  // 健康告警数据
  healthAlerts: [
    {
      alert_id: 'alert_001',
      family_id: 'family_001',
      member_id: 'member_002',
      alert_type: 'weight_gain',
      title: '体重异常增长',
      message: '妈妈的体重在过去一周增长了2kg，建议关注饮食和运动',
      severity: 'medium',
      status: 'active',
      created_at: '2024-06-16T00:00:00Z'
    }
  ],

  // 健康报告数据
  healthReports: [
    {
      report_id: 'report_001',
      user_id: 'user_001',
      title: '2024年6月健康月报',
      report_type: 'monthly', // weekly, monthly, quarterly
      period: {
        start_date: '2024-06-01T00:00:00Z',
        end_date: '2024-06-30T23:59:59Z'
      },
      status: 'completed',
      created_at: '2024-06-30T00:00:00Z',
      updated_at: '2024-06-30T00:00:00Z',

      // 健康指标数据
      metrics: {
        weight: {
          current: 68.5,
          previous: 70.0,
          change: -1.5,
          change_percentage: -2.14,
          trend: 'decreasing',
          target: 65.0,
          target_progress: 60.0
        },
        bmi: {
          current: 22.4,
          previous: 22.9,
          change: -0.5,
          category: 'normal'
        },
        exercise: {
          total_sessions: 18,
          total_duration: 1080, // 分钟
          avg_duration: 60,
          calories_burned: 5400,
          most_frequent_type: 'running'
        },
        sleep: {
          avg_duration: 7.2,
          avg_quality_score: 78,
          deep_sleep_percentage: 22,
          sleep_efficiency: 85,
          bedtime_consistency: 82
        },
        nutrition: {
          avg_calories: 1650,
          protein_percentage: 25,
          carbs_percentage: 45,
          fat_percentage: 30,
          water_intake: 2.1
        },
        mental_health: {
          stress_level: 3.2, // 1-5 scale
          mood_score: 7.8, // 1-10 scale
          anxiety_level: 2.1,
          meditation_sessions: 12
        }
      },

      // 时间序列数据
      time_series: {
        weight: [
          { date: '2024-06-01', value: 70.0 },
          { date: '2024-06-03', value: 69.8 },
          { date: '2024-06-05', value: 69.5 },
          { date: '2024-06-08', value: 69.2 },
          { date: '2024-06-10', value: 69.0 },
          { date: '2024-06-12', value: 68.8 },
          { date: '2024-06-15', value: 68.5 },
          { date: '2024-06-18', value: 68.3 },
          { date: '2024-06-20', value: 68.2 },
          { date: '2024-06-22', value: 68.0 },
          { date: '2024-06-25', value: 68.2 },
          { date: '2024-06-28', value: 68.5 },
          { date: '2024-06-30', value: 68.5 }
        ],
        exercise_duration: [
          { date: '2024-06-01', value: 45 },
          { date: '2024-06-02', value: 60 },
          { date: '2024-06-04', value: 30 },
          { date: '2024-06-06', value: 75 },
          { date: '2024-06-08', value: 60 },
          { date: '2024-06-09', value: 45 },
          { date: '2024-06-11', value: 90 },
          { date: '2024-06-13', value: 60 },
          { date: '2024-06-15', value: 45 },
          { date: '2024-06-16', value: 60 },
          { date: '2024-06-18', value: 75 },
          { date: '2024-06-20', value: 60 },
          { date: '2024-06-22', value: 45 },
          { date: '2024-06-24', value: 60 },
          { date: '2024-06-26', value: 75 },
          { date: '2024-06-28', value: 60 },
          { date: '2024-06-29', value: 45 },
          { date: '2024-06-30', value: 60 }
        ],
        sleep_duration: [
          { date: '2024-06-01', value: 7.5 },
          { date: '2024-06-02', value: 6.8 },
          { date: '2024-06-03', value: 7.2 },
          { date: '2024-06-04', value: 7.0 },
          { date: '2024-06-05', value: 7.8 },
          { date: '2024-06-06', value: 6.5 },
          { date: '2024-06-07', value: 7.3 },
          { date: '2024-06-08', value: 7.1 },
          { date: '2024-06-09', value: 7.6 },
          { date: '2024-06-10', value: 6.9 },
          { date: '2024-06-11', value: 7.4 },
          { date: '2024-06-12', value: 7.2 },
          { date: '2024-06-13', value: 6.7 },
          { date: '2024-06-14', value: 7.5 },
          { date: '2024-06-15', value: 7.0 },
          { date: '2024-06-16', value: 7.3 },
          { date: '2024-06-17', value: 6.8 },
          { date: '2024-06-18', value: 7.1 },
          { date: '2024-06-19', value: 7.4 },
          { date: '2024-06-20', value: 7.2 },
          { date: '2024-06-21', value: 6.9 },
          { date: '2024-06-22', value: 7.6 },
          { date: '2024-06-23', value: 7.3 },
          { date: '2024-06-24', value: 7.0 },
          { date: '2024-06-25', value: 7.5 },
          { date: '2024-06-26', value: 6.8 },
          { date: '2024-06-27', value: 7.2 },
          { date: '2024-06-28', value: 7.4 },
          { date: '2024-06-29', value: 7.1 },
          { date: '2024-06-30', value: 7.3 }
        ],
        mood_score: [
          { date: '2024-06-01', value: 8 },
          { date: '2024-06-02', value: 7 },
          { date: '2024-06-03', value: 8 },
          { date: '2024-06-04', value: 6 },
          { date: '2024-06-05', value: 9 },
          { date: '2024-06-06', value: 7 },
          { date: '2024-06-07', value: 8 },
          { date: '2024-06-08', value: 7 },
          { date: '2024-06-09', value: 9 },
          { date: '2024-06-10', value: 6 },
          { date: '2024-06-11', value: 8 },
          { date: '2024-06-12', value: 7 },
          { date: '2024-06-13', value: 6 },
          { date: '2024-06-14', value: 8 },
          { date: '2024-06-15', value: 9 },
          { date: '2024-06-16', value: 7 },
          { date: '2024-06-17', value: 8 },
          { date: '2024-06-18', value: 6 },
          { date: '2024-06-19', value: 9 },
          { date: '2024-06-20', value: 8 },
          { date: '2024-06-21', value: 7 },
          { date: '2024-06-22', value: 9 },
          { date: '2024-06-23', value: 8 },
          { date: '2024-06-24', value: 7 },
          { date: '2024-06-25', value: 8 },
          { date: '2024-06-26', value: 6 },
          { date: '2024-06-27', value: 9 },
          { date: '2024-06-28', value: 8 },
          { date: '2024-06-29', value: 7 },
          { date: '2024-06-30', value: 8 }
        ]
      },

      // Agent智能解读
      insights: [
        {
          insight_id: 'insight_001',
          category: 'weight_management',
          title: '体重管理成效显著',
          content: '恭喜您！本月体重下降1.5kg，减重进度良好。数据显示您的体重变化呈现稳定下降趋势，这表明您的饮食控制和运动计划执行得很好。建议继续保持当前的生活方式，预计再坚持2个月即可达到目标体重65kg。',
          severity: 'positive',
          confidence: 0.92,
          recommendations: [
            '继续保持每周3-4次的有氧运动',
            '维持当前的饮食热量控制',
            '注意补充足够的蛋白质以保持肌肉量'
          ],
          medical_references: [
            '根据《美国临床营养学杂志》研究，每周减重0.5-1kg是最健康的减重速度',
            '《运动医学》期刊指出，结合有氧运动和力量训练能更好地保持肌肉量'
          ]
        },
        {
          insight_id: 'insight_002',
          category: 'sleep_quality',
          title: '睡眠质量需要关注',
          content: '您的平均睡眠时长为7.2小时，基本达到推荐标准，但睡眠质量评分78分仍有提升空间。数据显示您的深睡眠比例为22%，略低于理想的25-30%。建议优化睡眠环境和睡前习惯。',
          severity: 'warning',
          confidence: 0.85,
          recommendations: [
            '睡前1小时避免使用电子设备',
            '保持卧室温度在18-22°C',
            '尝试睡前5分钟深呼吸放松练习',
            '建立固定的睡眠时间表'
          ],
          medical_references: [
            '《睡眠医学评论》指出，深睡眠比例低于20%会影响身体恢复',
            '美国睡眠基金会建议成年人每晚睡眠7-9小时'
          ]
        },
        {
          insight_id: 'insight_003',
          category: 'exercise_performance',
          title: '运动表现持续改善',
          content: '本月您完成了18次运动，总时长18小时，表现优秀！运动频率稳定，平均每次60分钟。数据显示您的运动强度和持续性都在提升，这对减重和心血管健康都非常有益。',
          severity: 'positive',
          confidence: 0.88,
          recommendations: [
            '可以适当增加力量训练比例',
            '尝试不同类型的运动以避免适应性平台期',
            '注意运动后的拉伸和恢复'
          ],
          medical_references: [
            '《体育科学与医学》研究表明，规律运动能提高基础代谢率',
            '世界卫生组织推荐每周至少150分钟中等强度有氧运动'
          ]
        }
      ],

      // 健康评分
      health_score: {
        overall: 82,
        categories: {
          physical_health: 85,
          mental_health: 78,
          lifestyle: 83,
          nutrition: 80
        },
        previous_score: 76,
        improvement: 6
      },

      // 下期目标和建议
      next_period_goals: [
        {
          category: 'weight',
          target: 67.0,
          description: '继续减重1.5kg，接近目标体重'
        },
        {
          category: 'sleep',
          target: 7.5,
          description: '提升睡眠质量，增加深睡眠比例'
        },
        {
          category: 'exercise',
          target: 20,
          description: '增加运动频次，加入力量训练'
        }
      ]
    }
  ]
})

// Mock数据操作工具
export const mockUtils = {
  // 生成唯一ID
  generateId: (prefix = 'id') => {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  },

  // 模拟API延迟
  delay: (ms = 500) => {
    return new Promise(resolve => setTimeout(resolve, ms))
  },

  // 模拟API响应格式
  createResponse: (data, success = true, message = '') => {
    return {
      success,
      message,
      data,
      timestamp: new Date().toISOString()
    }
  },

  // 模拟分页响应
  createPaginatedResponse: (data, page = 1, pageSize = 10, total = null) => {
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedData = data.slice(startIndex, endIndex)
    
    return {
      success: true,
      data: paginatedData,
      pagination: {
        page,
        pageSize,
        total: total || data.length,
        totalPages: Math.ceil((total || data.length) / pageSize)
      },
      timestamp: new Date().toISOString()
    }
  },

  // 查找数据
  findById: (collection, id, idField = 'id') => {
    return collection.find(item => item[idField] === id)
  },

  // 过滤数据
  filterBy: (collection, filters) => {
    return collection.filter(item => {
      return Object.keys(filters).every(key => {
        if (filters[key] === undefined || filters[key] === null) return true
        return item[key] === filters[key]
      })
    })
  },

  // 排序数据
  sortBy: (collection, field, order = 'asc') => {
    return [...collection].sort((a, b) => {
      if (order === 'asc') {
        return a[field] > b[field] ? 1 : -1
      } else {
        return a[field] < b[field] ? 1 : -1
      }
    })
  }
}

// 初始化Mock数据
export const initMockData = () => {
  // 设置当前用户
  mockData.currentUser = mockData.users[0]
  
  // 设置活跃成员
  mockData.activeMember = mockData.familyMembers[0]
  
  // 模拟登录状态
  mockData.authToken = 'mock_jwt_token_' + Date.now()
  
  console.log('Mock数据初始化完成')
}

// 重置Mock数据
export const resetMockData = () => {
  // 重置为初始状态
  initMockData()
  console.log('Mock数据已重置')
}

// 导出默认配置
export default {
  mockData,
  mockUtils,
  initMockData,
  resetMockData
}
