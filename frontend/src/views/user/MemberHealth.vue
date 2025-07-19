<template>
  <div class="member-health-page">
    <!-- 页面头部 -->
    <div class="page-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            {{ memberInfo?.display_name }} 的健康数据
          </h1>
          <p class="text-gray-600 mt-1">
            查看和管理成员的健康信息
          </p>
        </div>
        <div class="flex gap-3">
          <a-button @click="$router.go(-1)">
            <ArrowLeftOutlined />
            返回
          </a-button>
          <a-button @click="refreshData">
            <ReloadOutlined />
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 成员基本信息 -->
    <div class="member-info-section mb-6">
      <a-card class="member-info-card">
        <div class="flex items-center gap-6">
          <a-avatar :size="80" :src="memberInfo?.avatar">
            {{ memberInfo?.display_name?.charAt(0) }}
          </a-avatar>
          <div class="flex-1">
            <h2 class="text-xl font-semibold mb-2">{{ memberInfo?.display_name }}</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-500">角色:</span>
                <a-tag :color="getRoleColor(memberInfo?.role)" class="ml-2">
                  {{ getRoleText(memberInfo?.role) }}
                </a-tag>
              </div>
              <div>
                <span class="text-gray-500">年龄:</span>
                <span class="ml-2">{{ memberInfo?.age || '--' }} 岁</span>
              </div>
              <div>
                <span class="text-gray-500">性别:</span>
                <span class="ml-2">{{ getGenderText(memberInfo?.gender) }}</span>
              </div>
              <div>
                <span class="text-gray-500">BMI:</span>
                <span class="ml-2">{{ memberInfo?.bmi || '--' }}</span>
              </div>
            </div>
          </div>
        </div>
      </a-card>
    </div>

    <!-- 健康数据概览 -->
    <div class="health-overview-section mb-6">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="今日步数"
              :value="healthData.steps"
              :value-style="{ color: '#3f8600' }"
              suffix="步"
            >
              <template #prefix>
                <StepForwardOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="睡眠时长"
              :value="healthData.sleep_hours"
              :value-style="{ color: '#1890ff' }"
              suffix="小时"
              :precision="1"
            >
              <template #prefix>
                <ClockCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="消耗卡路里"
              :value="healthData.calories"
              :value-style="{ color: '#cf1322' }"
              suffix="卡"
            >
              <template #prefix>
                <FireOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card">
            <a-statistic
              title="心率"
              :value="healthData.heart_rate"
              :value-style="{ color: '#722ed1' }"
              suffix="bpm"
            >
              <template #prefix>
                <HeartOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 详细健康数据 -->
    <div class="health-details-section">
      <a-row :gutter="24">
        <!-- 左侧：健康趋势图表 -->
        <a-col :span="16">
          <a-card title="健康趋势" class="trends-card">
            <template #extra>
              <a-select
                v-model:value="selectedMetric"
                style="width: 120px"
                @change="updateChart"
              >
                <a-select-option value="steps">步数</a-select-option>
                <a-select-option value="sleep">睡眠</a-select-option>
                <a-select-option value="weight">体重</a-select-option>
                <a-select-option value="heart_rate">心率</a-select-option>
              </a-select>
            </template>
            
            <div class="chart-container">
              <v-chart
                :option="chartOption"
                :style="{ height: '300px' }"
                autoresize
              />
            </div>
          </a-card>
        </a-col>

        <!-- 右侧：健康指标详情 -->
        <a-col :span="8">
          <a-card title="健康指标" class="metrics-card">
            <div class="metrics-list">
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">体重</span>
                  <span class="metric-value">{{ healthData.weight || '--' }} kg</span>
                </div>
                <div class="metric-trend">
                  <span class="trend-text">较上周 +0.5kg</span>
                  <ArrowUpOutlined class="trend-icon text-red-500" />
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">血压</span>
                  <span class="metric-value">{{ healthData.blood_pressure || '--' }}</span>
                </div>
                <div class="metric-trend">
                  <span class="trend-text">正常范围</span>
                  <CheckCircleOutlined class="trend-icon text-green-500" />
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">血糖</span>
                  <span class="metric-value">{{ healthData.blood_sugar || '--' }} mg/dL</span>
                </div>
                <div class="metric-trend">
                  <span class="trend-text">正常范围</span>
                  <CheckCircleOutlined class="trend-icon text-green-500" />
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">体脂率</span>
                  <span class="metric-value">{{ healthData.body_fat || '--' }}%</span>
                </div>
                <div class="metric-trend">
                  <span class="trend-text">较上月 -1.2%</span>
                  <ArrowDownOutlined class="trend-icon text-green-500" />
                </div>
              </div>
            </div>
          </a-card>

          <!-- 健康目标 -->
          <a-card title="健康目标" class="goals-card mt-4">
            <div class="goals-list">
              <div
                v-for="goal in memberGoals"
                :key="goal.id"
                class="goal-item"
              >
                <div class="goal-header">
                  <span class="goal-name">{{ goal.title }}</span>
                  <span class="goal-progress">{{ goal.progress }}%</span>
                </div>
                <a-progress
                  :percent="goal.progress"
                  :stroke-color="getProgressColor(goal.progress)"
                  size="small"
                />
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 健康记录表格 -->
    <div class="health-records-section mt-6">
      <a-card title="健康记录" class="records-card">
        <template #extra>
          <a-range-picker
            v-model:value="dateRange"
            @change="handleDateRangeChange"
          />
        </template>

        <a-table
          :columns="recordColumns"
          :data-source="healthRecords"
          :loading="loading"
          :pagination="pagination"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'date'">
              {{ formatDate(record.date) }}
            </template>
            <template v-else-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  ReloadOutlined,
  StepForwardOutlined,
  ClockCircleOutlined,
  FireOutlined,
  HeartOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  CheckCircleOutlined
} from '@ant-design/icons-vue'
import { memberAPI } from '@/api/family'
import dayjs from 'dayjs'

const route = useRoute()
const memberId = route.params.memberId

// 响应式数据
const loading = ref(false)
const memberInfo = ref(null)
const selectedMetric = ref('steps')
const dateRange = ref([dayjs().subtract(7, 'day'), dayjs()])

// 健康数据
const healthData = reactive({
  steps: 8500,
  sleep_hours: 7.5,
  calories: 2200,
  heart_rate: 72,
  weight: 65.5,
  blood_pressure: '120/80',
  blood_sugar: 95,
  body_fat: 18.5
})

// 健康目标
const memberGoals = ref([
  { id: 1, title: '每日步数', progress: 85 },
  { id: 2, title: '睡眠质量', progress: 92 },
  { id: 3, title: '体重管理', progress: 67 }
])

// 健康记录
const healthRecords = ref([
  {
    id: 1,
    date: '2024-06-17',
    steps: 8500,
    sleep_hours: 7.5,
    weight: 65.5,
    status: 'good'
  },
  {
    id: 2,
    date: '2024-06-16',
    steps: 9200,
    sleep_hours: 8.0,
    weight: 65.3,
    status: 'excellent'
  }
])

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 表格列配置
const recordColumns = [
  { title: '日期', dataIndex: 'date', key: 'date' },
  { title: '步数', dataIndex: 'steps', key: 'steps' },
  { title: '睡眠(小时)', dataIndex: 'sleep_hours', key: 'sleep_hours' },
  { title: '体重(kg)', dataIndex: 'weight', key: 'weight' },
  { title: '状态', dataIndex: 'status', key: 'status' }
]

// 图表配置
const chartOption = ref({
  title: {
    text: '步数趋势'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    data: [8200, 9500, 7800, 10200, 8900, 9800, 8500],
    type: 'line',
    smooth: true
  }]
})

// 方法
const getRoleColor = (role) => {
  const colors = {
    'Owner': 'gold',
    'Manager': 'blue',
    'Member': 'default'
  }
  return colors[role] || 'default'
}

const getRoleText = (role) => {
  const texts = {
    'Owner': '拥有者',
    'Manager': '管理员',
    'Member': '成员'
  }
  return texts[role] || '成员'
}

const getGenderText = (gender) => {
  const texts = {
    'male': '男',
    'female': '女',
    'other': '其他'
  }
  return texts[gender] || '--'
}

const getProgressColor = (progress) => {
  if (progress >= 80) return '#52c41a'
  if (progress >= 60) return '#faad14'
  return '#ff4d4f'
}

const getStatusColor = (status) => {
  const colors = {
    'excellent': 'green',
    'good': 'blue',
    'normal': 'default',
    'poor': 'red'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    'excellent': '优秀',
    'good': '良好',
    'normal': '正常',
    'poor': '需改善'
  }
  return texts[status] || '未知'
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const refreshData = async () => {
  loading.value = true
  try {
    // 获取成员详细信息
    const memberResponse = await memberAPI.getMemberDetails(memberId)
    memberInfo.value = memberResponse

    // 获取成员健康数据
    const healthResponse = await memberAPI.getMemberHealthData(memberId, {
      start_date: dateRange.value[0].format('YYYY-MM-DD'),
      end_date: dateRange.value[1].format('YYYY-MM-DD')
    })
    
    // 更新健康数据
    Object.assign(healthData, healthResponse.summary || {})
    healthRecords.value = healthResponse.records || []
    pagination.total = healthResponse.total || 0

    message.success('数据刷新成功')
  } catch (error) {
    console.error('获取成员健康数据失败:', error)
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const updateChart = (metric) => {
  // 根据选择的指标更新图表
  const chartData = {
    steps: {
      title: '步数趋势',
      data: [8200, 9500, 7800, 10200, 8900, 9800, 8500]
    },
    sleep: {
      title: '睡眠趋势',
      data: [7.5, 8.0, 6.5, 7.8, 8.2, 7.0, 7.5]
    },
    weight: {
      title: '体重趋势',
      data: [65.8, 65.6, 65.5, 65.4, 65.3, 65.5, 65.5]
    },
    heart_rate: {
      title: '心率趋势',
      data: [72, 75, 68, 74, 71, 73, 72]
    }
  }

  const selected = chartData[metric]
  chartOption.value = {
    ...chartOption.value,
    title: { text: selected.title },
    series: [{ ...chartOption.value.series[0], data: selected.data }]
  }
}

const handleDateRangeChange = (dates) => {
  if (dates && dates.length === 2) {
    dateRange.value = dates
    refreshData()
  }
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  refreshData()
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.member-health-page {
  @apply p-6 min-h-screen bg-gray-50;
}

.stat-card {
  @apply transition-all duration-300 hover:shadow-md;
}

.chart-container {
  @apply w-full;
}

.metrics-list {
  @apply space-y-4;
}

.metric-item {
  @apply p-3 bg-gray-50 rounded-lg;
}

.metric-header {
  @apply flex justify-between items-center mb-2;
}

.metric-name {
  @apply text-sm font-medium text-gray-700;
}

.metric-value {
  @apply text-lg font-semibold text-gray-900;
}

.metric-trend {
  @apply flex items-center justify-between text-xs;
}

.trend-text {
  @apply text-gray-600;
}

.trend-icon {
  @apply text-sm;
}

.goals-list {
  @apply space-y-3;
}

.goal-item {
  @apply space-y-2;
}

.goal-header {
  @apply flex justify-between items-center;
}

.goal-name {
  @apply text-sm font-medium text-gray-700;
}

.goal-progress {
  @apply text-sm font-semibold text-gray-900;
}

@media (max-width: 768px) {
  .member-health-page {
    @apply p-4;
  }
  
  .health-overview-section .ant-col {
    @apply mb-4;
  }
  
  .health-details-section .ant-col {
    @apply mb-6;
  }
}
</style>
