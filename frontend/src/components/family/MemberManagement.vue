<template>
  <div class="member-management">
    <!-- 成员列表 -->
    <a-table
      :columns="columns"
      :data-source="familyStore.familyMembers"
      :loading="familyStore.loading.members"
      row-key="user_id"
      :pagination="false"
    >
      <!-- 成员信息列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'member'">
          <div class="flex items-center">
            <a-avatar
              :size="40"
              :src="record.avatar"
              class="mr-3"
            >
              {{ record.display_name?.charAt(0) }}
            </a-avatar>
            <div>
              <div class="font-medium">{{ record.display_name }}</div>
              <div class="text-sm text-gray-500">{{ record.email }}</div>
              <a-tag
                v-if="record.is_current_user"
                color="blue"
                size="small"
                class="mt-1"
              >
                当前用户
              </a-tag>
            </div>
          </div>
        </template>

        <!-- 角色列 -->
        <template v-else-if="column.key === 'role'">
          <a-tag :color="getRoleColor(record.role)">
            {{ getRoleText(record.role) }}
          </a-tag>
        </template>

        <!-- 状态列 -->
        <template v-else-if="column.key === 'status'">
          <a-badge
            :status="record.status === 'active' ? 'success' : 'default'"
            :text="record.status === 'active' ? '活跃' : '离线'"
          />
          <div class="text-xs text-gray-400 mt-1">
            最后活跃: {{ formatTime(record.last_active) }}
          </div>
        </template>

        <!-- 权限列 -->
        <template v-else-if="column.key === 'permissions'">
          <div class="flex flex-wrap gap-1">
            <a-tag
              v-for="permission in record.permissions"
              :key="permission"
              size="small"
              color="blue"
            >
              {{ getPermissionText(permission) }}
            </a-tag>
          </div>
        </template>

        <!-- 操作列 -->
        <template v-else-if="column.key === 'actions'">
          <div class="flex gap-2">
            <a-button
              v-if="canEditMember(record)"
              type="link"
              size="small"
              @click="editMember(record)"
            >
              编辑
            </a-button>
            <a-button
              v-if="canRemoveMember(record)"
              type="link"
              danger
              size="small"
              @click="removeMember(record)"
            >
              移除
            </a-button>
            <a-dropdown v-if="canManagePermissions(record)">
              <a-button type="link" size="small">
                更多 <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="managePermissions(record)">
                    权限管理
                  </a-menu-item>
                  <a-menu-item @click="viewHealthData(record)">
                    查看健康数据
                  </a-menu-item>
                  <a-menu-item @click="setHealthAlerts(record)">
                    设置健康告警
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </template>
      </template>
    </a-table>

    <!-- 编辑成员弹窗 -->
    <a-modal
      v-model:open="showEditModal"
      title="编辑成员信息"
      @ok="handleUpdateMember"
      :confirm-loading="updating"
    >
      <a-form :model="editForm" layout="vertical">
        <a-form-item label="显示名称">
          <a-input v-model:value="editForm.display_name" />
        </a-form-item>
        <a-form-item label="角色" v-if="familyStore.isAdmin">
          <a-select v-model:value="editForm.role">
            <a-select-option value="Member">普通成员</a-select-option>
            <a-select-option value="Manager">管理员</a-select-option>
            <a-select-option value="Owner" v-if="familyStore.userRole === 'Owner'">
              拥有者
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="editForm.note" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 权限管理弹窗 -->
    <a-modal
      v-model:open="showPermissionModal"
      title="权限管理"
      @ok="handleUpdatePermissions"
      :confirm-loading="updatingPermissions"
      width="600px"
    >
      <div class="permission-management">
        <div class="mb-4">
          <h4>为 {{ selectedMember?.display_name }} 设置权限</h4>
        </div>
        
        <a-form layout="vertical">
          <a-form-item label="基础权限">
            <a-checkbox-group v-model:value="permissionForm.basic_permissions">
              <div class="grid grid-cols-2 gap-2">
                <a-checkbox value="view_own_data">查看自己的数据</a-checkbox>
                <a-checkbox value="edit_own_data">编辑自己的数据</a-checkbox>
                <a-checkbox value="view_family_summary">查看家庭摘要</a-checkbox>
                <a-checkbox value="participate_challenges">参与挑战</a-checkbox>
              </div>
            </a-checkbox-group>
          </a-form-item>

          <a-form-item label="管理权限" v-if="familyStore.isAdmin">
            <a-checkbox-group v-model:value="permissionForm.admin_permissions">
              <div class="grid grid-cols-2 gap-2">
                <a-checkbox value="view_all_data">查看所有成员数据</a-checkbox>
                <a-checkbox value="invite_members">邀请新成员</a-checkbox>
                <a-checkbox value="manage_members">管理成员</a-checkbox>
                <a-checkbox value="set_alerts">设置健康告警</a-checkbox>
                <a-checkbox value="create_challenges">创建挑战</a-checkbox>
                <a-checkbox value="export_reports">导出报告</a-checkbox>
              </div>
            </a-checkbox-group>
          </a-form-item>

          <a-form-item label="告警权限">
            <a-checkbox-group v-model:value="permissionForm.alert_permissions">
              <div class="grid grid-cols-1 gap-2">
                <a-checkbox value="receive_health_alerts">接收健康告警</a-checkbox>
                <a-checkbox value="receive_emergency_alerts">接收紧急告警</a-checkbox>
                <a-checkbox value="manage_alert_settings">管理告警设置</a-checkbox>
              </div>
            </a-checkbox-group>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 健康告警设置弹窗 -->
    <a-modal
      v-model:open="showAlertModal"
      title="健康告警设置"
      @ok="handleSetAlerts"
      :confirm-loading="settingAlerts"
      width="700px"
    >
      <!-- 健康告警设置内容 -->
      <div v-if="showAlertModal && selectedMember">
        <p>为 {{ selectedMember.display_name }} 设置健康告警</p>
        <!-- 这里可以添加具体的告警设置表单 -->
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import { memberAPI } from '@/api/family'
// import HealthAlertSettings from './HealthAlertSettings.vue'

const familyStore = useFamilyStore()

// 响应式数据
const showEditModal = ref(false)
const showPermissionModal = ref(false)
const showAlertModal = ref(false)
const updating = ref(false)
const updatingPermissions = ref(false)
const settingAlerts = ref(false)
const selectedMember = ref(null)

// 表单数据
const editForm = ref({
  display_name: '',
  role: '',
  note: ''
})

const permissionForm = ref({
  basic_permissions: [],
  admin_permissions: [],
  alert_permissions: []
})

// 表格列定义
const columns = [
  {
    title: '成员',
    key: 'member',
    width: 200
  },
  {
    title: '角色',
    key: 'role',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 120
  },
  {
    title: '权限',
    key: 'permissions',
    width: 200
  },
  {
    title: '操作',
    key: 'actions',
    width: 150
  }
]

// 方法
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

const getPermissionText = (permission) => {
  const texts = {
    'view_all_data': '查看所有数据',
    'invite_members': '邀请成员',
    'manage_members': '管理成员',
    'set_alerts': '设置告警',
    'create_challenges': '创建挑战'
  }
  return texts[permission] || permission
}

const formatTime = (time) => {
  if (!time) return '从未'
  return new Date(time).toLocaleString()
}

const canEditMember = (member) => {
  return familyStore.canManageMembers && !member.is_current_user
}

const canRemoveMember = (member) => {
  return familyStore.canManageMembers && 
         !member.is_current_user && 
         member.role !== 'Owner'
}

const canManagePermissions = (member) => {
  return familyStore.isAdmin && !member.is_current_user
}

const editMember = (member) => {
  selectedMember.value = member
  editForm.value = {
    display_name: member.display_name,
    role: member.role,
    note: member.note || ''
  }
  showEditModal.value = true
}

const removeMember = (member) => {
  Modal.confirm({
    title: '确认移除成员',
    content: `确定要移除成员 ${member.display_name} 吗？此操作不可撤销。`,
    onOk: async () => {
      try {
        await memberAPI.removeMember(familyStore.currentFamily.family_id, member.user_id)
        message.success('成员移除成功')
        await familyStore.fetchFamilyMembers(familyStore.currentFamily.family_id)
      } catch (error) {
        console.error('移除成员失败:', error)
        message.error('移除成员失败')
      }
    }
  })
}

const managePermissions = (member) => {
  selectedMember.value = member
  permissionForm.value = {
    basic_permissions: member.permissions?.basic || [],
    admin_permissions: member.permissions?.admin || [],
    alert_permissions: member.permissions?.alert || []
  }
  showPermissionModal.value = true
}

const viewHealthData = (member) => {
  // 跳转到成员健康数据页面
  window.open(`/family/member/${member.user_id}/health`, '_blank')
}

const setHealthAlerts = (member) => {
  selectedMember.value = member
  showAlertModal.value = true
}

const handleUpdateMember = async () => {
  updating.value = true
  try {
    await memberAPI.updateMemberInfo(selectedMember.value.user_id, editForm.value)
    message.success('成员信息更新成功')
    showEditModal.value = false
    await familyStore.fetchFamilyMembers(familyStore.currentFamily.family_id)
  } catch (error) {
    console.error('更新成员信息失败:', error)
    message.error('更新成员信息失败')
  } finally {
    updating.value = false
  }
}

const handleUpdatePermissions = async () => {
  updatingPermissions.value = true
  try {
    await memberAPI.updateMemberPermissions(selectedMember.value.user_id, permissionForm.value)
    message.success('权限更新成功')
    showPermissionModal.value = false
    await familyStore.fetchFamilyMembers(familyStore.currentFamily.family_id)
  } catch (error) {
    console.error('更新权限失败:', error)
    message.error('更新权限失败')
  } finally {
    updatingPermissions.value = false
  }
}

const handleSetAlerts = async () => {
  settingAlerts.value = true
  try {
    // 处理告警设置逻辑
    message.success('告警设置保存成功')
    showAlertModal.value = false
  } catch (error) {
    console.error('设置告警失败:', error)
    message.error('设置告警失败')
  } finally {
    settingAlerts.value = false
  }
}

const handleSaveAlerts = (alertData) => {
  // 处理保存告警数据
  console.log('保存告警数据:', alertData)
}

// 生命周期
onMounted(() => {
  if (familyStore.currentFamily) {
    familyStore.fetchFamilyMembers(familyStore.currentFamily.family_id)
  }
})
</script>

<style scoped>
.member-management {
  @apply w-full;
}

.permission-management {
  @apply space-y-4;
}

.grid {
  @apply gap-2;
}

.ant-checkbox-group {
  @apply w-full;
}

.ant-checkbox-wrapper {
  @apply mb-2;
}
</style>
