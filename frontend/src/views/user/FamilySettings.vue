<template>
  <div class="family-settings-page">
    <!-- 页面头部 -->
    <div class="page-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">家庭设置</h1>
          <p class="text-gray-600 mt-1">
            管理 {{ familyStore.currentFamily?.family_name }} 的设置和权限
          </p>
        </div>
      </div>
    </div>

    <a-row :gutter="24">
      <!-- 左侧：基本设置 -->
      <a-col :span="16">
        <!-- 家庭基本信息 -->
        <a-card title="家庭基本信息" class="settings-card mb-6">
          <a-form
            :model="familyForm"
            layout="vertical"
            @finish="handleUpdateFamily"
          >
            <a-form-item label="家庭名称" name="family_name">
              <a-input
                v-model:value="familyForm.family_name"
                placeholder="请输入家庭名称"
                :disabled="!familyStore.isAdmin"
              />
            </a-form-item>
            
            <a-form-item label="家庭描述" name="description">
              <a-textarea
                v-model:value="familyForm.description"
                placeholder="请输入家庭描述"
                :rows="3"
                :disabled="!familyStore.isAdmin"
              />
            </a-form-item>

            <a-form-item v-if="familyStore.isAdmin">
              <a-button type="primary" html-type="submit" :loading="updating">
                保存更改
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- 健康告警设置 -->
        <a-card title="健康告警设置" class="settings-card mb-6">
          <div class="alert-settings">
            <div class="setting-item">
              <div class="setting-header">
                <h4>步数告警</h4>
                <a-switch
                  v-model:checked="alertSettings.steps_alert_enabled"
                  @change="updateAlertSetting('steps_alert_enabled', $event)"
                />
              </div>
              <p class="setting-description">当成员步数低于设定值时发送告警</p>
              <div v-if="alertSettings.steps_alert_enabled" class="setting-config">
                <a-input-number
                  v-model:value="alertSettings.steps_threshold"
                  :min="1000"
                  :max="20000"
                  :step="1000"
                  addon-before="阈值"
                  addon-after="步"
                  @change="updateAlertSetting('steps_threshold', $event)"
                />
              </div>
            </div>

            <a-divider />

            <div class="setting-item">
              <div class="setting-header">
                <h4>睡眠告警</h4>
                <a-switch
                  v-model:checked="alertSettings.sleep_alert_enabled"
                  @change="updateAlertSetting('sleep_alert_enabled', $event)"
                />
              </div>
              <p class="setting-description">当成员睡眠时间不足时发送告警</p>
              <div v-if="alertSettings.sleep_alert_enabled" class="setting-config">
                <a-input-number
                  v-model:value="alertSettings.sleep_threshold"
                  :min="4"
                  :max="12"
                  :step="0.5"
                  :precision="1"
                  addon-before="最少"
                  addon-after="小时"
                  @change="updateAlertSetting('sleep_threshold', $event)"
                />
              </div>
            </div>

            <a-divider />

            <div class="setting-item">
              <div class="setting-header">
                <h4>体重异常告警</h4>
                <a-switch
                  v-model:checked="alertSettings.weight_alert_enabled"
                  @change="updateAlertSetting('weight_alert_enabled', $event)"
                />
              </div>
              <p class="setting-description">当成员体重变化超过设定范围时发送告警</p>
              <div v-if="alertSettings.weight_alert_enabled" class="setting-config">
                <a-input-number
                  v-model:value="alertSettings.weight_change_threshold"
                  :min="1"
                  :max="10"
                  :step="0.5"
                  :precision="1"
                  addon-before="变化超过"
                  addon-after="kg/周"
                  @change="updateAlertSetting('weight_change_threshold', $event)"
                />
              </div>
            </div>
          </div>
        </a-card>

        <!-- 隐私设置 -->
        <a-card title="隐私设置" class="settings-card">
          <div class="privacy-settings">
            <div class="setting-item">
              <div class="setting-header">
                <h4>数据共享</h4>
                <a-switch
                  v-model:checked="privacySettings.data_sharing_enabled"
                  @change="updatePrivacySetting('data_sharing_enabled', $event)"
                />
              </div>
              <p class="setting-description">允许家庭成员查看彼此的健康数据</p>
            </div>

            <a-divider />

            <div class="setting-item">
              <div class="setting-header">
                <h4>活动可见性</h4>
                <a-select
                  v-model:value="privacySettings.activity_visibility"
                  style="width: 200px"
                  @change="updatePrivacySetting('activity_visibility', $event)"
                >
                  <a-select-option value="all">所有成员可见</a-select-option>
                  <a-select-option value="admin_only">仅管理员可见</a-select-option>
                  <a-select-option value="self_only">仅自己可见</a-select-option>
                </a-select>
              </div>
              <p class="setting-description">设置活动数据的可见范围</p>
            </div>
          </div>
        </a-card>
      </a-col>

      <!-- 右侧：快捷操作和信息 -->
      <a-col :span="8">
        <!-- 家庭统计 -->
        <a-card title="家庭统计" class="stats-card mb-6">
          <div class="family-stats">
            <div class="stat-item">
              <div class="stat-value">{{ familyStore.familyMembers.length }}</div>
              <div class="stat-label">家庭成员</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ activeMembersCount }}</div>
              <div class="stat-label">活跃成员</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ familyStore.dashboardData.challenges.length }}</div>
              <div class="stat-label">进行中挑战</div>
            </div>
          </div>
        </a-card>

        <!-- 快捷操作 -->
        <a-card title="快捷操作" class="actions-card mb-6">
          <div class="action-buttons">
            <a-button
              type="primary"
              block
              class="mb-3"
              @click="router.push('/family/members')"
            >
              <TeamOutlined />
              管理成员
            </a-button>
            
            <a-button
              block
              class="mb-3"
              @click="router.push('/family/challenges')"
            >
              <TrophyOutlined />
              管理挑战
            </a-button>
            
            <a-button
              block
              class="mb-3"
              @click="router.push('/family/alerts')"
            >
              <BellOutlined />
              查看告警
            </a-button>
            
            <a-button
              v-if="familyStore.userRole === 'Owner'"
              block
              danger
              @click="showDeleteConfirm"
            >
              <DeleteOutlined />
              删除家庭
            </a-button>
          </div>
        </a-card>

        <!-- 邀请链接 -->
        <a-card title="邀请链接" class="invite-card" v-if="familyStore.canInviteMembers">
          <div class="invite-section">
            <p class="text-sm text-gray-600 mb-3">
              分享此链接邀请新成员加入家庭
            </p>
            <a-input-group compact>
              <a-input
                v-model:value="inviteLink"
                readonly
                style="width: calc(100% - 80px)"
              />
              <a-button @click="copyInviteLink">
                <CopyOutlined />
              </a-button>
            </a-input-group>
            <a-button
              type="link"
              size="small"
              @click="generateNewInviteLink"
              class="mt-2"
            >
              生成新链接
            </a-button>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  TeamOutlined,
  TrophyOutlined,
  BellOutlined,
  DeleteOutlined,
  CopyOutlined
} from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import { familyAPI } from '@/api/family'
import { useRouter } from 'vue-router'

const familyStore = useFamilyStore()

const router = useRouter()

// 响应式数据
const updating = ref(false)
const inviteLink = ref('')

// 表单数据
const familyForm = reactive({
  family_name: '',
  description: ''
})

// 告警设置
const alertSettings = reactive({
  steps_alert_enabled: true,
  steps_threshold: 5000,
  sleep_alert_enabled: true,
  sleep_threshold: 6.0,
  weight_alert_enabled: false,
  weight_change_threshold: 2.0
})

// 隐私设置
const privacySettings = reactive({
  data_sharing_enabled: true,
  activity_visibility: 'all'
})

// 计算属性
const activeMembersCount = computed(() => {
  return familyStore.familyMembers.filter(member => member.status === 'active').length
})

// 方法
const handleUpdateFamily = async () => {
  updating.value = true
  try {
    // 调用API更新家庭信息
    await familyAPI.updateFamily(familyStore.currentFamily.family_id, familyForm)
    message.success('家庭信息更新成功')
    
    // 刷新家庭信息
    await familyStore.selectFamily(familyStore.currentFamily.family_id)
  } catch (error) {
    console.error('更新家庭信息失败:', error)
    message.error('更新失败')
  } finally {
    updating.value = false
  }
}

const updateAlertSetting = async (key, value) => {
  try {
    // 调用API更新告警设置
    await familyAPI.updateAlertSettings(familyStore.currentFamily.family_id, {
      [key]: value
    })
    message.success('告警设置已更新')
  } catch (error) {
    console.error('更新告警设置失败:', error)
    message.error('更新失败')
  }
}

const updatePrivacySetting = async (key, value) => {
  try {
    // 调用API更新隐私设置
    await familyAPI.updatePrivacySettings(familyStore.currentFamily.family_id, {
      [key]: value
    })
    message.success('隐私设置已更新')
  } catch (error) {
    console.error('更新隐私设置失败:', error)
    message.error('更新失败')
  }
}

const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(inviteLink.value)
    message.success('邀请链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    message.error('复制失败')
  }
}

const generateNewInviteLink = async () => {
  try {
    const response = await familyAPI.generateInviteLink(familyStore.currentFamily.family_id)
    inviteLink.value = response.invite_link
    message.success('新的邀请链接已生成')
  } catch (error) {
    console.error('生成邀请链接失败:', error)
    message.error('生成失败')
  }
}

const showDeleteConfirm = () => {
  Modal.confirm({
    title: '确认删除家庭',
    content: '删除家庭将移除所有成员和数据，此操作不可撤销。确定要继续吗？',
    okText: '确认删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await familyAPI.deleteFamily(familyStore.currentFamily.family_id)
        message.success('家庭已删除')
        
        // 重置家庭状态并跳转
        familyStore.resetState()
        router.push('/')
      } catch (error) {
        console.error('删除家庭失败:', error)
        message.error('删除失败')
      }
    }
  })
}

// 生命周期
onMounted(async () => {
  if (familyStore.currentFamily) {
    // 初始化表单数据
    Object.assign(familyForm, {
      family_name: familyStore.currentFamily.family_name,
      description: familyStore.currentFamily.description
    })

    // 生成邀请链接
    try {
      const response = await familyAPI.getInviteLink(familyStore.currentFamily.family_id)
      inviteLink.value = response.invite_link
    } catch (error) {
      console.error('获取邀请链接失败:', error)
    }
  }
})
</script>

<style scoped>
.family-settings-page {
  @apply p-6 min-h-screen bg-gray-50;
}

.settings-card {
  @apply shadow-sm;
}

.alert-settings,
.privacy-settings {
  @apply space-y-4;
}

.setting-item {
  @apply space-y-2;
}

.setting-header {
  @apply flex justify-between items-center;
}

.setting-header h4 {
  @apply text-base font-medium text-gray-900 m-0;
}

.setting-description {
  @apply text-sm text-gray-600 m-0;
}

.setting-config {
  @apply mt-3;
}

.family-stats {
  @apply grid grid-cols-1 gap-4;
}

.stat-item {
  @apply text-center p-4 bg-gray-50 rounded-lg;
}

.stat-value {
  @apply text-2xl font-bold text-blue-600;
}

.stat-label {
  @apply text-sm text-gray-600 mt-1;
}

.action-buttons {
  @apply space-y-0;
}

.invite-section {
  @apply space-y-3;
}

@media (max-width: 768px) {
  .family-settings-page {
    @apply p-4;
  }
  
  .family-stats {
    @apply grid-cols-3;
  }
  
  .stat-item {
    @apply p-2;
  }
  
  .stat-value {
    @apply text-lg;
  }
}
</style>
