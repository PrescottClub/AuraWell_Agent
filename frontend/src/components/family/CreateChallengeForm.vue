<template>
  <div class="create-challenge-form">
    <a-form :model="formData" layout="vertical" @finish="handleSubmit">
      <!-- 挑战基本信息 -->
      <a-form-item
        label="挑战名称"
        name="title"
        :rules="[{ required: true, message: '请输入挑战名称' }]"
      >
        <a-input
          v-model:value="formData.title"
          placeholder="例如：本周步数挑战"
          maxlength="50"
        />
      </a-form-item>

      <a-form-item label="挑战描述" name="description">
        <a-textarea
          v-model:value="formData.description"
          placeholder="描述挑战的目标和规则"
          :rows="3"
          maxlength="200"
        />
      </a-form-item>

      <!-- 挑战类型 -->
      <a-form-item
        label="挑战类型"
        name="type"
        :rules="[{ required: true, message: '请选择挑战类型' }]"
      >
        <a-select
          v-model:value="formData.type"
          placeholder="选择挑战类型"
          @change="handleTypeChange"
        >
          <a-select-option value="steps">
            <div class="flex items-center">
              <WalkOutlined class="mr-2" />
              步数挑战
            </div>
          </a-select-option>
          <a-select-option value="calories">
            <div class="flex items-center">
              <FireOutlined class="mr-2" />
              卡路里挑战
            </div>
          </a-select-option>
          <a-select-option value="sleep_hours">
            <div class="flex items-center">
              <MoonOutlined class="mr-2" />
              睡眠挑战
            </div>
          </a-select-option>
          <a-select-option value="active_days">
            <div class="flex items-center">
              <CalendarOutlined class="mr-2" />
              活跃天数挑战
            </div>
          </a-select-option>
          <a-select-option value="weight_loss">
            <div class="flex items-center">
              <ScaleOutlined class="mr-2" />
              减重挑战
            </div>
          </a-select-option>
        </a-select>
      </a-form-item>

      <!-- 目标值 -->
      <a-form-item
        label="目标值"
        name="target_value"
        :rules="[
          { required: true, message: '请输入目标值' },
          { type: 'number', min: 1, message: '目标值必须大于0' }
        ]"
      >
        <a-input-number
          v-model:value="formData.target_value"
          :placeholder="getTargetPlaceholder()"
          :min="1"
          :max="getMaxValue()"
          :step="getStep()"
          style="width: 100%"
        >
          <template #addonAfter>
            {{ getUnit() }}
          </template>
        </a-input-number>
      </a-form-item>

      <!-- 挑战时长 -->
      <a-form-item
        label="挑战时长"
        name="duration_days"
        :rules="[{ required: true, message: '请选择挑战时长' }]"
      >
        <a-select v-model:value="formData.duration_days" placeholder="选择时长">
          <a-select-option :value="1">1天</a-select-option>
          <a-select-option :value="3">3天</a-select-option>
          <a-select-option :value="7">1周</a-select-option>
          <a-select-option :value="14">2周</a-select-option>
          <a-select-option :value="30">1个月</a-select-option>
        </a-select>
      </a-form-item>

      <!-- 开始时间 -->
      <a-form-item label="开始时间" name="start_date">
        <a-date-picker
          v-model:value="formData.start_date"
          placeholder="选择开始时间"
          :disabled-date="disabledDate"
          style="width: 100%"
        />
      </a-form-item>

      <!-- 参与成员 -->
      <a-form-item label="参与成员" name="participants">
        <div class="participants-selection">
          <div class="mb-3">
            <a-checkbox
              :indeterminate="indeterminate"
              :checked="checkAll"
              @change="onCheckAllChange"
            >
              全选
            </a-checkbox>
          </div>
          
          <a-checkbox-group
            v-model:value="formData.participants"
            @change="onParticipantsChange"
          >
            <div class="grid grid-cols-1 gap-2">
              <a-checkbox
                v-for="member in familyMembers"
                :key="member.user_id"
                :value="member.user_id"
                class="participant-checkbox"
              >
                <div class="flex items-center">
                  <a-avatar
                    :size="32"
                    :src="member.avatar"
                    class="mr-3"
                  >
                    {{ member.display_name?.charAt(0) }}
                  </a-avatar>
                  <div>
                    <div class="font-medium">{{ member.display_name }}</div>
                    <div class="text-sm text-gray-500">{{ member.role }}</div>
                  </div>
                </div>
              </a-checkbox>
            </div>
          </a-checkbox-group>
        </div>
      </a-form-item>

      <!-- 挑战规则 -->
      <a-form-item label="挑战规则">
        <div class="challenge-rules p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">
            <div class="mb-2">
              <strong>{{ getChallengeRuleTitle() }}</strong>
            </div>
            <ul class="list-disc list-inside space-y-1">
              <li v-for="rule in getChallengeRules()" :key="rule">
                {{ rule }}
              </li>
            </ul>
          </div>
        </div>
      </a-form-item>

      <!-- 奖励设置 -->
      <a-form-item label="完成奖励">
        <a-input
          v-model:value="formData.reward"
          placeholder="例如：获得100积分，或者自定义奖励"
        />
      </a-form-item>

      <!-- 预览信息 -->
      <a-form-item label="挑战预览">
        <div class="challenge-preview p-4 border rounded-lg bg-blue-50">
          <h4 class="font-medium mb-2">{{ formData.title || '挑战名称' }}</h4>
          <p class="text-sm text-gray-600 mb-3">
            {{ formData.description || '挑战描述' }}
          </p>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">类型：</span>
              <span>{{ getTypeText() }}</span>
            </div>
            <div>
              <span class="text-gray-500">目标：</span>
              <span>{{ formData.target_value }} {{ getUnit() }}</span>
            </div>
            <div>
              <span class="text-gray-500">时长：</span>
              <span>{{ formData.duration_days }} 天</span>
            </div>
            <div>
              <span class="text-gray-500">参与者：</span>
              <span>{{ formData.participants.length }} 人</span>
            </div>
          </div>
        </div>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import {
  WalkOutlined,
  FireOutlined,
  MoonOutlined,
  CalendarOutlined,
  ScaleOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  familyMembers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// 表单数据
const formData = ref({
  title: '',
  description: '',
  type: 'steps',
  target_value: 10000,
  duration_days: 7,
  start_date: dayjs(),
  participants: [],
  reward: ''
})

// 参与者选择状态
const indeterminate = ref(false)
const checkAll = ref(false)

// 计算属性
const selectedParticipants = computed(() => formData.value.participants)

// 监听器
watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

watch(selectedParticipants, (newValue) => {
  indeterminate.value = newValue.length > 0 && newValue.length < props.familyMembers.length
  checkAll.value = newValue.length === props.familyMembers.length
})

// 方法
const handleTypeChange = (type) => {
  // 根据类型设置默认目标值
  const defaults = {
    steps: 10000,
    calories: 2000,
    sleep_hours: 8,
    active_days: 5,
    weight_loss: 2
  }
  formData.value.target_value = defaults[type] || 1
}

const getTargetPlaceholder = () => {
  const placeholders = {
    steps: '例如：10000',
    calories: '例如：2000',
    sleep_hours: '例如：8',
    active_days: '例如：5',
    weight_loss: '例如：2'
  }
  return placeholders[formData.value.type] || '请输入目标值'
}

const getUnit = () => {
  const units = {
    steps: '步',
    calories: '卡路里',
    sleep_hours: '小时',
    active_days: '天',
    weight_loss: '公斤'
  }
  return units[formData.value.type] || ''
}

const getMaxValue = () => {
  const maxValues = {
    steps: 100000,
    calories: 10000,
    sleep_hours: 12,
    active_days: 30,
    weight_loss: 50
  }
  return maxValues[formData.value.type] || 1000
}

const getStep = () => {
  const steps = {
    steps: 1000,
    calories: 100,
    sleep_hours: 0.5,
    active_days: 1,
    weight_loss: 0.1
  }
  return steps[formData.value.type] || 1
}

const getTypeText = () => {
  const texts = {
    steps: '步数挑战',
    calories: '卡路里挑战',
    sleep_hours: '睡眠挑战',
    active_days: '活跃天数挑战',
    weight_loss: '减重挑战'
  }
  return texts[formData.value.type] || '未知类型'
}

const getChallengeRuleTitle = () => {
  return `${getTypeText()}规则`
}

const getChallengeRules = () => {
  const rules = {
    steps: [
      '每日步数会自动统计',
      '达到目标步数即可获得积分',
      '连续达标可获得额外奖励'
    ],
    calories: [
      '每日消耗卡路里会自动统计',
      '包括运动和基础代谢消耗',
      '达到目标即可完成挑战'
    ],
    sleep_hours: [
      '每日睡眠时长会自动记录',
      '需要连续达到目标睡眠时长',
      '睡眠质量也会影响评分'
    ],
    active_days: [
      '活跃天数指有运动记录的天数',
      '每天至少需要30分钟活动',
      '可以是任何形式的运动'
    ],
    weight_loss: [
      '需要手动记录体重变化',
      '以挑战开始时的体重为基准',
      '健康减重速度为每周0.5-1公斤'
    ]
  }
  return rules[formData.value.type] || []
}

const disabledDate = (current) => {
  // 不能选择过去的日期
  return current && current < dayjs().startOf('day')
}

const onCheckAllChange = (e) => {
  if (e.target.checked) {
    formData.value.participants = props.familyMembers.map(member => member.user_id)
  } else {
    formData.value.participants = []
  }
}

const onParticipantsChange = (checkedList) => {
  formData.value.participants = checkedList
}

const handleSubmit = () => {
  emit('submit', formData.value)
}
</script>

<style scoped>
.create-challenge-form {
  @apply w-full;
}

.participants-selection {
  @apply border rounded-lg p-3 bg-gray-50;
}

.participant-checkbox {
  @apply w-full p-2 rounded hover:bg-white transition-colors;
}

.challenge-rules {
  @apply text-sm;
}

.challenge-preview {
  @apply transition-all duration-300;
}

.grid {
  @apply gap-2;
}

.ant-input-number {
  @apply w-full;
}

.ant-checkbox-group {
  @apply w-full;
}

.ant-checkbox-wrapper {
  @apply w-full;
}
</style>
