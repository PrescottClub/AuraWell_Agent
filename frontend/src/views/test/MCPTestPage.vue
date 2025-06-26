<template>
  <div class="mcp-test-page">
    <div class="test-header">
      <h1>🧪 MCP工具功能测试页面</h1>
      <p>测试验证所有MCP智能工具的前端展示功能</p>
      
      <div class="test-controls">
        <a-button-group>
          <a-button @click="loadTestData('full')" type="primary">
            完整MCP数据测试
          </a-button>
          <a-button @click="loadTestData('calculator')">
            计算器数据测试
          </a-button>
          <a-button @click="loadTestData('chart')">
            图表嵌入测试
          </a-button>
          <a-button @click="loadTestData('evidence')">
            科学依据测试
          </a-button>
          <a-button @click="loadTestData('personalization')">
            个性化标签测试
          </a-button>
          <a-button @click="loadTestData('animation')">
            交互动画测试
          </a-button>
          <a-button @click="loadTestData('conversation')">
            完整对话流程
          </a-button>
        </a-button-group>
        
        <div class="test-options">
          <a-switch 
            v-model="enableMcpFeatures" 
            checked-children="MCP功能开"
            un-checked-children="MCP功能关"
          />
          <a-switch 
            v-model="mobilePreview" 
            checked-children="移动端预览"
            un-checked-children="桌面端预览"
          />
        </div>
      </div>
    </div>

    <div class="test-content" :class="{ 'mobile-preview': mobilePreview }">
      <div class="chat-container">
        <h3>聊天消息展示测试</h3>
        <div class="messages-list">
          <ChatMessage
            v-for="message in currentTestMessages"
            :key="message.id"
            :message="message"
            :enable-mcp-features="enableMcpFeatures"
            @quick-reply="handleQuickReply"
            @suggestion-action="handleSuggestionAction"
          />
        </div>
      </div>

      <div class="test-info">
        <h3>📊 测试状态信息</h3>
        <div class="info-grid">
          <div class="info-card">
            <h4>当前测试场景</h4>
            <p>{{ currentTestName }}</p>
          </div>
          <div class="info-card">
            <h4>MCP功能状态</h4>
            <p>{{ enableMcpFeatures ? '✅ 已启用' : '❌ 已禁用' }}</p>
          </div>
          <div class="info-card">
            <h4>预览模式</h4>
            <p>{{ mobilePreview ? '📱 移动端' : '💻 桌面端' }}</p>
          </div>
          <div class="info-card">
            <h4>消息数量</h4>
            <p>{{ currentTestMessages.length }} 条</p>
          </div>
        </div>

        <div class="test-checklist">
          <h4>📋 Phase 1 & 2 功能检查清单</h4>
          <a-checkbox-group v-model="completedTests">
            <div class="checklist-items">
              <a-checkbox value="mcp-parsing">MCP数据正确解析和展示</a-checkbox>
              <a-checkbox value="chart-embed">图表URL能够正常嵌入和显示</a-checkbox>
              <a-checkbox value="calculator-cards">计算数据卡片样式正确</a-checkbox>
              <a-checkbox value="evidence-panel">科学依据面板功能正常</a-checkbox>
              <a-checkbox value="personalization-panel">个性化标签面板展示正确</a-checkbox>
              <a-checkbox value="interaction-animations">交互动画效果流畅</a-checkbox>
              <a-checkbox value="loading-states">加载状态指示器正常</a-checkbox>
              <a-checkbox value="mobile-display">手机浏览器打开正常显示</a-checkbox>
            </div>
          </a-checkbox-group>
        </div>

        <div class="test-results">
          <h4>✅ 测试结果统计</h4>
          <a-progress 
            :percent="(completedTests.length / 8) * 100" 
            :stroke-color="getProgressColor(completedTests.length)"
          />
          <p>已完成: {{ completedTests.length }}/8 项测试</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import { mcpTestData, mcpConversationFlow } from '@/mock/mcpTestData.js'

// 响应式数据
const currentTestMessages = ref([])
const currentTestName = ref('请选择测试场景')
const enableMcpFeatures = ref(true)
const mobilePreview = ref(false)
const completedTests = ref([])

// 测试场景数据映射
const testScenarios = {
  full: {
    name: '完整MCP数据展示',
    messages: [mcpTestData.fullMcpMessage]
  },
  calculator: {
    name: '计算器数据展示',
    messages: [mcpTestData.calculatorOnlyMessage]
  },
  chart: {
    name: '图表嵌入展示',
    messages: [mcpTestData.chartOnlyMessage]
  },
  evidence: {
    name: '科学依据展示',
    messages: [mcpTestData.evidenceOnlyMessage]
  },
  personalization: {
    name: '个性化标签系统',
    messages: [mcpTestData.personalizationTestMessage]
  },
  animation: {
    name: '交互动画效果',
    messages: [mcpTestData.animationTestMessage]
  },
  conversation: {
    name: '完整对话流程',
    messages: mcpConversationFlow
  }
}

// 方法
const loadTestData = (scenario) => {
  const testData = testScenarios[scenario]
  if (testData) {
    currentTestMessages.value = testData.messages
    currentTestName.value = testData.name
  }
}

const handleQuickReply = (reply) => {
  console.log('快速回复:', reply)
}

const handleSuggestionAction = (action) => {
  console.log('建议操作:', action)
}

const getProgressColor = (completed) => {
  if (completed === 8) return '#52c41a'
  if (completed >= 6) return '#1890ff'
  if (completed >= 4) return '#faad14'
  if (completed >= 2) return '#fadb14'
  return '#f5222d'
}

// 初始化加载完整测试数据
loadTestData('full')
</script>

<style scoped>
.mcp-test-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.test-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.test-header h1 {
  margin: 0 0 8px 0;
  color: #1890ff;
}

.test-header p {
  margin: 0 0 20px 0;
  color: #666;
}

.test-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.test-options {
  display: flex;
  gap: 16px;
  align-items: center;
}

.test-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  transition: all 0.3s ease;
}

.mobile-preview {
  grid-template-columns: 1fr;
}

.mobile-preview .chat-container {
  max-width: 375px;
  margin: 0 auto;
  border: 2px solid #ddd;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.chat-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chat-container h3 {
  padding: 16px 20px;
  margin: 0;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  color: #333;
}

.messages-list {
  max-height: 600px;
  overflow-y: auto;
  padding: 8px 0;
}

.test-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: fit-content;
}

.test-info h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 24px;
}

.info-card {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.info-card h4 {
  margin: 0 0 4px 0;
  font-size: 12px;
  color: #666;
}

.info-card p {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.test-checklist {
  margin-bottom: 24px;
}

.test-checklist h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-results h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.test-results p {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-content {
    grid-template-columns: 1fr;
  }
  
  .test-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .test-options {
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style> 