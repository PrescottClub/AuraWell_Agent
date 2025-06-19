import request from '../utils/request.js'

/**
 * 用户管理API服务 - 真实后端版本
 */
export class UserAPI {
  /**
   * 🔑 验证当前Token是否有效 - 轻量级认证检查
   * 这是专门为解决认证循环问题而设计的函数
   * @returns {Promise<boolean>} Token是否有效
   */
  static async validateCurrentToken() {
    try {
      const response = await request.get('/user/profile')
      return response && response.status === 'success'
    } catch (error) {
      // 任何错误（401、网络错误等）都表示Token无效
      console.warn('Token验证失败:', error.response?.status || error.message)
      return false
    }
  }

  /**
   * 获取当前用户信息 - 用于身份验证
   * @returns {Promise} 用户信息
   */
  static async getMe() {
    try {
      const response = await request.get('/user/profile')
      return {
        success: true,
        data: response.data,
        message: '获取用户信息成功'
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  /**
   * 获取用户个人档案
   * @returns {Promise} 用户档案数据
   */
  static async getProfile() {
    try {
      const response = await request.get('/user/profile')
      return response
    } catch (error) {
      console.error('获取用户档案失败:', error)
      throw error
    }
  }

  /**
   * 更新用户个人档案
   * @param {Object} profileData - 档案数据
   * @returns {Promise} API响应
   */
  static async updateProfile(profileData) {
    try {
      const response = await request.put('/user/profile', profileData)
      return response
    } catch (error) {
      console.error('更新用户档案失败:', error)
      throw error
    }
  }

  /**
   * 获取用户健康数据
   * @returns {Promise} 健康数据
   */
  static async getHealthData() {
    try {
      const response = await request.get('/user/health-data')
      return response
    } catch (error) {
      console.error('获取健康数据失败:', error)
      throw error
    }
  }

  /**
   * 更新用户健康数据
   * @param {Object} healthData - 健康数据
   * @returns {Promise} API响应
   */
  static async updateHealthData(healthData) {
    try {
      const response = await request.put('/user/health-data', healthData)
      return response
    } catch (error) {
      console.error('更新健康数据失败:', error)
      throw error
    }
  }

  /**
   * 获取用户健康目标
   * @returns {Promise} 健康目标列表
   */
  static async getHealthGoals() {
    try {
      const response = await request.get('/user/health-goals')
      return response
    } catch (error) {
      console.error('获取健康目标失败:', error)
      throw error
    }
  }

  /**
   * 创建健康目标
   * @param {Object} goalData - 目标数据
   * @returns {Promise} API响应
   */
  static async createHealthGoal(goalData) {
    try {
      const response = await request.post('/user/health-goals', goalData)
      return response
    } catch (error) {
      console.error('创建健康目标失败:', error)
      throw error
    }
  }

  /**
   * 更新健康目标
   * @param {string} goalId - 目标ID
   * @param {Object} goalData - 更新数据
   * @returns {Promise} API响应
   */
  static async updateHealthGoal(goalId, goalData) {
    try {
      const response = await request.put(`/user/health-goals/${goalId}`, goalData)
      return response
    } catch (error) {
      console.error('更新健康目标失败:', error)
      throw error
    }
  }

  /**
   * 删除健康目标
   * @param {string} goalId - 目标ID
   * @returns {Promise} API响应
   */
  static async deleteHealthGoal(goalId) {
    try {
      const response = await request.delete(`/user/health-goals/${goalId}`)
      return response
    } catch (error) {
      console.error('删除健康目标失败:', error)
      throw error
    }
  }

  /**
   * 用户登出
   * @returns {Promise} API响应
   */
  static async logout() {
    try {
      const response = await request.post('/auth/logout')
      return response
    } catch (error) {
      console.error('登出失败:', error)
      throw error
    }
  }
}

export default UserAPI
