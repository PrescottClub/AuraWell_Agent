import request from '../utils/request'

/**
 * 健康计划API服务
 */
export class HealthPlanAPI {
  /**
   * 生成个性化健康计划
   * @param {Object} planRequest - 计划生成请求
   * @returns {Promise} 健康计划数据
   */
  static async generatePlan(planRequest) {
    try {
      const response = await request.post('/health-plan/generate', planRequest)
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
      const response = await request.get('/health-plan/plans')
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
      const response = await request.get(`/health-plan/plans/${planId}`)
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
      const response = await request.put(`/health-plan/plans/${planId}`, planData)
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
      const response = await request.delete(`/health-plan/plans/${planId}`)
      return response
    } catch (error) {
      console.error('删除健康计划失败:', error)
      throw error
    }
  }

  /**
   * 导出健康计划
   * @param {string} planId - 计划ID
   * @param {string} format - 导出格式 (pdf, json, txt)
   * @returns {Promise} 导出文件
   */
  static async exportPlan(planId, format = 'pdf') {
    try {
      const response = await request.get(`/health-plan/plans/${planId}/export`, {
        params: { format },
        responseType: 'blob'
      })
      return response
    } catch (error) {
      console.error('导出健康计划失败:', error)
      throw error
    }
  }

  /**
   * 保存计划调整反馈
   * @param {string} planId - 计划ID
   * @param {Object} feedback - 反馈数据
   * @returns {Promise} API响应
   */
  static async saveFeedback(planId, feedback) {
    try {
      const response = await request.post(`/health-plan/plans/${planId}/feedback`, feedback)
      return response
    } catch (error) {
      console.error('保存计划反馈失败:', error)
      throw error
    }
  }

  /**
   * 获取计划执行进度
   * @param {string} planId - 计划ID
   * @returns {Promise} 进度数据
   */
  static async getPlanProgress(planId) {
    try {
      const response = await request.get(`/health-plan/plans/${planId}/progress`)
      return response
    } catch (error) {
      console.error('获取计划进度失败:', error)
      throw error
    }
  }

  /**
   * 更新计划执行进度
   * @param {string} planId - 计划ID
   * @param {Object} progressData - 进度数据
   * @returns {Promise} API响应
   */
  static async updatePlanProgress(planId, progressData) {
    try {
      const response = await request.put(`/health-plan/plans/${planId}/progress`, progressData)
      return response
    } catch (error) {
      console.error('更新计划进度失败:', error)
      throw error
    }
  }

  /**
   * 获取计划模板
   * @returns {Promise} 模板列表
   */
  static async getPlanTemplates() {
    try {
      const response = await request.get('/health-plan/templates')
      return response
    } catch (error) {
      console.error('获取计划模板失败:', error)
      throw error
    }
  }

  /**
   * 基于模板创建计划
   * @param {string} templateId - 模板ID
   * @param {Object} customData - 自定义数据
   * @returns {Promise} API响应
   */
  static async createFromTemplate(templateId, customData) {
    try {
      const response = await request.post(`/health-plan/templates/${templateId}/create`, customData)
      return response
    } catch (error) {
      console.error('基于模板创建计划失败:', error)
      throw error
    }
  }
}

export default HealthPlanAPI
