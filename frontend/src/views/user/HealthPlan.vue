<template>
  <div class="health-plan-container">
    <div class="plan-header">
      <h1>健康计划</h1>
      <p>AI驱动的个性化健康管理方案</p>
      <div class="header-actions">
        <a-button type="primary" @click="showGenerateModal = true">
          <template #icon>
            <PlusOutlined />
          </template>
          生成新计划
        </a-button>
      </div>
    </div>

    <!-- 计划列表 -->
    <div v-if="healthPlanStore.plans.length === 0 && !healthPlanStore.loading" class="empty-plans">
      <a-empty description="暂无健康计划">
        <a-button type="primary" @click="showGenerateModal = true">
          创建第一个健康计划
        </a-button>
      </a-empty>
    </div>

    <div v-else class="plans-grid">
      <a-row :gutter="24">
        <a-col 
          v-for="plan in healthPlanStore.plans" 
          :key="plan.id"
          :span="24" :lg="12" :xl="8"
        >
          <a-card 
            class="plan-card"
            :class="{ 'active-plan': plan.status === 'active' }"
            @click="viewPlanDetail(plan.id)"
          >
            <template #title>
              <div class="plan-title">
                <span>{{ plan.title }}</span>
                <a-tag :color="getPlanStatusColor(plan.status)">
                  {{ getPlanStatusLabel(plan.status) }}
                </a-tag>
              </div>
            </template>

            <template #extra>
              <a-dropdown>
                <a-button type="text" size="small">
                  <template #icon>
                    <MoreOutlined />
                  </template>
                </a-button>
                <template #overlay>
                  <a-menu>
                    <a-menu-item @click.stop="viewPlanDetail(plan.id)">查看详情</a-menu-item>
                    <a-menu-item @click.stop="exportPlan(plan.id)">导出计划</a-menu-item>
                    <a-menu-item @click.stop="deletePlan(plan.id)" danger>删除计划</a-menu-item>
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
        </a-col>
      </a-row>
    </div>

    <!-- 生成计划模态框 -->
    <a-modal
      v-model:open="showGenerateModal"
      title="生成个性化健康计划"
      @ok="handleGeneratePlan"
      @cancel="resetGenerateForm"
      :confirm-loading="healthPlanStore.generatingPlan"
      width="600px"
    >
      <a-form
        :model="generateForm"
        :rules="generateRules"
        layout="vertical"
        ref="generateFormRef"
      >
        <a-form-item label="计划标题" name="title">
          <a-input v-model:value="generateForm.title" placeholder="请输入计划标题" />
        </a-form-item>

        <a-form-item label="健康目标" name="goals">
          <a-select 
            v-model:value="generateForm.goals" 
            mode="multiple"
            placeholder="请选择您的健康目标"
          >
            <a-select-option value="weight_loss">减重</a-select-option>
            <a-select-option value="weight_gain">增重</a-select-option>
            <a-select-option value="muscle_gain">增肌</a-select-option>
            <a-select-option value="fitness">提升体能</a-select-option>
            <a-select-option value="nutrition">改善营养</a-select-option>
            <a-select-option value="sleep">改善睡眠</a-select-option>
            <a-select-option value="stress">压力管理</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="计划模块" name="modules">
          <a-checkbox-group v-model:value="generateForm.modules">
            <a-row>
              <a-col :span="12">
                <a-checkbox value="diet">饮食计划</a-checkbox>
              </a-col>
              <a-col :span="12">
                <a-checkbox value="exercise">运动计划</a-checkbox>
              </a-col>
              <a-col :span="12">
                <a-checkbox value="weight">体重管理</a-checkbox>
              </a-col>
              <a-col :span="12">
                <a-checkbox value="sleep">睡眠计划</a-checkbox>
              </a-col>
              <a-col :span="12">
                <a-checkbox value="mental">心理健康</a-checkbox>
              </a-col>
            </a-row>
          </a-checkbox-group>
        </a-form-item>

        <a-form-item label="计划时长" name="duration">
          <a-select v-model:value="generateForm.duration" placeholder="请选择计划时长">
            <a-select-option :value="7">1周</a-select-option>
            <a-select-option :value="14">2周</a-select-option>
            <a-select-option :value="30">1个月</a-select-option>
            <a-select-option :value="60">2个月</a-select-option>
            <a-select-option :value="90">3个月</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="特殊要求" name="requirements">
          <a-textarea 
            v-model:value="generateForm.requirements" 
            placeholder="请描述您的特殊要求或限制条件"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 计划详情模态框 -->
    <a-modal
      v-model:open="showDetailModal"
      :title="currentPlanDetail?.title"
      :footer="null"
      width="800px"
      class="plan-detail-modal"
    >
      <div v-if="currentPlanDetail" class="plan-detail">
        <div class="detail-header">
          <div class="detail-meta">
            <a-tag :color="getPlanStatusColor(currentPlanDetail.status)">
              {{ getPlanStatusLabel(currentPlanDetail.status) }}
            </a-tag>
            <span class="detail-date">{{ formatDate(currentPlanDetail.created_at) }}</span>
          </div>
          <div class="detail-actions">
            <a-button @click="exportPlan(currentPlanDetail.id)">
              <template #icon>
                <DownloadOutlined />
              </template>
              导出计划
            </a-button>
          </div>
        </div>

        <div class="detail-description">
          <p>{{ currentPlanDetail.description }}</p>
        </div>

        <div class="detail-progress">
          <h4>整体进度</h4>
          <a-progress 
            :percent="healthPlanStore.currentPlanProgress" 
            :status="currentPlanDetail.status === 'completed' ? 'success' : 'active'"
          />
        </div>

        <div class="detail-modules">
          <h4>计划模块</h4>
          <a-tabs v-model:activeKey="activeModuleTab">
            <a-tab-pane 
              v-for="module in currentPlanDetail.plan_modules" 
              :key="module.type"
              :tab="getModuleLabel(module.type)"
            >
              <div class="module-content">
                <h5>{{ module.title }}</h5>
                <p>{{ module.description }}</p>
                
                <div v-if="module.daily_tasks" class="daily-tasks">
                  <h6>每日任务</h6>
                  <a-list
                    :data-source="module.daily_tasks"
                    size="small"
                  >
                    <template #renderItem="{ item }">
                      <a-list-item>
                        <a-checkbox v-model:checked="item.completed">
                          {{ item.task }}
                        </a-checkbox>
                        <template #actions>
                          <span class="task-time">{{ item.time }}</span>
                        </template>
                      </a-list-item>
                    </template>
                  </a-list>
                </div>

                <div v-if="module.weekly_goals" class="weekly-goals">
                  <h6>周目标</h6>
                  <a-list
                    :data-source="module.weekly_goals"
                    size="small"
                  >
                    <template #renderItem="{ item }">
                      <a-list-item>
                        <div class="goal-item">
                          <span>{{ item.goal }}</span>
                          <a-progress 
                            :percent="item.progress || 0" 
                            size="small"
                            style="width: 100px;"
                          />
                        </div>
                      </a-list-item>
                    </template>
                  </a-list>
                </div>

                <div v-if="module.tips" class="module-tips">
                  <h6>小贴士</h6>
                  <ul>
                    <li v-for="tip in module.tips" :key="tip">{{ tip }}</li>
                  </ul>
                </div>
              </div>
            </a-tab-pane>
          </a-tabs>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  PlusOutlined, 
  MoreOutlined, 
  CalendarOutlined, 
  ClockCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'
import { useHealthPlanStore } from '../../stores/healthPlan.js'
import { useUserStore } from '../../stores/user.js'

const healthPlanStore = useHealthPlanStore()
const userStore = useUserStore()

// 响应式数据
const showGenerateModal = ref(false)
const showDetailModal = ref(false)
const currentPlanDetail = ref(null)
const activeModuleTab = ref('diet')
const generateFormRef = ref()

// 表单数据
const generateForm = reactive({
  title: '',
  goals: [],
  modules: ['diet', 'exercise'],
  duration: 30,
  requirements: ''
})

// 表单验证规则
const generateRules = {
  title: [{ required: true, message: '请输入计划标题' }],
  goals: [{ required: true, message: '请选择至少一个健康目标' }],
  modules: [{ required: true, message: '请选择至少一个计划模块' }],
  duration: [{ required: true, message: '请选择计划时长' }]
}

// 生命周期
onMounted(async () => {
  await healthPlanStore.fetchPlans()
})

// 方法
const handleGeneratePlan = async () => {
  try {
    await generateFormRef.value.validate()
    
    const planRequest = {
      ...generateForm,
      user_profile: userStore.userProfile,
      health_data: userStore.healthData,
      health_goals: userStore.healthGoals
    }

    await healthPlanStore.generatePlan(planRequest)
    message.success('健康计划生成成功！')
    resetGenerateForm()
  } catch (error) {
    if (error.errorFields) {
      return
    }
    message.error('生成计划失败，请重试')
  }
}

const viewPlanDetail = async (planId) => {
  try {
    currentPlanDetail.value = await healthPlanStore.fetchPlanDetail(planId)
    showDetailModal.value = true
    activeModuleTab.value = currentPlanDetail.value.plan_modules?.[0]?.type || 'diet'
  } catch (error) {
    message.error('获取计划详情失败')
  }
}

const exportPlan = async (planId, format = 'pdf') => {
  try {
    await healthPlanStore.exportPlan(planId, format)
    message.success('计划导出成功！')
  } catch (error) {
    message.error('导出失败，请重试')
  }
}

const deletePlan = async (planId) => {
  try {
    await healthPlanStore.deletePlan(planId)
    message.success('计划删除成功')
  } catch (error) {
    message.error('删除失败，请重试')
  }
}

const resetGenerateForm = () => {
  showGenerateModal.value = false
  Object.assign(generateForm, {
    title: '',
    goals: [],
    modules: ['diet', 'exercise'],
    duration: 30,
    requirements: ''
  })
}

const getPlanStatusColor = (status) => {
  const colors = {
    active: 'green',
    completed: 'blue',
    paused: 'orange',
    cancelled: 'red'
  }
  return colors[status] || 'default'
}

const getPlanStatusLabel = (status) => {
  const labels = {
    active: '进行中',
    completed: '已完成',
    paused: '已暂停',
    cancelled: '已取消'
  }
  return labels[status] || status
}

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
.health-plan-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.plan-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.plan-header p {
  color: #6b7280;
  margin: 4px 0 0 0;
}

.empty-plans {
  text-align: center;
  padding: 60px 0;
}

.plans-grid {
  margin-top: 24px;
}

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

.plan-detail-modal .ant-modal-body {
  padding: 24px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-date {
  color: #6b7280;
  font-size: 14px;
}

.detail-description {
  margin-bottom: 24px;
  color: #374151;
  line-height: 1.6;
}

.detail-progress {
  margin-bottom: 24px;
}

.detail-progress h4 {
  margin-bottom: 12px;
  color: #1f2937;
}

.detail-modules h4 {
  margin-bottom: 16px;
  color: #1f2937;
}

.module-content {
  padding: 16px 0;
}

.module-content h5 {
  margin-bottom: 8px;
  color: #1f2937;
  font-size: 16px;
}

.module-content h6 {
  margin: 16px 0 8px 0;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
}

.daily-tasks,
.weekly-goals {
  margin-bottom: 16px;
}

.task-time {
  color: #9ca3af;
  font-size: 12px;
}

.goal-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.module-tips ul {
  margin: 0;
  padding-left: 20px;
}

.module-tips li {
  margin-bottom: 4px;
  color: #6b7280;
}
</style>
