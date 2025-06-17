<template>
  <div class="family-members-page">
    <!-- 页面头部 -->
    <div class="page-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">家庭成员管理</h1>
          <p class="text-gray-600 mt-1">
            管理 {{ familyStore.currentFamily?.family_name }} 的成员
          </p>
        </div>
        <div class="flex gap-3">
          <a-button
            v-if="familyStore.canInviteMembers"
            type="primary"
            @click="showInviteModal = true"
          >
            <UserAddOutlined />
            邀请成员
          </a-button>
          <a-button @click="refreshMembers">
            <ReloadOutlined />
            刷新
          </a-button>
        </div>
      </div>
    </div>

    <!-- 成员切换器 -->
    <div class="mb-6">
      <MemberSwitcher />
    </div>

    <!-- 成员列表 -->
    <div class="members-section">
      <a-card title="成员列表" class="members-card">
        <template #extra>
          <a-space>
            <a-input-search
              v-model:value="searchKeyword"
              placeholder="搜索成员"
              style="width: 200px"
              @search="handleSearch"
            />
            <a-select
              v-model:value="roleFilter"
              placeholder="筛选角色"
              style="width: 120px"
              @change="handleRoleFilter"
            >
              <a-select-option value="">全部</a-select-option>
              <a-select-option value="Owner">拥有者</a-select-option>
              <a-select-option value="Manager">管理员</a-select-option>
              <a-select-option value="Member">成员</a-select-option>
            </a-select>
          </a-space>
        </template>

        <div class="members-grid">
          <div
            v-for="member in filteredMembers"
            :key="member.user_id"
            class="member-card"
            :class="{ 'active-member': member.user_id === familyStore.activeMember?.user_id }"
          >
            <!-- 成员头像和基本信息 -->
            <div class="member-header">
              <a-avatar
                :size="64"
                :src="member.avatar"
                class="member-avatar"
              >
                {{ member.display_name?.charAt(0) }}
              </a-avatar>
              <div class="member-info">
                <h3 class="member-name">{{ member.display_name }}</h3>
                <p class="member-email">{{ member.email }}</p>
                <div class="member-badges">
                  <a-tag :color="getRoleColor(member.role)">
                    {{ getRoleText(member.role) }}
                  </a-tag>
                  <a-tag v-if="member.is_current_user" color="blue">
                    当前用户
                  </a-tag>
                  <a-tag v-if="member.user_id === familyStore.activeMember?.user_id" color="green">
                    活跃成员
                  </a-tag>
                </div>
              </div>
            </div>

            <!-- 成员状态 -->
            <div class="member-status">
              <div class="status-item">
                <span class="status-label">状态:</span>
                <a-badge
                  :status="member.status === 'active' ? 'success' : 'default'"
                  :text="member.status === 'active' ? '在线' : '离线'"
                />
              </div>
              <div class="status-item">
                <span class="status-label">最后活跃:</span>
                <span class="status-value">{{ formatTime(member.last_active) }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">加入时间:</span>
                <span class="status-value">{{ formatTime(member.joined_at) }}</span>
              </div>
            </div>

            <!-- 健康数据概览 -->
            <div class="member-health-overview">
              <h4 class="overview-title">健康概览</h4>
              <div class="health-metrics">
                <div class="metric-item">
                  <span class="metric-label">今日步数</span>
                  <span class="metric-value">{{ member.health_data?.steps || '--' }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">睡眠时长</span>
                  <span class="metric-value">{{ member.health_data?.sleep_hours || '--' }}h</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">BMI</span>
                  <span class="metric-value">{{ member.health_data?.bmi || '--' }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="member-actions">
              <a-space>
                <a-button
                  size="small"
                  @click="switchToMember(member)"
                  :disabled="member.user_id === familyStore.activeMember?.user_id"
                >
                  切换到此成员
                </a-button>
                <a-button
                  size="small"
                  @click="viewMemberHealth(member)"
                >
                  查看健康数据
                </a-button>
                <a-dropdown v-if="canManageMember(member)">
                  <a-button size="small">
                    更多 <DownOutlined />
                  </a-button>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item @click="editMember(member)">
                        编辑信息
                      </a-menu-item>
                      <a-menu-item @click="managePermissions(member)">
                        权限管理
                      </a-menu-item>
                      <a-menu-item
                        v-if="canRemoveMember(member)"
                        @click="removeMember(member)"
                        class="text-red-500"
                      >
                        移除成员
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </a-space>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <a-empty v-if="filteredMembers.length === 0" description="没有找到匹配的成员">
          <a-button
            v-if="familyStore.canInviteMembers"
            type="primary"
            @click="showInviteModal = true"
          >
            邀请第一个成员
          </a-button>
        </a-empty>
      </a-card>
    </div>

    <!-- 邀请成员弹窗 -->
    <a-modal
      v-model:open="showInviteModal"
      title="邀请家庭成员"
      @ok="handleInviteMember"
      :confirm-loading="inviting"
    >
      <a-form :model="inviteForm" layout="vertical">
        <a-form-item label="邮箱地址" required>
          <a-input
            v-model:value="inviteForm.email"
            placeholder="请输入成员邮箱"
            type="email"
          />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="inviteForm.role" placeholder="选择角色">
            <a-select-option value="Member">普通成员</a-select-option>
            <a-select-option value="Manager" v-if="familyStore.isAdmin">管理员</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea
            v-model:value="inviteForm.note"
            placeholder="邀请备注（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 成员管理弹窗 -->
    <a-modal
      v-model:open="showMemberManagement"
      title="成员管理"
      width="800px"
      :footer="null"
    >
      <MemberManagement v-if="showMemberManagement" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  UserAddOutlined,
  ReloadOutlined,
  DownOutlined
} from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import { memberAPI } from '@/api/family'
import MemberSwitcher from '@/components/family/MemberSwitcher.vue'
import MemberManagement from '@/components/family/MemberManagement.vue'

const router = useRouter()
const familyStore = useFamilyStore()

// 响应式数据
const showInviteModal = ref(false)
const showMemberManagement = ref(false)
const inviting = ref(false)
const searchKeyword = ref('')
const roleFilter = ref('')

// 邀请表单
const inviteForm = ref({
  email: '',
  role: 'Member',
  note: ''
})

// 计算属性
const filteredMembers = computed(() => {
  let members = familyStore.familyMembers || []
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    members = members.filter(member =>
      member.display_name?.toLowerCase().includes(keyword) ||
      member.email?.toLowerCase().includes(keyword)
    )
  }
  
  // 角色过滤
  if (roleFilter.value) {
    members = members.filter(member => member.role === roleFilter.value)
  }
  
  return members
})

// 方法
const refreshMembers = async () => {
  if (familyStore.currentFamily) {
    await familyStore.fetchFamilyMembers(familyStore.currentFamily.family_id)
    message.success('成员列表已刷新')
  }
}

const handleSearch = (value) => {
  searchKeyword.value = value
}

const handleRoleFilter = (value) => {
  roleFilter.value = value
}

const getRoleColor = (role) => {
  const colors = {
    'Owner': 'gold',
    'Manager': 'blue',
    'Member': 'default'
  }
  return colors[role] || 'default'
}

const getRoleText = (role) => {
  const texts = {
    'Owner': '拥有者',
    'Manager': '管理员',
    'Member': '成员'
  }
  return texts[role] || '成员'
}

const formatTime = (time) => {
  if (!time) return '从未'
  return new Date(time).toLocaleString()
}

const canManageMember = (member) => {
  return familyStore.canManageMembers && !member.is_current_user
}

const canRemoveMember = (member) => {
  return familyStore.canManageMembers && 
         !member.is_current_user && 
         member.role !== 'Owner'
}

const switchToMember = async (member) => {
  try {
    await familyStore.switchActiveMember(member.user_id)
  } catch (error) {
    console.error('切换成员失败:', error)
  }
}

const viewMemberHealth = (member) => {
  router.push(`/family/member/${member.user_id}/health`)
}

const editMember = (member) => {
  // 打开编辑成员弹窗
  showMemberManagement.value = true
}

const managePermissions = (member) => {
  // 打开权限管理弹窗
  showMemberManagement.value = true
}

const removeMember = (member) => {
  Modal.confirm({
    title: '确认移除成员',
    content: `确定要移除成员 ${member.display_name} 吗？此操作不可撤销。`,
    onOk: async () => {
      try {
        await memberAPI.removeMember(familyStore.currentFamily.family_id, member.user_id)
        message.success('成员移除成功')
        await refreshMembers()
      } catch (error) {
        console.error('移除成员失败:', error)
        message.error('移除成员失败')
      }
    }
  })
}

const handleInviteMember = async () => {
  if (!inviteForm.value.email) {
    message.error('请输入邮箱地址')
    return
  }

  inviting.value = true
  try {
    await familyStore.inviteMember(inviteForm.value)
    showInviteModal.value = false
    inviteForm.value = {
      email: '',
      role: 'Member',
      note: ''
    }
  } catch (error) {
    console.error('邀请失败:', error)
  } finally {
    inviting.value = false
  }
}

// 生命周期
onMounted(async () => {
  if (familyStore.currentFamily) {
    await refreshMembers()
  }
})
</script>

<style scoped>
.family-members-page {
  @apply p-6 min-h-screen bg-gray-50;
}

.members-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}

.member-card {
  @apply bg-white rounded-lg shadow-sm border p-6 transition-all duration-300 hover:shadow-md;
}

.member-card.active-member {
  @apply border-blue-500 bg-blue-50;
}

.member-header {
  @apply flex items-start gap-4 mb-4;
}

.member-avatar {
  @apply flex-shrink-0;
}

.member-info {
  @apply flex-1 min-w-0;
}

.member-name {
  @apply text-lg font-semibold text-gray-900 mb-1;
}

.member-email {
  @apply text-sm text-gray-600 mb-2;
}

.member-badges {
  @apply flex flex-wrap gap-1;
}

.member-status {
  @apply space-y-2 mb-4 p-3 bg-gray-50 rounded;
}

.status-item {
  @apply flex justify-between text-sm;
}

.status-label {
  @apply text-gray-600;
}

.status-value {
  @apply text-gray-900;
}

.member-health-overview {
  @apply mb-4;
}

.overview-title {
  @apply text-sm font-medium text-gray-900 mb-2;
}

.health-metrics {
  @apply grid grid-cols-3 gap-2;
}

.metric-item {
  @apply text-center p-2 bg-gray-50 rounded;
}

.metric-label {
  @apply block text-xs text-gray-600 mb-1;
}

.metric-value {
  @apply block text-sm font-semibold text-gray-900;
}

.member-actions {
  @apply pt-4 border-t border-gray-200;
}

@media (max-width: 768px) {
  .family-members-page {
    @apply p-4;
  }
  
  .members-grid {
    @apply grid-cols-1;
  }
  
  .member-header {
    @apply flex-col items-center text-center;
  }
  
  .health-metrics {
    @apply grid-cols-1 gap-1;
  }
}
</style>
