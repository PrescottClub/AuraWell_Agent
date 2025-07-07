<template>
  <div class="health-line-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <a-select
          v-model:value="selectedPeriod"
          @change="handlePeriodChange"
          style="width: 120px; margin-right: 12px;"
        >
          <a-select-option value="7d">近7天</a-select-option>
          <a-select-option value="30d">近30天</a-select-option>
          <a-select-option value="90d">近3个月</a-select-option>
        </a-select>
        
        <a-button 
          type="text" 
          size="small"
          @click="handleChartClick"
          :loading="chatLoading"
        >
          <MessageOutlined />
          分析趋势
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
    
    <div v-if="showSummary" class="chart-summary">
      <div class="summary-item">
        <span class="label">平均值:</span>
        <span class="value">{{ formatValue(summary.avg) }}</span>
      </div>
      <div class="summary-item">
        <span class="label">趋势:</span>
        <span class="value" :class="trendClass">{{ trendText }}</span>
      </div>
      <div class="summary-item">
        <span class="label">变化:</span>
        <span class="value" :class="changeClass">{{ changeText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { MessageOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useTheme } from '../../composables/useTheme.js'
import { getChartTheme } from '../../utils/chartThemes.js'
import { healthReportAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '健康趋势'
  },
  metricType: {
    type: String,
    required: true
  },
  unit: {
    type: String,
    default: ''
  },
  chartHeight: {
    type: Number,
    default: 300
  },
  showSummary: {
    type: Boolean,
    default: true
  },
  color: {
    type: String,
    default: '#1890ff'
  }
})

// Emits
const emit = defineEmits(['chart-click', 'period-change'])

// 主题相关
const { isDark } = useTheme()

// 响应式数据
const chartRef = ref(null)
const loading = ref(false)
const chatLoading = ref(false)
const selectedPeriod = ref('30d')
const chartData = ref([])
const summary = ref({})

// 计算属性
const chartOption = computed(() => {
  if (!chartData.value.length) return {}

  // 获取当前主题配置
  const currentTheme = getChartTheme(isDark.value)
  const primaryColor = props.color || currentTheme.color[0] || '#14b8a6'

  return {
    // 应用主题配置
    ...currentTheme,
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const point = params[0]
        return `${point.name}<br/>${props.title}: ${formatValue(point.value)}${props.unit}`
      },
      ...currentTheme.tooltip
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
      ...currentTheme.grid
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.value.map(item => formatDate(item.date)),
      axisLabel: {
        fontSize: 12,
        color: currentTheme.categoryAxis?.axisLabel?.color || (isDark.value ? '#94a3b8' : '#64748b')
      },
      ...currentTheme.categoryAxis
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 12,
        color: currentTheme.valueAxis?.axisLabel?.color || (isDark.value ? '#94a3b8' : '#64748b'),
        formatter: (value) => formatValue(value) + props.unit
      },
      ...currentTheme.valueAxis
    },
    series: [
      {
        name: props.title,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: primaryColor,
          width: 3
        },
        itemStyle: {
          color: primaryColor
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: primaryColor + '40' },
              { offset: 1, color: primaryColor + '10' }
            ]
          }
        },
        data: chartData.value.map(item => item.value),
        markLine: {
          silent: true,
          lineStyle: {
            color: '#ff4d4f',
            type: 'dashed'
          },
          data: getMarkLines()
        }
      }
    ]
  }
})

const trendClass = computed(() => {
  if (!summary.value.trend) return ''
  return summary.value.trend === 'increasing' ? 'trend-up' : 'trend-down'
})

const trendText = computed(() => {
  if (!summary.value.trend) return '-'
  return summary.value.trend === 'increasing' ? '上升' : '下降'
})

const changeClass = computed(() => {
  if (!chartData.value.length) return ''
  const first = chartData.value[0]?.value || 0
  const last = chartData.value[chartData.value.length - 1]?.value || 0
  return last > first ? 'change-positive' : 'change-negative'
})

const changeText = computed(() => {
  if (!chartData.value.length) return '-'
  const first = chartData.value[0]?.value || 0
  const last = chartData.value[chartData.value.length - 1]?.value || 0
  const change = last - first
  const percentage = first !== 0 ? ((change / first) * 100).toFixed(1) : '0'
  return `${change > 0 ? '+' : ''}${formatValue(change)}${props.unit} (${percentage}%)`
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    const endDate = new Date().toISOString()
    const startDate = getStartDate(selectedPeriod.value)
    
    const response = await healthReportAPI.getHealthMetricsTimeSeries({
      metric_type: props.metricType,
      start_date: startDate,
      end_date: endDate,
      interval: 'daily'
    })
    
    chartData.value = response.data.data || []
    summary.value = response.data.summary || {}
  } catch (error) {
    console.error('获取图表数据失败:', error)
    message.error('获取图表数据失败')
  } finally {
    loading.value = false
  }
}

const getStartDate = (period) => {
  const now = new Date()
  switch (period) {
    case '7d':
      return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString()
    case '30d':
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
    case '90d':
      return new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString()
    default:
      return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const formatValue = (value) => {
  if (typeof value !== 'number') return '-'
  return value.toFixed(1)
}

const getMarkLines = () => {
  // 根据指标类型返回参考线
  const lines = []
  
  if (props.metricType === 'weight') {
    // 目标体重线
    lines.push({
      yAxis: 65,
      label: { formatter: '目标体重' }
    })
  } else if (props.metricType === 'sleep_duration') {
    // 推荐睡眠时间
    lines.push({
      yAxis: 7.5,
      label: { formatter: '推荐睡眠' }
    })
  }
  
  return lines
}

const handlePeriodChange = (period) => {
  selectedPeriod.value = period
  fetchData()
  emit('period-change', period)
}

const onChartClick = (params) => {
  if (params.componentType === 'series') {
    const dataPoint = {
      date: chartData.value[params.dataIndex]?.date,
      value: params.value,
      metric: props.metricType,
      title: props.title
    }
    emit('chart-click', dataPoint)
  }
}

const handleChartClick = async () => {
  chatLoading.value = true
  try {
    const chartContext = {
      metric: props.title,
      trend: summary.value.trend,
      value: summary.value.avg,
      period: selectedPeriod.value,
      data: chartData.value
    }
    
    const response = await healthReportAPI.triggerReportChat('current', chartContext)
    
    // 触发父组件处理聊天
    emit('chart-click', {
      type: 'chat',
      sessionId: response.data.session_id,
      analysis: response.data.initial_analysis
    })
    
    message.success('已为您启动趋势分析对话')
  } catch (error) {
    console.error('启动分析对话失败:', error)
    message.error('启动分析对话失败')
  } finally {
    chatLoading.value = false
  }
}

// 监听器
watch(() => props.metricType, () => {
  fetchData()
}, { immediate: false })

// 监听主题变化
watch(isDark, () => {
  // 主题变化时图表会自动重新渲染
})

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
.health-line-chart {
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

.chart-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.summary-item {
  text-align: center;
}

.summary-item .label {
  display: block;
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.summary-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.trend-up {
  color: #52c41a;
}

.trend-down {
  color: #ff4d4f;
}

.change-positive {
  color: #52c41a;
}

.change-negative {
  color: #ff4d4f;
}
</style>
