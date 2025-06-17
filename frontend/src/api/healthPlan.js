// 使用Mock API替代真实API调用
import { healthPlanAPI as mockHealthPlanAPI } from '../mock/api.js'

/**
 * 健康计划API服务 - Mock版本
 */
export class HealthPlanAPI {
  /**
   * 生成个性化健康计划
   * @param {Object} planRequest - 计划生成请求
   * @returns {Promise} 健康计划数据
   */
  static async generatePlan(planRequest) {
    try {
      const response = await mockHealthPlanAPI.createHealthPlan({
        title: planRequest.title || '个性化健康计划',
        description: planRequest.description || '基于您的需求定制的健康管理方案',
        plan_type: planRequest.plan_type || 'general',
        ...planRequest
      })
      return response
    } catch (error) {
      console.error('生成健康计划失败:', error)
      throw error
    }
  }

  /**
   * 获取用户的健康计划列表
   * @returns {Promise} 计划列表
   */
  static async getPlans() {
    try {
      const response = await mockHealthPlanAPI.getUserHealthPlans()
      return response
    } catch (error) {
      console.error('获取健康计划失败:', error)
      throw error
    }
  }

  /**
   * 获取特定健康计划详情
   * @param {string} planId - 计划ID
   * @returns {Promise} 计划详情
   */
  static async getPlanDetail(planId) {
    try {
      const response = await mockHealthPlanAPI.getHealthPlan(planId)
      return response
    } catch (error) {
      console.error('获取计划详情失败:', error)
      throw error
    }
  }

  /**
   * 更新健康计划
   * @param {string} planId - 计划ID
   * @param {Object} planData - 计划数据
   * @returns {Promise} API响应
   */
  static async updatePlan(planId, planData) {
    try {
      const response = await mockHealthPlanAPI.updateHealthPlan(planId, planData)
      return response
    } catch (error) {
      console.error('更新健康计划失败:', error)
      throw error
    }
  }

  /**
   * 删除健康计划
   * @param {string} planId - 计划ID
   * @returns {Promise} API响应
   */
  static async deletePlan(planId) {
    try {
      const response = await mockHealthPlanAPI.deleteHealthPlan(planId)
      return response
    } catch (error) {
      console.error('删除健康计划失败:', error)
      throw error
    }
  }

  /**
   * 导出健康计划 - Mock实现
   * @param {string} planId - 计划ID
   * @param {string} format - 导出格式 (pdf, json, txt)
   * @returns {Promise} 导出文件
   */
  static async exportPlan(planId, format = 'pdf') {
    try {
      // 模拟导出过程
      await new Promise(resolve => setTimeout(resolve, 1000))

      const plan = await mockHealthPlanAPI.getHealthPlan(planId)
      const exportData = {
        plan: plan.data,
        exportFormat: format,
        exportTime: new Date().toISOString(),
        downloadUrl: `mock://export/${planId}.${format}`
      }

      return {
        success: true,
        data: exportData,
        message: '计划导出成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('导出健康计划失败:', error)
      throw error
    }
  }

  /**
   * 保存计划调整反馈 - Mock实现
   * @param {string} planId - 计划ID
   * @param {Object} feedback - 反馈数据
   * @returns {Promise} API响应
   */
  static async saveFeedback(planId, feedback) {
    try {
      // 模拟保存反馈
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        data: {
          feedback_id: 'feedback_' + Date.now(),
          plan_id: planId,
          ...feedback,
          created_at: new Date().toISOString()
        },
        message: '反馈保存成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('保存计划反馈失败:', error)
      throw error
    }
  }

  /**
   * 获取计划执行进度 - Mock实现
   * @param {string} planId - 计划ID
   * @returns {Promise} 进度数据
   */
  static async getPlanProgress(planId) {
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const mockProgress = {
        plan_id: planId,
        overall_progress: 65,
        weekly_progress: 80,
        daily_progress: 75,
        completed_tasks: 13,
        total_tasks: 20,
        milestones: [
          {
            milestone_id: 'milestone_001',
            title: '第一周目标',
            status: 'completed',
            completion_date: '2024-06-10T00:00:00Z'
          },
          {
            milestone_id: 'milestone_002',
            title: '第二周目标',
            status: 'in_progress',
            completion_date: null
          }
        ],
        last_updated: new Date().toISOString()
      }

      return {
        success: true,
        data: mockProgress,
        message: '获取计划进度成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('获取计划进度失败:', error)
      throw error
    }
  }

  /**
   * 更新计划执行进度 - Mock实现
   * @param {string} planId - 计划ID
   * @param {Object} progressData - 进度数据
   * @returns {Promise} API响应
   */
  static async updatePlanProgress(planId, progressData) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        data: {
          plan_id: planId,
          ...progressData,
          updated_at: new Date().toISOString()
        },
        message: '计划进度更新成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('更新计划进度失败:', error)
      throw error
    }
  }

  /**
   * 获取计划模板 - Mock实现
   * @returns {Promise} 模板列表
   */
  static async getPlanTemplates() {
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const mockTemplates = [
        {
          template_id: 'template_001',
          title: '减重计划模板',
          description: '适合需要减重的用户',
          category: 'weight_loss',
          duration_weeks: 12,
          difficulty: 'medium',
          preview_image: null
        },
        {
          template_id: 'template_002',
          title: '增肌计划模板',
          description: '适合需要增肌的用户',
          category: 'muscle_gain',
          duration_weeks: 16,
          difficulty: 'hard',
          preview_image: null
        },
        {
          template_id: 'template_003',
          title: '心血管健康模板',
          description: '改善心血管健康',
          category: 'cardiovascular',
          duration_weeks: 8,
          difficulty: 'easy',
          preview_image: null
        }
      ]

      return {
        success: true,
        data: mockTemplates,
        message: '获取计划模板成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('获取计划模板失败:', error)
      throw error
    }
  }

  /**
   * 基于模板创建计划 - Mock实现
   * @param {string} templateId - 模板ID
   * @param {Object} customData - 自定义数据
   * @returns {Promise} API响应
   */
  static async createFromTemplate(templateId, customData) {
    try {
      const response = await mockHealthPlanAPI.createHealthPlan({
        title: customData.title || '基于模板的健康计划',
        description: customData.description || '基于模板定制的健康管理方案',
        template_id: templateId,
        ...customData
      })
      return response
    } catch (error) {
      console.error('基于模板创建计划失败:', error)
      throw error
    }
  }
}

export default HealthPlanAPI
