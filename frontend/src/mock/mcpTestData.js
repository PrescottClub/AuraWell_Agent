/**
 * MCP工具测试数据 - 用于验证MCP功能展示
 */

export const mcpTestData = {
  // 🔥 带有完整MCP数据的测试消息
  fullMcpMessage: {
    id: 'test-mcp-001',
    sender: 'agent',
    content: '根据你的身体数据分析，我为你计算了详细的健康指标，并找到了相关的科学研究支撑。让我为你详细展示分析结果：',
    timestamp: new Date().toISOString(),
    mcpData: {
      // 计算器数据
      calculatorData: {
        bmi: 22.5,
        bmr: 1680,
        tdee: 2350,
        body_fat: 15.2,
        muscle_mass: 58.3
      },
      
      // 图表URL数据 (使用QuickChart示例)
      chartUrls: [
        'https://quickchart.io/chart?c={type:"line",data:{labels:["1月","2月","3月","4月","5月","6月"],datasets:[{label:"BMI变化",data:[23.1,22.8,22.5,22.2,22.5,22.3],borderColor:"rgb(75,192,192)",tension:0.1}]}',
        'https://quickchart.io/chart?c={type:"doughnut",data:{labels:["蛋白质","碳水化合物","脂肪"],datasets:[{data:[30,50,20],backgroundColor:["#FF6384","#36A2EB","#FFCE56"]}]}}'
      ],
      
      // 科学研究依据
      researchEvidence: [
        {
          title: 'BMI与健康风险的最新研究',
          summary: '2023年发表在《柳叶刀》的大规模队列研究表明，BMI在18.5-24.9范围内的人群具有最低的全因死亡率风险。',
          content: '这项包含68万人的前瞻性队列研究跟踪了20年，发现BMI与健康风险呈U型关系。',
          credibility: 95,
          url: 'https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(23)00001-X/fulltext'
        },
        {
          title: '基础代谢率与体重管理',
          summary: '美国营养学会2023年的研究显示，准确计算BMR对于制定个性化营养计划至关重要。',
          content: '研究发现，基于BMR的营养计划比传统方法多提高30%的减重成功率。',
          credibility: 88,
          url: 'https://academic.oup.com/ajcn/article/117/4/123456789/7123456'
        }
      ],
      
      // 用户画像数据
      userProfile: {
        healthLevel: '良好',
        riskFactors: ['轻度缺乏运动', '睡眠不足'],
        strengths: ['BMI正常', '基础代谢良好', '饮食习惯规律'],
        recommendations: ['增加有氧运动', '保持当前饮食习惯', '改善睡眠质量', '增加蛋白质摄入']
      },
      
      // 分步骤交付
      stepDelivery: {
        current_step: 2,
        total_steps: 4,
        step_title: '数据分析与可视化',
        steps: [
          '收集健康数据',
          '数据分析与可视化',
          '科学依据查证',
          '个性化建议生成'
        ]
      }
    }
  },

  // 🎯 只有计算数据的消息
  calculatorOnlyMessage: {
    id: 'test-calc-001',
    sender: 'agent',
    content: '基于你提供的身高体重信息，我为你计算了基础健康指标：',
    timestamp: new Date().toISOString(),
    mcpData: {
      calculatorData: {
        bmi: 21.8,
        bmr: 1620,
        tdee: 2270
      }
    }
  },

  // 📊 只有图表的消息
  chartOnlyMessage: {
    id: 'test-chart-001',
    sender: 'agent',
    content: '这是你过去6个月的健康数据趋势图：',
    timestamp: new Date().toISOString(),
    mcpData: {
      chartUrls: [
        'https://quickchart.io/chart?c={type:"bar",data:{labels:["周一","周二","周三","周四","周五","周六","周日"],datasets:[{label:"步数",data:[8200,7800,9200,8600,7200,10500,11200],backgroundColor:"rgba(54,162,235,0.8)"}]}}'
      ]
    }
  },

  // 🔬 只有科学依据的消息
  evidenceOnlyMessage: {
    id: 'test-evidence-001',
    sender: 'agent',
    content: '关于你询问的健康问题，我找到了以下科学研究支撑：',
    timestamp: new Date().toISOString(),
    mcpData: {
      researchEvidence: [
        {
          title: '运动对心血管健康的影响',
          summary: '世界卫生组织2023年报告显示，每周150分钟中等强度运动可显著降低心血管疾病风险。',
          credibility: 98,
          url: 'https://www.who.int/news-room/fact-sheets/detail/physical-activity'
        }
      ]
    }
  },

  // 📈 带步骤指示的消息
  stepDeliveryMessage: {
    id: 'test-step-001',
    sender: 'agent',
    content: '正在为你分析健康数据，请稍等...',
    timestamp: new Date().toISOString(),
    mcpData: {
      stepDelivery: {
        current_step: 1,
        total_steps: 3,
        step_title: '数据收集中',
        steps: ['数据收集中', '分析处理', '生成报告']
      }
    }
  },

  // 🎯 个性化测试消息
  personalizationTestMessage: {
    id: 'test-personalization-001',
    sender: 'agent',
    content: '基于您的个人健康画像，我为您提供了高度个性化的健康建议：',
    timestamp: new Date().toISOString(),
    mcpData: {
      userProfile: {
        healthLevel: '优秀',
        riskFactors: ['工作压力大', '久坐不动'],
        strengths: ['新陈代谢快', '心肺功能良好', '营养意识强'],
        recommendations: ['工作间隙站立活动', '学习压力管理技巧', '增加力量训练', '保持早睡早起']
      },
      calculatorData: {
        bmi: 21.2,
        bmr: 1720,
        tdee: 2380,
        stress_level: 6.5,
        personalization_score: 92
      }
    }
  },

  // 💫 交互动画测试消息
  animationTestMessage: {
    id: 'test-animation-001',
    sender: 'agent',
    content: '体验MCP智能工具的流畅交互效果：',
    timestamp: new Date().toISOString(),
    mcpData: {
      calculatorData: {
        heart_rate: 72,
        blood_pressure: '120/80',
        oxygen_saturation: 98
      },
      chartUrls: [
        'https://quickchart.io/chart?c={type:"line",data:{labels:["6:00","9:00","12:00","15:00","18:00","21:00"],datasets:[{label:"心率变化",data:[65,72,78,82,75,68],borderColor:"#ff6b6b",tension:0.4}]}}'
      ],
      userProfile: {
        healthLevel: '良好',
        riskFactors: ['轻微心率不齐'],
        strengths: ['血压正常', '血氧充足']
      }
    }
  }
}

// 🎭 模拟对话流程的测试数据
export const mcpConversationFlow = [
  {
    id: 'user-001',
    sender: 'user',
    content: '请帮我分析一下我的健康数据，身高175cm，体重70kg，30岁男性',
    timestamp: new Date(Date.now() - 60000).toISOString()
  },
  mcpTestData.stepDeliveryMessage,
  mcpTestData.fullMcpMessage,
  {
    id: 'user-002',
    sender: 'user',
    content: '这个BMI值正常吗？有什么需要注意的？',
    timestamp: new Date().toISOString()
  },
  mcpTestData.evidenceOnlyMessage
]

export default mcpTestData 