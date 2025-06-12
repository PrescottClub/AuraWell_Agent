<template>
  <div class="simple-demo">
    <div class="demo-container">
      <h1>🌟 AuraWell 健康管理助手</h1>
      <p>体验智能健康咨询，获取个性化建议</p>
      
      <div class="features">
        <div class="feature">
          <h3>💬 智能对话</h3>
          <p>与AI健康助手自然对话</p>
        </div>
        <div class="feature">
          <h3>💡 个性化建议</h3>
          <p>基于您的情况提供定制方案</p>
        </div>
        <div class="feature">
          <h3>🔄 持续跟踪</h3>
          <p>记住偏好，持续优化建议</p>
        </div>
      </div>
      
      <div class="demo-examples">
        <h2>💬 对话示例</h2>
        
        <div class="example">
          <h3>减重咨询</h3>
          <div class="conversation">
            <div class="message user">
              <strong>用户：</strong>我想制定一个减重计划
            </div>
            <div class="message ai">
              <strong>AI助手：</strong>很好！为了制定最适合您的减重计划，我需要了解：
              <ul>
                <li>您目前的身高体重？</li>
                <li>平时的运动习惯？</li>
                <li>有没有饮食限制？</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="example">
          <h3>睡眠改善</h3>
          <div class="conversation">
            <div class="message user">
              <strong>用户：</strong>最近睡眠质量很差，经常失眠
            </div>
            <div class="message ai">
              <strong>AI助手：</strong>睡眠问题确实影响健康。让我了解一下：
              <ul>
                <li>通常几点睡觉？</li>
                <li>入睡困难还是容易醒？</li>
                <li>睡前有什么习惯？</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div class="action-buttons">
        <button class="start-btn" @click="startChat">
          💬 开始健康咨询
        </button>
        <button class="home-btn" @click="goHome">
          🏠 返回首页
        </button>
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

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.simple-demo {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  color: white;
}

.demo-container {
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 40px 0;
}

.feature {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.feature h3 {
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.demo-examples {
  margin: 40px 0;
}

.demo-examples h2 {
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.example {
  background: rgba(255, 255, 255, 0.1);
  margin: 20px 0;
  padding: 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  text-align: left;
}

.example h3 {
  text-align: center;
  margin-bottom: 15px;
  color: #ffd700;
}

.conversation {
  max-height: 300px;
  overflow-y: auto;
}

.message {
  margin: 10px 0;
  padding: 12px;
  border-radius: 8px;
  line-height: 1.5;
}

.message.user {
  background: rgba(24, 144, 255, 0.3);
  border-left: 3px solid #1890ff;
}

.message.ai {
  background: rgba(82, 196, 26, 0.3);
  border-left: 3px solid #52c41a;
}

.message ul {
  margin: 8px 0 0 20px;
}

.action-buttons {
  margin-top: 40px;
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.start-btn, .home-btn {
  padding: 15px 30px;
  font-size: 18px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.start-btn {
  background: #52c41a;
  color: white;
}

.start-btn:hover {
  background: #389e0d;
  transform: translateY(-2px);
}

.home-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.home-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .start-btn, .home-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
