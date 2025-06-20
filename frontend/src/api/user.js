// 使用Mock API替代真实API调用
import { authAPI } from '../mock/api'

/**
 * 用户管理API服务 - Mock版本
 */
export class UserAPI {
  /**
   * 🔑 验证当前Token是否有效 - 轻量级认证检查
   * 这是专门为解决认证循环问题而设计的函数
   * @returns {Promise<boolean>} Token是否有效
   */
  static async validateCurrentToken() {
    try {
      const response = await authAPI.getCurrentUser()
      return response && response.success
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
      const response = await authAPI.getCurrentUser()
      return response
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
      const response = await authAPI.getCurrentUser()
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
      const response = await authAPI.updateProfile(profileData)
      return response
    } catch (error) {
      console.error('更新用户档案失败:', error)
      throw error
    }
  }

  /**
   * 获取用户健康数据 - Mock实现
   * @returns {Promise} 健康数据
   */
  static async getHealthData() {
    try {
      // 模拟健康数据
      await new Promise(resolve => setTimeout(resolve, 300))

      const mockHealthData = {
        weight: 70,
        height: 175,
        bmi: 22.9,
        blood_pressure: '120/80',
        heart_rate: 72,
        steps_today: 8500,
        sleep_hours: 7.5,
        water_intake: 2.1,
        last_updated: new Date().toISOString()
      }

      return {
        success: true,
        data: mockHealthData,
        message: '获取健康数据成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('获取健康数据失败:', error)
      throw error
    }
  }

  /**
   * 更新用户健康数据 - Mock实现
   * @param {Object} healthData - 健康数据
   * @returns {Promise} API响应
   */
  static async updateHealthData(healthData) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        data: {
          ...healthData,
          last_updated: new Date().toISOString()
        },
        message: '健康数据更新成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('更新健康数据失败:', error)
      throw error
    }
  }

  /**
   * 获取用户健康目标 - Mock实现
   * @returns {Promise} 健康目标列表
   */
  static async getHealthGoals() {
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      const mockGoals = [
        {
          goal_id: 'goal_001',
          title: '减重目标',
          description: '3个月内减重5kg',
          target_value: 65,
          current_value: 70,
          unit: 'kg',
          deadline: '2024-09-17',
          status: 'active',
          progress: 0
        },
        {
          goal_id: 'goal_002',
          title: '每日步数',
          description: '每天走10000步',
          target_value: 10000,
          current_value: 8500,
          unit: '步',
          deadline: '2024-12-31',
          status: 'active',
          progress: 85
        }
      ]

      return {
        success: true,
        data: mockGoals,
        message: '获取健康目标成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('获取健康目标失败:', error)
      throw error
    }
  }

  /**
   * 创建健康目标 - Mock实现
   * @param {Object} goalData - 目标数据
   * @returns {Promise} API响应
   */
  static async createHealthGoal(goalData) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500))

      const newGoal = {
        goal_id: 'goal_' + Date.now(),
        ...goalData,
        current_value: 0,
        progress: 0,
        status: 'active',
        created_at: new Date().toISOString()
      }

      return {
        success: true,
        data: newGoal,
        message: '健康目标创建成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('创建健康目标失败:', error)
      throw error
    }
  }

  /**
   * 更新健康目标 - Mock实现
   * @param {string} goalId - 目标ID
   * @param {Object} goalData - 更新数据
   * @returns {Promise} API响应
   */
  static async updateHealthGoal(goalId, goalData) {
    try {
      await new Promise(resolve => setTimeout(resolve, 500))

      const updatedGoal = {
        goal_id: goalId,
        ...goalData,
        updated_at: new Date().toISOString()
      }

      return {
        success: true,
        data: updatedGoal,
        message: '健康目标更新成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('更新健康目标失败:', error)
      throw error
    }
  }

  /**
   * 删除健康目标 - Mock实现
   * @param {string} goalId - 目标ID
   * @returns {Promise} API响应
   */
  static async deleteHealthGoal(goalId) {
    try {
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: null,
        message: '健康目标删除成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      console.error('删除健康目标失败:', error)
      throw error
    }
  }

  /**
   * 用户登录 - Mock实现
   * @param {Object} credentials - 登录凭据
   * @returns {Promise} API响应
   */
  static async login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      return response
    } catch (error) {
      console.error('用户登录失败:', error)
      throw error
    }
  }

  /**
   * 用户登出 - Mock实现
   * @returns {Promise} API响应
   */
  static async logout() {
    try {
      const response = await authAPI.logout()
      return response
    } catch (error) {
      console.error('用户登出失败:', error)
      throw error
    }
  }
}

export default UserAPI
