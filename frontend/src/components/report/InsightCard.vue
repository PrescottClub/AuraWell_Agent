<template>
  <div 
    class="insight-card" 
    :class="severityClass"
    v-motion
    :initial="{ y: 0, boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }"
    :hovered="{ y: -5, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)' }"
  >
    <div class="insight-header">
      <div class="insight-icon">
        <component :is="iconComponent" :style="{ color: iconColor }" />
      </div>
      <div class="insight-meta">
        <h4 class="insight-title">{{ insight.title }}</h4>
        <div class="insight-category">{{ categoryLabel }}</div>
      </div>
      <div class="insight-confidence">
        <a-tooltip :title="`AI分析置信度: ${(insight.confidence * 100).toFixed(0)}%`">
          <div class="confidence-bar">
            <div 
              class="confidence-fill" 
              :style="{ width: (insight.confidence * 100) + '%' }"
            ></div>
          </div>
        </a-tooltip>
      </div>
    </div>
    
    <div class="insight-content">
      <p class="insight-text">{{ insight.content }}</p>
      
      <div v-if="insight.recommendations?.length" class="insight-recommendations">
        <h5>个性化建议:</h5>
        <ul>
          <li v-for="(rec, index) in insight.recommendations" :key="index">
            {{ rec }}
          </li>
        </ul>
      </div>
      
      <div v-if="showReferences && insight.medical_references?.length" class="insight-references">
        <a-button 
          type="text" 
          size="small"
          @click="toggleReferences"
          class="references-toggle"
        >
          <BookOutlined />
          医学参考 ({{ insight.medical_references.length }})
          <DownOutlined v-if="!referencesExpanded" />
          <UpOutlined v-else />
        </a-button>
        
        <div v-show="referencesExpanded" class="references-list">
          <div 
            v-for="(ref, index) in insight.medical_references" 
            :key="index"
            class="reference-item"
          >
            <QuestionCircleOutlined class="reference-icon" />
            <span class="reference-text">{{ ref }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="insight-actions">
      <a-button 
        type="text" 
        size="small"
        @click="handleDiscuss"
        :loading="discussing"
      >
        <MessageOutlined />
        深入讨论
      </a-button>
      
      <a-button 
        type="text" 
        size="small"
        @click="handleAdjustPlan"
        :loading="adjusting"
      >
        <EditOutlined />
        调整计划
      </a-button>
      
      <a-dropdown>
        <a-button type="text" size="small">
          <MoreOutlined />
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item @click="handleShare">
              <ShareAltOutlined />
              分享洞察
            </a-menu-item>
            <a-menu-item @click="handleSave">
              <StarOutlined />
              收藏
            </a-menu-item>
            <a-menu-item @click="handleFeedback">
              <LikeOutlined />
              反馈
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  BookOutlined, 
  DownOutlined, 
  UpOutlined, 
  MessageOutlined,
  EditOutlined,
  MoreOutlined,
  ShareAltOutlined,
  StarOutlined,
  LikeOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { healthReportAPI } from '../../mock/api.js'

// Props
const props = defineProps({
  insight: {
    type: Object,
    required: true
  },
  showReferences: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['discuss', 'adjust-plan', 'share', 'save', 'feedback'])

// 响应式数据
const referencesExpanded = ref(false)
const discussing = ref(false)
const adjusting = ref(false)

// 计算属性
const severityClass = computed(() => {
  return `insight-${props.insight.severity || 'info'}`
})

const categoryLabel = computed(() => {
  const labels = {
    weight_management: '体重管理',
    sleep_quality: '睡眠质量',
    exercise_performance: '运动表现',
    nutrition: '营养状况',
    mental_health: '心理健康',
    lifestyle: '生活方式',
    general: '综合分析'
  }
  return labels[props.insight.category] || '健康分析'
})

const iconComponent = computed(() => {
  switch (props.insight.severity) {
    case 'positive':
      return CheckCircleOutlined
    case 'warning':
      return WarningOutlined
    case 'critical':
      return ExclamationCircleOutlined
    default:
      return InfoCircleOutlined
  }
})

const iconColor = computed(() => {
  switch (props.insight.severity) {
    case 'positive':
      return '#52c41a'
    case 'warning':
      return '#faad14'
    case 'critical':
      return '#ff4d4f'
    default:
      return '#1890ff'
  }
})

// 方法
const toggleReferences = () => {
  referencesExpanded.value = !referencesExpanded.value
}

const handleDiscuss = async () => {
  discussing.value = true
  try {
    // 创建基于洞察的对话
    const chatContext = {
      type: 'insight_discussion',
      insight: props.insight,
      category: props.insight.category,
      title: props.insight.title
    }
    
    const response = await healthReportAPI.triggerReportChat('insight', chatContext)
    
    emit('discuss', {
      sessionId: response.data.session_id,
      insight: props.insight,
      initialMessage: response.data.initial_analysis
    })
    
    message.success('已为您启动深入讨论')
  } catch (error) {
    console.error('启动讨论失败:', error)
    message.error('启动讨论失败')
  } finally {
    discussing.value = false
  }
}

const handleAdjustPlan = async () => {
  adjusting.value = true
  try {
    // 基于洞察调整健康计划
    const adjustmentData = {
      insight_id: props.insight.insight_id,
      category: props.insight.category,
      recommendations: props.insight.recommendations,
      severity: props.insight.severity
    }
    
    emit('adjust-plan', adjustmentData)
    message.success('正在为您调整健康计划...')
  } catch (error) {
    console.error('调整计划失败:', error)
    message.error('调整计划失败')
  } finally {
    adjusting.value = false
  }
}

const handleShare = () => {
  // 分享洞察
  const shareData = {
    title: props.insight.title,
    content: props.insight.content,
    category: props.insight.category
  }
  
  emit('share', shareData)
  message.success('洞察已复制到剪贴板')
}

const handleSave = () => {
  // 收藏洞察
  emit('save', props.insight)
  message.success('洞察已收藏')
}

const handleFeedback = () => {
  // 反馈洞察质量
  emit('feedback', {
    insight_id: props.insight.insight_id,
    type: 'helpful'
  })
  message.success('感谢您的反馈')
}
</script>

<style scoped>
.insight-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #1890ff;
  transition: all 0.3s ease;
}

.insight-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.insight-positive {
  border-left-color: #52c41a;
}

.insight-warning {
  border-left-color: #faad14;
}

.insight-critical {
  border-left-color: #ff4d4f;
}

.insight-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.insight-icon {
  font-size: 20px;
  margin-top: 2px;
}

.insight-meta {
  flex: 1;
}

.insight-title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
}

.insight-category {
  font-size: 12px;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.insight-confidence {
  width: 60px;
}

.confidence-bar {
  width: 100%;
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff4d4f 0%, #faad14 50%, #52c41a 100%);
  transition: width 0.3s ease;
}

.insight-content {
  margin-bottom: 16px;
}

.insight-text {
  margin: 0 0 16px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #595959;
}

.insight-recommendations {
  margin-bottom: 16px;
}

.insight-recommendations h5 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #262626;
}

.insight-recommendations ul {
  margin: 0;
  padding-left: 16px;
}

.insight-recommendations li {
  font-size: 13px;
  line-height: 1.5;
  color: #595959;
  margin-bottom: 4px;
}

.insight-references {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.references-toggle {
  padding: 0;
  height: auto;
  font-size: 12px;
  color: #1890ff;
}

.references-list {
  margin-top: 8px;
}

.reference-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 6px;
}

.reference-icon {
  color: #8c8c8c;
  font-size: 12px;
  margin-top: 2px;
}

.reference-text {
  font-size: 12px;
  line-height: 1.4;
  color: #595959;
}

.insight-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.insight-actions .ant-btn {
  padding: 0 8px;
  height: 28px;
  font-size: 12px;
}
</style>
