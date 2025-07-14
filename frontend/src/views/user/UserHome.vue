<template>
  <div class="dashboard-container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12 bg-background">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-state">
      <div class="dashboard-header mb-8">
        <div class="w-64 h-8 bg-gray-200 rounded animate-shimmer mb-4"></div>
        <div class="w-96 h-4 bg-gray-200 rounded animate-shimmer"></div>
      </div>

      <!-- 骨架屏网格 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 auto-rows-fr gap-6">
        <SkeletonLoader v-for="n in 6" :key="n" :class="n === 1 || n === 5 ? 'lg:col-span-2' : ''" />
      </div>
    </div>

    <!-- 正常内容 -->
    <div v-else v-motion-fade-visible>
    <!-- 仪表盘顶部 -->
    <div class="dashboard-header mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-display mb-2">
            你好, {{ userStore.username || '朋友' }}
          </h1>
          <p class="text-body-large">
            今天感觉怎么样？让我们开始健康的一天吧！
          </p>
        </div>
        <div class="flex items-center space-x-4">
          <button class="aura-btn aura-btn--primary">
            <span class="text-sm font-medium">同步数据</span>
          </button>
          <div class="w-12 h-12 bg-background-surface rounded-full flex items-center justify-center border border-border">
            <UserOutlined class="w-6 h-6 text-text-primary" />
          </div>
        </div>
      </div>
    </div>

    <!-- Bento Grid 主仪表盘 - Apple风格大间距 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 auto-rows-fr gap-6">
      <!-- 健康评分卡片 (大卡片) -->
      <HealthCard 
        class="lg:col-span-2"
        title="健康评分"
        category="今日健康"
        :value="healthScore"
        unit="分"
        :icon="TrophyOutlined"
        :trend="5.2"
        :status="getHealthStatus(healthScore)"
        :show-chart="true"
        :chart-data="[65, 72, 68, 75, 80, 85, 88]"
      />

      <!-- 步数统计 -->
      <HealthCard 
        title="今日步数"
        category="运动数据"
        :value="formatNumber(dailySteps)"
        unit="步"
        :icon="UserOutlined"
        :trend="12.5"
        :status="getStepsStatus(dailySteps)"
      />

      <!-- 卡路里消耗 -->
      <HealthCard 
        title="卡路里消耗"
        category="运动数据"
        :value="caloriesBurned"
        unit="kcal"
        :icon="FireOutlined"
        :trend="-3.1"
        :status="getCaloriesStatus(caloriesBurned)"
      />

      <!-- AI聊天快速入口 (大卡片) -->
      <div class="lg:col-span-2 aura-card group cursor-pointer"
           @click="router.push('/health-chat')">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center space-x-4">
            <div class="w-12 h-12 rounded-xl bg-background-surface border border-border flex items-center justify-center">
              <MessageOutlined class="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 class="text-heading-4">AI健康助手</h3>
              <p class="text-body-small">随时为您提供健康咨询</p>
            </div>
          </div>
          <div class="w-8 h-8 flex items-center justify-center rounded-full text-text-muted/0 group-hover:text-text-muted transition-colors duration-200">
            <RightOutlined class="w-5 h-5" />
          </div>
        </div>

        <div class="bg-background-elevated p-4 rounded-xl border border-border-light">
          <p class="text-body-small text-text-primary mb-2">
            💡 <strong>今日建议</strong>
          </p>
          <p class="text-body-small">
            根据您的健康数据，建议增加15分钟的中等强度运动，并保持充足的水分摄入。
          </p>
        </div>
      </div>

      <!-- 睡眠质量 -->
      <HealthCard 
        title="睡眠质量"
        category="昨夜睡眠"
        :value="sleepQuality"
        unit="分"
        :icon="BulbOutlined"
        :trend="8.3"
        :status="getSleepStatus(sleepQuality)"
      />

      <!-- 心率数据 -->
      <HealthCard 
        title="静息心率"
        category="心血管健康"
        :value="restingHeartRate"
        unit="bpm"
        :icon="HeartOutlined"
        :trend="-2.1"
        :status="getHeartRateStatus(restingHeartRate)"
      />

      <!-- 健康计划进度 (大卡片) -->
      <div class="md:col-span-2 lg:col-span-4 lg:row-span-2 aura-card">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-heading-4 mb-2">本周健康计划进度</h3>
            <p class="text-body-small">距离完成目标还有 {{ remainingDays }} 天</p>
          </div>
          <button class="aura-btn aura-btn--secondary text-sm" @click="router.push('/health-plan')">
            查看全部
          </button>
        </div>

        <!-- 进度条网格 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="goal in healthGoals" :key="goal.id" class="bg-background-elevated p-4 rounded-xl border border-border-light hover:border-border transition-colors duration-200">
            <div class="flex items-center justify-between mb-2">
              <span class="text-body-small font-medium text-text-primary">{{ goal.name }}</span>
              <span class="text-caption">{{ goal.progress }}%</span>
            </div>
            <div class="w-full bg-background-surface rounded-full h-2">
              <div
                class="bg-primary h-2 rounded-full transition-all duration-300"
                :style="{ width: goal.progress + '%' }"
              ></div>
            </div>
            <p class="text-caption mt-1">{{ goal.current }}/{{ goal.target }} {{ goal.unit }}</p>
          </div>
        </div>
      </div>

      <!-- 快速操作区域 -->
      <div class="lg:col-span-2 aura-card">
        <h3 class="text-heading-4 mb-4">快速操作</h3>
        <div class="grid grid-cols-2 gap-4">
          <button
            v-for="action in quickActions"
            :key="action.name"
            class="flex flex-col items-center justify-center p-4 bg-background-elevated rounded-xl border border-border-light hover:border-border transition-all duration-200 group focus-ring"
            @click="handleQuickAction(action)"
          >
            <component :is="action.icon" class="w-6 h-6 text-primary mb-2 transition-transform duration-200 group-hover:scale-105" />
            <span class="text-body-small font-medium text-center">{{ action.name }}</span>
          </button>
        </div>
      </div>

      <!-- 最近健康咨询 -->
      <div class="lg:col-span-2 aura-card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-heading-4">最近咨询</h3>
          <button class="aura-btn aura-btn--secondary text-sm" @click="router.push('/health-chat')">
            查看全部
          </button>
        </div>
        <div class="space-y-3">
          <div v-for="chat in recentChats" :key="chat.id" class="flex items-start space-x-3 p-3 bg-background-elevated rounded-lg border border-border-light hover:border-border cursor-pointer transition-colors duration-200">
            <div class="w-8 h-8 bg-background-surface rounded-full flex items-center justify-center flex-shrink-0 border border-border-light">
              <MessageOutlined class="w-4 h-4 text-primary" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-body-small font-medium text-truncate">{{ chat.title }}</p>
              <p class="text-caption">{{ chat.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import HealthCard from '@/components/health/HealthCard.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'

import {
  UserOutlined,
  TrophyOutlined,
  FireOutlined,
  MessageOutlined,
  BulbOutlined,
  HeartOutlined,
  RightOutlined,
  CalendarOutlined,
  FileTextOutlined,
  SettingOutlined,
  BellOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 健康数据
const healthScore = ref(88)
const dailySteps = ref(8547)
const caloriesBurned = ref(342)
const sleepQuality = ref(92)
const restingHeartRate = ref(68)
const remainingDays = ref(4)

// 健康目标进度
const healthGoals = ref([
  { id: 1, name: '每日步数', current: 8547, target: 10000, unit: '步', progress: 85 },
  { id: 2, name: '睡眠时长', current: 7.5, target: 8, unit: '小时', progress: 94 },
  { id: 3, name: '饮水量', current: 1.8, target: 2.5, unit: '升', progress: 72 },
  { id: 4, name: '运动时长', current: 25, target: 30, unit: '分钟', progress: 83 }
])

// 快速操作
const quickActions = ref([
  { name: '记录体重', icon: CalendarOutlined, action: 'record-weight' },
  { name: '查看报告', icon: FileTextOutlined, action: 'view-reports' },
  { name: '设置提醒', icon: BellOutlined, action: 'set-reminder' },
  { name: '偏好设置', icon: SettingOutlined, action: 'preferences' }
])

// 最近聊天记录
const recentChats = ref([
  { id: 1, title: '关于睡眠质量改善的建议', time: '2小时前' },
  { id: 2, title: '营养搭配咨询', time: '昨天' },
  { id: 3, title: '运动计划制定', time: '3天前' }
])

// 工具函数

const formatNumber = (num) => {
  return num.toLocaleString()
}

const getHealthStatus = (score) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '正常'
  if (score >= 60) return '注意'
  return '需要改善'
}

const getStepsStatus = (steps) => {
  if (steps >= 10000) return '目标达成'
  if (steps >= 8000) return '接近目标'
  return '需要努力'
}

const getCaloriesStatus = (calories) => {
  if (calories >= 400) return '活跃'
  if (calories >= 200) return '正常'
  return '偏低'
}

const getSleepStatus = (quality) => {
  if (quality >= 90) return '优质睡眠'
  if (quality >= 80) return '良好睡眠'
  return '需要改善'
}

const getHeartRateStatus = (hr) => {
  if (hr >= 60 && hr <= 80) return '正常范围'
  if (hr < 60) return '偏低'
  return '偏高'
}

const handleQuickAction = (action) => {
  switch (action.action) {
    case 'record-weight':
      // 弹出体重记录对话框
      console.log('记录体重')
      break
    case 'view-reports':
      router.push('/health-report')
      break
    case 'set-reminder':
      // 打开提醒设置
      console.log('设置提醒')
      break
    case 'preferences':
      router.push('/profile')
      break
  }
}

// 加载状态
const isLoading = ref(true)

// 模拟加载数据
const loadDashboardData = async () => {
  isLoading.value = true
  
  // 模拟 API 调用延迟
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  // 加载完成
  isLoading.value = false
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
/* 自定义动画 */
.dashboard-container {
  animation: fadeIn 0.5s ease-out forwards;
}

/* 使用新的aura-card设计系统，无需自定义样式 */

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 进度条动画 */
.bg-primary-500 {
  animation: progressGrow 1s ease-out forwards;
}

@keyframes progressGrow {
  from {
    width: 0%;
  }
}

/* 卡片悬浮效果 */
.group:hover {
  transform: translateY(-4px);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>