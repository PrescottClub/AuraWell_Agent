<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-container">
      <!-- 头像 -->
      <div class="avatar-container">
        <a-avatar :size="40" :src="avatarSrc" :style="avatarStyle">
          {{ avatarText }}
        </a-avatar>
      </div>
      
      <!-- 消息内容 -->
      <div class="message-content">
        <!-- 发送者名称和时间 -->
        <div class="message-header">
          <span class="sender-name">{{ senderName }}</span>
          <span class="message-time">{{ formattedTime }}</span>
        </div>
        
        <!-- 🆕 新增: 步骤指示器 -->
        <div v-if="stepDelivery && enableMcpFeatures" class="step-indicator">
          <div class="step-info">
            <a-progress 
              :percent="(stepDelivery.current_step / stepDelivery.total_steps) * 100"
              :show-info="false"
              size="small"
              stroke-color="#52c41a"
            />
            <span class="step-text">
              步骤 {{ stepDelivery.current_step }}/{{ stepDelivery.total_steps }}: 
              {{ stepDelivery.step_title }}
            </span>
          </div>
        </div>
        
        <!-- 消息文本 -->
        <div class="message-text" v-html="formattedMessage"></div>

        <!-- 🆕 新增: 计算数据卡片 -->
        <div v-if="hasCalculatorData && enableMcpFeatures" class="calculator-data-section">
          <h4 class="section-title">📊 精确数据分析</h4>
          <div class="health-metrics-grid">
            <div 
              v-for="(value, key) in mcpData.calculatorData" 
              :key="key"
              class="metric-card"
            >
              <div class="metric-value">{{ formatMetricValue(value) }}</div>
              <div class="metric-label">{{ getMetricLabel(key) }}</div>
            </div>
          </div>
        </div>

        <!-- 🆕 新增: 图表嵌入区域 -->
        <div v-if="hasChartUrls && enableMcpFeatures" class="charts-section">
          <h4 class="section-title">📈 数据可视化</h4>
          <div class="charts-container">
            <div 
              v-for="(chartUrl, index) in mcpData.chartUrls" 
              :key="index"
              class="chart-frame"
            >
              <iframe 
                :src="chartUrl"
                class="embedded-chart"
                frameborder="0"
                @load="onChartLoad"
              ></iframe>
            </div>
          </div>
        </div>

        <!-- 🆕 新增: 科学依据面板 -->
        <div v-if="hasResearchEvidence && enableMcpFeatures" class="research-evidence-section">
          <h4 class="section-title">🔬 科学依据</h4>
          <div class="evidence-list">
            <a-card
              v-for="(evidence, index) in mcpData.researchEvidence"
              :key="index"
              size="small"
              class="evidence-card"
            >
              <template #title>
                <div class="evidence-header">
                  <span class="evidence-title">{{ evidence.title }}</span>
                  <a-tag 
                    v-if="evidence.credibility" 
                    :color="getCredibilityColor(evidence.credibility)"
                    class="credibility-tag"
                  >
                    可信度: {{ evidence.credibility }}%
                  </a-tag>
                </div>
              </template>
              <p class="evidence-content">{{ evidence.summary || evidence.content }}</p>
              <div class="evidence-actions">
                <a-button 
                  type="link" 
                  size="small"
                  @click="openResearchLink(evidence.url)"
                >
                  查看研究原文
                </a-button>
              </div>
            </a-card>
          </div>
        </div>

        <!-- 🆕 新增: 个性化面板 -->
        <UserPersonalizationPanel
          v-if="hasUserProfile && enableMcpFeatures"
          :user-profile="mcpData.userProfile"
          :personalization-score="getPersonalizationScore()"
        />

        <!-- 🆕 新增: 加载状态指示器 -->
        <div v-if="isLoading && enableMcpFeatures" class="loading-section">
          <LoadingIndicator 
            :type="loadingType"
            :text="loadingText"
            size="medium"
          />
        </div>

        <!-- RAG检索结果 -->
        <div v-if="message.type === 'rag_results' && message.ragResults && message.ragResults.length > 0" class="rag-results-container">
          <h4>📚 相关文档</h4>
          <div class="rag-results">
            <a-card
              v-for="(doc, index) in message.ragResults"
              :key="index"
              size="small"
              class="rag-result-card"
            >
              <template #title>
                <div class="rag-result-header">
                  <span class="rag-result-title">{{ doc.title || `文档 ${index + 1}` }}</span>
                  <a-tag v-if="doc.score" color="blue" size="small">
                    相似度: {{ (doc.score * 100).toFixed(1) }}%
                  </a-tag>
                </div>
              </template>
              <div class="rag-result-content">
                <p class="rag-result-text">{{ doc.content || doc.text }}</p>
                <div v-if="doc.metadata" class="rag-result-metadata">
                  <a-tag v-if="doc.metadata.source" size="small" color="green">
                    来源: {{ doc.metadata.source }}
                  </a-tag>
                  <a-tag v-if="doc.metadata.category" size="small" color="orange">
                    分类: {{ doc.metadata.category }}
                  </a-tag>
                </div>
              </div>
            </a-card>
          </div>
        </div>

        <!-- 健康建议卡片 -->
        <div v-if="message.suggestions && message.suggestions.length > 0" class="suggestions-container">
          <h4>💡 个性化建议</h4>
          <div class="suggestion-cards">
            <a-card 
              v-for="(suggestion, index) in message.suggestions" 
              :key="index"
              size="small"
              class="suggestion-card"
            >
              <template #title>
                <span class="suggestion-title">{{ suggestion.title }}</span>
              </template>
              <p class="suggestion-content">{{ suggestion.content }}</p>
              <div v-if="suggestion.action" class="suggestion-action">
                <a-button type="link" size="small" @click="handleSuggestionAction(suggestion.action)">
                  {{ suggestion.actionText || '了解更多' }}
                </a-button>
              </div>
            </a-card>
          </div>
        </div>
        
        <!-- 快速回复按钮 -->
        <div v-if="message.quickReplies && message.quickReplies.length > 0" class="quick-replies">
          <a-button 
            v-for="(reply, index) in message.quickReplies" 
            :key="index"
            size="small"
            type="default"
            class="quick-reply-btn"
            @click="handleQuickReply(reply)"
          >
            {{ reply.text }}
          </a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { UserOutlined, RobotOutlined } from '@ant-design/icons-vue'
import UserPersonalizationPanel from '@/components/personalization/UserPersonalizationPanel.vue'
import LoadingIndicator from '@/components/ui/LoadingIndicator.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  // 🆕 新增: 是否显示MCP增强功能
  enableMcpFeatures: {
    type: Boolean,
    default: true
  },
  // 🆕 新增: 加载状态
  isLoading: {
    type: Boolean,
    default: false
  },
  // 🆕 新增: 加载类型
  loadingType: {
    type: String,
    default: 'mcp'
  },
  // 🆕 新增: 加载文本
  loadingText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['quick-reply', 'suggestion-action'])

// 计算属性
const messageClass = computed(() => ({
  'user-message': props.message.sender === 'user',
  'agent-message': props.message.sender === 'agent'
}))

const senderName = computed(() => {
  return props.message.sender === 'user' ? '我' : 'AuraWell 健康助手'
})

const avatarSrc = computed(() => {
  return props.message.sender === 'user' ? null : '/logo.png'
})

const avatarText = computed(() => {
  return props.message.sender === 'user' ? '我' : 'AI'
})

const avatarStyle = computed(() => ({
  backgroundColor: props.message.sender === 'user' ? '#1890ff' : '#52c41a'
}))

const formattedTime = computed(() => {
  const date = new Date(props.message.timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
})

const formattedMessage = computed(() => {
  let text = props.message.content || props.message.text || ''
  
  // 简单的markdown渲染
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>')
  text = text.replace(/\n/g, '<br>')
  
  return text
})

// 🆕 新增MCP数据计算属性
const mcpData = computed(() => props.message.mcpData || {})

const hasCalculatorData = computed(() => 
  mcpData.value.calculatorData && Object.keys(mcpData.value.calculatorData).length > 0
)

const hasChartUrls = computed(() => 
  mcpData.value.chartUrls && mcpData.value.chartUrls.length > 0
)

const hasResearchEvidence = computed(() => 
  mcpData.value.researchEvidence && mcpData.value.researchEvidence.length > 0
)

const stepDelivery = computed(() => mcpData.value.stepDelivery)

const hasUserProfile = computed(() => 
  mcpData.value.userProfile && Object.keys(mcpData.value.userProfile).length > 0
)

// 🆕 新增方法
const formatMetricValue = (value) => {
  if (typeof value === 'number') {
    return value.toFixed(1)
  }
  return value
}

const getMetricLabel = (key) => {
  const labels = {
    bmi: 'BMI指数',
    bmr: 'BMR (卡路里/天)',
    tdee: 'TDEE (卡路里/天)',
    body_fat: '体脂率 (%)',
    muscle_mass: '肌肉量 (kg)'
  }
  return labels[key] || key.toUpperCase()
}

const getCredibilityColor = (credibility) => {
  if (credibility >= 90) return 'green'
  if (credibility >= 80) return 'blue'
  if (credibility >= 70) return 'orange'
  return 'red'
}

const onChartLoad = () => {
  console.log('Chart loaded successfully')
}

const openResearchLink = (url) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 🆕 新增: 计算个性化程度
const getPersonalizationScore = () => {
  const profile = mcpData.value.userProfile
  if (!profile) return 0
  
  let score = 0
  if (profile.healthLevel) score += 25
  if (profile.riskFactors && profile.riskFactors.length > 0) score += 25
  if (profile.strengths && profile.strengths.length > 0) score += 25
  if (profile.recommendations && profile.recommendations.length > 0) score += 25
  
  return score
}

// 事件处理
const handleQuickReply = (reply) => {
  emit('quick-reply', reply)
}

const handleSuggestionAction = (action) => {
  emit('suggestion-action', action)
}
</script>

<style scoped>
.chat-message {
  margin-bottom: 16px;
  padding: 0 16px;
}

.message-container {
  display: flex;
  gap: 12px;
}

.user-message .message-container {
  flex-direction: row-reverse;
}

.avatar-container {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #666;
}

.user-message .message-header {
  justify-content: flex-end;
}

.sender-name {
  font-weight: 500;
}

.message-time {
  color: #999;
}

.message-text {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
}

.user-message .message-text {
  background: #1890ff;
  color: white;
}

.suggestions-container {
  margin-top: 12px;
}

.suggestions-container h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #52c41a;
}

.suggestion-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-card {
  border-left: 3px solid #52c41a;
}

.suggestion-title {
  font-size: 13px;
  font-weight: 500;
}

.suggestion-content {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.suggestion-action {
  margin-top: 8px;
}

.quick-replies {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-reply-btn {
  border-radius: 16px;
  font-size: 12px;
}

.user-message .quick-replies {
  justify-content: flex-end;
}

/* RAG结果样式 */
.rag-results-container {
  margin-top: 12px;
}

.rag-results-container h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #1890ff;
  display: flex;
  align-items: center;
  gap: 4px;
}

.rag-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rag-result-card {
  border-left: 3px solid #1890ff;
  background: #f8f9ff;
}

.rag-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.rag-result-title {
  font-size: 13px;
  font-weight: 500;
  color: #1890ff;
}

.rag-result-content {
  margin: 0;
}

.rag-result-text {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #333;
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.rag-result-metadata {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 🆕 MCP元素进入动画 */
.mcp-section-enter-active {
  animation: fadeInUp 0.6s ease-out;
}

.mcp-section-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 🆕 新增: 步骤指示器样式 */
.step-indicator {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border-left: 4px solid #1890ff;
  animation: fadeInUp 0.6s ease-out;
}

.step-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-text {
  font-size: 12px;
  color: #1890ff;
  font-weight: 500;
}

/* 🆕 新增: 计算数据卡片样式 */
.calculator-data-section {
  margin: 16px 0;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 4px;
}

.health-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.metric-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 12px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.metric-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.metric-card:hover::before {
  left: 100%;
}

.metric-card:active {
  transform: translateY(-2px) scale(1.01);
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  opacity: 0.9;
}

/* 🆕 新增: 图表嵌入样式 */
.charts-section {
  margin: 16px 0;
  animation: fadeInUp 1s ease-out 0.4s both;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-frame {
  width: 100%;
  min-height: 300px;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #d9d9d9;
  transition: all 0.3s ease;
  position: relative;
}

.chart-frame:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  border-color: #1890ff;
}

.embedded-chart {
  width: 100%;
  height: 300px;
  min-height: 300px;
}

/* 🆕 新增: 科学依据样式 */
.research-evidence-section {
  margin: 16px 0;
  animation: fadeInUp 1.2s ease-out 0.6s both;
}

.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evidence-card {
  border-left: 4px solid #52c41a;
  background: #f6ffed;
  transition: all 0.3s ease;
  cursor: pointer;
}

.evidence-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.15);
  background: #f0fff0;
}

.evidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.evidence-title {
  font-weight: 500;
  flex: 1;
}

.credibility-tag {
  flex-shrink: 0;
}

.evidence-content {
  margin: 8px 0;
  color: #595959;
  line-height: 1.5;
}

.evidence-actions {
  margin-top: 8px;
}

/* 📱 手机浏览器适配 */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }

  .health-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .metric-card {
    padding: 12px 8px;
  }

  .metric-value {
    font-size: 16px;
  }

  .metric-label {
    font-size: 11px;
  }

  .charts-container {
    gap: 12px;
  }

  .embedded-chart {
    height: 250px;
    min-height: 250px;
  }

  .evidence-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .section-title {
    font-size: 13px;
  }
}

/* 📱 手机竖屏优化 */
@media (max-width: 480px) {
  .health-metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .embedded-chart {
    height: 200px;
    min-height: 200px;
  }

  .metric-card {
    padding: 10px 6px;
  }

  .metric-value {
    font-size: 14px;
  }
}
</style>
