<template>
  <div class="test-page">
    <h1>测试页面</h1>
    <p>如果您能看到这个页面，说明路由和基本组件都工作正常。</p>
    
    <div class="test-buttons">
      <a-button type="primary" @click="goToDemo">
        前往Demo页面
      </a-button>
      <a-button @click="goToChat">
        前往聊天页面
      </a-button>
      <a-button @click="goHome">
        返回首页
      </a-button>
    </div>
    
    <div class="debug-info">
      <h3>调试信息：</h3>
      <p>当前路由：{{ $route.path }}</p>
      <p>当前时间：{{ currentTime }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentTime = ref('')

onMounted(() => {
  currentTime.value = new Date().toLocaleString()
})

const goToDemo = () => {
  router.push('/health-chat-demo')
}

const goToChat = () => {
  router.push('/health-chat')
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.test-page {
  padding: 40px;
  text-align: center;
}

.test-buttons {
  margin: 30px 0;
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.debug-info {
  margin-top: 40px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
</style>
