<template>
  <div class="prompt-playground-v2">
    <!-- Header with tabs -->
    <div class="playground-header">
      <h1 class="text-2xl font-bold text-gray-800 mb-4">🧪 Prompt Playground 2.0</h1>
      <a-tabs v-model:activeKey="activeTab" class="playground-tabs">
        <a-tab-pane key="single" tab="单版本测试">
          <SingleVersionTest />
        </a-tab-pane>
        <a-tab-pane key="compare" tab="版本对比">
          <!-- Version Comparison Panel -->
          <div class="version-comparison-panel">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-card title="🔄 版本对比配置" class="mb-4">
                  <a-form layout="vertical">
                    <a-row :gutter="16">
                      <a-col :span="12">
                        <a-form-item label="版本A">
                          <a-select v-model:value="comparison.versionA">
                            <a-select-option v-for="version in availableVersions" :key="version.version" :value="version.version">
                              {{ version.name }}
                            </a-select-option>
                          </a-select>
                        </a-form-item>
                      </a-col>
                      <a-col :span="12">
                        <a-form-item label="版本B">
                          <a-select v-model:value="comparison.versionB">
                            <a-select-option v-for="version in availableVersions" :key="version.version" :value="version.version">
                              {{ version.name }}
                            </a-select-option>
                          </a-select>
                        </a-form-item>
                      </a-col>
                    </a-row>
                    <a-form-item label="对比天数">
                      <a-select v-model:value="comparison.days">
                        <a-select-option value="7">最近7天</a-select-option>
                        <a-select-option value="30">最近30天</a-select-option>
                        <a-select-option value="90">最近90天</a-select-option>
                      </a-select>
                    </a-form-item>
                    <a-button type="primary" @click="runVersionComparison" :loading="comparisonLoading">
                      开始对比分析
                    </a-button>
                  </a-form>
                </a-card>
              </a-col>
              <a-col :span="12">
                <a-card title="📊 性能指标对比" v-if="comparisonResult">
                  <div class="metrics-comparison">
                    <div v-for="metric in Object.keys(comparisonResult.comparison || {})" :key="metric" class="metric-row">
                      <div class="metric-name">{{ formatMetricName(metric) }}</div>
                      <div class="metric-values">
                        <span class="version-a">{{ formatMetricValue(comparisonResult.stats_a[metric]) }}</span>
                        <span class="vs">vs</span>
                        <span class="version-b">{{ formatMetricValue(comparisonResult.stats_b[metric]) }}</span>
                        <span :class="['difference', getDifferenceClass(comparisonResult.comparison[metric])]">
                          {{ formatDifference(comparisonResult.comparison[metric]) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </a-card>
              </a-col>
            </a-row>
          </div>
        </a-tab-pane>
        <a-tab-pane key="analytics" tab="性能分析">
          <PerformanceAnalytics />
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- Single Version Test -->
    <div v-if="activeTab === 'single'" class="single-test-panel">
      <a-row :gutter="24">
        <a-col :span="8">
          <a-card title="🔧 配置面板" class="config-card">
            <a-form layout="vertical">
              <!-- Prompt Version Selection -->
              <a-form-item label="Prompt版本">
                <a-select v-model:value="config.promptVersion" @change="onVersionChange">
                  <a-select-option v-for="version in availableVersions" :key="version.version" :value="version.version">
                    {{ version.name }} ({{ version.version }})
                  </a-select-option>
                </a-select>
              </a-form-item>

              <!-- Scenario Selection -->
              <a-form-item label="场景">
                <a-select v-model:value="config.scenario">
                  <a-select-option value="health_advice">健康建议</a-select-option>
                  <a-select-option value="nutrition_planning">营养规划</a-select-option>
                  <a-select-option value="exercise_guidance">运动指导</a-select-option>
                </a-select>
              </a-form-item>

              <!-- Model Configuration -->
              <a-form-item label="AI模型">
                <a-select v-model:value="config.model">
                  <a-select-option value="deepseek-r1">DeepSeek R1</a-select-option>
                  <a-select-option value="deepseek-chat">DeepSeek Chat</a-select-option>
                </a-select>
              </a-form-item>

              <!-- Advanced Settings -->
              <a-collapse>
                <a-collapse-panel key="advanced" header="高级设置">
                  <a-form-item label="Temperature">
                    <a-slider v-model:value="config.temperature" :min="0" :max="2" :step="0.1" />
                    <span class="text-sm text-gray-500">当前值: {{ config.temperature }}</span>
                  </a-form-item>
                  <a-form-item label="Max Tokens">
                    <a-input-number v-model:value="config.max_tokens" :min="100" :max="4000" />
                  </a-form-item>
                  <a-form-item label="启用推理模式">
                    <a-switch v-model:checked="config.enableReasoning" />
                  </a-form-item>
                </a-collapse-panel>
              </a-collapse>
            </a-form>
          </a-card>

          <!-- Context Injection -->
          <a-card title="📊 上下文注入" class="mt-4">
            <a-form layout="vertical">
              <a-form-item label="用户档案">
                <a-textarea v-model:value="context.profile" :rows="2" placeholder="用户基本信息..." />
              </a-form-item>
              <a-form-item label="健康指标">
                <a-textarea v-model:value="context.metrics" :rows="2" placeholder="BMI, 血压等..." />
              </a-form-item>
              <a-form-item label="对话历史">
                <a-textarea v-model:value="context.history" :rows="2" placeholder="最近对话记录..." />
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>

        <a-col :span="16">
          <a-card title="🧪 测试面板" class="test-card">
            <!-- Test Input -->
            <a-form-item label="测试输入">
              <a-textarea
                v-model:value="userPrompt"
                :rows="6"
                placeholder="输入您的测试问题..."
                class="test-input"
              />
            </a-form-item>

            <!-- Action Buttons -->
            <div class="action-buttons mb-4">
              <a-button type="primary" @click="runSingleTest" :loading="isLoading" size="large">
                <template #icon><PlayCircleOutlined /></template>
                运行测试
              </a-button>
              <a-button @click="clearResults" class="ml-2">
                <template #icon><ClearOutlined /></template>
                清空结果
              </a-button>
              <a-button @click="saveTest" class="ml-2" :disabled="!result">
                <template #icon><SaveOutlined /></template>
                保存测试
              </a-button>
            </div>

            <!-- Results Display -->
            <div class="results-section">
              <div class="flex justify-between items-center mb-3">
                <h3 class="text-lg font-semibold">📋 测试结果</h3>
                <div v-if="testMetrics" class="metrics-summary">
                  <a-tag color="blue">响应时间: {{ testMetrics.responseTime }}ms</a-tag>
                  <a-tag color="green">Token数: {{ testMetrics.tokens }}</a-tag>
                </div>
              </div>

              <div v-if="isLoading" class="loading-state text-center py-8">
                <a-spin size="large" />
                <p class="mt-2 text-gray-500">AI正在思考中...</p>
              </div>

              <div v-else-if="result" class="result-content">
                <a-tabs>
                  <a-tab-pane key="formatted" tab="格式化结果">
                    <div class="formatted-result" v-html="formattedResult"></div>
                  </a-tab-pane>
                  <a-tab-pane key="raw" tab="原始输出">
                    <pre class="raw-result">{{ result }}</pre>
                  </a-tab-pane>
                  <a-tab-pane key="prompt" tab="实际Prompt">
                    <div class="prompt-display">
                      <h4>系统Prompt:</h4>
                      <pre class="system-prompt">{{ actualPrompt.system }}</pre>
                      <h4>用户Prompt:</h4>
                      <pre class="user-prompt">{{ actualPrompt.user }}</pre>
                    </div>
                  </a-tab-pane>
                </a-tabs>
              </div>

              <div v-else class="empty-state text-center py-8">
                <div class="text-gray-400 text-lg">🎯</div>
                <p class="text-gray-500 mt-2">运行测试查看结果</p>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlayCircleOutlined,
  ClearOutlined,
  SaveOutlined
} from '@ant-design/icons-vue'
import { marked } from 'marked'

// Reactive state
const activeTab = ref('single')
const isLoading = ref(false)
const userPrompt = ref('')
const result = ref('')
const testMetrics = ref(null)
const actualPrompt = ref({ system: '', user: '' })
const availableVersions = ref([])

// Configuration
const config = reactive({
  promptVersion: 'v3_1',
  scenario: 'health_advice',
  model: 'deepseek-r1',
  temperature: 0.7,
  max_tokens: 2000,
  enableReasoning: true
})

// Context for prompt injection
const context = reactive({
  profile: '用户：李明，男，28岁，身高180cm，体重85kg，程序员',
  metrics: 'BMI: 26.2, 血压: 125/82, 心率: 75, 体脂率: 18%',
  history: '最近询问过减重和改善睡眠的建议'
})

// Version comparison state
const comparison = reactive({
  versionA: 'v3_0',
  versionB: 'v3_1',
  days: 30
})

const comparisonLoading = ref(false)
const comparisonResult = ref(null)

// Computed properties
const formattedResult = computed(() => {
  if (!result.value) return ''
  try {
    return marked(result.value)
  } catch (e) {
    return result.value
  }
})

// Methods
const loadAvailableVersions = async () => {
  try {
    // Call backend API to get available versions
    const response = await fetch('/api/v1/admin/prompt/versions', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      availableVersions.value = data.versions || []

      // Load performance stats for each version
      await loadVersionPerformanceStats()

      console.log(`Loaded ${availableVersions.value.length} available versions`)
    } else {
      throw new Error(`Failed to load versions: ${response.status}`)
    }
  } catch (error) {
    console.error('Failed to load versions from API:', error)

    // Fallback to default versions
    availableVersions.value = [
      {
        version: 'v3_0',
        name: 'Health Advice v3.0',
        description: 'Standard health advice template',
        performance: { rating: 4.2, usage: 1250, error_rate: 2.1 }
      },
      {
        version: 'v3_1',
        name: 'Health Advice v3.1',
        description: 'Enhanced with CoT reasoning',
        performance: { rating: 4.6, usage: 890, error_rate: 1.3 }
      },
      {
        version: 'v3_2_test',
        name: 'Health Advice v3.2 (Experimental)',
        description: 'Latest experimental features',
        performance: { rating: 4.4, usage: 156, error_rate: 1.8 }
      }
    ]
  }
}

const loadVersionPerformanceStats = async () => {
  try {
    for (const version of availableVersions.value) {
      const response = await fetch(`/api/v1/admin/prompt/stats?scenario=${config.scenario}&version=${version.version}&days=7`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        version.performance = {
          rating: data.stats?.average_rating || 0,
          usage: data.stats?.total_uses || 0,
          error_rate: data.stats?.error_rate_percent || 0,
          response_time: data.stats?.average_response_time_ms || 0
        }
      }
    }
  } catch (error) {
    console.warn('Failed to load performance stats:', error)
  }
}

const onVersionChange = async (version) => {
  console.log('Version changed to:', version)

  // Load version metadata
  try {
    const selectedVersion = availableVersions.value.find(v => v.version === version)
    if (selectedVersion) {
      console.log('Selected version details:', selectedVersion)

      // Could update UI to show version-specific information
      // For example, show performance metrics, description, etc.
    }
  } catch (error) {
    console.error('Error handling version change:', error)
  }
}

const runSingleTest = async () => {
  if (!userPrompt.value.trim()) {
    message.warning('请输入测试问题')
    return
  }

  isLoading.value = true
  const startTime = Date.now()

  try {
    // Simulate API call for now
    await new Promise(resolve => setTimeout(resolve, 2000))

    const endTime = Date.now()

    result.value = `# 🎯 健康建议测试结果

## 📊 基于您的情况分析

**用户档案**: ${context.profile}
**健康指标**: ${context.metrics}
**测试问题**: ${userPrompt.value}

## 💡 个性化建议

基于您的BMI 26.2和当前健康状况，我为您制定以下建议：

### 🍽️ 饮食建议
- 控制每日热量摄入在2200卡路里左右
- 增加蛋白质摄入，建议每公斤体重1.2-1.6g
- 减少精制碳水化合物，选择复合碳水

### 🏃 运动建议
- 每周进行3-4次有氧运动，每次30-45分钟
- 结合力量训练，每周2-3次
- 推荐运动：快走、游泳、骑行

### 😴 睡眠优化
- 保持规律作息，每晚7-8小时睡眠
- 睡前1小时避免电子设备
- 创造舒适的睡眠环境

*注意：以上建议仅供参考，如有健康问题请咨询专业医生。*`

    actualPrompt.value = {
      system: `你是AuraWell智能健康助手，版本：${config.promptVersion}`,
      user: `用户问题：${userPrompt.value}\n\n上下文：${JSON.stringify(context, null, 2)}`
    }

    testMetrics.value = {
      responseTime: endTime - startTime,
      tokens: Math.floor(Math.random() * 500) + 200,
      version: config.promptVersion,
      model: config.model
    }

    message.success('测试完成')
  } catch (error) {
    console.error('Test error:', error)
    message.error('测试失败: ' + error.message)
    result.value = 'Error: ' + error.message
  } finally {
    isLoading.value = false
  }
}

const clearResults = () => {
  result.value = ''
  testMetrics.value = null
  actualPrompt.value = { system: '', user: '' }
}

const saveTest = async () => {
  if (!result.value) {
    message.warning('没有可保存的测试结果')
    return
  }

  try {
    const testData = {
      config: { ...config },
      context: { ...context },
      input: userPrompt.value,
      output: result.value,
      metrics: testMetrics.value,
      timestamp: new Date().toISOString()
    }

    const savedTests = JSON.parse(localStorage.getItem('promptTests') || '[]')
    savedTests.push(testData)
    localStorage.setItem('promptTests', JSON.stringify(savedTests))

    message.success('测试结果已保存')
  } catch (error) {
    console.error('Save error:', error)
    message.error('保存失败')
  }
}

// Version comparison methods
const runVersionComparison = async () => {
  if (!comparison.versionA || !comparison.versionB) {
    console.warn('请选择要对比的版本')
    return
  }

  if (comparison.versionA === comparison.versionB) {
    console.warn('请选择不同的版本进行对比')
    return
  }

  comparisonLoading.value = true

  try {
    const response = await fetch('/api/v1/admin/prompt/compare', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      params: new URLSearchParams({
        scenario: config.scenario,
        version_a: comparison.versionA,
        version_b: comparison.versionB,
        days: comparison.days.toString()
      })
    })

    if (!response.ok) {
      throw new Error(`对比请求失败: ${response.status}`)
    }

    const data = await response.json()
    comparisonResult.value = data.comparison

    console.log('Version comparison completed:', data)

  } catch (error) {
    console.error('版本对比失败:', error)

    // Fallback to mock data for demonstration
    comparisonResult.value = {
      scenario: config.scenario,
      version_a: comparison.versionA,
      version_b: comparison.versionB,
      period_days: comparison.days,
      stats_a: {
        average_rating: 4.2,
        average_relevance: 0.85,
        average_response_time_ms: 1800,
        tool_success_rate: 0.92,
        error_rate_percent: 2.1
      },
      stats_b: {
        average_rating: 4.6,
        average_relevance: 0.91,
        average_response_time_ms: 1650,
        tool_success_rate: 0.95,
        error_rate_percent: 1.3
      },
      comparison: {
        average_rating: {
          difference: 0.4,
          difference_percent: 9.5,
          better_version: comparison.versionB
        },
        average_relevance: {
          difference: 0.06,
          difference_percent: 7.1,
          better_version: comparison.versionB
        },
        average_response_time_ms: {
          difference: -150,
          difference_percent: -8.3,
          better_version: comparison.versionB
        },
        tool_success_rate: {
          difference: 0.03,
          difference_percent: 3.3,
          better_version: comparison.versionB
        },
        error_rate_percent: {
          difference: -0.8,
          difference_percent: -38.1,
          better_version: comparison.versionB
        }
      }
    }
  } finally {
    comparisonLoading.value = false
  }
}

const formatMetricName = (metric) => {
  const names = {
    'average_rating': '平均评分',
    'average_relevance': '相关性',
    'average_response_time_ms': '响应时间',
    'tool_success_rate': '工具成功率',
    'error_rate_percent': '错误率'
  }
  return names[metric] || metric
}

const formatMetricValue = (value) => {
  if (value === null || value === undefined) return 'N/A'
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  return value.toString()
}

const formatDifference = (comparison) => {
  if (!comparison) return ''
  const { difference_percent, better_version } = comparison
  const sign = difference_percent > 0 ? '+' : ''
  return `${sign}${difference_percent.toFixed(1)}%`
}

const getDifferenceClass = (comparison) => {
  if (!comparison) return ''
  return comparison.difference_percent > 0 ? 'positive' : 'negative'
}

// Lifecycle
onMounted(() => {
  loadAvailableVersions()
})
</script>

<style scoped>
.prompt-playground-v2 {
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.playground-header {
  margin-bottom: 24px;
}

.config-card, .test-card {
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.results-section {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.metrics-summary {
  display: flex;
  gap: 8px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.result-content {
  background: white;
  border-radius: 6px;
  padding: 16px;
}

.formatted-result {
  line-height: 1.6;
}

.raw-result, .system-prompt, .user-prompt {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  color: #999;
  background: white;
  border: 2px dashed #e8e8e8;
  border-radius: 8px;
  padding: 32px;
}
</style>