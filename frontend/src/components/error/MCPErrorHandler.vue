<template>
  <div class="mcp-error-handler">
    <!-- 网络错误 -->
    <div v-if="errorType === 'network'" class="error-card network-error">
      <div class="error-icon">🌐</div>
      <div class="error-content">
        <h4 class="error-title">网络连接异常</h4>
        <p class="error-message">{{ errorMessage || '无法连接到服务器，请检查网络连接后重试' }}</p>
        <div class="error-actions">
          <a-button type="primary" size="small" @click="handleRetry">
            <template #icon><ReloadOutlined /></template>
            重试
          </a-button>
          <a-button size="small" @click="handleDismiss">关闭</a-button>
        </div>
      </div>
    </div>

    <!-- MCP工具错误 -->
    <div v-else-if="errorType === 'mcp_tool'" class="error-card mcp-tool-error">
      <div class="error-icon">🔧</div>
      <div class="error-content">
        <h4 class="error-title">MCP工具处理异常</h4>
        <p class="error-message">{{ errorMessage || '智能工具暂时不可用，正在使用基础功能为您服务' }}</p>
        <div class="degraded-service-note">
          <a-tag color="orange" size="small">降级服务模式</a-tag>
          <span>基础功能仍然可用</span>
        </div>
        <div class="error-actions">
          <a-button type="primary" size="small" @click="handleRetry">
            重新尝试MCP工具
          </a-button>
          <a-button size="small" @click="handleDismiss">继续使用基础功能</a-button>
        </div>
      </div>
    </div>

    <!-- 图表加载错误 -->
    <div v-else-if="errorType === 'chart_load'" class="error-card chart-error">
      <div class="error-icon">📊</div>
      <div class="error-content">
        <h4 class="error-title">图表加载失败</h4>
        <p class="error-message">{{ errorMessage || '图表生成遇到问题，为您提供数据摘要' }}</p>
        
        <!-- 数据摘要展示 -->
        <div v-if="fallbackData" class="fallback-data">
          <h5>📋 数据摘要</h5>
          <div class="data-summary">
            <div 
              v-for="(value, key) in fallbackData" 
              :key="key"
              class="summary-item"
            >
              <span class="item-label">{{ key }}:</span>
              <span class="item-value">{{ value }}</span>
            </div>
          </div>
        </div>

        <div class="error-actions">
          <a-button type="primary" size="small" @click="handleRetry">
            重新加载图表
          </a-button>
          <a-button size="small" @click="handleDismiss">仅查看数据</a-button>
        </div>
      </div>
    </div>

    <!-- 数据解析错误 -->
    <div v-else-if="errorType === 'data_parse'" class="error-card parse-error">
      <div class="error-icon">⚠️</div>
      <div class="error-content">
        <h4 class="error-title">数据解析异常</h4>
        <p class="error-message">{{ errorMessage || '部分数据格式异常，已为您显示可用信息' }}</p>
        <div class="error-actions">
          <a-button type="primary" size="small" @click="handleRetry">
            重新获取数据
          </a-button>
          <a-button size="small" @click="handleDismiss">继续浏览</a-button>
        </div>
      </div>
    </div>

    <!-- 通用错误 -->
    <div v-else class="error-card generic-error">
      <div class="error-icon">❌</div>
      <div class="error-content">
        <h4 class="error-title">出现异常</h4>
        <p class="error-message">{{ errorMessage || '系统遇到未知错误，请稍后再试' }}</p>
        <div class="error-actions">
          <a-button type="primary" size="small" @click="handleRetry">
            重试
          </a-button>
          <a-button size="small" @click="handleDismiss">关闭</a-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ReloadOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  errorType: {
    type: String,
    required: true,
    validator: (value) => ['network', 'mcp_tool', 'chart_load', 'data_parse', 'generic'].includes(value)
  },
  errorMessage: {
    type: String,
    default: ''
  },
  fallbackData: {
    type: Object,
    default: () => ({})
  },
  retryCount: {
    type: Number,
    default: 0
  },
  maxRetries: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['retry', 'dismiss', 'fallback-mode'])

const handleRetry = () => {
  if (props.retryCount < props.maxRetries) {
    emit('retry')
  } else {
    // 超过最大重试次数，进入降级模式
    emit('fallback-mode')
  }
}

const handleDismiss = () => {
  emit('dismiss')
}
</script>

<style scoped>
.mcp-error-handler {
  margin: 16px 0;
}

.error-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.network-error {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.mcp-tool-error {
  border-color: #faad14;
  background: #fffbe6;
}

.chart-error {
  border-color: #1890ff;
  background: #f0f5ff;
}

.parse-error {
  border-color: #fa8c16;
  background: #fff7e6;
}

.generic-error {
  border-color: #f5222d;
  background: #fff1f0;
}

.error-icon {
  font-size: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}

.error-content {
  flex: 1;
}

.error-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.error-message {
  margin: 0 0 12px 0;
  color: #595959;
  line-height: 1.5;
}

.degraded-service-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #fa8c16;
}

.fallback-data {
  margin: 12px 0;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.fallback-data h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #262626;
}

.data-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
  font-size: 12px;
}

.item-label {
  color: #8c8c8c;
}

.item-value {
  font-weight: 500;
  color: #262626;
}

.error-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-card {
    flex-direction: column;
    text-align: center;
  }
  
  .error-icon {
    align-self: center;
  }
  
  .data-summary {
    grid-template-columns: 1fr;
  }
  
  .error-actions {
    justify-content: center;
  }
}
</style> 