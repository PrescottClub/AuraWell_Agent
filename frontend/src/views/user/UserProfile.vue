<template>
  <div class="profile-container">
    <div class="profile-header">
      <h1>个人档案</h1>
      <p>管理您的个人信息和健康数据</p>
    </div>

    <!-- 家庭成员切换器 -->
    <div class="member-switcher-section mb-6">
      <MemberSwitcher />
    </div>

    <a-row :gutter="24">
      <!-- 基本信息卡片 -->
      <a-col :span="24" :lg="12">
        <a-card title="基本信息" class="profile-card">
          <a-form
            :model="profileForm"
            :rules="profileRules"
            layout="vertical"
            @finish="handleUpdateProfile"
          >
            <a-form-item label="用户名" name="username">
              <a-input 
                v-model:value="profileForm.username" 
                placeholder="请输入用户名"
              />
            </a-form-item>

            <a-form-item label="邮箱" name="email">
              <a-input 
                v-model:value="profileForm.email" 
                placeholder="请输入邮箱地址"
              />
            </a-form-item>

            <a-form-item>
              <a-button 
                type="primary" 
                html-type="submit" 
                :loading="userStore.loading"
              >
                更新基本信息
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <!-- 健康数据卡片 -->
      <a-col :span="24" :lg="12">
        <a-card title="健康数据" class="profile-card">
          <div class="health-stats">
            <div class="stat-item">
              <div class="stat-label">BMI</div>
              <div class="stat-value">
                {{ userStore.bmi || '--' }}
                <span class="stat-category">{{ userStore.bmiCategory }}</span>
              </div>
            </div>
          </div>

          <a-form
            :model="healthForm"
            :rules="healthRules"
            layout="vertical"
            @finish="handleUpdateHealth"
          >
            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="年龄" name="age">
                  <a-input-number 
                    v-model:value="healthForm.age" 
                    :min="1"
                    :max="120"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="性别" name="gender">
                  <a-select v-model:value="healthForm.gender">
                    <a-select-option value="male">男</a-select-option>
                    <a-select-option value="female">女</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="16">
              <a-col :span="12">
                <a-form-item label="身高 (cm)" name="height">
                  <a-input-number 
                    v-model:value="healthForm.height" 
                    :min="100"
                    :max="250"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="体重 (kg)" name="weight">
                  <a-input-number 
                    v-model:value="healthForm.weight" 
                    :min="30"
                    :max="300"
                    :precision="1"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="活动水平" name="activity_level">
              <a-select v-model:value="healthForm.activity_level">
                <a-select-option value="sedentary">久坐不动</a-select-option>
                <a-select-option value="light">轻度活动</a-select-option>
                <a-select-option value="moderate">中度活动</a-select-option>
                <a-select-option value="active">积极活动</a-select-option>
                <a-select-option value="very_active">非常活跃</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="睡眠时间 (小时)" name="sleep_hours">
              <a-input-number 
                v-model:value="healthForm.sleep_hours" 
                :min="1"
                :max="24"
                :precision="1"
                style="width: 100%"
              />
            </a-form-item>

            <a-form-item label="压力水平" name="stress_level">
              <a-select v-model:value="healthForm.stress_level">
                <a-select-option value="low">低</a-select-option>
                <a-select-option value="medium">中等</a-select-option>
                <a-select-option value="high">高</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item>
              <a-button 
                type="primary" 
                html-type="submit" 
                :loading="userStore.loading"
              >
                更新健康数据
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>

    <!-- 健康目标管理 -->
    <a-row :gutter="24" style="margin-top: 24px;">
      <a-col :span="24">
        <a-card title="健康目标" class="profile-card">
          <template #extra>
            <a-button type="primary" @click="showGoalModal = true">
              添加目标
            </a-button>
          </template>

          <div v-if="userStore.healthGoals.length === 0" class="empty-goals">
            <a-empty description="暂无健康目标">
              <a-button type="primary" @click="showGoalModal = true">
                创建第一个目标
              </a-button>
            </a-empty>
          </div>

          <div v-else class="goals-list">
            <a-row :gutter="16">
              <a-col 
                v-for="goal in userStore.healthGoals" 
                :key="goal.id"
                :span="24" :md="12" :lg="8"
              >
                <div class="goal-card">
                  <div class="goal-header">
                    <h4>{{ goal.title }}</h4>
                    <a-dropdown>
                      <a-button type="text" size="small">
                        <template #icon>
                          <MoreOutlined />
                        </template>
                      </a-button>
                      <template #overlay>
                        <a-menu>
                          <a-menu-item @click="editGoal(goal)">编辑</a-menu-item>
                          <a-menu-item @click="deleteGoal(goal.id)">删除</a-menu-item>
                        </a-menu>
                      </template>
                    </a-dropdown>
                  </div>
                  <p class="goal-description">{{ goal.description }}</p>
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
                </div>
              </a-col>
            </a-row>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 添加/编辑目标模态框 -->
    <a-modal
      v-model:open="showGoalModal"
      :title="editingGoal ? '编辑目标' : '添加目标'"
      @ok="handleSaveGoal"
      @cancel="resetGoalForm"
      :confirm-loading="userStore.loading"
    >
      <a-form
        :model="goalForm"
        :rules="goalRules"
        layout="vertical"
        ref="goalFormRef"
      >
        <a-form-item label="目标标题" name="title">
          <a-input v-model:value="goalForm.title" placeholder="请输入目标标题" />
        </a-form-item>

        <a-form-item label="目标描述" name="description">
          <a-textarea 
            v-model:value="goalForm.description" 
            placeholder="请描述您的目标"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="目标类型" name="type">
          <a-select v-model:value="goalForm.type">
            <a-select-option value="weight_loss">减重</a-select-option>
            <a-select-option value="weight_gain">增重</a-select-option>
            <a-select-option value="fitness">健身</a-select-option>
            <a-select-option value="nutrition">营养</a-select-option>
            <a-select-option value="sleep">睡眠</a-select-option>
            <a-select-option value="stress">压力管理</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="目标日期" name="target_date">
          <a-date-picker 
            v-model:value="goalForm.target_date" 
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </a-form-item>

        <a-form-item label="目标值" name="target_value">
          <a-input-number 
            v-model:value="goalForm.target_value" 
            placeholder="请输入目标值"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="单位" name="unit">
          <a-input v-model:value="goalForm.unit" placeholder="如：kg, 次, 小时" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { MoreOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '../../stores/user.js'
// import { useFamilyStore } from '../../stores/family.js' // 暂时未使用
import MemberSwitcher from '../../components/family/MemberSwitcher.vue'
import dayjs from 'dayjs'

const userStore = useUserStore()
// const familyStore = useFamilyStore() // 暂时未使用

// 响应式数据
const showGoalModal = ref(false)
const editingGoal = ref(null)
const goalFormRef = ref()

// 表单数据
const profileForm = reactive({
  username: '',
  email: ''
})

const healthForm = reactive({
  age: null,
  gender: '',
  height: null,
  weight: null,
  activity_level: '',
  sleep_hours: null,
  stress_level: ''
})

const goalForm = reactive({
  title: '',
  description: '',
  type: '',
  target_date: null,
  target_value: null,
  unit: ''
})

// 表单验证规则
const profileRules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址' },
    { type: 'email', message: '请输入有效的邮箱地址' }
  ]
}

const healthRules = {
  age: [{ required: true, message: '请输入年龄' }],
  gender: [{ required: true, message: '请选择性别' }],
  height: [{ required: true, message: '请输入身高' }],
  weight: [{ required: true, message: '请输入体重' }],
  activity_level: [{ required: true, message: '请选择活动水平' }]
}

const goalRules = {
  title: [{ required: true, message: '请输入目标标题' }],
  type: [{ required: true, message: '请选择目标类型' }],
  target_date: [{ required: true, message: '请选择目标日期' }]
}

// 生命周期
onMounted(async () => {
  await userStore.fetchUserProfile()
  await userStore.fetchHealthData()
  await userStore.fetchHealthGoals()
  
  // 初始化表单数据
  Object.assign(profileForm, userStore.userProfile)
  Object.assign(healthForm, userStore.healthData)
})

// 监听用户数据变化
watch(() => userStore.userProfile, (newProfile) => {
  Object.assign(profileForm, newProfile)
}, { deep: true })

watch(() => userStore.healthData, (newHealthData) => {
  Object.assign(healthForm, newHealthData)
}, { deep: true })

// 方法
const handleUpdateProfile = async () => {
  try {
    await userStore.updateUserProfile(profileForm)
    message.success('基本信息更新成功')
  } catch (error) {
    message.error('更新失败，请重试')
  }
}

const handleUpdateHealth = async () => {
  try {
    await userStore.updateHealthData(healthForm)
    message.success('健康数据更新成功')
  } catch (error) {
    message.error('更新失败，请重试')
  }
}

const handleSaveGoal = async () => {
  try {
    await goalFormRef.value.validate()
    
    const goalData = {
      ...goalForm,
      target_date: goalForm.target_date ? goalForm.target_date.format('YYYY-MM-DD') : null
    }

    if (editingGoal.value) {
      await userStore.updateHealthGoal(editingGoal.value.id, goalData)
      message.success('目标更新成功')
    } else {
      await userStore.createHealthGoal(goalData)
      message.success('目标创建成功')
    }
    
    resetGoalForm()
  } catch (error) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error('操作失败，请重试')
  }
}

const editGoal = (goal) => {
  editingGoal.value = goal
  Object.assign(goalForm, {
    ...goal,
    target_date: goal.target_date ? dayjs(goal.target_date) : null
  })
  showGoalModal.value = true
}

const deleteGoal = async (goalId) => {
  try {
    await userStore.deleteHealthGoal(goalId)
    message.success('目标删除成功')
  } catch (error) {
    message.error('删除失败，请重试')
  }
}

const resetGoalForm = () => {
  showGoalModal.value = false
  editingGoal.value = null
  Object.assign(goalForm, {
    title: '',
    description: '',
    type: '',
    target_date: null,
    target_value: null,
    unit: ''
  })
}

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
  return date ? dayjs(date).format('YYYY-MM-DD') : ''
}

const disabledDate = (current) => {
  return current && current < dayjs().startOf('day')
}
</script>

<style scoped>
.profile-container {
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #FDF2F8 0%, #F7D9E6 50%, #E8C5E8 100%);
  min-height: 100vh;
}

.profile-header {
  margin-bottom: 24px;
}

.profile-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.profile-header p {
  color: #6b7280;
  font-size: 16px;
}

.profile-card {
  margin-bottom: 32px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.health-stats {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.stat-category {
  font-size: 14px;
  color: #6b7280;
  margin-left: 8px;
}

.empty-goals {
  text-align: center;
  padding: 40px 0;
}

.goals-list {
  margin-top: 16px;
}

.goal-card {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.goal-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.goal-description {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 12px;
}

.goal-progress {
  margin-bottom: 12px;
}

.goal-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
}

.goal-type {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
