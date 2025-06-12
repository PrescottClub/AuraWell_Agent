<template>
  <a-card 
    class="plan-card"
    :class="{ 'active-plan': plan.status === 'active' }"
    @click="$emit('view', plan.id)"
  >
    <template #title>
      <div class="plan-title">
        <span>{{ plan.title }}</span>
        <a-tag :color="statusColor">
          {{ statusLabel }}
        </a-tag>
      </div>
    </template>

    <template #extra>
      <a-dropdown>
        <a-button type="text" size="small" @click.stop>
          <template #icon>
            <MoreOutlined />
          </template>
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item @click.stop="$emit('view', plan.id)">
              <EyeOutlined />
              查看详情
            </a-menu-item>
            <a-menu-item @click.stop="$emit('export', plan.id)">
              <DownloadOutlined />
              导出计划
            </a-menu-item>
            <a-menu-item @click.stop="$emit('edit', plan.id)">
              <EditOutlined />
              编辑计划
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item @click.stop="$emit('delete', plan.id)" danger>
              <DeleteOutlined />
              删除计划
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </template>

    <div class="plan-content">
      <p class="plan-description">{{ plan.description }}</p>
      
      <div class="plan-modules">
        <a-tag 
          v-for="module in plan.modules" 
          :key="module"
          color="blue"
          class="module-tag"
        >
          {{ getModuleLabel(module) }}
        </a-tag>
      </div>

      <div class="plan-progress">
        <div class="progress-label">
          <span>完成进度</span>
          <span>{{ plan.progress || 0 }}%</span>
        </div>
        <a-progress 
          :percent="plan.progress || 0" 
          :status="plan.status === 'completed' ? 'success' : 'active'"
          :show-info="false"
        />
      </div>

      <div class="plan-meta">
        <div class="meta-item">
          <CalendarOutlined />
          <span>{{ formatDate(plan.created_at) }}</span>
        </div>
        <div class="meta-item">
          <ClockCircleOutlined />
          <span>{{ plan.duration }}天</span>
        </div>
      </div>
    </div>
  </a-card>
</template>

<script setup>
import { computed } from 'vue'
import { 
  MoreOutlined, 
  EyeOutlined,
  DownloadOutlined,
  EditOutlined,
  DeleteOutlined,
  CalendarOutlined, 
  ClockCircleOutlined 
} from '@ant-design/icons-vue'

const props = defineProps({
  plan: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view', 'export', 'edit', 'delete'])

const statusColor = computed(() => {
  const colors = {
    active: 'green',
    completed: 'blue',
    paused: 'orange',
    cancelled: 'red'
  }
  return colors[props.plan.status] || 'default'
})

const statusLabel = computed(() => {
  const labels = {
    active: '进行中',
    completed: '已完成',
    paused: '已暂停',
    cancelled: '已取消'
  }
  return labels[props.plan.status] || props.plan.status
})

const getModuleLabel = (module) => {
  const labels = {
    diet: '饮食计划',
    exercise: '运动计划',
    weight: '体重管理',
    sleep: '睡眠计划',
    mental: '心理健康'
  }
  return labels[module] || module
}

const formatDate = (date) => {
  return date ? new Date(date).toLocaleDateString() : ''
}
</script>

<style scoped>
.plan-card {
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 24px;
}

.plan-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.active-plan {
  border: 2px solid #1890ff;
}

.plan-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-description {
  color: #6b7280;
  margin-bottom: 16px;
  line-height: 1.5;
}

.plan-modules {
  margin-bottom: 16px;
}

.module-tag {
  margin-bottom: 4px;
}

.plan-progress {
  margin-bottom: 16px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #374151;
}

.plan-meta {
  display: flex;
  justify-content: space-between;
  color: #9ca3af;
  font-size: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
