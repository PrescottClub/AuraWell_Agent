<template>
  <div class="member-switcher">
    <!-- 家庭选择器 -->
    <div class="family-selector mb-4" v-if="familyStore.userFamilies.length > 1">
      <a-select
        v-model:value="selectedFamilyId"
        placeholder="选择家庭"
        style="width: 200px"
        @change="handleFamilyChange"
        :loading="familyStore.loading.families"
      >
        <a-select-option
          v-for="family in familyStore.userFamilies"
          :key="family.family_id"
          :value="family.family_id"
        >
          <div class="flex items-center">
            <HomeOutlined class="mr-2" />
            {{ family.family_name }}
            <a-tag v-if="family.role === 'Owner'" color="gold" size="small" class="ml-2">
              管理员
            </a-tag>
          </div>
        </a-select-option>
      </a-select>
    </div>

    <!-- 成员切换器 -->
    <div class="member-selector">
      <a-select
        v-model:value="selectedMemberId"
        placeholder="选择家庭成员"
        style="width: 250px"
        @change="handleMemberChange"
        :loading="familyStore.loading.switching"
        :disabled="!familyStore.currentFamily"
      >
        <template #suffixIcon>
          <UserSwitchOutlined />
        </template>
        
        <a-select-option
          v-for="member in familyStore.familyMembers"
          :key="member.user_id"
          :value="member.user_id"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <a-avatar
                :size="24"
                :src="member.avatar"
                class="mr-2"
              >
                {{ member.display_name?.charAt(0) }}
              </a-avatar>
              <span>{{ member.display_name }}</span>
              <a-tag
                v-if="member.is_current_user"
                color="blue"
                size="small"
                class="ml-2"
              >
                我
              </a-tag>
            </div>
            <div class="flex items-center">
              <a-tag
                :color="getRoleColor(member.role)"
                size="small"
              >
                {{ getRoleText(member.role) }}
              </a-tag>
              <div
                v-if="member.user_id === familyStore.activeMember?.user_id"
                class="ml-2 w-2 h-2 bg-green-500 rounded-full"
                title="当前活跃成员"
              ></div>
            </div>
          </div>
        </a-select-option>
      </a-select>

      <!-- 活跃成员信息显示 -->
      <div
        v-if="familyStore.activeMember"
        class="active-member-info mt-2 p-2 bg-blue-50 rounded-lg"
      >
        <div class="flex items-center text-sm text-blue-600">
          <CheckCircleOutlined class="mr-1" />
          当前为 <strong class="mx-1">{{ familyStore.activeMember.display_name }}</strong> 生成健康建议
        </div>
      </div>
    </div>

    <!-- 快速操作按钮 -->
    <div class="quick-actions mt-4 flex gap-2">
      <a-button
        v-if="familyStore.canInviteMembers"
        type="primary"
        ghost
        size="small"
        @click="showInviteModal = true"
      >
        <UserAddOutlined />
        邀请成员
      </a-button>
      
      <a-button
        v-if="familyStore.canManageMembers"
        size="small"
        @click="showMemberManagement = true"
      >
        <SettingOutlined />
        成员管理
      </a-button>
      
      <a-button
        size="small"
        @click="$router.push('/family/dashboard')"
      >
        <DashboardOutlined />
        家庭仪表盘
      </a-button>
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
import { ref, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  HomeOutlined,
  UserSwitchOutlined,
  UserAddOutlined,
  SettingOutlined,
  DashboardOutlined,
  CheckCircleOutlined
} from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import MemberManagement from './MemberManagement.vue'

const familyStore = useFamilyStore()

// 响应式数据
const selectedFamilyId = ref(null)
const selectedMemberId = ref(null)
const showInviteModal = ref(false)
const showMemberManagement = ref(false)
const inviting = ref(false)

// 邀请表单
const inviteForm = ref({
  email: '',
  role: 'Member',
  note: ''
})

// 计算属性
const currentFamily = computed(() => familyStore.currentFamily)
const activeMember = computed(() => familyStore.activeMember)

// 方法
const handleFamilyChange = async (familyId) => {
  try {
    await familyStore.selectFamily(familyId)
    selectedMemberId.value = familyStore.activeMember?.user_id
  } catch (error) {
    console.error('切换家庭失败:', error)
  }
}

const handleMemberChange = async (memberId) => {
  try {
    await familyStore.switchActiveMember(memberId)
  } catch (error) {
    console.error('切换成员失败:', error)
  }
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

// 监听器
watch(currentFamily, (newFamily) => {
  if (newFamily) {
    selectedFamilyId.value = newFamily.family_id
  }
})

watch(activeMember, (newMember) => {
  if (newMember) {
    selectedMemberId.value = newMember.user_id
  }
})

// 生命周期
onMounted(async () => {
  try {
    await familyStore.fetchUserFamilies()
    if (familyStore.currentFamily) {
      selectedFamilyId.value = familyStore.currentFamily.family_id
      selectedMemberId.value = familyStore.activeMember?.user_id
    }
  } catch (error) {
    console.error('初始化家庭数据失败:', error)
  }
})
</script>

<style scoped>
.member-switcher {
  @apply p-4 bg-white rounded-lg shadow-sm border;
}

.family-selector .ant-select {
  @apply w-full;
}

.member-selector .ant-select {
  @apply w-full;
}

.active-member-info {
  @apply transition-all duration-300;
}

.quick-actions {
  @apply flex flex-wrap gap-2;
}

@media (max-width: 768px) {
  .member-switcher {
    @apply p-3;
  }
  
  .quick-actions {
    @apply flex-col;
  }
  
  .quick-actions .ant-btn {
    @apply w-full;
  }
}
</style>
