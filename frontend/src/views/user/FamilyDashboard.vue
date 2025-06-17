<template>
  <div class="family-dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            {{ familyStore.currentFamily?.family_name }} 家庭仪表盘
          </h1>
          <p class="text-gray-600 mt-1">
            共 {{ familyStore.familyMembers.length }} 名成员
          </p>
        </div>
        <div class="flex gap-3">
          <a-button type="primary" @click="showCreateChallenge = true">
            <PlusOutlined />
            创建挑战
          </a-button>
          <a-button @click="refreshDashboard">
            <ReloadOutlined />
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 成员切换器 -->
    <div class="mb-6">
      <MemberSwitcher />
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <a-card class="stat-card">
        <a-statistic
          title="今日总步数"
          :value="dashboardStats.totalSteps"
          :value-style="{ color: '#3f8600' }"
          suffix="步"
        >
          <template #prefix>
            <WalkOutlined />
          </template>
        </a-statistic>
      </a-card>

      <a-card class="stat-card">
        <a-statistic
          title="平均睡眠时长"
          :value="dashboardStats.avgSleep"
          :value-style="{ color: '#1890ff' }"
          suffix="小时"
          :precision="1"
        >
          <template #prefix>
            <MoonOutlined />
          </template>
        </a-statistic>
      </a-card>

      <a-card class="stat-card">
        <a-statistic
          title="活跃成员"
          :value="dashboardStats.activeMembers"
          :value-style="{ color: '#cf1322' }"
          suffix="人"
        >
          <template #prefix>
            <UserOutlined />
          </template>
        </a-statistic>
      </a-card>

      <a-card class="stat-card">
        <a-statistic
          title="本周挑战"
          :value="dashboardStats.weeklyGoals"
          :value-style="{ color: '#722ed1' }"
          suffix="个"
        >
          <template #prefix>
            <TrophyOutlined />
          </template>
        </a-statistic>
      </a-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：排行榜和挑战 -->
      <div class="lg:col-span-2 space-y-6">
        <!-- 家庭排行榜 -->
        <a-card title="本周排行榜" class="leaderboard-card">
          <template #extra>
            <a-select
              v-model:value="leaderboardMetric"
              style="width: 120px"
              @change="fetchLeaderboard"
            >
              <a-select-option value="steps">步数</a-select-option>
              <a-select-option value="calories">卡路里</a-select-option>
              <a-select-option value="sleep_hours">睡眠</a-select-option>
            </a-select>
          </template>

          <div class="leaderboard-list">
            <div
              v-for="(member, index) in leaderboardData"
              :key="member.user_id"
              class="leaderboard-item flex items-center justify-between p-3 rounded-lg mb-2"
              :class="getRankClass(index)"
            >
              <div class="flex items-center">
                <div class="rank-badge">
                  <span v-if="index < 3" class="rank-icon">
                    {{ ['🥇', '🥈', '🥉'][index] }}
                  </span>
                  <span v-else class="rank-number">{{ index + 1 }}</span>
                </div>
                <a-avatar
                  :size="40"
                  :src="member.avatar"
                  class="mx-3"
                >
                  {{ member.display_name?.charAt(0) }}
                </a-avatar>
                <div>
                  <div class="font-medium">{{ member.display_name }}</div>
                  <div class="text-sm text-gray-500">
                    {{ formatMetricValue(member.value, leaderboardMetric) }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <a-button
                  type="text"
                  size="small"
                  @click="likeMember(member)"
                  :disabled="member.liked_by_current_user"
                >
                  <HeartOutlined :class="{ 'text-red-500': member.liked_by_current_user }" />
                  {{ member.likes_count || 0 }}
                </a-button>
              </div>
            </div>
          </div>
        </a-card>

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ReloadOutlined,
  WalkOutlined,
  MoonOutlined,
  UserOutlined,
  TrophyOutlined,
  HeartOutlined,
  BellOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import { familyDashboardAPI } from '@/api/family'
import MemberSwitcher from '@/components/family/MemberSwitcher.vue'
import CreateChallengeForm from '@/components/family/CreateChallengeForm.vue'

const familyStore = useFamilyStore()

// 响应式数据
const showCreateChallenge = ref(false)
const creatingChallenge = ref(false)
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
    const response = await familyDashboardAPI.getFamilyHealthReport(
      familyStore.currentFamily.family_id,
      { period: 'today' }
    )
    
    Object.assign(dashboardStats, {
      totalSteps: response.summary?.total_steps || 0,
      avgSleep: response.summary?.avg_sleep_hours || 0,
      activeMembers: response.summary?.active_members || 0,
      weeklyGoals: response.summary?.weekly_challenges || 0
    })
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchLeaderboard = async () => {
  try {
    const response = await familyDashboardAPI.getFamilyLeaderboard(
      familyStore.currentFamily.family_id,
      { metric: leaderboardMetric.value, period: 'weekly' }
    )
    leaderboardData.value = response.leaderboard || []
  } catch (error) {
    console.error('获取排行榜失败:', error)
  }
}

const fetchChallenges = async () => {
  try {
    const response = await familyDashboardAPI.getFamilyChallenges(
      familyStore.currentFamily.family_id
    )
    activeChallenges.value = response.challenges?.filter(c => c.status === 'active') || []
  } catch (error) {
    console.error('获取挑战数据失败:', error)
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
    await familyDashboardAPI.likeMember(member.user_id, {
      type: 'achievement_like'
    })
    member.liked_by_current_user = true
    member.likes_count = (member.likes_count || 0) + 1
    message.success(`已为 ${member.display_name} 点赞`)
  } catch (error) {
    console.error('点赞失败:', error)
    message.error('点赞失败')
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

// 生命周期
onMounted(async () => {
  if (familyStore.currentFamily) {
    await refreshDashboard()
  }
})
</script>

<style scoped>
.family-dashboard {
  @apply p-6 min-h-screen bg-gray-50;
}

.stat-card {
  @apply transition-all duration-300 hover:shadow-md;
}

.leaderboard-item {
  @apply transition-all duration-300 hover:shadow-sm;
}

.rank-badge {
  @apply w-8 h-8 flex items-center justify-center;
}

.rank-icon {
  @apply text-lg;
}

.rank-number {
  @apply text-sm font-bold text-gray-600;
}

.challenge-item {
  @apply transition-all duration-300 hover:shadow-sm;
}

.metric-item {
  @apply border-b border-gray-100 pb-3 last:border-b-0;
}

.member-metric {
  @apply transition-all duration-300;
}

.alert-item {
  @apply transition-all duration-300 hover:shadow-sm;
}

@media (max-width: 768px) {
  .family-dashboard {
    @apply p-4;
  }
  
  .grid {
    @apply grid-cols-1;
  }
  
  .stats-cards {
    @apply grid-cols-2;
  }
}
</style>
