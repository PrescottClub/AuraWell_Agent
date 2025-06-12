import request from '../utils/request'

/**
 * 用户管理API服务
 */
export class UserAPI {
  /**
   * 用户注册
   * @param {Object} userData - 用户注册数据
   * @returns {Promise} API响应
   */
  static async register(userData) {
    try {
      const response = await request.post('/auth/register', userData)
      return response
    } catch (error) {
      console.error('用户注册失败:', error)
      throw error
    }
  }

  /**
   * 用户登录
   * @param {Object} credentials - 登录凭据
   * @returns {Promise} API响应
   */
  static async login(credentials) {
    try {
      const response = await request.post('/auth/login', credentials)
      return response
    } catch (error) {
      console.error('用户登录失败:', error)
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
   * @param {Object} goalData - 目标数据
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
}

export default UserAPI
