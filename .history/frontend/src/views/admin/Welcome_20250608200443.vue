<template>
  <div class="welcome-container">
    <a-card class="welcome-card">
      <template #title>
        <div class="welcome-title">
          <span class="welcome-icon">👋</span>
          <span>欢迎使用 AuraWell 管理系统</span>
        </div>
      </template>
      <div class="welcome-content">
        <p class="welcome-message">感谢您使用 AuraWell 健康管理系统。在这里，您可以：</p>
        <ul class="feature-list">
          <li>管理用户信息和权限</li>
          <li>查看系统运行状态</li>
          <li>配置系统参数</li>
          <li>监控健康数据</li>
        </ul>
        <div class="quick-stats">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-statistic title="活跃用户" :value="1128" />
            </a-col>
            <a-col :span="8">
              <a-statistic title="今日访问" :value="93" />
            </a-col>
            <a-col :span="8">
              <a-statistic title="系统消息" :value="5" />
            </a-col>
          </a-row>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('Welcome page mounted')
})
</script>

<style scoped>
.welcome-container {
  padding: 24px;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 500;
}

.welcome-icon {
  font-size: 24px;
}

.welcome-content {
  margin-top: 24px;
}

.welcome-message {
  font-size: 16px;
  color: #666;
  margin-bottom: 24px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0 0 24px 0;
}

.feature-list li {
  padding: 8px 0;
  color: #666;
  position: relative;
  padding-left: 24px;
}

.feature-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #1890ff;
}

.quick-stats {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}
</style> 