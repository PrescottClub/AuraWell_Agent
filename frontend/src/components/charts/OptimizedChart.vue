<template>
  <div class="optimized-chart" ref="chartContainer">
    <!-- 加载状态 -->
    <div v-if="loading" class="chart-loading">
      <a-spin size="large">
        <template #indicator>
          <LoadingOutlined style="font-size: 24px" spin />
        </template>
      </a-spin>
      <div class="loading-text">{{ loadingText }}</div>
    </div>
    
    <!-- 图表控制栏 -->
    <div v-if="!loading" class="chart-controls">
      <div class="controls-left">
        <a-select
          v-model:value="selectedTimeRange"
          @change="handleTimeRangeChange"
          style="width: 120px; margin-right: 12px;"
        >
          <a-select-option value="7d">近7天</a-select-option>
          <a-select-option value="30d">近30天</a-select-option>
          <a-select-option value="90d">近3个月</a-select-option>
          <a-select-option value="1y">近1年</a-select-option>
        </a-select>
        
        <a-select
          v-model:value="selectedSamplingMode"
          @change="handleSamplingModeChange"
          style="width: 140px; margin-right: 12px;"
        >
          <a-select-option value="auto">智能抽样</a-select-option>
          <a-select-option value="uniform">均匀抽样</a-select-option>
          <a-select-option value="intelligent">关键点抽样</a-select-option>
          <a-select-option value="none">不抽样</a-select-option>
        </a-select>
        
        <a-tooltip title="数据点数量">
          <a-tag color="blue">{{ displayDataCount }} 点</a-tag>
        </a-tooltip>
      </div>
      
      <div class="controls-right">
        <a-tooltip title="性能信息">
          <a-button 
            type="text" 
            size="small"
            @click="showPerformanceInfo = !showPerformanceInfo"
          >
            <DashboardOutlined />
          </a-button>
        </a-tooltip>
        
        <a-tooltip title="刷新数据">
          <a-button 
            type="text" 
            size="small"
            @click="refreshData"
            :loading="refreshing"
          >
            <ReloadOutlined />
          </a-button>
        </a-tooltip>
        
        <a-tooltip title="全屏显示">
          <a-button 
            type="text" 
            size="small"
            @click="toggleFullscreen"
          >
            <FullscreenOutlined v-if="!isFullscreen" />
            <FullscreenExitOutlined v-else />
          </a-button>
        </a-tooltip>
      </div>
    </div>
    
    <!-- 性能信息面板 -->
    <div v-if="showPerformanceInfo" class="performance-info">
      <div class="perf-item">
        <span class="perf-label">渲染时间:</span>
        <span class="perf-value">{{ performanceMetrics.renderTime }}ms</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">数据处理:</span>
        <span class="perf-value">{{ performanceMetrics.dataProcessTime }}ms</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">原始数据:</span>
        <span class="perf-value">{{ rawDataCount }} 点</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">显示数据:</span>
        <span class="perf-value">{{ displayDataCount }} 点</span>
      </div>
      <div class="perf-item">
        <span class="perf-label">压缩比:</span>
        <span class="perf-value">{{ compressionRatio }}%</span>
      </div>
    </div>
    
    <!-- 图表容器 -->
    <div 
      v-if="!loading"
      class="chart-wrapper"
      :class="{ 'fullscreen': isFullscreen }"
      ref="chartWrapper"
    >
      <v-chart
        ref="chartRef"
        :option="optimizedChartOption"
        :loading="chartLoading"
        @click="handleChartClick"
        @dataZoom="handleDataZoom"
        autoresize
        :style="chartStyle"
      />
    </div>
    
    <!-- 数据缺失提示 -->
    <div v-if="!loading && !rawData.length" class="empty-state">
      <a-empty description="暂无数据">
        <a-button type="primary" @click="refreshData">
          重新加载
        </a-button>
      </a-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { 
  LoadingOutlined,
  DashboardOutlined,
  ReloadOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { 
  DataSampling, 
  globalPerformanceMonitor,
  debounce,
  performanceUtils
} from '../../utils/performance.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '数据图表'
  },
  chartType: {
    type: String,
    default: 'line' // line, bar, scatter
  },
  dataSource: {
    type: Function,
    required: true
  },
  maxDataPoints: {
    type: Number,
    default: 500
  },
  autoRefresh: {
    type: Boolean,
    default: false
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30秒
  },
  enableDataZoom: {
    type: Boolean,
    default: true
  },
  enableBrush: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['chart-click', 'data-zoom', 'data-loaded'])

// 响应式数据
const chartContainer = ref(null)
const chartWrapper = ref(null)
const chartRef = ref(null)
const loading = ref(false)
const chartLoading = ref(false)
const refreshing = ref(false)
const loadingText = ref('加载中...')
const showPerformanceInfo = ref(false)
const isFullscreen = ref(false)

// 数据相关
const rawData = ref([])
const processedData = ref([])
const selectedTimeRange = ref('30d')
const selectedSamplingMode = ref('auto')

// 性能指标
const performanceMetrics = ref({
  renderTime: 0,
  dataProcessTime: 0,
  lastUpdateTime: Date.now()
})

// 自动刷新定时器
let refreshTimer = null

// 计算属性
const rawDataCount = computed(() => rawData.value.length)
const displayDataCount = computed(() => processedData.value.length)

const compressionRatio = computed(() => {
  if (rawDataCount.value === 0) return 0
  return Math.round((1 - displayDataCount.value / rawDataCount.value) * 100)
})

const chartStyle = computed(() => {
  const devicePerf = performanceUtils.getDevicePerformance()
  const baseHeight = isFullscreen.value ? '80vh' : '400px'
  
  return {
    height: baseHeight,
    width: '100%',
    // 根据设备性能调整渲染质量
    ...(devicePerf.level === 'low' && {
      'image-rendering': 'pixelated'
    })
  }
})

const optimizedChartOption = computed(() => {
  if (!processedData.value.length) return {}
  
  const devicePerf = performanceUtils.getDevicePerformance()
  const isLowPerf = devicePerf.level === 'low'
  
  const baseOption = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        animation: !isLowPerf
      },
      formatter: (params) => {
        const point = params[0]
        return `${point.name}<br/>${point.seriesName}: ${point.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: props.enableDataZoom ? '15%' : '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: processedData.value.map(item => formatDate(item.date)),
      axisLabel: {
        fontSize: 12,
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 12,
        color: '#666'
      }
    },
    series: [
      {
        name: props.title,
        type: props.chartType,
        data: processedData.value.map(item => item.value),
        smooth: props.chartType === 'line' && !isLowPerf,
        symbol: displayDataCount.value > 100 ? 'none' : 'circle',
        symbolSize: 4,
        lineStyle: {
          width: 2
        },
        itemStyle: {
          color: '#1890ff'
        },
        // 大数据量时禁用动画
        animation: !isLowPerf && displayDataCount.value < 1000,
        animationDuration: isLowPerf ? 0 : 1000
      }
    ]
  }
  
  // 添加数据缩放
  if (props.enableDataZoom) {
    baseOption.dataZoom = [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 30
      }
    ]
  }
  
  // 添加刷选工具
  if (props.enableBrush) {
    baseOption.brush = {
      toolbox: ['rect', 'polygon', 'clear'],
      xAxisIndex: 0
    }
  }
  
  return baseOption
})

// 方法
const fetchData = async () => {
  loading.value = true
  loadingText.value = '获取数据中...'
  
  try {
    globalPerformanceMonitor.startTiming('dataFetch')
    
    const timeRange = getTimeRangeParams(selectedTimeRange.value)
    const response = await props.dataSource(timeRange)
    
    globalPerformanceMonitor.endTiming('dataFetch')
    
    rawData.value = response.data || []
    await processData()
    
    emit('data-loaded', {
      rawCount: rawDataCount.value,
      processedCount: displayDataCount.value
    })
    
  } catch (error) {
    console.error('获取数据失败:', error)
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const processData = async () => {
  if (!rawData.value.length) {
    processedData.value = []
    return
  }
  
  loadingText.value = '处理数据中...'
  globalPerformanceMonitor.startTiming('dataProcess')
  
  try {
    let processed = [...rawData.value]
    
    // 根据抽样模式处理数据
    if (selectedSamplingMode.value !== 'none' && processed.length > props.maxDataPoints) {
      switch (selectedSamplingMode.value) {
        case 'uniform':
          processed = DataSampling.uniformSampling(processed, props.maxDataPoints)
          break
        case 'intelligent':
          processed = DataSampling.intelligentSampling(processed, props.maxDataPoints, 'value')
          break
        case 'auto':
        default:
          // 根据数据特征自动选择抽样方式
          const hasHighVariance = checkDataVariance(processed)
          processed = hasHighVariance 
            ? DataSampling.intelligentSampling(processed, props.maxDataPoints, 'value')
            : DataSampling.uniformSampling(processed, props.maxDataPoints)
          break
      }
    }
    
    processedData.value = processed
    
    globalPerformanceMonitor.endTiming('dataProcess')
    
    // 更新性能指标
    const metrics = globalPerformanceMonitor.getAllMetrics()
    performanceMetrics.value.dataProcessTime = Math.round(metrics.dataProcess?.duration || 0)
    
  } catch (error) {
    console.error('数据处理失败:', error)
    processedData.value = rawData.value.slice(0, props.maxDataPoints)
  }
}

const checkDataVariance = (data) => {
  if (data.length < 10) return false
  
  const values = data.map(item => item.value)
  const mean = values.reduce((sum, val) => sum + val, 0) / values.length
  const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length
  const stdDev = Math.sqrt(variance)
  
  // 如果标准差大于均值的30%，认为是高变异数据
  return stdDev > mean * 0.3
}

const getTimeRangeParams = (range) => {
  const now = new Date()
  const params = { end_date: now.toISOString() }
  
  switch (range) {
    case '7d':
      params.start_date = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString()
      break
    case '30d':
      params.start_date = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString()
      break
    case '90d':
      params.start_date = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString()
      break
    case '1y':
      params.start_date = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000).toISOString()
      break
  }
  
  return params
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const handleTimeRangeChange = debounce(async (range) => {
  selectedTimeRange.value = range
  await fetchData()
}, 300)

const handleSamplingModeChange = debounce(async (mode) => {
  selectedSamplingMode.value = mode
  await processData()
}, 300)

const refreshData = async () => {
  refreshing.value = true
  try {
    await fetchData()
    message.success('数据刷新成功')
  } finally {
    refreshing.value = false
  }
}

const handleChartClick = (params) => {
  emit('chart-click', {
    dataIndex: params.dataIndex,
    data: processedData.value[params.dataIndex],
    seriesName: params.seriesName
  })
}

const handleDataZoom = (params) => {
  emit('data-zoom', params)
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  
  nextTick(() => {
    if (chartRef.value) {
      chartRef.value.resize()
    }
  })
}

const startAutoRefresh = () => {
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(() => {
      fetchData()
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听器
watch(() => props.autoRefresh, (enabled) => {
  if (enabled) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// 性能监控
globalPerformanceMonitor.addObserver((name, metric) => {
  if (name === 'chartRender') {
    performanceMetrics.value.renderTime = Math.round(metric.duration)
  }
})

// 生命周期
onMounted(async () => {
  await fetchData()
  startAutoRefresh()
  
  // 监听图表渲染性能
  if (chartRef.value) {
    const observer = new MutationObserver(() => {
      globalPerformanceMonitor.startTiming('chartRender')
      setTimeout(() => {
        globalPerformanceMonitor.endTiming('chartRender')
      }, 100)
    })
    
    observer.observe(chartRef.value.$el, {
      childList: true,
      subtree: true
    })
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  refreshData,
  exportData: () => processedData.value,
  getPerformanceMetrics: () => performanceMetrics.value
})
</script>

<style scoped>
.optimized-chart {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: 16px;
}

.loading-text {
  font-size: 14px;
  color: #8c8c8c;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.controls-left {
  display: flex;
  align-items: center;
}

.controls-right {
  display: flex;
  gap: 8px;
}

.performance-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 12px;
}

.perf-item {
  display: flex;
  gap: 4px;
}

.perf-label {
  color: #8c8c8c;
}

.perf-value {
  color: #262626;
  font-weight: 600;
}

.chart-wrapper {
  position: relative;
  transition: all 0.3s ease;
}

.chart-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: white;
  padding: 20px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}
</style>
