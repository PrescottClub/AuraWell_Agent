<template>
  <div class="health-heatmap">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <a-select
          v-model:value="selectedYear"
          @change="handleYearChange"
          style="width: 100px; margin-right: 12px;"
        >
          <a-select-option value="2024">2024年</a-select-option>
          <a-select-option value="2023">2023年</a-select-option>
        </a-select>
        
        <a-button 
          type="text" 
          size="small"
          @click="handlePatternAnalysis"
          :loading="analyzing"
        >
          <HeatMapOutlined />
          模式分析
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
    
    <div class="heatmap-legend">
      <div class="legend-item">
        <div class="legend-color" style="background: #ebedf0;"></div>
        <span>无数据</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #c6e48b;"></div>
        <span>较少</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #7bc96f;"></div>
        <span>一般</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #239a3b;"></div>
        <span>较多</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #196127;"></div>
        <span>很多</span>
      </div>
    </div>
    
    <div v-if="showInsights" class="heatmap-insights">
      <div class="insight-item" v-for="insight in insights" :key="insight.type">
        <div class="insight-icon">{{ insight.icon }}</div>
        <div class="insight-content">
          <div class="insight-title">{{ insight.title }}</div>
          <div class="insight-desc">{{ insight.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { HeatMapOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { healthReportAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '睡眠热力图'
  },
  metricType: {
    type: String,
    default: 'sleep_duration'
  },
  chartHeight: {
    type: Number,
    default: 200
  },
  showInsights: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['chart-click', 'pattern-analysis'])

// 响应式数据
const chartRef = ref(null)
const loading = ref(false)
const analyzing = ref(false)
const selectedYear = ref('2024')
const heatmapData = ref([])

// 计算属性
const chartOption = computed(() => {
  if (!heatmapData.value.length) return {}
  
  return {
    tooltip: {
      position: 'top',
      formatter: (params) => {
        const date = params.data[0]
        const value = params.data[1]
        return `${date}<br/>${props.title}: ${value ? value.toFixed(1) + '小时' : '无数据'}`
      }
    },
    grid: {
      height: '50%',
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: getMonths(),
      splitArea: {
        show: true
      },
      axisLabel: {
        fontSize: 12,
        color: '#666'
      }
    },
    yAxis: {
      type: 'category',
      data: getWeekdays(),
      splitArea: {
        show: true
      },
      axisLabel: {
        fontSize: 12,
        color: '#666'
      }
    },
    visualMap: {
      min: 0,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%',
      inRange: {
        color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
      },
      text: ['高', '低'],
      textStyle: {
        fontSize: 12,
        color: '#666'
      }
    },
    series: [
      {
        name: props.title,
        type: 'heatmap',
        data: heatmapData.value,
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

const insights = computed(() => {
  if (!heatmapData.value.length) return []
  
  const patterns = analyzePatterns()
  return [
    {
      type: 'consistency',
      icon: '📊',
      title: '规律性分析',
      description: patterns.consistency
    },
    {
      type: 'weekday',
      icon: '📅',
      title: '工作日模式',
      description: patterns.weekdayPattern
    },
    {
      type: 'weekend',
      icon: '🎉',
      title: '周末模式',
      description: patterns.weekendPattern
    }
  ]
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    const startDate = `${selectedYear.value}-01-01T00:00:00Z`
    const endDate = `${selectedYear.value}-12-31T23:59:59Z`
    
    const response = await healthReportAPI.getHealthMetricsTimeSeries({
      metric_type: props.metricType,
      start_date: startDate,
      end_date: endDate,
      interval: 'daily'
    })
    
    heatmapData.value = processHeatmapData(response.data.data || [])
  } catch (error) {
    console.error('获取热力图数据失败:', error)
    message.error('获取热力图数据失败')
  } finally {
    loading.value = false
  }
}

const processHeatmapData = (rawData) => {
  const data = []
  const year = parseInt(selectedYear.value)
  
  // 生成一年的数据
  for (let month = 0; month < 12; month++) {
    const daysInMonth = new Date(year, month + 1, 0).getDate()
    
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day)
      const dateStr = date.toISOString().split('T')[0]
      const weekday = date.getDay()
      
      // 查找对应日期的数据
      const dayData = rawData.find(item => item.date === dateStr)
      const value = dayData ? dayData.value : null
      
      data.push([
        getMonthWeek(date),
        weekday,
        value
      ])
    }
  }
  
  return data
}

const getMonths = () => {
  const months = []
  for (let i = 1; i <= 12; i++) {
    months.push(`${i}月`)
  }
  return months
}

const getWeekdays = () => {
  return ['日', '一', '二', '三', '四', '五', '六']
}

const getMonthWeek = (date) => {
  return date.getMonth()
}

const analyzePatterns = () => {
  const weekdayData = []
  const weekendData = []
  
  heatmapData.value.forEach(item => {
    const weekday = item[1]
    const value = item[2]
    
    if (value !== null) {
      if (weekday === 0 || weekday === 6) {
        weekendData.push(value)
      } else {
        weekdayData.push(value)
      }
    }
  })
  
  const weekdayAvg = weekdayData.length ? 
    (weekdayData.reduce((sum, val) => sum + val, 0) / weekdayData.length).toFixed(1) : 0
  const weekendAvg = weekendData.length ? 
    (weekendData.reduce((sum, val) => sum + val, 0) / weekendData.length).toFixed(1) : 0
  
  const consistency = calculateConsistency()
  
  return {
    consistency: `您的${props.title}规律性为${consistency}%，${consistency > 80 ? '非常规律' : consistency > 60 ? '比较规律' : '需要改善'}`,
    weekdayPattern: `工作日平均${weekdayAvg}小时，${weekdayAvg >= 7 ? '表现良好' : '建议增加'}`,
    weekendPattern: `周末平均${weekendAvg}小时，${weekendAvg > weekdayAvg ? '周末补眠较多' : '作息比较规律'}`
  }
}

const calculateConsistency = () => {
  const values = heatmapData.value
    .filter(item => item[2] !== null)
    .map(item => item[2])
  
  if (values.length < 7) return 0
  
  const avg = values.reduce((sum, val) => sum + val, 0) / values.length
  const variance = values.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / values.length
  const stdDev = Math.sqrt(variance)
  
  // 标准差越小，规律性越高
  const consistency = Math.max(0, 100 - (stdDev / avg) * 100)
  return Math.round(consistency)
}

const handleYearChange = (year) => {
  selectedYear.value = year
  fetchData()
}

const onChartClick = (params) => {
  if (params.componentType === 'series') {
    const monthIndex = params.data[0]
    const weekday = params.data[1]
    const value = params.data[2]
    
    emit('chart-click', {
      month: monthIndex + 1,
      weekday,
      value,
      metric: props.metricType
    })
  }
}

const handlePatternAnalysis = async () => {
  analyzing.value = true
  try {
    const analysisData = {
      type: 'pattern',
      metric: props.metricType,
      year: selectedYear.value,
      insights: insights.value,
      data: heatmapData.value
    }
    
    emit('pattern-analysis', analysisData)
    message.success('正在为您分析睡眠模式...')
  } catch (error) {
    console.error('模式分析失败:', error)
    message.error('模式分析失败')
  } finally {
    analyzing.value = false
  }
}

// 监听器
watch(selectedYear, () => {
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
.health-heatmap {
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

.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.heatmap-insights {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.insight-icon {
  font-size: 20px;
  line-height: 1;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.insight-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}
</style>
