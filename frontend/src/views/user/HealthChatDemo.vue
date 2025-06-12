<template>
  <div class="health-chat-demo">
    <div class="demo-header">
      <h1>🤖 AuraWell 健康管理对话演示</h1>
      <p>体验与AI健康助手的智能对话，获取个性化健康建议</p>
    </div>

    <div class="demo-content">
      <!-- 功能介绍 -->
      <div class="feature-intro">
        <a-row :gutter="24">
          <a-col :span="8">
            <a-card class="feature-card">
              <template #title>
                <span>💬 智能对话</span>
              </template>
              <p>与AI健康助手进行自然语言对话，就像与真人顾问交流一样</p>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card class="feature-card">
              <template #title>
                <span>💡 个性化建议</span>
              </template>
              <p>基于您的健康目标和当前状态，提供量身定制的健康方案</p>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card class="feature-card">
              <template #title>
                <span>🔄 持续跟踪</span>
              </template>
              <p>多轮对话中记住您的偏好，持续优化和调整建议</p>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <!-- 演示对话示例 -->
      <div class="demo-examples">
        <h2>💬 对话示例</h2>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-card title="减重咨询示例" class="example-card">
              <div class="conversation-example">
                <div class="example-message user">
                  <strong>用户：</strong>我想制定一个减重计划，目标是3个月减重10公斤
                </div>
                <div class="example-message agent">
                  <strong>AI助手：</strong>很好的目标！为了制定最适合您的减重计划，我需要了解一些信息：
                  <ul>
                    <li>您目前的身高体重是多少？</li>
                    <li>平时的运动习惯如何？</li>
                    <li>有没有特殊的饮食偏好或限制？</li>
                  </ul>
                </div>
                <div class="example-message user">
                  <strong>用户：</strong>身高170cm，体重75kg，平时很少运动，没有特殊饮食限制
                </div>
                <div class="example-message agent">
                  <strong>AI助手：</strong>根据您的情况，我为您制定了以下减重计划：
                  <br><strong>📊 目标分析：</strong>您的BMI为26，属于轻度超重，减重10kg是合理目标
                  <br><strong>🏃 运动建议：</strong>每周3-4次有氧运动，每次30-45分钟
                  <br><strong>🥗 饮食建议：</strong>控制热量摄入，建议每日1500-1600卡路里
                </div>
              </div>
            </a-card>
          </a-col>
          <a-col :span="12">
            <a-card title="睡眠改善示例" class="example-card">
              <div class="conversation-example">
                <div class="example-message user">
                  <strong>用户：</strong>最近睡眠质量很差，经常失眠，有什么改善方法吗？
                </div>
                <div class="example-message agent">
                  <strong>AI助手：</strong>睡眠问题确实会影响健康。让我了解一下您的具体情况：
                  <ul>
                    <li>通常几点上床睡觉？</li>
                    <li>入睡困难还是容易醒来？</li>
                    <li>睡前有什么习惯？</li>
                  </ul>
                </div>
                <div class="example-message user">
                  <strong>用户：</strong>通常12点左右睡觉，但要躺很久才能睡着，睡前会看手机
                </div>
                <div class="example-message agent">
                  <strong>AI助手：</strong>我为您推荐以下睡眠改善方案：
                  <br><strong>🌙 睡前准备：</strong>睡前1小时停止使用电子设备
                  <br><strong>🛏️ 环境优化：</strong>保持卧室温度18-22°C，使用遮光窗帘
                  <br><strong>⏰ 作息调整：</strong>建议提前到11点上床，建立固定睡眠时间
                </div>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <!-- 开始体验按钮 -->
      <div class="demo-actions">
        <a-button type="primary" size="large" @click="startChat" class="start-chat-btn">
          💬 开始健康咨询
        </a-button>
        <p class="demo-tip">点击按钮开始与AI健康助手对话</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const startChat = () => {
  router.push('/health-chat')
}
</script>

<style scoped>
.health-chat-demo {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.demo-header {
  text-align: center;
  color: white;
  margin-bottom: 40px;
}

.demo-header h1 {
  font-size: 2.5rem;
  margin-bottom: 16px;
  color: white;
}

.demo-header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.demo-content {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-intro {
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-card .ant-card-head-title {
  color: #1890ff;
  font-weight: 600;
}

.demo-examples {
  margin-bottom: 40px;
}

.demo-examples h2 {
  color: white;
  text-align: center;
  margin-bottom: 24px;
  font-size: 1.8rem;
}

.example-card {
  height: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.conversation-example {
  max-height: 400px;
  overflow-y: auto;
}

.example-message {
  margin-bottom: 12px;
  padding: 12px;
  border-radius: 8px;
  line-height: 1.6;
}

.example-message.user {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.example-message.agent {
  background: #f6ffed;
  border-left: 3px solid #52c41a;
}

.example-message strong {
  color: #262626;
}

.example-message ul {
  margin: 8px 0 0 20px;
}

.demo-actions {
  text-align: center;
}

.start-chat-btn {
  height: 60px;
  padding: 0 40px;
  font-size: 18px;
  border-radius: 30px;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.demo-tip {
  color: white;
  margin-top: 16px;
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .demo-header h1 {
    font-size: 2rem;
  }
  
  .demo-header p {
    font-size: 1rem;
  }
  
  .demo-examples h2 {
    font-size: 1.5rem;
  }
  
  .start-chat-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
