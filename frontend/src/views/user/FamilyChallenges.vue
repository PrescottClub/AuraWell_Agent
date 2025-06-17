<template>
  <div class="family-challenges-page">
    <div class="page-header mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">家庭挑战</h1>
          <p class="text-gray-600 mt-1">参与和管理家庭健康挑战</p>
        </div>
        <a-button type="primary" @click="showCreateModal = true">
          <PlusOutlined />
          创建挑战
        </a-button>
      </div>
    </div>

    <!-- 挑战列表 -->
    <div class="challenges-grid">
      <div
        v-for="challenge in challenges"
        :key="challenge.id"
        class="challenge-card"
      >
        <div class="challenge-header">
          <h3>{{ challenge.title }}</h3>
          <a-tag :color="getStatusColor(challenge.status)">
            {{ challenge.status }}
          </a-tag>
        </div>
        <p class="challenge-description">{{ challenge.description }}</p>
        <div class="challenge-progress">
          <a-progress :percent="challenge.progress" />
        </div>
        <div class="challenge-actions">
          <a-button size="small" @click="joinChallenge(challenge)">
            参与挑战
          </a-button>
        </div>
      </div>
    </div>

    <!-- 创建挑战弹窗 -->
    <a-modal
      v-model:open="showCreateModal"
      title="创建挑战"
      @ok="handleCreateChallenge"
    >
      <CreateChallengeForm v-model="challengeForm" :family-members="familyStore.familyMembers" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useFamilyStore } from '@/stores/family'
import CreateChallengeForm from '@/components/family/CreateChallengeForm.vue'

const familyStore = useFamilyStore()
const showCreateModal = ref(false)
const challengeForm = ref({})

const challenges = ref([
  {
    id: 1,
    title: '本周步数挑战',
    description: '全家一起达到70000步',
    status: 'active',
    progress: 65
  }
])

const getStatusColor = (status) => {
  return status === 'active' ? 'green' : 'default'
}

const joinChallenge = (challenge) => {
  console.log('加入挑战:', challenge)
}

const handleCreateChallenge = () => {
  console.log('创建挑战:', challengeForm.value)
  showCreateModal.value = false
}
</script>

<style scoped>
.family-challenges-page {
  @apply p-6 min-h-screen bg-gray-50;
}

.challenges-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
}

.challenge-card {
  @apply bg-white p-6 rounded-lg shadow-sm border;
}

.challenge-header {
  @apply flex justify-between items-center mb-3;
}

.challenge-description {
  @apply text-gray-600 mb-4;
}

.challenge-progress {
  @apply mb-4;
}

.challenge-actions {
  @apply flex justify-end;
}
</style>
