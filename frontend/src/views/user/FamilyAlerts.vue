<template>
  <div class="family-alerts-page">
    <div class="page-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">健康告警</h1>
          <p class="text-gray-600 mt-1">查看和管理家庭健康告警</p>
        </div>
        <a-button @click="markAllAsRead">
          全部标记为已读
        </a-button>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="alerts-list">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="alert-item"
        :class="getAlertClass(alert.level)"
      >
        <div class="alert-content">
          <div class="alert-header">
            <component :is="getAlertIcon(alert.level)" class="alert-icon" />
            <h4>{{ alert.title }}</h4>
            <a-tag :color="getLevelColor(alert.level)">
              {{ alert.level }}
            </a-tag>
          </div>
          <p class="alert-message">{{ alert.message }}</p>
          <div class="alert-meta">
            <span>{{ alert.member_name }}</span>
            <span>{{ formatTime(alert.created_at) }}</span>
          </div>
        </div>
        <div class="alert-actions">
          <a-button
            v-if="!alert.is_read"
            size="small"
            @click="markAsRead(alert)"
          >
            标记已读
          </a-button>
        </div>
      </div>
    </div>

    <a-empty v-if="alerts.length === 0" description="暂无告警信息" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'

const alerts = ref([
  {
    id: 1,
    title: '睡眠不足提醒',
    message: '张三昨晚只睡了5小时，建议增加睡眠时间',
    level: 'warning',
    member_name: '张三',
    is_read: false,
    created_at: new Date().toISOString()
  }
])

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

const getLevelColor = (level) => {
  const colors = {
    info: 'blue',
    warning: 'orange',
    error: 'red'
  }
  return colors[level] || 'default'
}

const formatTime = (time) => {
  return new Date(time).toLocaleString()
}

const markAsRead = (alert) => {
  alert.is_read = true
}

const markAllAsRead = () => {
  alerts.value.forEach(alert => {
    alert.is_read = true
  })
}
</script>

<style scoped>
.family-alerts-page {
  @apply p-6 min-h-screen bg-gray-50;
}

.alerts-list {
  @apply space-y-4;
}

.alert-item {
  @apply bg-white p-4 rounded-lg border-l-4 flex justify-between items-start;
}

.alert-content {
  @apply flex-1;
}

.alert-header {
  @apply flex items-center gap-2 mb-2;
}

.alert-icon {
  @apply text-lg;
}

.alert-message {
  @apply text-gray-700 mb-2;
}

.alert-meta {
  @apply flex justify-between text-sm text-gray-500;
}

.alert-actions {
  @apply ml-4;
}
</style>
