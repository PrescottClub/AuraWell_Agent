<template>
  <div class="personalization-panel" v-if="userProfile && Object.keys(userProfile).length > 0">
    <div class="panel-header">
      <h4 class="panel-title">
        <span class="title-icon">🎯</span>
        个性化健康画像
      </h4>
      <div class="personalization-score">
        <a-progress 
          type="circle"
          :size="50"
          :percent="personalizationScore"
          :stroke-color="getScoreColor(personalizationScore)"
          :format="formatScore"
        />
        <span class="score-label">个性化程度</span>
      </div>
    </div>

    <div class="profile-content">
      <!-- 健康水平指示 -->
      <div v-if="userProfile.healthLevel" class="health-level-section">
        <div class="section-header">
          <span class="section-icon">💪</span>
          <span class="section-title">健康水平</span>
        </div>
        <a-tag 
          :color="getHealthLevelColor(userProfile.healthLevel)"
          class="health-level-tag"
        >
          {{ userProfile.healthLevel }}
        </a-tag>
      </div>

      <!-- 风险因素 -->
      <div v-if="userProfile.riskFactors && userProfile.riskFactors.length > 0" class="risk-factors-section">
        <div class="section-header">
          <span class="section-icon">⚠️</span>
          <span class="section-title">关注点</span>
        </div>
        <div class="tags-container">
          <a-tag
            v-for="(risk, index) in userProfile.riskFactors"
            :key="index"
            color="orange"
            class="risk-tag"
          >
            {{ risk }}
          </a-tag>
        </div>
      </div>

      <!-- 优势特点 -->
      <div v-if="userProfile.strengths && userProfile.strengths.length > 0" class="strengths-section">
        <div class="section-header">
          <span class="section-icon">✨</span>
          <span class="section-title">健康优势</span>
        </div>
        <div class="tags-container">
          <a-tag
            v-for="(strength, index) in userProfile.strengths"
            :key="index"
            color="green"
            class="strength-tag"
          >
            {{ strength }}
          </a-tag>
        </div>
      </div>

      <!-- 个性化建议标签 -->
      <div v-if="userProfile.recommendations && userProfile.recommendations.length > 0" class="recommendations-section">
        <div class="section-header">
          <span class="section-icon">🎯</span>
          <span class="section-title">专属建议</span>
        </div>
        <div class="recommendations-list">
          <div 
            v-for="(recommendation, index) in userProfile.recommendations"
            :key="index"
            class="recommendation-item"
          >
            <a-tag color="blue" class="recommendation-tag">
              {{ recommendation }}
            </a-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 个性化标识 -->
    <div class="personalization-badge">
      <span class="badge-text">基于您的健康画像定制</span>
      <span class="badge-icon">🔥</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  userProfile: {
    type: Object,
    default: () => ({})
  },
  // 个性化程度评分（0-100）
  personalizationScore: {
    type: Number,
    default: 85
  }
})

// 计算属性
const getScoreColor = (score) => {
  if (score >= 90) return '#52c41a'  // 绿色 - 高度个性化
  if (score >= 75) return '#1890ff'  // 蓝色 - 中度个性化
  if (score >= 60) return '#faad14'  // 黄色 - 一般个性化
  return '#f5222d'  // 红色 - 个性化不足
}

const getHealthLevelColor = (level) => {
  const levelColors = {
    '优秀': 'green',
    '良好': 'blue',
    '一般': 'orange',
    '需改善': 'red'
  }
  return levelColors[level] || 'default'
}

const formatScore = (percent) => `${percent}%`
</script>

<style scoped>
.personalization-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px;
  margin: 16px 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.personalization-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  pointer-events: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 18px;
}

.personalization-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  opacity: 0.9;
}

.profile-content {
  position: relative;
  z-index: 1;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  opacity: 0.9;
}

.health-level-section,
.risk-factors-section,
.strengths-section,
.recommendations-section {
  margin-bottom: 16px;
}

.health-level-tag {
  font-weight: 500;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.risk-tag,
.strength-tag,
.recommendation-tag {
  font-size: 12px;
  border-radius: 8px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recommendation-item {
  display: flex;
  align-items: center;
}

.personalization-badge {
  position: absolute;
  bottom: 8px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  opacity: 0.8;
}

.badge-text {
  font-style: italic;
}

.badge-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .tags-container {
    justify-content: center;
  }

  .personalization-badge {
    position: static;
    justify-content: center;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
  }
}
</style> 