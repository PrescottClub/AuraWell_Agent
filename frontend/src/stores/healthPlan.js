import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { HealthPlanAPI } from '../api/healthPlan.js'

export const useHealthPlanStore = defineStore('healthPlan', () => {
  // 状态
  const plans = ref([])
  const currentPlan = ref(null)
  const planTemplates = ref([])
  const loading = ref(false)
  const error = ref('')
  const generatingPlan = ref(false)

  // 计算属性
  const activePlans = computed(() => {
    return plans.value.filter(plan => plan.status === 'active')
  })

  const completedPlans = computed(() => {
    return plans.value.filter(plan => plan.status === 'completed')
  })

  const currentPlanProgress = computed(() => {
    if (!currentPlan.value || !currentPlan.value.progress) return 0
    const progress = currentPlan.value.progress
    const totalTasks = progress.total_tasks || 1
    const completedTasks = progress.completed_tasks || 0
    return Math.round((completedTasks / totalTasks) * 100)
  })

  // 方法
  const fetchPlans = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.getPlans()
      if (response.data) {
        plans.value = response.data
      }
    } catch (err) {
      error.value = '获取健康计划失败'
      console.error('获取健康计划失败:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchPlanDetail = async (planId) => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.getPlanDetail(planId)
      if (response.data) {
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = '获取计划详情失败'
      console.error('获取计划详情失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const generatePlan = async (planRequest) => {
    generatingPlan.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.generatePlan(planRequest)
      if (response.data) {
        plans.value.unshift(response.data)
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = '生成健康计划失败'
      console.error('生成健康计划失败:', err)
      throw err
    } finally {
      generatingPlan.value = false
    }
  }

  const updatePlan = async (planId, planData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.updatePlan(planId, planData)
      if (response.data) {
        const index = plans.value.findIndex(plan => plan.id === planId)
        if (index !== -1) {
          plans.value[index] = response.data
        }
        if (currentPlan.value && currentPlan.value.id === planId) {
          currentPlan.value = response.data
        }
      }
      return response.data
    } catch (err) {
      error.value = '更新健康计划失败'
      console.error('更新健康计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deletePlan = async (planId) => {
    loading.value = true
    error.value = ''
    try {
      await HealthPlanAPI.deletePlan(planId)
      plans.value = plans.value.filter(plan => plan.id !== planId)
      if (currentPlan.value && currentPlan.value.id === planId) {
        currentPlan.value = null
      }
    } catch (err) {
      error.value = '删除健康计划失败'
      console.error('删除健康计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportPlan = async (planId, format = 'pdf') => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.exportPlan(planId, format)
      
      // 创建下载链接
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'application/octet-stream' 
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `health-plan-${planId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      return response
    } catch (err) {
      error.value = '导出健康计划失败'
      console.error('导出健康计划失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const savePlanFeedback = async (planId, feedback) => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.saveFeedback(planId, feedback)
      return response
    } catch (err) {
      error.value = '保存计划反馈失败'
      console.error('保存计划反馈失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPlanProgress = async (planId) => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.getPlanProgress(planId)
      if (response.data && currentPlan.value && currentPlan.value.id === planId) {
        currentPlan.value.progress = response.data
      }
      return response.data
    } catch (err) {
      error.value = '获取计划进度失败'
      console.error('获取计划进度失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePlanProgress = async (planId, progressData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.updatePlanProgress(planId, progressData)
      if (response.data && currentPlan.value && currentPlan.value.id === planId) {
        currentPlan.value.progress = response.data
      }
      return response.data
    } catch (err) {
      error.value = '更新计划进度失败'
      console.error('更新计划进度失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPlanTemplates = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.getPlanTemplates()
      if (response.data) {
        planTemplates.value = response.data
      }
    } catch (err) {
      error.value = '获取计划模板失败'
      console.error('获取计划模板失败:', err)
    } finally {
      loading.value = false
    }
  }

  const createFromTemplate = async (templateId, customData) => {
    generatingPlan.value = true
    error.value = ''
    try {
      const response = await HealthPlanAPI.createFromTemplate(templateId, customData)
      if (response.data) {
        plans.value.unshift(response.data)
        currentPlan.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = '基于模板创建计划失败'
      console.error('基于模板创建计划失败:', err)
      throw err
    } finally {
      generatingPlan.value = false
    }
  }

  const clearCurrentPlan = () => {
    currentPlan.value = null
  }

  const clearError = () => {
    error.value = ''
  }

  return {
    // 状态
    plans,
    currentPlan,
    planTemplates,
    loading,
    error,
    generatingPlan,
    
    // 计算属性
    activePlans,
    completedPlans,
    currentPlanProgress,
    
    // 方法
    fetchPlans,
    fetchPlanDetail,
    generatePlan,
    updatePlan,
    deletePlan,
    exportPlan,
    savePlanFeedback,
    fetchPlanProgress,
    updatePlanProgress,
    fetchPlanTemplates,
    createFromTemplate,
    clearCurrentPlan,
    clearError
  }
})
