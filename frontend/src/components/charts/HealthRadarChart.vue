<template>
  <div class="health-radar-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <a-select
          v-model:value="selectedPeriod"
          @change="handlePeriodChange"
          style="width: 120px; margin-right: 12px;"
        >
          <a-select-option value="current">本期</a-select-option>
          <a-select-option value="previous">上期</a-select-option>
          <a-select-option value="compare">对比</a-select-option>
        </a-select>
        
        <a-button 
          type="text" 
          size="small"
          @click="handleBalanceAnalysis"
          :loading="analyzing"
        >
          <RadarChartOutlined />
          平衡分析
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
    
    <div v-if="showScores" class="radar-scores">
      <div class="score-item" v-for="dimension in dimensions" :key="dimension.name">
        <div class="score-name">{{ dimension.label }}</div>
        <div class="score-value" :class="getScoreClass(dimension.value)">
          {{ dimension.value }}
        </div>
        <div class="score-change" :class="getChangeClass(dimension.change)">
          {{ formatChange(dimension.change) }}
        </div>
      </div>
    </div>
    
    <div v-if="showRecommendations" class="radar-recommendations">
      <h4>个性化建议</h4>
      <div class="recommendation-item" v-for="rec in recommendations" :key="rec.dimension">
        <div class="rec-icon" :style="{ color: rec.color }">{{ rec.icon }}</div>
        <div class="rec-content">
          <div class="rec-title">{{ rec.title }}</div>
          <div class="rec-desc">{{ rec.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { RadarChartOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { healthReportAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '健康雷达图'
  },
  chartHeight: {
    type: Number,
    default: 400
  },
  showScores: {
    type: Boolean,
    default: true
  },
  showRecommendations: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['chart-click', 'balance-analysis'])

// 响应式数据
const chartRef = ref(null)
const loading = ref(false)
const analyzing = ref(false)
const selectedPeriod = ref('current')
const radarData = ref({})

// 计算属性
const dimensions = computed(() => {
  if (!radarData.value.current) return []
  
  const current = radarData.value.current
  const previous = radarData.value.previous || {}
  
  return [
    {
      name: 'physical',
      label: '身体健康',
      value: current.physical || 0,
      change: (current.physical || 0) - (previous.physical || 0)
    },
    {
      name: 'mental',
      label: '心理健康',
      value: current.mental || 0,
      change: (current.mental || 0) - (previous.mental || 0)
    },
    {
      name: 'exercise',
      label: '运动表现',
      value: current.exercise || 0,
      change: (current.exercise || 0) - (previous.exercise || 0)
    },
    {
      name: 'nutrition',
      label: '营养状况',
      value: current.nutrition || 0,
      change: (current.nutrition || 0) - (previous.nutrition || 0)
    },
    {
      name: 'sleep',
      label: '睡眠质量',
      value: current.sleep || 0,
      change: (current.sleep || 0) - (previous.sleep || 0)
    },
    {
      name: 'lifestyle',
      label: '生活方式',
      value: current.lifestyle || 0,
      change: (current.lifestyle || 0) - (previous.lifestyle || 0)
    }
  ]
})

const chartOption = computed(() => {
  if (!dimensions.value.length) return {}
  
  const indicator = dimensions.value.map(dim => ({
    name: dim.label,
    max: 100
  }))
  
  const series = []
  
  // 当前期数据
  if (radarData.value.current) {
    series.push({
      name: '本期',
      type: 'radar',
      data: [{
        value: dimensions.value.map(dim => dim.value),
        name: '本期',
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: 'rgba(24, 144, 255, 0.2)'
        }
      }]
    })
  }
  
  // 对比模式下显示上期数据
  if (selectedPeriod.value === 'compare' && radarData.value.previous) {
    series.push({
      name: '上期',
      type: 'radar',
      data: [{
        value: Object.values(radarData.value.previous),
        name: '上期',
        itemStyle: {
          color: '#52c41a'
        },
        areaStyle: {
          color: 'rgba(82, 196, 26, 0.2)'
        }
      }]
    })
  }
  
  return {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const data = params.data
        let html = `${data.name}<br/>`
        data.value.forEach((value, index) => {
          html += `${indicator[index].name}: ${value}<br/>`
        })
        return html
      }
    },
    legend: {
      data: series.map(s => s.name),
      bottom: 10
    },
    radar: {
      indicator,
      radius: '70%',
      splitNumber: 5,
      splitArea: {
        areaStyle: {
          color: ['rgba(114, 172, 209, 0.2)', 'rgba(114, 172, 209, 0.4)',
                  'rgba(114, 172, 209, 0.6)', 'rgba(114, 172, 209, 0.8)',
                  'rgba(114, 172, 209, 1)'].reverse()
        }
      },
      axisLabel: {
        fontSize: 12,
        color: '#666'
      }
    },
    series
  }
})

const recommendations = computed(() => {
  if (!dimensions.value.length) return []
  
  const recs = []
  
  dimensions.value.forEach(dim => {
    if (dim.value < 60) {
      recs.push(generateRecommendation(dim))
    }
  })
  
  return recs.slice(0, 3) // 最多显示3个建议
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    // 模拟获取雷达图数据
    const response = await healthReportAPI.getHealthInsights({
      category: 'comprehensive',
      period: selectedPeriod.value
    })
    
    // 生成模拟的雷达图数据
    radarData.value = {
      current: {
        physical: 75 + Math.random() * 20,
        mental: 68 + Math.random() * 25,
        exercise: 82 + Math.random() * 15,
        nutrition: 71 + Math.random() * 20,
        sleep: 65 + Math.random() * 25,
        lifestyle: 78 + Math.random() * 18
      },
      previous: {
        physical: 70 + Math.random() * 20,
        mental: 65 + Math.random() * 25,
        exercise: 75 + Math.random() * 20,
        nutrition: 68 + Math.random() * 22,
        sleep: 62 + Math.random() * 25,
        lifestyle: 72 + Math.random() * 20
      }
    }
  } catch (error) {
    console.error('获取雷达图数据失败:', error)
    message.error('获取雷达图数据失败')
  } finally {
    loading.value = false
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-excellent'
  if (score >= 70) return 'score-good'
  if (score >= 60) return 'score-fair'
  return 'score-poor'
}

const getChangeClass = (change) => {
  if (change > 0) return 'change-positive'
  if (change < 0) return 'change-negative'
  return 'change-neutral'
}

const formatChange = (change) => {
  if (change === 0) return '持平'
  return `${change > 0 ? '+' : ''}${change.toFixed(1)}`
}

const generateRecommendation = (dimension) => {
  const recommendations = {
    physical: {
      icon: '💪',
      color: '#ff4d4f',
      title: '提升身体健康',
      description: '建议增加有氧运动，保持规律作息，定期体检'
    },
    mental: {
      icon: '🧠',
      color: '#722ed1',
      title: '改善心理状态',
      description: '尝试冥想练习，保持社交活动，寻求专业帮助'
    },
    exercise: {
      icon: '🏃',
      color: '#52c41a',
      title: '加强运动锻炼',
      description: '制定运动计划，逐步增加运动强度和频次'
    },
    nutrition: {
      icon: '🥗',
      color: '#faad14',
      title: '优化营养摄入',
      description: '均衡饮食，增加蔬果摄入，控制加工食品'
    },
    sleep: {
      icon: '😴',
      color: '#1890ff',
      title: '改善睡眠质量',
      description: '建立睡眠规律，优化睡眠环境，避免睡前刺激'
    },
    lifestyle: {
      icon: '🌱',
      color: '#13c2c2',
      title: '调整生活方式',
      description: '减少压力源，培养健康习惯，保持工作生活平衡'
    }
  }
  
  return recommendations[dimension.name] || {
    icon: '📈',
    color: '#666',
    title: '持续改善',
    description: '保持当前良好状态，继续努力提升'
  }
}

const handlePeriodChange = (period) => {
  selectedPeriod.value = period
  fetchData()
}

const onChartClick = (params) => {
  if (params.componentType === 'series') {
    const dimensionIndex = params.dataIndex
    const dimension = dimensions.value[dimensionIndex]
    
    emit('chart-click', {
      dimension: dimension.name,
      label: dimension.label,
      value: dimension.value,
      change: dimension.change
    })
  }
}

const handleBalanceAnalysis = async () => {
  analyzing.value = true
  try {
    const analysisData = {
      type: 'balance',
      dimensions: dimensions.value,
      overall_score: dimensions.value.reduce((sum, dim) => sum + dim.value, 0) / dimensions.value.length,
      recommendations: recommendations.value
    }
    
    emit('balance-analysis', analysisData)
    message.success('正在为您生成健康平衡分析...')
  } catch (error) {
    console.error('平衡分析失败:', error)
    message.error('平衡分析失败')
  } finally {
    analyzing.value = false
  }
}

// 监听器
watch(selectedPeriod, () => {
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
.health-radar-chart {
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

.radar-scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.score-item {
  text-align: center;
}

.score-name {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.score-value {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 2px;
}

.score-excellent {
  color: #52c41a;
}

.score-good {
  color: #1890ff;
}

.score-fair {
  color: #faad14;
}

.score-poor {
  color: #ff4d4f;
}

.score-change {
  font-size: 11px;
}

.change-positive {
  color: #52c41a;
}

.change-negative {
  color: #ff4d4f;
}

.change-neutral {
  color: #8c8c8c;
}

.radar-recommendations {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.radar-recommendations h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.rec-icon {
  font-size: 18px;
  line-height: 1;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-size: 13px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 2px;
}

.rec-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}
</style>
