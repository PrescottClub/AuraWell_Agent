<template>
  <div
    class="aura-card cursor-pointer"
    :class="{ 'border-l-4 border-l-primary': plan.status === 'active' }"
    @click="$emit('view', plan.plan_id || plan.id)"
  >
    <!-- 标题区域 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <h3 class="text-heading-4">{{ plan.title }}</h3>
        <a-tag :color="statusColor">
          {{ statusLabel }}
        </a-tag>
      </div>

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
    </div>

    <!-- 内容区域 -->
    <div class="space-y-4">
      <p class="text-body">{{ plan.description }}</p>

      <div class="flex flex-wrap gap-2">
        <a-tag
          v-for="module in getModulesList(plan.modules)"
          :key="getModuleKey(module)"
          color="blue"
          class="text-xs"
        >
          {{ getModuleLabel(module) }}
        </a-tag>
      </div>

      <div>
        <div class="flex justify-between items-center mb-2">
          <span class="text-body-small">完成进度</span>
          <span class="text-body-small font-medium">{{ plan.progress || 0 }}%</span>
        </div>
        <a-progress
          :percent="plan.progress || 0"
          :status="plan.status === 'completed' ? 'success' : 'active'"
          :show-info="false"
        />
      </div>

      <div class="flex justify-between items-center text-caption">
        <div class="flex items-center gap-1">
          <CalendarOutlined />
          <span>{{ formatDate(plan.created_at) }}</span>
        </div>
        <div class="flex items-center gap-1">
          <ClockCircleOutlined />
          <span>{{ plan.duration_days || plan.duration }}天</span>
        </div>
      </div>
    </div>
  </div>
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

defineEmits(['view', 'export', 'edit', 'delete'])

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

const getModulesList = (modules) => {
  if (!modules) return []

  // 如果modules是对象数组（后端格式），提取module_type
  if (Array.isArray(modules) && modules.length > 0 && typeof modules[0] === 'object') {
    return modules.map(module => module.module_type || module.type || module)
  }

  // 如果modules是字符串数组（前端格式），直接返回
  if (Array.isArray(modules)) {
    return modules
  }

  return []
}

const getModuleKey = (module) => {
  // 如果module是对象，使用其ID或type作为key
  if (typeof module === 'object') {
    return module.id || module.module_type || module.type || JSON.stringify(module)
  }
  // 如果module是字符串，直接使用
  return module
}

const getModuleLabel = (module) => {
  const labels = {
    diet: '饮食计划',
    exercise: '运动计划',
    weight: '体重管理',
    sleep: '睡眠计划',
    mental: '心理健康'
  }

  // 如果module是对象，提取其类型
  const moduleType = typeof module === 'object' ? (module.module_type || module.type) : module

  return labels[moduleType] || moduleType || module
}

const formatDate = (date) => {
  return date ? new Date(date).toLocaleDateString() : ''
}
</script>

<style scoped>
/* 使用新的aura设计系统，无需自定义样式 */
</style>
