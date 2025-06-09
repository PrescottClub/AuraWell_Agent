<template>
  <div class="health-summary-container">
    <a-card class="summary-card">
      <template #title>
        <div class="card-header">
          <h2>健康信息摘要</h2>
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
                  <div class="value">{{ healthSummary.activity_summary.steps }}</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>距离</template>
                  <div class="value">{{ healthSummary.activity_summary.distance_km }} km</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>消耗卡路里</template>
                  <div class="value">{{ healthSummary.activity_summary.calories_burned }} kcal</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>活动时间</template>
                  <div class="value">{{ healthSummary.activity_summary.active_minutes }} 分钟</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>运动次数</template>
                  <div class="value">{{ healthSummary.activity_summary.exercise_sessions }} 次</div>
                </a-card>
              </div>
            </a-tab-pane>

            <a-tab-pane key="sleep" tab="睡眠数据">
              <div class="summary-grid">
                <a-card class="summary-item">
                  <template #title>总睡眠时间</template>
                  <div class="value">{{ healthSummary.sleep_summary.total_sleep_hours }} 小时</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>深度睡眠</template>
                  <div class="value">{{ healthSummary.sleep_summary.deep_sleep_hours }} 小时</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>浅度睡眠</template>
                  <div class="value">{{ healthSummary.sleep_summary.light_sleep_hours }} 小时</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>REM睡眠</template>
                  <div class="value">{{ healthSummary.sleep_summary.rem_sleep_hours }} 小时</div>
                </a-card>
                <a-card class="summary-item">
                  <template #title>睡眠效率</template>
                  <div class="value">{{ healthSummary.sleep_summary.sleep_efficiency }}%</div>
                </a-card>
              </div>
            </a-tab-pane>
          </a-tabs>

          <div class="additional-info">
            <a-card title="其他信息" class="mt-4">
              <p>平均心率: {{ healthSummary.average_heart_rate }} bpm</p>
              <p>体重趋势: {{ healthSummary.weight_trend }}</p>
              <div class="key-insights">
                <h3>关键洞察</h3>
                <ul>
                  <li v-for="(insight, index) in healthSummary.key_insights" :key="index">
                    {{ insight }}
                  </li>
                </ul>
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

const { healthSummary, loading, error } = healthStore

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

.mt-4 {
  margin-top: 16px;
}
</style> 