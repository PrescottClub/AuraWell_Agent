<template>
  <div class="aura-card">
    <div class="flex items-start justify-between mb-4">
      <h4 class="text-heading-4">{{ goal.title }}</h4>
      <a-dropdown>
        <a-button type="text" size="small">
          <template #icon>
            <MoreOutlined />
          </template>
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item @click="$emit('edit', goal)">
              <EditOutlined />
              编辑
            </a-menu-item>
            <a-menu-item @click="$emit('delete', goal.id)" danger>
              <DeleteOutlined />
              删除
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <p class="text-body mb-4">{{ goal.description }}</p>
    
    <div class="goal-progress">
      <a-progress 
        :percent="goal.progress || 0" 
        :status="goal.status === 'completed' ? 'success' : 'active'"
      />
    </div>
    
    <div class="goal-meta">
      <span class="goal-type">{{ getGoalTypeLabel(goal.type) }}</span>
      <span class="goal-deadline">{{ formatDate(goal.target_date) }}</span>
    </div>

    <div v-if="goal.target_value" class="goal-target">
      <div class="target-info">
        <span class="target-label">目标值:</span>
        <span class="target-value">{{ goal.target_value }} {{ goal.unit }}</span>
      </div>
      <div v-if="goal.current_value" class="current-info">
        <span class="current-label">当前值:</span>
        <span class="current-value">{{ goal.current_value }} {{ goal.unit }}</span>
      </div>
    </div>

    <div class="flex gap-2 mt-4">
      <button
        v-if="goal.status !== 'completed'"
        class="aura-btn aura-btn--primary text-sm"
        @click="$emit('update-progress', goal)"
      >
        更新进度
      </button>
      <button
        v-if="goal.status === 'active'"
        class="aura-btn aura-btn--secondary text-sm"
        @click="$emit('complete', goal.id)"
      >
        标记完成
      </button>
    </div>
  </div>
</template>

<script setup>
import { MoreOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'

defineProps({
  goal: {
    type: Object,
    required: true
  }
})

defineEmits(['edit', 'delete', 'update-progress', 'complete'])

const getGoalTypeLabel = (type) => {
  const labels = {
    weight_loss: '减重',
    weight_gain: '增重',
    fitness: '健身',
    nutrition: '营养',
    sleep: '睡眠',
    stress: '压力管理'
  }
  return labels[type] || type
}

const formatDate = (date) => {
  return date ? new Date(date).toLocaleDateString() : ''
}
</script>

<style scoped>
/* 使用新的设计系统，无需自定义样式 */

.goal-type {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.goal-target {
  background: #f3f4f6;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 12px;
  font-size: 13px;
}

.target-info,
.current-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.target-info:last-child,
.current-info:last-child {
  margin-bottom: 0;
}

.target-label,
.current-label {
  color: #6b7280;
}

.target-value {
  color: #1f2937;
  font-weight: 600;
}

.current-value {
  color: #059669;
  font-weight: 600;
}

.goal-actions {
  display: flex;
  gap: 8px;
}

.goal-actions .ant-btn {
  flex: 1;
}
</style>
