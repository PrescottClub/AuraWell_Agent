/**
 * 家庭管理API接口
 */
import request from '@/utils/request'

// 家庭管理
export const familyAPI = {
  // 创建家庭
  createFamily(data) {
    return request({
      url: '/family',
      method: 'post',
      data
    })
  },

  // 获取用户的家庭列表
  getUserFamilies() {
    return request({
      url: '/family',
      method: 'get'
    })
  },

  // 获取家庭详情
  getFamilyInfo(familyId) {
    return request({
      url: `/family/${familyId}`,
      method: 'get'
    })
  },

  // 邀请家庭成员
  inviteMember(familyId, data) {
    return request({
      url: `/family/${familyId}/invite`,
      method: 'post',
      data
    })
  },

  // 接受家庭邀请
  acceptInvitation(data) {
    return request({
      url: '/family/invitation/accept',
      method: 'post',
      data
    })
  },

  // 拒绝家庭邀请
  declineInvitation(data) {
    return request({
      url: '/family/invitation/decline',
      method: 'post',
      data
    })
  },

  // 获取家庭成员列表
  getFamilyMembers(familyId) {
    return request({
      url: `/family/${familyId}/members`,
      method: 'get'
    })
  },

  // 获取家庭权限
  getFamilyPermissions(familyId) {
    return request({
      url: `/family/${familyId}/permissions`,
      method: 'get'
    })
  },

  // 切换活跃成员
  switchActiveMember(data) {
    return request({
      url: '/family/switch-member',
      method: 'post',
      data
    })
  }
}

// 家庭仪表盘
export const familyDashboardAPI = {
  // 获取家庭健康报告
  getFamilyHealthReport(familyId, params = {}) {
    return request({
      url: `/family/${familyId}/report`,
      method: 'get',
      params
    })
  },

  // 获取家庭排行榜
  getFamilyLeaderboard(familyId, params = {}) {
    return request({
      url: `/family/${familyId}/leaderboard`,
      method: 'get',
      params
    })
  },

  // 获取家庭挑战
  getFamilyChallenges(familyId) {
    return request({
      url: `/family/${familyId}/challenges`,
      method: 'get'
    })
  },

  // 创建家庭挑战
  createFamilyChallenge(familyId, data) {
    return request({
      url: `/family/${familyId}/challenges`,
      method: 'post',
      data
    })
  },

  // 参与家庭挑战
  joinChallenge(challengeId) {
    return request({
      url: `/family/challenges/${challengeId}/join`,
      method: 'post'
    })
  },

  // 为成员点赞
  likeMember(memberId, data) {
    return request({
      url: `/family/members/${memberId}/like`,
      method: 'post',
      data
    })
  }
}

// 家庭健康数据
export const familyHealthAPI = {
  // 获取家庭成员健康摘要
  getFamilyHealthSummary(familyId, params = {}) {
    return request({
      url: `/family/${familyId}/health/summary`,
      method: 'get',
      params
    })
  },

  // 获取成员健康数据对比
  getMembersHealthComparison(familyId, params = {}) {
    return request({
      url: `/family/${familyId}/health/comparison`,
      method: 'get',
      params
    })
  },

  // 获取家庭健康趋势
  getFamilyHealthTrends(familyId, params = {}) {
    return request({
      url: `/family/${familyId}/health/trends`,
      method: 'get',
      params
    })
  },

  // 设置健康告警
  setHealthAlert(familyId, data) {
    return request({
      url: `/family/${familyId}/health/alerts`,
      method: 'post',
      data
    })
  },

  // 获取健康告警列表
  getHealthAlerts(familyId) {
    return request({
      url: `/family/${familyId}/health/alerts`,
      method: 'get'
    })
  },

  // 更新告警状态
  updateAlertStatus(alertId, data) {
    return request({
      url: `/family/health/alerts/${alertId}`,
      method: 'put',
      data
    })
  }
}

// 成员管理
export const memberAPI = {
  // 更新成员信息
  updateMemberInfo(memberId, data) {
    return request({
      url: `/family/members/${memberId}`,
      method: 'put',
      data
    })
  },

  // 更新成员权限
  updateMemberPermissions(memberId, data) {
    return request({
      url: `/family/members/${memberId}/permissions`,
      method: 'put',
      data
    })
  },

  // 移除家庭成员
  removeMember(familyId, memberId) {
    return request({
      url: `/family/${familyId}/members/${memberId}`,
      method: 'delete'
    })
  },

  // 获取成员详细信息
  getMemberDetails(memberId) {
    return request({
      url: `/family/members/${memberId}`,
      method: 'get'
    })
  },

  // 获取成员健康数据
  getMemberHealthData(memberId, params = {}) {
    return request({
      url: `/family/members/${memberId}/health`,
      method: 'get',
      params
    })
  }
}

// 权限管理
export const permissionAPI = {
  // 获取角色列表
  getRoles() {
    return request({
      url: '/family/roles',
      method: 'get'
    })
  },

  // 获取权限列表
  getPermissions() {
    return request({
      url: '/family/permissions',
      method: 'get'
    })
  },

  // 检查用户权限
  checkPermission(familyId, permission) {
    return request({
      url: `/family/${familyId}/check-permission`,
      method: 'post',
      data: { permission }
    })
  }
}

export default {
  familyAPI,
  familyDashboardAPI,
  familyHealthAPI,
  memberAPI,
  permissionAPI
}
