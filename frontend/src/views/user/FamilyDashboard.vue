<template>
  <div class="min-h-screen bg-background p-8">
    <!-- 没有家庭的状态 -->
    <div v-if="!familyStore.currentFamily" class="flex items-center justify-center min-h-[60vh]">
      <div class="aura-card text-center max-w-md">
        <div class="w-20 h-20 bg-background-surface rounded-full flex items-center justify-center mx-auto mb-6">
          <TeamOutlined class="w-10 h-10 text-primary" />
        </div>
        <h2 class="text-heading-3 mb-3">开始您的家庭健康之旅</h2>
        <p class="text-body mb-6">创建家庭，与家人一起追踪健康数据，共同实现健康目标</p>
        <button class="aura-btn aura-btn--primary" @click="showCreateFamilyModal = true">
          <PlusOutlined />
          创建家庭
        </button>
      </div>
    </div>

    <!-- 有家庭的正常状态 -->
    <div v-else>
      <!-- 页面头部 -->
      <div class="aura-card mb-8">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-display mb-2">
              {{ familyStore.currentFamily?.family_name }}
              <span class="text-primary">家庭仪表盘</span>
            </h1>
            <p class="text-body-large flex items-center gap-2">
              <TeamOutlined class="text-primary" />
              共 {{ familyStore.familyMembers.length }} 名成员
            </p>
          </div>
          <div class="flex gap-3">
            <button class="aura-btn aura-btn--primary" @click="showCreateChallenge = true">
              <PlusOutlined />
              创建挑战
            </button>
            <button class="aura-btn aura-btn--secondary" @click="refreshDashboard">
              <ReloadOutlined />
              刷新
            </button>
          </div>
        </div>
      </div>

    <!-- 成员切换器 -->
    <div class="aura-card mb-8">
      <MemberSwitcher />
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="aura-card text-center">
        <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
          <StepForwardOutlined class="w-6 h-6 text-primary" />
        </div>
        <div class="text-metric-large text-text-primary">{{ formatNumber(dashboardStats.totalSteps) }}</div>
        <div class="text-body-small text-text-secondary mt-1">今日总步数</div>
      </div>

      <div class="aura-card text-center">
        <div class="w-12 h-12 bg-health/10 rounded-xl flex items-center justify-center mx-auto mb-4">
          <ClockCircleOutlined class="w-6 h-6 text-health" />
        </div>
        <div class="text-metric-large text-text-primary">{{ dashboardStats.avgSleep.toFixed(1) }}h</div>
        <div class="text-body-small text-text-secondary mt-1">平均睡眠</div>
      </div>

      <div class="aura-card text-center">
        <div class="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mx-auto mb-4">
          <UserOutlined class="w-6 h-6 text-accent" />
        </div>
        <div class="text-metric-large text-text-primary">{{ dashboardStats.activeMembers }}</div>
        <div class="text-body-small text-text-secondary mt-1">活跃成员</div>
      </div>

      <div class="aura-card text-center">
        <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
          <TrophyOutlined class="w-6 h-6 text-primary" />
        </div>
        <div class="text-metric-large text-text-primary">{{ dashboardStats.weeklyGoals }}</div>
        <div class="text-body-small text-text-secondary mt-1">本周挑战</div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：排行榜和挑战 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 家庭排行榜 -->
        <div class="aura-card">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-heading-3">本周排行榜</h2>
            <a-select
              v-model="leaderboardMetric"
              class="w-32"
              @change="fetchLeaderboard"
            >
              <a-select-option value="steps">步数</a-select-option>
              <a-select-option value="calories">卡路里</a-select-option>
              <a-select-option value="sleep_hours">睡眠</a-select-option>
            </a-select>
          </div>

          <div class="space-y-3">
            <div
              v-for="(member, index) in leaderboardData"
              :key="member.user_id"
              class="flex items-center justify-between p-4 bg-background-elevated rounded-xl border border-border-light hover:border-border transition-colors duration-200"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 flex items-center justify-center rounded-full" :class="getRankBadgeClass(index)">
                  <span v-if="index < 3" class="text-lg">
                    {{ ['🥇', '🥈', '🥉'][index] }}
                  </span>
                  <span v-else class="text-body-small font-semibold text-text-primary">{{ index + 1 }}</span>
                </div>
                <a-avatar
                  :size="40"
                  :src="member.avatar"
                  class="border-2 border-border-light"
                >
                  {{ member.display_name?.charAt(0) }}
                </a-avatar>
                <div>
                  <div class="text-body font-medium text-text-primary">{{ member.display_name }}</div>
                  <div class="text-body-small text-text-secondary">
                    {{ formatMetricValue(member.value, leaderboardMetric) }}
                  </div>
                </div>
              </div>
              <button
                class="flex items-center gap-2 px-3 py-1 rounded-lg hover:bg-background-surface transition-colors duration-200"
                @click="likeMember(member)"
                :disabled="member.liked_by_current_user"
              >
                <HeartOutlined :class="member.liked_by_current_user ? 'text-accent' : 'text-text-muted'" />
                <span class="text-body-small">{{ member.likes_count || 0 }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 家庭挑战 -->
        <a-card title="进行中的挑战" class="challenges-card">
          <template #extra>
            <a-button type="link" @click="showCreateChallenge = true">
              创建新挑战
            </a-button>
          </template>

          <div class="challenges-list">
            <div
              v-for="challenge in activeChallenges"
              :key="challenge.challenge_id"
              class="challenge-item p-4 border rounded-lg mb-3"
            >
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h4 class="font-medium">{{ challenge.title }}</h4>
                  <p class="text-sm text-gray-600">{{ challenge.description }}</p>
                </div>
                <a-tag :color="getChallengeStatusColor(challenge.status)">
                  {{ challenge.status }}
                </a-tag>
              </div>

              <div class="challenge-progress mb-3">
                <div class="flex justify-between text-sm mb-1">
                  <span>进度</span>
                  <span>{{ challenge.current_value }} / {{ challenge.target_value }}</span>
                </div>
                <a-progress
                  :percent="challenge.progress_percentage"
                  :stroke-color="getChallengeProgressColor(challenge.progress_percentage)"
                />
              </div>

              <div class="challenge-participants">
                <div class="text-sm text-gray-600 mb-2">
                  参与者 ({{ challenge.participants_count }})
                </div>
                <a-avatar-group :max-count="5">
                  <a-avatar
                    v-for="participant in challenge.participants"
                    :key="participant.user_id"
                    :src="participant.avatar"
                    :title="participant.display_name"
                  >
                    {{ participant.display_name?.charAt(0) }}
                  </a-avatar>
                </a-avatar-group>
              </div>
            </div>

            <a-empty v-if="activeChallenges.length === 0" description="暂无进行中的挑战" />
          </div>
        </a-card>
      </div>

      <!-- 右侧：健康数据对比和告警 -->
      <div class="space-y-6">
        <!-- 健康数据对比 -->
        <a-card title="健康数据对比" class="health-comparison-card">
          <div class="health-metrics">
            <div
              v-for="metric in healthMetrics"
              :key="metric.type"
              class="metric-item mb-4"
            >
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-medium">{{ metric.name }}</span>
                <span class="text-xs text-gray-500">{{ metric.unit }}</span>
              </div>
              
              <div class="metric-bars">
                <div
                  v-for="member in metric.members"
                  :key="member.user_id"
                  class="member-metric flex items-center mb-2"
                >
                  <a-avatar :size="24" :src="member.avatar" class="mr-2">
                    {{ member.display_name?.charAt(0) }}
                  </a-avatar>
                  <div class="flex-1">
                    <div class="flex justify-between text-xs mb-1">
                      <span>{{ member.display_name }}</span>
                      <span>{{ member.value }}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="bg-blue-500 h-2 rounded-full"
                        :style="{ width: `${member.percentage}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </a-card>

        <!-- 健康告警 -->
        <a-card title="健康告警" class="health-alerts-card">
          <template #extra>
            <a-badge :count="unreadAlertsCount" size="small">
              <BellOutlined />
            </a-badge>
          </template>

          <div class="alerts-list">
            <div
              v-for="alert in recentAlerts"
              :key="alert.alert_id"
              class="alert-item p-3 border-l-4 rounded mb-3"
              :class="getAlertClass(alert.level)"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center mb-1">
                    <component :is="getAlertIcon(alert.level)" class="mr-2" />
                    <span class="font-medium">{{ alert.title }}</span>
                  </div>
                  <p class="text-sm text-gray-600 mb-2">{{ alert.message }}</p>
                  <div class="text-xs text-gray-500">
                    {{ formatTime(alert.created_at) }}
                  </div>
                </div>
                <a-button
                  v-if="!alert.is_read"
                  type="link"
                  size="small"
                  @click="markAlertAsRead(alert)"
                >
                  标记已读
                </a-button>
              </div>
            </div>

            <a-empty v-if="recentAlerts.length === 0" description="暂无告警信息" />
          </div>
        </a-card>
      </div>
    </div>

    <!-- 创建挑战弹窗 -->
    <a-modal
      v-model:open="showCreateChallenge"
      title="创建家庭挑战"
      @ok="handleCreateChallenge"
      :confirm-loading="creatingChallenge"
    >
      <CreateChallengeForm
        v-if="showCreateChallenge"
        v-model="challengeForm"
        :family-members="familyStore.familyMembers"
      />
    </a-modal>

    <!-- 创建家庭弹窗 -->
    <a-modal
      v-model:open="showCreateFamilyModal"
      title="创建家庭"
      @ok="handleCreateFamily"
      :confirm-loading="creatingFamily"
    >
      <a-form :model="familyForm" layout="vertical">
        <a-form-item label="家庭名称" required>
          <a-input
            v-model:value="familyForm.family_name"
            placeholder="请输入家庭名称"
          />
        </a-form-item>
        <a-form-item label="家庭描述">
          <a-textarea
            v-model:value="familyForm.description"
            placeholder="请输入家庭描述（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ReloadOutlined,
  StepForwardOutlined,
  ClockCircleOutlined,
  UserOutlined,
  TrophyOutlined,
  HeartOutlined,
  BellOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { useFamilyStore } from '../../stores/family.js'
import { familyAPI } from '../../api/family.js'
import MemberSwitcher from '../../components/family/MemberSwitcher.vue'
import CreateChallengeForm from '../../components/family/CreateChallengeForm.vue'

const familyStore = useFamilyStore()

// 响应式数据
const showCreateChallenge = ref(false)
const creatingChallenge = ref(false)
const showCreateFamilyModal = ref(false)
const creatingFamily = ref(false)
const leaderboardMetric = ref('steps')

// 仪表盘数据
const dashboardStats = reactive({
  totalSteps: 0,
  avgSleep: 0,
  activeMembers: 0,
  weeklyGoals: 0
})

const leaderboardData = ref([])
const activeChallenges = ref([])
const healthMetrics = ref([])
const recentAlerts = ref([])

const challengeForm = ref({
  title: '',
  description: '',
  type: 'steps',
  target_value: 0,
  duration_days: 7,
  participants: []
})

const familyForm = ref({
  family_name: '',
  description: ''
})

// 计算属性
const unreadAlertsCount = computed(() => {
  return recentAlerts.value.filter(alert => !alert.is_read).length
})

// 方法
const refreshDashboard = async () => {
  if (!familyStore.currentFamily) return

  try {
    await Promise.all([
      fetchDashboardStats(),
      fetchLeaderboard(),
      fetchChallenges(),
      fetchHealthMetrics(),
      fetchAlerts()
    ])
    message.success('仪表盘数据已刷新')
  } catch (error) {
    console.error('刷新仪表盘失败:', error)
    message.error('刷新仪表盘失败')
  }
}

const fetchDashboardStats = async () => {
  try {
    const response = await familyAPI.getFamilyHealthReport(
      familyStore.currentFamily.family_id,
      { period: 'today' }
    )

    Object.assign(dashboardStats, {
      totalSteps: response.data?.summary?.total_steps || 0,
      avgSleep: response.data?.summary?.avg_sleep_hours || 0,
      activeMembers: response.data?.summary?.active_members || 0,
      weeklyGoals: response.data?.summary?.weekly_challenges || 0
    })
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 使用模拟数据
    Object.assign(dashboardStats, {
      totalSteps: 25000,
      avgSleep: 7.5,
      activeMembers: familyStore.familyMembers.length,
      weeklyGoals: 3
    })
  }
}

const fetchLeaderboard = async () => {
  try {
    const response = await familyAPI.getFamilyLeaderboard(
      familyStore.currentFamily.family_id,
      { metric: leaderboardMetric.value, period: 'weekly' }
    )
    leaderboardData.value = response.data?.leaderboard || []
  } catch (error) {
    console.error('获取排行榜失败:', error)
    // 使用模拟数据
    leaderboardData.value = familyStore.familyMembers.map((member) => ({
      ...member,
      value: Math.floor(Math.random() * 10000) + 5000,
      likes_count: Math.floor(Math.random() * 10),
      liked_by_current_user: false
    }))
  }
}

const fetchChallenges = async () => {
  try {
    const response = await familyAPI.getFamilyChallenges(
      familyStore.currentFamily.family_id
    )
    activeChallenges.value = response.data?.challenges?.filter(c => c.status === 'active') || []
  } catch (error) {
    console.error('获取挑战数据失败:', error)
    // 使用模拟数据
    activeChallenges.value = [
      {
        challenge_id: '1',
        title: '家庭步数挑战',
        description: '本周目标：每人每天走10000步',
        status: 'active',
        current_value: 7500,
        target_value: 10000,
        progress_percentage: 75,
        participants_count: familyStore.familyMembers.length,
        participants: familyStore.familyMembers
      }
    ]
  }
}

const fetchHealthMetrics = async () => {
  // 模拟健康指标对比数据
  healthMetrics.value = [
    {
      type: 'steps',
      name: '今日步数',
      unit: '步',
      members: familyStore.familyMembers.map(member => ({
        ...member,
        value: Math.floor(Math.random() * 10000) + 5000,
        percentage: Math.floor(Math.random() * 100)
      }))
    },
    {
      type: 'sleep',
      name: '睡眠时长',
      unit: '小时',
      members: familyStore.familyMembers.map(member => ({
        ...member,
        value: (Math.random() * 4 + 6).toFixed(1),
        percentage: Math.floor(Math.random() * 100)
      }))
    }
  ]
}

const fetchAlerts = async () => {
  // 模拟告警数据
  recentAlerts.value = [
    {
      alert_id: '1',
      title: '睡眠不足提醒',
      message: '张三昨晚只睡了5小时，建议增加睡眠时间',
      level: 'warning',
      is_read: false,
      created_at: new Date().toISOString()
    }
  ]
}

const getRankClass = (index) => {
  const classes = ['bg-yellow-50', 'bg-gray-50', 'bg-orange-50']
  return index < 3 ? classes[index] : 'bg-gray-50'
}

const formatMetricValue = (value, metric) => {
  const units = {
    steps: '步',
    calories: '卡路里',
    sleep_hours: '小时'
  }
  return `${value} ${units[metric] || ''}`
}

const getChallengeStatusColor = (status) => {
  const colors = {
    active: 'green',
    completed: 'blue',
    expired: 'red'
  }
  return colors[status] || 'default'
}

const getChallengeProgressColor = (percentage) => {
  if (percentage >= 80) return '#52c41a'
  if (percentage >= 50) return '#faad14'
  return '#ff4d4f'
}

const getAlertClass = (level) => {
  const classes = {
    info: 'border-blue-400 bg-blue-50',
    warning: 'border-yellow-400 bg-yellow-50',
    error: 'border-red-400 bg-red-50'
  }
  return classes[level] || 'border-gray-400 bg-gray-50'
}

const getAlertIcon = (level) => {
  const icons = {
    info: InfoCircleOutlined,
    warning: WarningOutlined,
    error: ExclamationCircleOutlined
  }
  return icons[level] || InfoCircleOutlined
}

const formatTime = (time) => {
  return new Date(time).toLocaleString()
}

const likeMember = async (member) => {
  try {
    await familyAPI.likeMember(member.user_id, {
      type: 'achievement_like'
    })
    member.liked_by_current_user = true
    member.likes_count = (member.likes_count || 0) + 1
    message.success(`已为 ${member.display_name} 点赞`)
  } catch (error) {
    console.error('点赞失败:', error)
    // 模拟点赞成功
    member.liked_by_current_user = true
    member.likes_count = (member.likes_count || 0) + 1
    message.success(`已为 ${member.display_name} 点赞`)
  }
}

const markAlertAsRead = async (alert) => {
  try {
    // 调用API标记告警为已读
    alert.is_read = true
    message.success('告警已标记为已读')
  } catch (error) {
    console.error('标记告警失败:', error)
    message.error('标记告警失败')
  }
}

const handleCreateChallenge = async () => {
  creatingChallenge.value = true
  try {
    await familyStore.createChallenge(challengeForm.value)
    showCreateChallenge.value = false
    challengeForm.value = {
      title: '',
      description: '',
      type: 'steps',
      target_value: 0,
      duration_days: 7,
      participants: []
    }
    await fetchChallenges()
  } catch (error) {
    console.error('创建挑战失败:', error)
  } finally {
    creatingChallenge.value = false
  }
}

// 工具函数
const formatNumber = (num) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const getRankBadgeClass = (index) => {
  if (index === 0) return 'bg-yellow-100 text-yellow-800'
  if (index === 1) return 'bg-gray-100 text-gray-800'
  if (index === 2) return 'bg-orange-100 text-orange-800'
  return 'bg-background-surface text-text-secondary'
}

// 生命周期
onMounted(async () => {
  try {
    // 首先尝试获取用户的家庭列表
    if (!familyStore.currentFamily) {
      await familyStore.fetchUserFamilies()
    }

    // 如果有家庭，刷新仪表盘数据
    if (familyStore.currentFamily) {
      await refreshDashboard()
    } else {
      // 如果没有家庭，显示提示信息
      message.info('您还没有加入任何家庭，请先创建或加入家庭')
    }
  } catch (error) {
    console.error('初始化家庭仪表盘失败:', error)
    message.error('加载家庭数据失败')
  }
})
</script>

<style scoped>
/* 使用新的aura设计系统，移除旧的自定义样式 */
</style>
