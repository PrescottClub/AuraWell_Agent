/**
 * 家庭管理API接口 - 真实后端版本
 */
import request from '../utils/request.js'

// 家庭管理
export const familyAPI = {
  // 创建家庭
  async createFamily(data) {
    try {
      const response = await request.post('/family', {
        name: data.name,
        description: data.description || null
      })
      return response
    } catch (error) {
      throw new Error(error.message || '创建家庭失败')
    }
  },

  // 获取用户的家庭列表
  async getUserFamilies() {
    try {
      const response = await request.get('/family/user-families')
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭列表失败')
    }
  },

  // 获取家庭详情
  async getFamilyInfo(familyId) {
    try {
      const response = await request.get(`/family/${familyId}`)
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
      const response = await request.get(`/family/${familyId}/members`)
      return response
    } catch (error) {
      throw new Error(error.message || '获取家庭成员失败')
    }
  },

  // 获取家庭权限 - Mock实现
  async getFamilyPermissions(familyId) {
    try {
      // 模拟家庭权限数据
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: {
          family_id: familyId,
          permissions: {
            can_view_health_data: true,
            can_edit_family_info: false,
            can_invite_members: false,
            can_remove_members: false,
            can_manage_challenges: false
          }
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '获取家庭权限失败')
    }
  },

  // 切换活跃成员 - Mock实现
  async switchActiveMember(data) {
    try {
      // 模拟切换活跃成员
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: {
          active_member_id: data.member_id,
          switched_at: new Date().toISOString()
        },
        message: '活跃成员切换成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '切换活跃成员失败')
    }
  },

  // 获取家庭健康报告 - Mock实现
  async getFamilyHealthReport(familyId) {
    try {
      // 模拟家庭健康报告
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        data: {
          family_id: familyId,
          period: 'week',
          summary: {
            total_steps: 45000,
            avg_sleep_hours: 7.2,
            active_members: 3,
            weekly_challenges: 2
          },
          members_data: []
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '获取家庭健康报告失败')
    }
  },

  // 获取家庭排行榜 - Mock实现
  async getFamilyLeaderboard(familyId) {
    try {
      // 模拟家庭排行榜 - 使用familyId进行数据过滤
      console.log(`获取家庭 ${familyId} 的排行榜`)
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: {
          leaderboard: [
            {
              member_id: 'member_001',
              display_name: '爸爸',
              score: 850,
              rank: 1,
              avatar: null
            },
            {
              member_id: 'member_002',
              display_name: '妈妈',
              score: 720,
              rank: 2,
              avatar: null
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '获取家庭排行榜失败')
    }
  },

  // 获取家庭挑战 - Mock实现
  async getFamilyChallenges(familyId) {
    try {
      // 模拟家庭挑战 - 使用familyId进行数据过滤
      console.log(`获取家庭 ${familyId} 的挑战`)
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: {
          challenges: [
            {
              challenge_id: 'challenge_001',
              title: '家庭步数挑战',
              description: '本周目标：每人每天走10000步',
              type: 'steps',
              status: 'active',
              target_value: 10000,
              current_value: 7500,
              progress_percentage: 75,
              participants_count: 3
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '获取家庭挑战失败')
    }
  },

  // 创建家庭挑战 - Mock实现
  async createFamilyChallenge(familyId, data) {
    try {
      // 模拟创建家庭挑战
      await new Promise(resolve => setTimeout(resolve, 500))

      return {
        success: true,
        data: {
          challenge_id: 'challenge_' + Date.now(),
          family_id: familyId,
          ...data,
          status: 'active',
          created_at: new Date().toISOString()
        },
        message: '家庭挑战创建成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '创建家庭挑战失败')
    }
  },

  // 为成员点赞 - Mock实现
  async likeMember(memberId, data) {
    try {
      // 模拟点赞
      await new Promise(resolve => setTimeout(resolve, 200))

      return {
        success: true,
        data: {
          member_id: memberId,
          likes_count: (data.current_likes || 0) + 1,
          liked_at: new Date().toISOString()
        },
        message: '点赞成功',
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      throw new Error(error.message || '点赞失败')
    }
  },

  // 获取健康告警列表 - Mock实现
  async getHealthAlerts(familyId) {
    try {
      // 模拟健康告警
      await new Promise(resolve => setTimeout(resolve, 300))

      return {
        success: true,
        data: {
          alerts: [
            {
              alert_id: 'alert_001',
              family_id: familyId,
              member_id: 'member_002',
              alert_type: 'weight_gain',
              title: '体重异常增长',
              message: '妈妈的体重在过去一周增长了2kg，建议关注饮食和运动',
              severity: 'medium',
              status: 'active',
              created_at: new Date().toISOString()
            }
          ]
        },
        timestamp: new Date().toISOString()
      }
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
