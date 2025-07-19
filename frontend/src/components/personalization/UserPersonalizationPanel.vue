<template>
  <div 
    v-motion-slide-right="{
      initial: { x: 30, opacity: 0 },
      visible: { 
        x: 0, 
        opacity: 1,
        transition: {
          delay: 900,
          duration: 600
        }
      }
    }"
    class="personalization-panel"
  >
    <div class="panel-header">
      <div class="header-content">
        <h4 class="panel-title">🎯 个性化健康画像</h4>
        <div class="personalization-score">
          <span class="score-label">个性化程度</span>
          <div class="score-bar">
            <div 
              class="score-fill" 
              :style="{ width: `${personalizationScore}%` }"
            ></div>
          </div>
          <span class="score-value">{{ personalizationScore }}%</span>
        </div>
      </div>
    </div>

    <div class="panel-content">
      <!-- 用户基本信息 -->
      <div v-if="userProfile.basicInfo" class="info-section">
        <h5 class="section-title">👤 基本信息</h5>
        <div class="info-grid">
          <div 
            v-for="(value, key) in userProfile.basicInfo" 
            :key="key"
            v-motion-pop="{
              initial: { scale: 0, opacity: 0 },
              visible: { 
                scale: 1, 
                opacity: 1,
                transition: {
                  type: 'spring',
                  delay: 1000 + (Object.keys(userProfile.basicInfo).indexOf(key) * 100)
                }
              }
            }"
            class="info-item"
          >
            <span class="info-label">{{ getInfoLabel(key) }}</span>
            <span class="info-value">{{ formatInfoValue(key, value) }}</span>
          </div>
        </div>
      </div>

      <!-- 健康水平评估 -->
      <div v-if="userProfile.healthLevel" class="health-level-section">
        <h5 class="section-title">📊 健康水平</h5>
        <div 
          v-motion-fade-visible="{
            initial: { opacity: 0, y: 20 },
            visible: { 
              opacity: 1, 
              y: 0,
              transition: { delay: 1200 }
            }
          }"
          class="health-level-card"
          :class="getHealthLevelClass(userProfile.healthLevel.overall)"
        >
          <div class="level-content">
            <div class="level-score">
              {{ userProfile.healthLevel.overall }}
            </div>
            <div class="level-details">
              <div class="level-text">{{ getHealthLevelText(userProfile.healthLevel.overall) }}</div>
              <div v-if="userProfile.healthLevel.breakdown" class="level-breakdown">
                <div 
                  v-for="(score, category) in userProfile.healthLevel.breakdown" 
                  :key="category"
                  class="breakdown-item"
                >
                  <span class="breakdown-label">{{ getCategoryLabel(category) }}</span>
                  <div class="breakdown-bar">
                    <div 
                      class="breakdown-fill" 
                      :style="{ width: `${score}%` }"
                      :class="getScoreClass(score)"
                    ></div>
                  </div>
                  <span class="breakdown-value">{{ score }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 风险因子 -->
      <div v-if="userProfile.riskFactors && userProfile.riskFactors.length > 0" class="risk-factors-section">
        <h5 class="section-title">⚠️ 风险因子</h5>
        <div class="risk-factors">
          <div 
            v-for="(risk, index) in userProfile.riskFactors" 
            :key="index"
            v-motion-slide-left="{
              initial: { x: -20, opacity: 0 },
              visible: { 
                x: 0, 
                opacity: 1,
                transition: { delay: 1400 + (index * 100) }
              }
            }"
            class="risk-factor"
            :class="getRiskLevelClass(risk.level)"
          >
            <div class="risk-icon">{{ getRiskIcon(risk.category) }}</div>
            <div class="risk-content">
              <div class="risk-name">{{ risk.name }}</div>
              <div class="risk-description">{{ risk.description }}</div>
            </div>
            <div class="risk-level">{{ risk.level }}</div>
          </div>
        </div>
      </div>

      <!-- 健康优势 -->
      <div v-if="userProfile.strengths && userProfile.strengths.length > 0" class="strengths-section">
        <h5 class="section-title">💪 健康优势</h5>
        <div class="strengths">
          <div 
            v-for="(strength, index) in userProfile.strengths" 
            :key="index"
            v-motion-bounce-visible="{
              initial: { scale: 0, opacity: 0 },
              visible: { 
                scale: 1, 
                opacity: 1,
                transition: {
                  type: 'spring',
                  delay: 1600 + (index * 80)
                }
              }
            }"
            class="strength-item"
          >
            <div class="strength-icon">✨</div>
            <div class="strength-text">{{ strength }}</div>
          </div>
        </div>
      </div>

      <!-- 个性化建议 -->
      <div v-if="userProfile.recommendations && userProfile.recommendations.length > 0" class="recommendations-section">
        <h5 class="section-title">🔧 个性化建议</h5>
        <div class="recommendations">
          <a-card 
            v-for="(rec, index) in userProfile.recommendations" 
            :key="index"
            v-motion-slide-up="{
              initial: { y: 30, opacity: 0 },
              visible: { 
                y: 0, 
                opacity: 1,
                transition: { delay: 1800 + (index * 150) }
              }
            }"
            size="small"
            class="recommendation-card"
          >
            <template #title>
              <div class="rec-header">
                <span class="rec-category">{{ rec.category }}</span>
                <span class="rec-priority" :class="getPriorityClass(rec.priority)">
                  {{ rec.priority }}
                </span>
              </div>
            </template>
            <div class="rec-content">
              <p class="rec-text">{{ rec.content }}</p>
              <div v-if="rec.expectedOutcome" class="rec-outcome">
                <strong>预期效果:</strong> {{ rec.expectedOutcome }}
              </div>
            </div>
          </a-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  userProfile: {
    type: Object,
    required: true
  },
  personalizationScore: {
    type: Number,
    default: 0
  }
})

// 信息标签映射
const getInfoLabel = (key) => {
  const labels = {
    age: '年龄',
    gender: '性别',
    height: '身高',
    weight: '体重',
    activityLevel: '运动水平',
    goals: '健康目标',
    medicalHistory: '病史'
  }
  return labels[key] || key
}

// 格式化信息值
const formatInfoValue = (key, value) => {
  if (key === 'height') return `${value} cm`
  if (key === 'weight') return `${value} kg`
  if (key === 'age') return `${value} 岁`
  if (Array.isArray(value)) return value.join(', ')
  return value
}

// 健康水平样式
const getHealthLevelClass = (level) => {
  if (level >= 90) return 'level-excellent'
  if (level >= 80) return 'level-good'
  if (level >= 70) return 'level-normal'
  if (level >= 60) return 'level-warning'
  return 'level-danger'
}

// 健康水平文本
const getHealthLevelText = (level) => {
  if (level >= 90) return '优秀'
  if (level >= 80) return '良好'
  if (level >= 70) return '正常'
  if (level >= 60) return '需要注意'
  return '需要改善'
}

// 分类标签
const getCategoryLabel = (category) => {
  const labels = {
    physical: '身体',
    mental: '心理',
    nutrition: '营养',
    sleep: '睡眠',
    exercise: '运动'
  }
  return labels[category] || category
}

// 分数样式
const getScoreClass = (score) => {
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-normal'
  return 'score-warning'
}

// 风险等级样式
const getRiskLevelClass = (level) => {
  if (level === 'high') return 'risk-high'
  if (level === 'medium') return 'risk-medium'
  return 'risk-low'
}

// 风险图标
const getRiskIcon = (category) => {
  const icons = {
    cardiovascular: '❤️',
    diabetes: '🩸',
    nutrition: '🥗',
    exercise: '🏃',
    sleep: '😴',
    stress: '😰'
  }
  return icons[category] || '⚠️'
}

// 优先级样式
const getPriorityClass = (priority) => {
  if (priority === 'high') return 'priority-high'
  if (priority === 'medium') return 'priority-medium'
  return 'priority-low'
}
</script>

<style scoped>
.personalization-panel {
  margin: 16px 0;
  background: linear-gradient(135deg,
    theme('colors.gray.50') 0%,
    theme('colors.blue.50') 50%,
    theme('colors.purple.50') 100%
  );
  border-radius: var(--border-radius-card);
  border: 1px solid theme('colors.gray.200');
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.panel-header {
  padding: 20px;
  background: theme('colors.primary.500');
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.personalization-score {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.score-bar {
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
  border-radius: 3px;
  transition: width 1s ease-out;
}

.score-value {
  font-weight: 600;
  min-width: 35px;
}

.panel-content {
  padding: 20px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid theme('colors.gray.200');
  transition: all 0.3s ease;
}

.info-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.info-label {
  font-size: 12px;
  color: #666;
}

.info-value {
  font-size: 12px;
  font-weight: 500;
  color: #262626;
}

.health-level-section {
  margin-bottom: 24px;
}

.health-level-card {
  padding: 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.level-excellent {
  background: linear-gradient(135deg, theme('colors.green.100') 0%, theme('colors.green.200') 100%);
  border: 2px solid theme('colors.green.300');
}

.level-good {
  background: linear-gradient(135deg, theme('colors.blue.100') 0%, theme('colors.blue.200') 100%);
  border: 2px solid theme('colors.blue.300');
}

.level-normal {
  background: linear-gradient(135deg, theme('colors.yellow.100') 0%, theme('colors.yellow.200') 100%);
  border: 2px solid theme('colors.yellow.300');
}

.level-warning {
  background: linear-gradient(135deg, theme('colors.orange.100') 0%, theme('colors.orange.200') 100%);
  border: 2px solid theme('colors.orange.300');
}

.level-danger {
  background: linear-gradient(135deg, theme('colors.red.100') 0%, theme('colors.red.200') 100%);
  border: 2px solid theme('colors.red.300');
}

.level-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.level-score {
  font-size: 32px;
  font-weight: bold;
  color: #262626;
}

.level-details {
  flex: 1;
}

.level-text {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #262626;
}

.level-breakdown {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.breakdown-label {
  min-width: 40px;
  color: #666;
}

.breakdown-bar {
  flex: 1;
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
}

.score-good { background: #52c41a; }
.score-normal { background: #faad14; }
.score-warning { background: #ff4d4f; }

.breakdown-value {
  min-width: 30px;
  font-weight: 500;
}

.risk-factors-section {
  margin-bottom: 24px;
}

.risk-factors {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-factor {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.risk-high {
  background: theme('colors.red.50');
  border-left: 4px solid theme('colors.red.500');
}

.risk-medium {
  background: theme('colors.orange.50');
  border-left: 4px solid theme('colors.orange.500');
}

.risk-low {
  background: theme('colors.yellow.50');
  border-left: 4px solid theme('colors.yellow.500');
}

.risk-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.risk-content {
  flex: 1;
}

.risk-name {
  font-size: 13px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 2px;
}

.risk-description {
  font-size: 11px;
  color: #666;
}

.risk-level {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.1);
}

.strengths-section {
  margin-bottom: 24px;
}

.strengths {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.strength-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, theme('colors.green.100') 0%, theme('colors.green.200') 100%);
  border-radius: 16px;
  border: 1px solid theme('colors.green.300');
  font-size: 12px;
  color: #262626;
  transition: all 0.3s ease;
}

.strength-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card);
}

.strength-icon {
  font-size: 14px;
}

.recommendations-section {
  margin-bottom: 0;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rec-category {
  font-size: 12px;
  font-weight: 500;
  color: #262626;
}

.rec-priority {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 500;
}

.priority-high {
  background: theme('colors.red.100');
  color: theme('colors.red.700');
}

.priority-medium {
  background: theme('colors.orange.100');
  color: theme('colors.orange.700');
}

.priority-low {
  background: theme('colors.green.100');
  color: theme('colors.green.700');
}

.rec-content {
  font-size: 12px;
}

.rec-text {
  margin: 0 0 8px 0;
  color: #595959;
  line-height: 1.4;
}

.rec-outcome {
  font-size: 11px;
  color: #1890ff;
  font-style: italic;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .level-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .level-score {
    font-size: 24px;
  }

  .breakdown-item {
    font-size: 11px;
  }

  .personalization-score {
    font-size: 11px;
  }

  .score-bar {
    width: 60px;
  }
}
</style>