/**
 * 家庭管理API接口 - Mock版本
 */
// 使用Mock API替代真实API调用
import { familyAPI as mockFamilyAPI } from '../mock/api.js'

// 家庭管理
export const familyAPI = {
  // 创建家庭
  async createFamily(data) {
    try {
      const response = await mockFamilyAPI.createFamily(data)
      return response
    } catch (error) {
      throw new Error(error.message || '创建家庭失败')
    }
  },

  // 获取用户的家庭列表
  async getUserFamilies() {
    try {
      const response = await mockFamilyAPI.getUserFamilies()
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭列表失败')
    }
  },

  // 获取家庭详情
  async getFamilyInfo(familyId) {
    try {
      const response = await mockFamilyAPI.getFamilyInfo(familyId)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭信息失败')
    }
  },

  // 邀请家庭成员
  async inviteMember(familyId, data) {
    try {
      // 模拟邀请成员
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        message: '邀请发送成功',
        data: {
          invitation_id: 'invite_' + Date.now(),
          family_id: familyId,
          ...data,
          status: 'pending',
          created_at: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '邀请成员失败')
    }
  },

  // 接受家庭邀请
  async acceptInvitation(data) {
    try {
      // 模拟接受邀请
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        message: '邀请接受成功',
        data: {
          ...data,
          status: 'accepted',
          accepted_at: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '接受邀请失败')
    }
  },

  // 拒绝家庭邀请
  async declineInvitation(data) {
    try {
      // 模拟拒绝邀请
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        message: '邀请已拒绝',
        data: {
          ...data,
          status: 'declined',
          declined_at: new Date().toISOString()
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '拒绝邀请失败')
    }
  },

  // 获取家庭成员列表
  async getFamilyMembers(familyId) {
    try {
      const response = await mockFamilyAPI.getFamilyMembers(familyId)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭成员失败')
    }
  },

  // 获取家庭权限
  async getFamilyPermissions(familyId) {
    try {
      const response = await mockFamilyAPI.getFamilyPermissions(familyId)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭权限失败')
    }
  },

  // 切换活跃成员
  async switchActiveMember(data) {
    try {
      const response = await mockFamilyAPI.switchActiveMember(data)
      return response
    } catch (error) {
      throw new Error(error.message || '切换活跃成员失败')
    }
  },

  // 获取家庭健康报告
  async getFamilyHealthReport(familyId, params = {}) {
    try {
      const response = await mockFamilyAPI.getFamilyHealthReport(familyId, params)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭健康报告失败')
    }
  },

  // 获取家庭排行榜
  async getFamilyLeaderboard(familyId, params = {}) {
    try {
      const response = await mockFamilyAPI.getFamilyLeaderboard(familyId, params)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭排行榜失败')
    }
  },

  // 获取家庭挑战
  async getFamilyChallenges(familyId) {
    try {
      const response = await mockFamilyAPI.getFamilyChallenges(familyId)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭挑战失败')
    }
  },

  // 创建家庭挑战
  async createFamilyChallenge(familyId, data) {
    try {
      const response = await mockFamilyAPI.createFamilyChallenge(familyId, data)
      return response
    } catch (error) {
      throw new Error(error.message || '创建家庭挑战失败')
    }
  },

  // 为成员点赞
  async likeMember(memberId, data) {
    try {
      const response = await mockFamilyAPI.likeMember(memberId, data)
      return response
    } catch (error) {
      throw new Error(error.message || '点赞失败')
    }
  },

  // 获取健康告警列表
  async getHealthAlerts(familyId) {
    try {
      const response = await mockFamilyAPI.getHealthAlerts(familyId)
      return response
    } catch (error) {
      throw new Error(error.message || '获取健康告警失败')
    }
  }
}

// 为了保持向后兼容，导出相同的API结构
export const familyDashboardAPI = familyAPI
export const familyHealthAPI = familyAPI
export const memberAPI = familyAPI
export const permissionAPI = familyAPI

export default {
  familyAPI,
  familyDashboardAPI,
  familyHealthAPI,
  memberAPI,
  permissionAPI
}
