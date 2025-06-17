<template>
  <div class="report-summary">
    <div class="summary-header">
      <div class="summary-title">
        <h2>{{ report.title }}</h2>
        <div class="summary-meta">
          <span class="period">{{ formatPeriod(report.period) }}</span>
          <span class="generated-time">生成于 {{ formatDate(report.created_at) }}</span>
        </div>
      </div>
      
      <div class="summary-actions">
        <a-button @click="handleExport" :loading="exporting">
          <DownloadOutlined />
          导出报告
        </a-button>
        <a-button type="primary" @click="handleDiscuss" :loading="discussing">
          <MessageOutlined />
          与AI讨论
        </a-button>
      </div>
    </div>
    
    <!-- 健康评分 -->
    <div class="health-score-section">
      <div class="score-card main-score">
        <div class="score-header">
          <h3>综合健康评分</h3>
          <a-tooltip title="基于多维度健康数据综合计算">
            <InfoCircleOutlined class="info-icon" />
          </a-tooltip>
        </div>
        <div class="score-display">
          <div class="score-value" :class="getScoreClass(report.health_score.overall)">
            {{ report.health_score.overall }}
          </div>
          <div class="score-change" :class="getChangeClass(report.health_score.improvement)">
            <ArrowUpOutlined v-if="report.health_score.improvement > 0" />
            <ArrowDownOutlined v-else-if="report.health_score.improvement < 0" />
            {{ Math.abs(report.health_score.improvement) }}分
          </div>
        </div>
        <div class="score-description">
          {{ getScoreDescription(report.health_score.overall) }}
        </div>
      </div>
      
      <div class="score-categories">
        <div 
          v-for="(score, category) in report.health_score.categories" 
          :key="category"
          class="category-score"
        >
          <div class="category-name">{{ getCategoryName(category) }}</div>
          <div class="category-value" :class="getScoreClass(score)">{{ score }}</div>
          <div class="category-bar">
            <div 
              class="category-fill" 
              :style="{ width: score + '%', backgroundColor: getScoreColor(score) }"
            ></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 关键指标 -->
    <div class="key-metrics-section">
      <h3>关键指标概览</h3>
      <div class="metrics-grid">
        <div class="metric-card" v-for="(metric, key) in keyMetrics" :key="key">
          <div class="metric-icon" :style="{ color: metric.color }">
            <component :is="metric.icon" />
          </div>
          <div class="metric-content">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value">
              {{ formatMetricValue(metric.current, metric.unit) }}
            </div>
            <div class="metric-change" :class="getTrendClass(metric.trend)">
              <component :is="getTrendIcon(metric.trend)" />
              {{ formatChange(metric.change, metric.unit) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI洞察摘要 -->
    <div class="insights-summary-section">
      <h3>AI智能洞察</h3>
      <div class="insights-overview">
        <div class="insight-stats">
          <div class="stat-item">
            <div class="stat-value positive">{{ positiveInsights }}</div>
            <div class="stat-label">积极发现</div>
          </div>
          <div class="stat-item">
            <div class="stat-value warning">{{ warningInsights }}</div>
            <div class="stat-label">需要关注</div>
          </div>
          <div class="stat-item">
            <div class="stat-value critical">{{ criticalInsights }}</div>
            <div class="stat-label">重要提醒</div>
          </div>
        </div>
        
        <div class="top-insights">
          <div 
            v-for="insight in topInsights" 
            :key="insight.insight_id"
            class="insight-preview"
            @click="handleInsightClick(insight)"
          >
            <div class="insight-indicator" :class="`indicator-${insight.severity}`"></div>
            <div class="insight-content">
              <div class="insight-title">{{ insight.title }}</div>
              <div class="insight-excerpt">{{ truncateText(insight.content, 60) }}</div>
            </div>
            <RightOutlined class="insight-arrow" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 下期目标 -->
    <div class="next-goals-section">
      <h3>下期健康目标</h3>
      <div class="goals-list">
        <div 
          v-for="goal in report.next_period_goals" 
          :key="goal.category"
          class="goal-item"
        >
          <div class="goal-icon">🎯</div>
          <div class="goal-content">
            <div class="goal-title">{{ goal.description }}</div>
            <div class="goal-target">目标: {{ goal.target }}</div>
          </div>
          <a-button size="small" @click="handleGoalAdjust(goal)">
            调整
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  DownloadOutlined,
  MessageOutlined,
  InfoCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  RightOutlined,
  MinusOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

// Props
const props = defineProps({
  report: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['export', 'discuss', 'insight-click', 'goal-adjust'])

// 响应式数据
const exporting = ref(false)
const discussing = ref(false)

// 计算属性
const keyMetrics = computed(() => {
  const metrics = props.report.metrics || {}
  return {
    weight: {
      label: '体重',
      current: metrics.weight?.current || 0,
      change: metrics.weight?.change || 0,
      trend: metrics.weight?.trend || 'stable',
      unit: 'kg',
      color: '#1890ff',
      icon: 'ScaleOutlined'
    },
    exercise: {
      label: '运动时长',
      current: metrics.exercise?.total_duration || 0,
      change: metrics.exercise?.total_duration - (metrics.exercise?.previous_duration || 0),
      trend: 'increasing',
      unit: '分钟',
      color: '#52c41a',
      icon: 'ThunderboltOutlined'
    },
    sleep: {
      label: '平均睡眠',
      current: metrics.sleep?.avg_duration || 0,
      change: metrics.sleep?.avg_duration - (metrics.sleep?.previous_avg || 0),
      trend: 'stable',
      unit: '小时',
      color: '#722ed1',
      icon: 'MoonOutlined'
    },
    mood: {
      label: '心情指数',
      current: metrics.mental_health?.mood_score || 0,
      change: metrics.mental_health?.mood_score - (metrics.mental_health?.previous_mood || 0),
      trend: 'increasing',
      unit: '分',
      color: '#faad14',
      icon: 'SmileOutlined'
    }
  }
})

const positiveInsights = computed(() => {
  return props.report.insights?.filter(i => i.severity === 'positive').length || 0
})

const warningInsights = computed(() => {
  return props.report.insights?.filter(i => i.severity === 'warning').length || 0
})

const criticalInsights = computed(() => {
  return props.report.insights?.filter(i => i.severity === 'critical').length || 0
})

const topInsights = computed(() => {
  return props.report.insights?.slice(0, 3) || []
})

// 方法
const formatPeriod = (period) => {
  const start = new Date(period.start_date).toLocaleDateString()
  const end = new Date(period.end_date).toLocaleDateString()
  return `${start} - ${end}`
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString()
}

const getScoreClass = (score) => {
  if (score >= 85) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 65) return 'score-fair'
  return 'score-poor'
}

const getChangeClass = (change) => {
  return change > 0 ? 'change-positive' : change < 0 ? 'change-negative' : 'change-neutral'
}

const getScoreDescription = (score) => {
  if (score >= 85) return '健康状况优秀，继续保持！'
  if (score >= 75) return '健康状况良好，稍作调整更佳'
  if (score >= 65) return '健康状况一般，建议重点改善'
  return '健康状况需要关注，建议咨询专业人士'
}

const getCategoryName = (category) => {
  const names = {
    physical_health: '身体健康',
    mental_health: '心理健康',
    lifestyle: '生活方式',
    nutrition: '营养状况'
  }
  return names[category] || category
}

const getScoreColor = (score) => {
  if (score >= 85) return '#52c41a'
  if (score >= 75) return '#1890ff'
  if (score >= 65) return '#faad14'
  return '#ff4d4f'
}

const formatMetricValue = (value, unit) => {
  if (typeof value !== 'number') return '-'
  return value.toFixed(1) + unit
}

const getTrendClass = (trend) => {
  switch (trend) {
    case 'increasing': return 'trend-up'
    case 'decreasing': return 'trend-down'
    default: return 'trend-stable'
  }
}

const getTrendIcon = (trend) => {
  switch (trend) {
    case 'increasing': return ArrowUpOutlined
    case 'decreasing': return ArrowDownOutlined
    default: return MinusOutlined
  }
}

const formatChange = (change, unit) => {
  if (typeof change !== 'number') return '-'
  const prefix = change > 0 ? '+' : ''
  return `${prefix}${change.toFixed(1)}${unit}`
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const handleExport = async () => {
  exporting.value = true
  try {
    emit('export', props.report)
    message.success('报告导出成功')
  } catch (error) {
    message.error('报告导出失败')
  } finally {
    exporting.value = false
  }
}

const handleDiscuss = async () => {
  discussing.value = true
  try {
    emit('discuss', props.report)
  } finally {
    discussing.value = false
  }
}

const handleInsightClick = (insight) => {
  emit('insight-click', insight)
}

const handleGoalAdjust = (goal) => {
  emit('goal-adjust', goal)
}
</script>

<style scoped>
.report-summary {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.summary-title h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.summary-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #8c8c8c;
}

.summary-actions {
  display: flex;
  gap: 12px;
}

.health-score-section {
  margin-bottom: 32px;
}

.score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}

.score-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.score-header h3 {
  margin: 0;
  color: white;
  font-size: 18px;
}

.info-icon {
  color: rgba(255, 255, 255, 0.8);
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 8px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.score-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 600;
}

.change-positive {
  color: #52c41a;
}

.change-negative {
  color: #ff4d4f;
}

.score-description {
  font-size: 16px;
  opacity: 0.9;
}

.score-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.category-score {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.category-name {
  font-size: 14px;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.category-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.category-bar {
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.category-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.key-metrics-section {
  margin-bottom: 32px;
}

.key-metrics-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.metric-icon {
  font-size: 24px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 2px;
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.trend-up {
  color: #52c41a;
}

.trend-down {
  color: #ff4d4f;
}

.trend-stable {
  color: #8c8c8c;
}

.insights-summary-section {
  margin-bottom: 32px;
}

.insights-summary-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.insights-overview {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
}

.insight-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  background: #fafafa;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-value.positive {
  color: #52c41a;
}

.stat-value.warning {
  color: #faad14;
}

.stat-value.critical {
  color: #ff4d4f;
}

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
}

.top-insights {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.insight-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.insight-preview:hover {
  background: #f0f0f0;
}

.insight-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
}

.indicator-positive {
  background: #52c41a;
}

.indicator-warning {
  background: #faad14;
}

.indicator-critical {
  background: #ff4d4f;
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

.insight-excerpt {
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.4;
}

.insight-arrow {
  color: #bfbfbf;
  font-size: 12px;
}

.next-goals-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.goal-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.goal-icon {
  font-size: 20px;
}

.goal-content {
  flex: 1;
}

.goal-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.goal-target {
  font-size: 12px;
  color: #8c8c8c;
}
</style>
