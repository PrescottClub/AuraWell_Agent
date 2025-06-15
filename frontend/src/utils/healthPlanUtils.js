/**
 * 健康计划数据处理工具函数
 * 用于处理前后端数据格式不一致的问题
 */

/**
 * 标准化健康计划数据
 * @param {Object} plan - 原始计划数据
 * @returns {Object} 标准化后的计划数据
 */
export function normalizePlan(plan) {
  if (!plan) return null

  return {
    // 统一ID字段
    id: plan.plan_id || plan.id,
    plan_id: plan.plan_id || plan.id,
    
    // 基本信息
    title: plan.title || '',
    description: plan.description || '',
    status: plan.status || 'active',
    
    // 时间字段
    duration: plan.duration_days || plan.duration || 30,
    duration_days: plan.duration_days || plan.duration || 30,
    
    // 进度字段
    progress: normalizeProgress(plan.progress),
    
    // 模块字段
    modules: normalizeModules(plan.modules),
    
    // 时间戳
    created_at: plan.created_at,
    updated_at: plan.updated_at,
    
    // 保留其他字段
    ...plan
  }
}

/**
 * 标准化进度数据
 * @param {number|Object} progress - 原始进度数据
 * @returns {number} 标准化后的进度值 (0-100)
 */
export function normalizeProgress(progress) {
  if (typeof progress === 'number') {
    return Math.max(0, Math.min(100, progress))
  }
  
  if (typeof progress === 'object' && progress !== null) {
    const totalTasks = progress.total_tasks || 1
    const completedTasks = progress.completed_tasks || 0
    return Math.round((completedTasks / totalTasks) * 100)
  }
  
  return 0
}

/**
 * 标准化模块数据
 * @param {Array} modules - 原始模块数据
 * @returns {Array} 标准化后的模块数组
 */
export function normalizeModules(modules) {
  if (!Array.isArray(modules)) return []

  return modules.map(module => {
    if (typeof module === 'string') {
      // 如果是字符串，转换为对象格式
      return {
        module_type: module,
        type: module,
        title: getModuleTitle(module),
        description: `${getModuleTitle(module)}的详细内容`,
        content: {},
        duration_days: 30
      }
    }

    if (typeof module === 'object' && module !== null) {
      // 如果是对象，确保包含所有必要字段
      return {
        module_type: module.module_type || module.type,
        type: module.module_type || module.type,
        title: module.title || getModuleTitle(module.module_type || module.type),
        description: module.description || `${getModuleTitle(module.module_type || module.type)}的详细内容`,
        content: module.content || {},
        duration_days: module.duration_days || 30,
        ...module
      }
    }

    return module
  })
}

/**
 * 获取模块类型对应的标题
 * @param {string} moduleType - 模块类型
 * @returns {string} 模块标题
 */
export function getModuleTitle(moduleType) {
  const titles = {
    diet: '饮食计划',
    exercise: '运动计划',
    weight: '体重管理',
    sleep: '睡眠计划',
    mental: '心理健康'
  }
  return titles[moduleType] || moduleType || '健康模块'
}

/**
 * 获取模块类型列表（用于显示）
 * @param {Array} modules - 模块数组
 * @returns {Array} 模块类型字符串数组
 */
export function getModuleTypes(modules) {
  if (!Array.isArray(modules)) return []
  
  return modules.map(module => {
    if (typeof module === 'string') return module
    if (typeof module === 'object') return module.module_type || module.type
    return module
  }).filter(Boolean)
}

/**
 * 标准化计划列表
 * @param {Array} plans - 原始计划列表
 * @returns {Array} 标准化后的计划列表
 */
export function normalizePlanList(plans) {
  if (!Array.isArray(plans)) return []
  return plans.map(plan => normalizePlan(plan))
}

/**
 * 标准化API响应数据
 * @param {Object} response - API响应
 * @returns {Object} 标准化后的响应数据
 */
export function normalizeApiResponse(response) {
  if (!response) return response

  // 处理新的API响应格式：plan字段在根级别
  if (response.plan) {
    return {
      ...response,
      plan: normalizePlan(response.plan),
      data: response.data || response.plan
    }
  }

  // 如果没有data字段，直接返回
  if (!response.data) return response

  // 处理单个计划响应
  if (response.data.plan) {
    return {
      ...response,
      data: {
        ...response.data,
        plan: normalizePlan(response.data.plan)
      }
    }
  }

  // 处理计划列表响应
  if (response.data.plans) {
    return {
      ...response,
      data: {
        ...response.data,
        plans: normalizePlanList(response.data.plans)
      }
    }
  }

  // 处理直接的计划数据
  if (response.data.plan_id || response.data.id) {
    return {
      ...response,
      data: normalizePlan(response.data)
    }
  }

  // 处理计划数组
  if (Array.isArray(response.data) && response.data.length > 0 &&
      (response.data[0].plan_id || response.data[0].id)) {
    return {
      ...response,
      data: normalizePlanList(response.data)
    }
  }

  return response
}

/**
 * 格式化日期显示
 * @param {string|Date} date - 日期
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date) {
  if (!date) return ''
  
  try {
    const dateObj = new Date(date)
    return dateObj.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    console.warn('日期格式化失败:', error)
    return ''
  }
}

/**
 * 获取计划状态标签
 * @param {string} status - 计划状态
 * @returns {Object} 状态标签和颜色
 */
export function getStatusInfo(status) {
  const statusMap = {
    active: { label: '进行中', color: 'green' },
    completed: { label: '已完成', color: 'blue' },
    paused: { label: '已暂停', color: 'orange' },
    cancelled: { label: '已取消', color: 'red' }
  }
  
  return statusMap[status] || { label: status || '未知', color: 'default' }
}

/**
 * 验证计划数据完整性
 * @param {Object} plan - 计划数据
 * @returns {Object} 验证结果
 */
export function validatePlan(plan) {
  const errors = []
  
  if (!plan) {
    errors.push('计划数据不能为空')
    return { valid: false, errors }
  }
  
  if (!plan.title || plan.title.trim() === '') {
    errors.push('计划标题不能为空')
  }
  
  if (!plan.modules || !Array.isArray(plan.modules) || plan.modules.length === 0) {
    errors.push('计划必须包含至少一个模块')
  }
  
  if (!plan.duration_days || plan.duration_days < 1) {
    errors.push('计划持续时间必须大于0天')
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}
