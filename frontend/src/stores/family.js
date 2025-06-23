/**
 * 家庭管理状态管理
 */
import { defineStore } from 'pinia'
import { familyAPI } from '../api/family.js'
import { message } from 'ant-design-vue'

export const useFamilyStore = defineStore('family', {
  state: () => ({
    // 当前用户的家庭列表
    userFamilies: [],
    
    // 当前选中的家庭
    currentFamily: null,
    
    // 当前活跃成员
    activeMember: null,
    
    // 家庭成员列表
    familyMembers: [],
    
    // 家庭权限信息
    familyPermissions: {},
    
    // 家庭健康数据
    familyHealthData: {
      summary: null,
      comparison: null,
      trends: null
    },
    
    // 家庭仪表盘数据
    dashboardData: {
      leaderboard: [],
      challenges: [],
      report: null
    },
    
    // 健康告警
    healthAlerts: [],
    
    // 加载状态
    loading: {
      families: false,
      members: false,
      dashboard: false,
      health: false,
      switching: false
    },
    
    // 用户角色和权限
    userRole: null,
    userPermissions: []
  }),

  getters: {
    // 是否有家庭
    hasFamilies: (state) => state.userFamilies.length > 0,
    
    // 当前用户是否为家庭管理员
    isAdmin: (state) => state.userRole === 'Owner' || state.userRole === 'Manager',
    
    // 是否可以邀请成员
    canInviteMembers: (state) => state.userPermissions.includes('invite_members'),
    
    // 是否可以管理成员
    canManageMembers: (state) => state.userPermissions.includes('manage_members'),
    
    // 是否可以查看所有成员数据
    canViewAllData: (state) => state.userPermissions.includes('view_all_data'),
    
    // 是否可以设置告警
    canSetAlerts: (state) => state.userPermissions.includes('set_alerts'),
    
    // 获取活跃成员信息
    activeMemberInfo: (state) => {
      if (!state.activeMember) return null
      return state.familyMembers.find(member => member.user_id === state.activeMember.user_id)
    },
    
    // 获取未读告警数量
    unreadAlertsCount: (state) => {
      return state.healthAlerts.filter(alert => !alert.is_read).length
    }
  },

  actions: {
    // 获取用户家庭列表
    async fetchUserFamilies() {
      this.loading.families = true
      try {
        const response = await familyAPI.getUserFamilies()
        // API返回的data字段直接是家庭数组
        this.userFamilies = response.data || []

        // 如果有家庭且没有选中当前家庭，选择第一个
        if (this.userFamilies.length > 0 && !this.currentFamily) {
          await this.selectFamily(this.userFamilies[0].family_id)
        }

        return this.userFamilies
      } catch (error) {
        console.error('获取家庭列表失败:', error)
        // 使用模拟数据，不显示错误消息，让用户可以创建家庭
        this.userFamilies = []
        return this.userFamilies
      } finally {
        this.loading.families = false
      }
    },

    // 选择家庭
    async selectFamily(familyId) {
      try {
        const response = await familyAPI.getFamilyInfo(familyId)
        this.currentFamily = response.data

        // 获取家庭成员和权限
        await Promise.all([
          this.fetchFamilyMembers(familyId),
          this.fetchFamilyPermissions(familyId)
        ])

        // 设置当前用户为活跃成员（如果没有设置的话）
        if (!this.activeMember && this.familyMembers.length > 0) {
          const currentUser = this.familyMembers.find(member => member.is_current_user)
          if (currentUser) {
            this.activeMember = currentUser
          }
        }

        return response
      } catch (error) {
        console.error('选择家庭失败:', error)
        // 使用模拟数据
        this.currentFamily = {
          family_id: familyId,
          family_name: '我的家庭',
          description: '模拟家庭数据'
        }
        this.familyMembers = [
          {
            user_id: 'current_user',
            display_name: '我',
            role: 'Owner',
            is_current_user: true,
            avatar: null
          }
        ]
        this.activeMember = this.familyMembers[0]
        this.userRole = 'Owner'
        this.userPermissions = ['invite_members', 'manage_members', 'view_all_data', 'set_alerts']
        return this.currentFamily
      }
    },

    // 创建家庭
    async createFamily(familyData) {
      try {
        const response = await familyAPI.createFamily(familyData)
        message.success('家庭创建成功')
        
        // 刷新家庭列表
        await this.fetchUserFamilies()
        
        return response
      } catch (error) {
        console.error('创建家庭失败:', error)
        message.error('创建家庭失败')
        throw error
      }
    },

    // 获取家庭成员
    async fetchFamilyMembers(familyId) {
      this.loading.members = true
      try {
        const response = await familyAPI.getFamilyMembers(familyId)
        this.familyMembers = response.data?.members || []
        return this.familyMembers
      } catch (error) {
        console.error('获取家庭成员失败:', error)
        // 使用模拟数据
        this.familyMembers = [
          {
            user_id: 'current_user',
            display_name: '我',
            role: 'Owner',
            is_current_user: true,
            avatar: null
          }
        ]
        return this.familyMembers
      } finally {
        this.loading.members = false
      }
    },

    // 获取家庭权限
    async fetchFamilyPermissions(familyId) {
      try {
        const response = await familyAPI.getFamilyPermissions(familyId)
        this.familyPermissions = response.data
        this.userRole = response.data?.role
        this.userPermissions = response.data?.permissions || []
        return response
      } catch (error) {
        console.error('获取家庭权限失败:', error)
        // 使用模拟数据
        this.familyPermissions = {
          role: 'Owner',
          permissions: ['invite_members', 'manage_members', 'view_all_data', 'set_alerts']
        }
        this.userRole = 'Owner'
        this.userPermissions = ['invite_members', 'manage_members', 'view_all_data', 'set_alerts']
        return this.familyPermissions
      }
    },

    // 邀请家庭成员
    async inviteMember(inviteData) {
      try {
        const response = await familyAPI.inviteMember(this.currentFamily.family_id, inviteData)
        message.success('邀请发送成功')
        return response
      } catch (error) {
        console.error('邀请成员失败:', error)
        message.error('邀请成员失败')
        throw error
      }
    },

    // 切换活跃成员
    async switchActiveMember(memberId) {
      this.loading.switching = true
      try {
        const response = await familyAPI.switchActiveMember({
          target_member_id: memberId
        })
        
        // 更新活跃成员
        const member = this.familyMembers.find(m => m.user_id === memberId)
        if (member) {
          this.activeMember = member
          message.success(`已切换到 ${member.display_name}`)
        }
        
        return response
      } catch (error) {
        console.error('切换活跃成员失败:', error)
        message.error('切换活跃成员失败')
        throw error
      } finally {
        this.loading.switching = false
      }
    },

    // 获取家庭仪表盘数据
    async fetchDashboardData(familyId) {
      this.loading.dashboard = true
      try {
        const [leaderboard, challenges, report] = await Promise.all([
          familyAPI.getFamilyLeaderboard(familyId),
          familyAPI.getFamilyChallenges(familyId),
          familyAPI.getFamilyHealthReport(familyId)
        ])

        this.dashboardData = {
          leaderboard: leaderboard.data?.leaderboard || [],
          challenges: challenges.data?.challenges || [],
          report: report.data
        }

        return this.dashboardData
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
        // 使用模拟数据
        this.dashboardData = {
          leaderboard: [],
          challenges: [],
          report: null
        }
        throw error
      } finally {
        this.loading.dashboard = false
      }
    },

    // 获取家庭健康数据
    async fetchFamilyHealthData(familyId, params = {}) {
      this.loading.health = true
      try {
        const [summary, comparison, trends] = await Promise.all([
          familyAPI.getFamilyHealthSummary(familyId, params),
          familyAPI.getMembersHealthComparison(familyId, params),
          familyAPI.getFamilyHealthTrends(familyId, params)
        ])

        this.familyHealthData = {
          summary: summary.data,
          comparison: comparison.data,
          trends: trends.data
        }

        return this.familyHealthData
      } catch (error) {
        console.error('获取家庭健康数据失败:', error)
        // 使用模拟数据
        this.familyHealthData = {
          summary: null,
          comparison: null,
          trends: null
        }
        throw error
      } finally {
        this.loading.health = false
      }
    },

    // 获取健康告警
    async fetchHealthAlerts(familyId) {
      try {
        const response = await familyAPI.getHealthAlerts(familyId)
        this.healthAlerts = response.data?.alerts || []
        return this.healthAlerts
      } catch (error) {
        console.error('获取健康告警失败:', error)
        // 使用模拟数据
        this.healthAlerts = []
        throw error
      }
    },

    // 创建家庭挑战
    async createChallenge(challengeData) {
      try {
        const response = await familyAPI.createFamilyChallenge(
          this.currentFamily.family_id,
          challengeData
        )
        message.success('挑战创建成功')

        // 刷新挑战列表
        await this.fetchDashboardData(this.currentFamily.family_id)

        return response
      } catch (error) {
        console.error('创建挑战失败:', error)
        message.error('创建挑战失败')
        throw error
      }
    },

    // 重置状态
    resetState() {
      this.userFamilies = []
      this.currentFamily = null
      this.activeMember = null
      this.familyMembers = []
      this.familyPermissions = {}
      this.familyHealthData = {
        summary: null,
        comparison: null,
        trends: null
      }
      this.dashboardData = {
        leaderboard: [],
        challenges: [],
        report: null
      }
      this.healthAlerts = []
      this.userRole = null
      this.userPermissions = []
    }
  }
})
