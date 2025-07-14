<template>
  <div class="min-h-screen bg-background p-8">
    <!-- 页面头部 -->
    <div class="aura-card mb-8">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-display mb-2">智能健康报告</h1>
          <p class="text-body-large">AI驱动的个性化健康分析与建议</p>
        </div>

        <div class="flex items-center gap-3">
          <a-select
            v-model="selectedReportType"
            @change="handleReportTypeChange"
            class="w-32"
          >
            <a-select-option value="weekly">周报</a-select-option>
            <a-select-option value="monthly">月报</a-select-option>
            <a-select-option value="quarterly">季报</a-select-option>
          </a-select>

          <button
            class="aura-btn aura-btn--primary"
            @click="handleGenerateReport"
            :disabled="generating"
          >
            <ThunderboltOutlined v-if="!generating" />
            <span v-if="generating" class="loading-dots">
              <div></div><div></div><div></div>
            </span>
            {{ generating ? '生成中...' : '生成新报告' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 报告列表 -->
    <div v-if="!currentReport" class="reports-list">
      <VirtualReportList
        :data-source="fetchReportsData"
        :item-height="120"
        :container-height="600"
        :page-size="50"
        @item-click="handleSelectReport"
        @item-select="handleReportSelect"
        @batch-action="handleBatchAction"
      />
    </div>
    
    <!-- 报告详情 -->
    <div v-else class="space-y-8">
      <div class="aura-card">
        <div class="flex justify-between items-center">
          <button @click="handleBackToList" class="aura-btn aura-btn--secondary">
            <ArrowLeftOutlined />
            返回列表
          </button>

          <div class="flex gap-3">
            <button @click="handleShareReport" class="aura-btn aura-btn--secondary">
              <ShareAltOutlined />
              分享
            </button>
            <button @click="handleExportReport" class="aura-btn aura-btn--secondary">
              <DownloadOutlined />
              导出
            </button>
          </div>
        </div>
      </div>
      
      <!-- 报告摘要 -->
      <ReportSummary 
        :report="currentReport"
        @export="handleExportReport"
        @discuss="handleDiscussReport"
        @insight-click="handleInsightClick"
        @goal-adjust="handleGoalAdjust"
      />
      
      <!-- 数据可视化 -->
      <div class="aura-card">
        <h2 class="text-heading-2 mb-6">数据可视化分析</h2>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- 体重趋势 - 优化版本 -->
          <div class="aura-card aura-card--elevated">
            <OptimizedChart
              title="体重变化趋势"
              chart-type="line"
              :data-source="getWeightDataSource"
              :max-data-points="300"
              :auto-refresh="true"
              :refresh-interval="60000"
              @chart-click="handleChartInteraction"
              @data-loaded="handleDataLoaded"
            />
          </div>

          <!-- 运动数据 - 优化版本 -->
          <div class="aura-card aura-card--elevated">
            <OptimizedChart
              title="运动表现分析"
              chart-type="bar"
              :data-source="getExerciseDataSource"
              :max-data-points="200"
              :enable-data-zoom="true"
              @chart-click="handleChartInteraction"
              @data-loaded="handleDataLoaded"
            />
          </div>

          <!-- 睡眠热力图 -->
          <div class="lg:col-span-2 aura-card aura-card--elevated">
            <HealthHeatmap
              title="睡眠模式热力图"
              metric-type="sleep_duration"
              @chart-click="handleChartInteraction"
              @pattern-analysis="handlePatternAnalysis"
            />
          </div>

          <!-- 健康雷达图 -->
          <div class="lg:col-span-2 aura-card aura-card--elevated">
            <HealthRadarChart
              title="综合健康评估"
              @chart-click="handleChartInteraction"
              @balance-analysis="handleBalanceAnalysis"
            />
          </div>
        </div>
      </div>
      
      <!-- AI洞察 -->
      <div class="aura-card">
        <h2 class="text-heading-2 mb-6">AI智能洞察</h2>
        <div class="space-y-4">
          <InsightCard
            v-for="insight in currentReport.insights"
            :key="insight.insight_id"
            :insight="insight"
            @discuss="handleInsightDiscuss"
            @adjust-plan="handleInsightAdjustPlan"
            @share="handleInsightShare"
            @save="handleInsightSave"
            @feedback="handleInsightFeedback"
          />
        </div>
      </div>
    </div>

    <!-- 聊天集成组件 -->
    <ChatIntegration
      :report-data="currentReport"
      :show-float-button="!!currentReport"
      @chat-started="handleChatStarted"
      @plan-updated="handlePlanUpdated"
      @context-changed="handleContextChanged"
    />

    <!-- 对话弹窗 - Refactored -->
    <ReportChatModal
      v-model="showChatModal"
      :context="chatContext"
      :session-id="currentSessionId"
      @close="handleCloseChatModal"
      @sent="handleMessageSent"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  ThunderboltOutlined,
  ArrowLeftOutlined,
  ShareAltOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { healthReportAPI } from '../../mock/api.js'
import ReportSummary from '../../components/report/ReportSummary.vue'
import InsightCard from '../../components/report/InsightCard.vue'
import VirtualReportList from '../../components/report/VirtualReportList.vue'
import OptimizedChart from '../../components/charts/OptimizedChart.vue'
import HealthHeatmap from '../../components/charts/HealthHeatmap.vue'
import HealthRadarChart from '../../components/charts/HealthRadarChart.vue'
import ChatIntegration from '../../components/report/ChatIntegration.vue'
import ReportChatModal from '../../components/report/ReportChatModal.vue'

// 响应式数据
const reports = ref([])
const currentReport = ref(null)
const selectedReportType = ref('monthly')
const generating = ref(false)
const loading = ref(false)

// 性能相关
const chartPerformanceData = ref(new Map())

// 对话相关
const showChatModal = ref(false)
const chatContext = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
// const chatLoading = ref(false) // 暂时未使用
const currentSessionId = ref(null)

// 数据源方法
const fetchReportsData = async (params) => {
  try {
    const response = await healthReportAPI.getHealthReports(params)
    return response
  } catch (error) {
    console.error('获取报告数据失败:', error)
    throw error
  }
}

const getWeightDataSource = async (timeRange) => {
  try {
    const response = await healthReportAPI.getHealthMetricsTimeSeries({
      metric_type: 'weight',
      ...timeRange
    })
    return response
  } catch (error) {
    console.error('获取体重数据失败:', error)
    throw error
  }
}

const getExerciseDataSource = async (timeRange) => {
  try {
    const response = await healthReportAPI.getHealthMetricsTimeSeries({
      metric_type: 'exercise_duration',
      ...timeRange
    })
    return response
  } catch (error) {
    console.error('获取运动数据失败:', error)
    throw error
  }
}

// 方法
const handleReportSelect = (report) => {
  console.log('报告选择:', report)
}

const handleBatchAction = (data) => {
  console.log('批量操作:', data)
  if (data.action === 'export') {
    message.success(`批量导出 ${data.ids.length} 个报告`)
  } else if (data.action === 'delete') {
    message.success(`批量删除 ${data.ids.length} 个报告`)
  }
}

const handleDataLoaded = (data) => {
  console.log('图表数据加载完成:', data)
  chartPerformanceData.value.set(Date.now(), data)
}

const handleGenerateReport = async () => {
  generating.value = true
  try {
    const response = await healthReportAPI.generateHealthReport({
      report_type: selectedReportType.value
    })
    
    message.success('健康报告生成成功！')
    
    // 添加到报告列表
    reports.value.unshift(response.data)
    
    // 自动打开新生成的报告
    currentReport.value = response.data
  } catch (error) {
    console.error("生成报告失败:", error)
    message.error('生成报告失败，请稍后重试。')
  } finally {
    generating.value = false
  }
}

const handleSelectReport = (report) => {
  currentReport.value = report
}

const handleBackToList = () => {
  currentReport.value = null
}

const handleReportTypeChange = (type) => {
  selectedReportType.value = type
}

// 移除未使用的函数

// 图表交互处理
const handleChartInteraction = (data) => {
  if (data.type === 'chat') {
    // 打开聊天对话
    openChatModal({
      title: `关于${data.metric || '健康数据'}的分析`,
      description: '让我们深入分析这个趋势',
      sessionId: data.sessionId,
      initialMessage: data.analysis
    })
  } else {
    // 其他图表点击事件
    console.log('图表交互:', data)
  }
}

// const handleChartAnalyze = (data) => {
//   message.info('正在为您生成深度分析...')
//   // 这里可以触发更详细的分析
// }

const handlePatternAnalysis = () => {
  message.info('正在分析您的睡眠模式...')
  // 这里可以触发模式分析
}

const handleBalanceAnalysis = () => {
  message.info('正在生成健康平衡分析...')
  // 这里可以触发平衡分析
}

// 洞察交互处理
const handleInsightClick = (insight) => {
  // 滚动到对应的洞察卡片
  const element = document.querySelector(`[data-insight-id="${insight.insight_id}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const handleInsightDiscuss = (data) => {
  openChatModal({
    title: data.insight.title,
    description: '让我们深入讨论这个健康洞察',
    sessionId: data.sessionId,
    initialMessage: data.initialMessage
  })
}

const handleInsightAdjustPlan = () => {
  message.info('正在为您调整健康计划...')
  // 这里可以触发计划调整
}

const handleInsightShare = (data) => {
  // 分享洞察
  navigator.clipboard.writeText(`${data.title}\n\n${data.content}`)
  message.success('洞察内容已复制到剪贴板')
}

const handleInsightSave = () => {
  message.success('洞察已收藏')
}

const handleInsightFeedback = () => {
  message.success('感谢您的反馈')
}

// 对话处理
const openChatModal = (context) => {
  chatContext.value = context
  currentSessionId.value = context.sessionId
  showChatModal.value = true
  
  // 如果有初始消息，添加到对话中
  if (context.initialMessage) {
    chatMessages.value = [
      {
        id: Date.now(),
        role: 'assistant',
        content: context.initialMessage,
        timestamp: new Date().toISOString()
      }
    ]
  } else {
    chatMessages.value = []
  }
}

const handleCloseChatModal = () => {
  showChatModal.value = false
  chatContext.value = null
  chatMessages.value = []
  chatInput.value = ''
  currentSessionId.value = null
}

const handleMessageSent = (message) => {
  // Can optionally track sent messages here if needed
  console.log('Message sent from modal:', message);
}

// 其他操作
const handleDiscussReport = (report) => {
  openChatModal({
    title: `关于${report.title}的讨论`,
    description: '让我们深入分析您的健康报告',
    sessionId: null
  })
}

const handleGoalAdjust = (goal) => {
  message.info(`正在调整${goal.description}...`)
}

const handleShareReport = () => {
  message.success('报告分享链接已复制')
}

const handleExportReport = () => {
  message.success('报告导出成功')
}

// 聊天集成处理
const handleChatStarted = () => {
  console.log('聊天已启动')
}

const handlePlanUpdated = (data) => {
  console.log('计划已更新:', data)
  message.success(`健康计划已${data.type === 'replan' ? '重新制定' : '微调'}`)
}

const handleContextChanged = (context) => {
  console.log('聊天上下文变更:', context)
}

// 生命周期
onMounted(async () => {
  loading.value = true
  // 初始化时不需要获取报告列表，由VirtualReportList组件处理
})
</script>

<style scoped>
/* 使用新的aura设计系统，移除自定义页面样式 */

/* 报告列表样式已移至VirtualReportList组件 */

.report-score {
  text-align: center;
  margin-bottom: 16px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
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

.score-label {
  font-size: 12px;
  color: #8c8c8c;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8c8c8c;
}

.report-status {
  text-align: center;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-completed {
  color: #52c41a;
  background: #f6ffed;
}

.status-generating {
  color: #1890ff;
  background: #e6f7ff;
}

.status-failed {
  color: #ff4d4f;
  background: #fff2f0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.detail-actions {
  display: flex;
  gap: 12px;
}

.charts-section {
  margin-bottom: 32px;
}

.charts-section h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-item.full-width {
  grid-column: 1 / -1;
}

.insights-section h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-context {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 16px;
}

.context-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.context-desc {
  font-size: 12px;
  color: #8c8c8c;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.chat-message {
  margin-bottom: 16px;
}

.chat-message.user {
  text-align: right;
}

.chat-message.assistant {
  text-align: left;
}

.message-content {
  display: inline-block;
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.chat-message.user .message-content {
  background: #1890ff;
  color: white;
}

.chat-message.assistant .message-content {
  background: #f5f5f5;
  color: #262626;
}

.message-time {
  font-size: 11px;
  color: #8c8c8c;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  gap: 12px;
  padding-top: 16px;
}

.chat-input .ant-input {
  flex: 1;
}
</style>
