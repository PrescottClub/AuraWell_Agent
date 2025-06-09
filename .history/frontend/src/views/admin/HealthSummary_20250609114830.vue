<template>
  <div class="health-summary-container">
    <a-card class="summary-card">
      <template #title>
        <div class="card-header">
          <h2>健康信息摘要</h2>
          <div class="header-controls">
            <span class="period-info" v-if="periodInfo.start && periodInfo.end">
              {{ periodInfo.start }} 至 {{ periodInfo.end }}
            </span>
            <a-select
              v-model:value="selectedDays"
              style="width: 120px"
              @change="handleDaysChange"
            >
              <a-select-option value="7">最近7天</a-select-option>
              <a-select-option value="14">最近14天</a-select-option>
              <a-select-option value="30">最近30天</a-select-option>
            </a-select>
          </div>
        </div>
      </template>

      <a-spin :spinning="loading">
        <div v-if="error" class="error-message">
          <a-alert type="error" :message="error" />
        </div>

        <template v-else-if="healthSummary">
          <a-tabs v-model:activeKey="activeTab">
            <a-tab-pane key="activity" tab="活动数据">
              <div class="summary-grid">
                <a-card class="summary-item">
                  <template #title>步数</template>
                  <div class="value">{{ healthSummary.activity.steps || '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>距离</template>
                  <div class="value">{{ healthSummary.activity.distance_km ? `${healthSummary.activity.distance_km} km` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>消耗卡路里</template>
                  <div class="value">{{ healthSummary.activity.calories_burned ? `${healthSummary.activity.calories_burned} kcal` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>活动时间</template>
                  <div class="value">{{ healthSummary.activity.active_minutes ? `${healthSummary.activity.active_minutes} 分钟` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>运动次数</template>
                  <div class="value">{{ healthSummary.activity.exercise_sessions || 0 }} 次</div>
                </a-card>
              </div>
            </a-tab-pane>

            <a-tab-pane key="sleep" tab="睡眠数据">
              <div class="summary-grid">
                <a-card class="summary-item">
                  <template #title>总睡眠时间</template>
                  <div class="value">{{ healthSummary.sleep.total_sleep_hours ? `${healthSummary.sleep.total_sleep_hours} 小时` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>深度睡眠</template>
                  <div class="value">{{ healthSummary.sleep.deep_sleep_hours ? `${healthSummary.sleep.deep_sleep_hours} 小时` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>浅度睡眠</template>
                  <div class="value">{{ healthSummary.sleep.light_sleep_hours ? `${healthSummary.sleep.light_sleep_hours} 小时` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>REM睡眠</template>
                  <div class="value">{{ healthSummary.sleep.rem_sleep_hours ? `${healthSummary.sleep.rem_sleep_hours} 小时` : '暂无数据' }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>睡眠效率</template>
                  <div class="value">{{ healthSummary.sleep.sleep_efficiency ? `${healthSummary.sleep.sleep_efficiency}%` : '暂无数据' }}</div>
                </a-card>
              </div>
            </a-tab-pane>
          </a-tabs>

          <div class="additional-info">
            <a-card title="其他信息" class="mt-4">
              <p>平均心率: {{ healthSummary.heartRate ? `${healthSummary.heartRate} bpm` : '暂无数据' }}</p>
              <p>体重趋势: {{ healthSummary.weightTrend || '暂无数据' }}</p>
              <div class="key-insights" v-if="healthSummary.insights && healthSummary.insights.length > 0">
                <h3>关键洞察</h3>
                <ul>
                  <li v-for="(insight, index) in healthSummary.insights" :key="index">
                    {{ insight }}
                  </li>
                </ul>
              </div>
              <div v-else class="no-insights">
                <p>暂无关键洞察</p>
              </div>
            </a-card>
          </div>
        </template>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useHealthStore } from '../../stores/health'

const healthStore = useHealthStore()
const selectedDays = ref('7')
const activeTab = ref('activity')

const { healthSummary, periodInfo, loading, error } = healthStore

const handleDaysChange = (value) => {
  healthStore.fetchHealthSummary(parseInt(value))
}

onMounted(() => {
  healthStore.fetchHealthSummary(7)
})
</script>

<style scoped>
.health-summary-container {
  padding: 24px;
}

.summary-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.period-info {
  color: #666;
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.summary-item {
  text-align: center;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.error-message {
  margin: 16px 0;
}

.additional-info {
  margin-top: 24px;
}

.key-insights {
  margin-top: 16px;
}

.key-insights h3 {
  margin-bottom: 8px;
}

.key-insights ul {
  padding-left: 20px;
}

.no-insights {
  color: #999;
  text-align: center;
  padding: 16px;
}

.mt-4 {
  margin-top: 16px;
}
</style> 