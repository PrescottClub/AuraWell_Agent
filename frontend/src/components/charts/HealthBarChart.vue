<template>
  <div class="health-bar-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <a-select
          v-model:value="selectedMetric"
          @change="handleMetricChange"
          style="width: 140px; margin-right: 12px;"
        >
          <a-select-option value="duration">运动时长</a-select-option>
          <a-select-option value="calories">消耗热量</a-select-option>
          <a-select-option value="frequency">运动频次</a-select-option>
        </a-select>
        
        <a-button 
          type="text" 
          size="small"
          @click="handleAnalyzeClick"
          :loading="analyzing"
        >
          <BarChartOutlined />
          深度分析
        </a-button>
      </div>
    </div>
    
    <div class="chart-container" :style="{ height: chartHeight + 'px' }">
      <v-chart
        ref="chartRef"
        :option="chartOption"
        :loading="loading"
        @click="onChartClick"
        autoresize
      />
    </div>
    
    <div v-if="showStats" class="chart-stats">
      <div class="stat-item">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总计</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.average }}</div>
        <div class="stat-label">平均</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.best }}</div>
        <div class="stat-label">最佳</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.improvement }}</div>
        <div class="stat-label">改善</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { BarChartOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { healthReportAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '运动数据'
  },
  chartHeight: {
    type: Number,
    default: 300
  },
  showStats: {
    type: Boolean,
    default: true
  },
  colors: {
    type: Array,
    default: () => ['#1890ff', '#52c41a', '#faad14', '#f5222d']
  }
})

// Emits
const emit = defineEmits(['chart-click', 'analyze'])

// 响应式数据
const chartRef = ref(null)
const loading = ref(false)
const analyzing = ref(false)
const selectedMetric = ref('duration')
const chartData = ref([])

// 计算属性
const chartOption = computed(() => {
  if (!chartData.value.length) return {}
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const point = params[0]
        return `${point.name}<br/>${getMetricLabel()}: ${point.value}${getMetricUnit()}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.value.map(item => formatDate(item.date)),
      axisLabel: {
        fontSize: 12,
        color: '#666',
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 12,
        color: '#666',
        formatter: (value) => value + getMetricUnit()
      }
    },
    series: [
      {
        name: getMetricLabel(),
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          color: (params) => {
            const colors = props.colors
            return colors[params.dataIndex % colors.length]
          },
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          }
        },
        data: chartData.value.map(item => ({
          value: getMetricValue(item),
          itemStyle: {
            color: getBarColor(item)
          }
        }))
      }
    ]
  }
})

const stats = computed(() => {
  if (!chartData.value.length) {
    return {
      total: '-',
      average: '-',
      best: '-',
      improvement: '-'
    }
  }
  
  const values = chartData.value.map(item => getMetricValue(item))
  const total = values.reduce((sum, val) => sum + val, 0)
  const average = (total / values.length).toFixed(1)
  const best = Math.max(...values)
  
  // 计算改善程度（最近一周vs前一周）
  const recentWeek = values.slice(-7)
  const previousWeek = values.slice(-14, -7)
  const recentAvg = recentWeek.reduce((sum, val) => sum + val, 0) / recentWeek.length
  const previousAvg = previousWeek.reduce((sum, val) => sum + val, 0) / previousWeek.length
  const improvement = previousAvg ? (((recentAvg - previousAvg) / previousAvg) * 100).toFixed(1) : 0
  
  return {
    total: total.toFixed(0) + getMetricUnit(),
    average: average + getMetricUnit(),
    best: best.toFixed(0) + getMetricUnit(),
    improvement: `${improvement > 0 ? '+' : ''}${improvement}%`
  }
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    const endDate = new Date().toISOString()
    const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
    
    const response = await healthReportAPI.getHealthMetricsTimeSeries({
      metric_type: 'exercise_' + selectedMetric.value,
      start_date: startDate,
      end_date: endDate,
      interval: 'daily'
    })
    
    chartData.value = response.data.data || []
  } catch (error) {
    console.error('获取运动数据失败:', error)
    message.error('获取运动数据失败')
  } finally {
    loading.value = false
  }
}

const getMetricLabel = () => {
  switch (selectedMetric.value) {
    case 'duration':
      return '运动时长'
    case 'calories':
      return '消耗热量'
    case 'frequency':
      return '运动频次'
    default:
      return '运动数据'
  }
}

const getMetricUnit = () => {
  switch (selectedMetric.value) {
    case 'duration':
      return '分钟'
    case 'calories':
      return '卡'
    case 'frequency':
      return '次'
    default:
      return ''
  }
}

const getMetricValue = (item) => {
  switch (selectedMetric.value) {
    case 'duration':
      return item.value || 0
    case 'calories':
      return (item.value || 0) * 8 // 假设每分钟消耗8卡路里
    case 'frequency':
      return item.value > 0 ? 1 : 0 // 有运动记录就算1次
    default:
      return item.value || 0
  }
}

const getBarColor = (item) => {
  const value = getMetricValue(item)
  
  if (selectedMetric.value === 'duration') {
    if (value >= 60) return '#52c41a' // 绿色：优秀
    if (value >= 30) return '#1890ff' // 蓝色：良好
    if (value > 0) return '#faad14'   // 橙色：一般
    return '#f5222d'                  // 红色：需要改善
  }
  
  return props.colors[0]
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleMetricChange = (metric) => {
  selectedMetric.value = metric
  fetchData()
}

const onChartClick = (params) => {
  if (params.componentType === 'series') {
    const dataPoint = {
      date: chartData.value[params.dataIndex]?.date,
      value: params.value,
      metric: selectedMetric.value,
      title: getMetricLabel()
    }
    emit('chart-click', dataPoint)
  }
}

const handleAnalyzeClick = async () => {
  analyzing.value = true
  try {
    const analysisData = {
      metric: selectedMetric.value,
      data: chartData.value,
      stats: stats.value,
      period: '30天'
    }
    
    emit('analyze', analysisData)
    message.success('正在为您生成深度分析报告...')
  } catch (error) {
    console.error('启动分析失败:', error)
    message.error('启动分析失败')
  } finally {
    analyzing.value = false
  }
}

// 监听器
watch(selectedMetric, () => {
  fetchData()
}, { immediate: false })

// 生命周期
onMounted(() => {
  fetchData()
})

// 暴露方法给父组件
defineExpose({
  refreshData: fetchData
})
</script>

<style scoped>
.health-bar-chart {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.chart-container {
  width: 100%;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
}
</style>
