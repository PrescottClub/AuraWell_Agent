<template>
    <div class="home-container">
        <!-- Hero Section -->
        <section class="hero-section">
            <!-- 动态背景粒子 -->
            <div class="particles-bg">
                <div v-for="i in 50" :key="i" class="particle" :style="getParticleStyle(i)"></div>
            </div>

            <!-- 浮动元素 -->
            <div class="floating-elements">
                <div class="floating-icon health-icon">💊</div>
                <div class="floating-icon heart-icon">❤️</div>
                <div class="floating-icon brain-icon">🧠</div>
                <div class="floating-icon fitness-icon">💪</div>
                <div class="floating-icon meditation-icon">🧘‍♀️</div>
            </div>

            <div class="hero-content" ref="heroContent">
                <div class="hero-badge animate-fade-in-up">
                    <span class="badge-text">🚀 AI驱动的健康管理平台</span>
                </div>
                <h1 class="hero-title animate-fade-in-up">
                    <span class="title-gradient">AuraWell</span>
                    <br>
                    <span class="title-subtitle">智能健康管理助手</span>
                </h1>
                <p class="hero-subtitle animate-fade-in-up">
                    基于先进AI技术的个性化健康管理平台<br>
                    为您提供专业的健康咨询和生活方式建议
                </p>
                <div class="hero-buttons animate-fade-in-up">
                    <button class="cta-button primary" @click="startHealthChat">
                        <span class="button-content">
                            <span class="button-icon">💬</span>
                            <span class="button-text">开始健康咨询</span>
                        </span>
                        <div class="button-ripple"></div>
                    </button>
                    <button class="cta-button secondary" @click="viewDemo">
                        <span class="button-content">
                            <span class="button-icon">▶️</span>
                            <span class="button-text">查看演示</span>
                        </span>
                        <div class="button-ripple"></div>
                    </button>
                </div>

                <!-- 滚动提示 -->
                <div class="scroll-indicator animate-bounce">
                    <div class="scroll-arrow">↓</div>
                    <span class="scroll-text">向下滚动探索更多</span>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features-section" ref="featuresSection">
            <div class="section-header">
                <h2 class="section-title animate-on-scroll">
                    <span class="title-icon">🎯</span>
                    <span class="title-text">核心功能</span>
                </h2>
                <p class="section-subtitle animate-on-scroll">
                    全方位的健康管理解决方案，让健康生活更简单
                </p>
            </div>

            <div class="features-grid">
                <div class="feature-card animate-on-scroll" data-delay="0">
                    <div class="feature-card-inner">
                        <div class="feature-icon-container">
                            <div class="feature-icon">💬</div>
                            <div class="icon-glow"></div>
                        </div>
                        <div class="feature-content">
                            <h3>智能健康咨询</h3>
                            <p>与AI健康助手对话，获取个性化的健康建议和方案</p>
                            <div class="feature-arrow">→</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card animate-on-scroll" data-delay="100">
                    <div class="feature-card-inner">
                        <div class="feature-icon-container">
                            <div class="feature-icon">📊</div>
                            <div class="icon-glow"></div>
                        </div>
                        <div class="feature-content">
                            <h3>健康数据分析</h3>
                            <p>整合多平台健康数据，提供深度健康分析报告</p>
                            <div class="feature-arrow">→</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card animate-on-scroll" data-delay="200">
                    <div class="feature-card-inner">
                        <div class="feature-icon-container">
                            <div class="feature-icon">🏆</div>
                            <div class="icon-glow"></div>
                        </div>
                        <div class="feature-content">
                            <h3>目标管理</h3>
                            <p>制定健康目标，跟踪进度，建立健康生活习惯</p>
                            <div class="feature-arrow">→</div>
                        </div>
                    </div>
                </div>

                <div class="feature-card animate-on-scroll" data-delay="300">
                    <div class="feature-card-inner">
                        <div class="feature-icon-container">
                            <div class="feature-icon">📈</div>
                            <div class="icon-glow"></div>
                        </div>
                        <div class="feature-content">
                            <h3>进度可视化</h3>
                            <p>直观的图表展示健康数据变化趋势和改善效果</p>
                            <div class="feature-arrow">→</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section" ref="statsSection">
            <div class="stats-bg-pattern"></div>
            <div class="stats-container">
                <div class="stat-item animate-on-scroll" data-delay="0">
                    <div class="stat-icon">👥</div>
                    <div class="stat-number" ref="stat1">{{ animatedStats.users }}</div>
                    <div class="stat-label">活跃用户</div>
                    <div class="stat-progress">
                        <div class="progress-bar" :style="{ width: statsProgress + '%' }"></div>
                    </div>
                </div>

                <div class="stat-item animate-on-scroll" data-delay="100">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-number" ref="stat2">{{ animatedStats.satisfaction }}%</div>
                    <div class="stat-label">用户满意度</div>
                    <div class="stat-progress">
                        <div class="progress-bar" :style="{ width: statsProgress + '%' }"></div>
                    </div>
                </div>

                <div class="stat-item animate-on-scroll" data-delay="200">
                    <div class="stat-icon">💬</div>
                    <div class="stat-number" ref="stat3">{{ animatedStats.consultations }}</div>
                    <div class="stat-label">健康咨询次数</div>
                    <div class="stat-progress">
                        <div class="progress-bar" :style="{ width: statsProgress + '%' }"></div>
                    </div>
                </div>

                <div class="stat-item animate-on-scroll" data-delay="300">
                    <div class="stat-icon">🤖</div>
                    <div class="stat-number" ref="stat4">{{ animatedStats.uptime }}</div>
                    <div class="stat-label">AI助手在线</div>
                    <div class="stat-progress">
                        <div class="progress-bar" :style="{ width: statsProgress + '%' }"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="cta-section">
            <div class="cta-container animate-on-scroll">
                <div class="cta-content">
                    <h2 class="cta-title">开始您的健康管理之旅</h2>
                    <p class="cta-subtitle">
                        加入数万用户的健康管理社区，让AI助手成为您的专属健康顾问
                    </p>
                    <div class="cta-buttons">
                        <button class="cta-button primary large" @click="startHealthChat">
                            <span class="button-content">
                                <span class="button-icon">🚀</span>
                                <span class="button-text">立即开始</span>
                            </span>
                            <div class="button-ripple"></div>
                        </button>
                    </div>
                </div>
                <div class="cta-visual">
                    <div class="floating-health-icons">
                        <div class="health-icon-float">💊</div>
                        <div class="health-icon-float">🏃‍♂️</div>
                        <div class="health-icon-float">🥗</div>
                        <div class="health-icon-float">😴</div>
                        <div class="health-icon-float">📱</div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const heroContent = ref(null)
const featuresSection = ref(null)
const statsSection = ref(null)
const statsProgress = ref(0)

// 动画统计数据
const animatedStats = reactive({
  users: '0',
  satisfaction: 0,
  consultations: '0',
  uptime: '24/7'
})

// 目标数据
const targetStats = {
  users: 100000,
  satisfaction: 95,
  consultations: 1000000,
  uptime: '24/7'
}

// 粒子样式生成
const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const animationDelay = Math.random() * 20
  const animationDuration = Math.random() * 10 + 10

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`
  }
}

// 数字动画函数
const animateNumber = (start, end, duration, callback) => {
  const startTime = performance.now()
  const isInteger = Number.isInteger(end)

  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    // 使用缓动函数
    const easeOutQuart = 1 - Math.pow(1 - progress, 4)
    const current = start + (end - start) * easeOutQuart

    if (isInteger) {
      callback(Math.floor(current))
    } else {
      callback(current.toFixed(1))
    }

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  requestAnimationFrame(animate)
}

// 格式化大数字
const formatNumber = (num) => {
  if (num >= 1000000) {
    return Math.floor(num / 10000) + '万+'
  } else if (num >= 10000) {
    return Math.floor(num / 10000) + '万+'
  }
  return num.toString()
}

// 滚动动画观察器
let observer = null

const initScrollAnimations = () => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const element = entry.target
        const delay = parseInt(element.dataset.delay) || 0

        setTimeout(() => {
          element.classList.add('animate-in')

          // 如果是统计数据部分，启动数字动画
          if (element.closest('.stats-section')) {
            startStatsAnimation()
          }
        }, delay)
      }
    })
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  })

  // 观察所有需要动画的元素
  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el)
  })
}

// 启动统计数据动画
const startStatsAnimation = () => {
  // 进度条动画
  statsProgress.value = 100

  // 数字动画
  animateNumber(0, targetStats.users, 2000, (value) => {
    animatedStats.users = formatNumber(value)
  })

  animateNumber(0, targetStats.satisfaction, 2000, (value) => {
    animatedStats.satisfaction = Math.floor(value)
  })

  animateNumber(0, targetStats.consultations, 2500, (value) => {
    animatedStats.consultations = formatNumber(value)
  })
}

// 路由导航
const startHealthChat = () => {
  router.push('/health-chat')
}

const viewDemo = () => {
  router.push('/simple-demo')
}

// 生命周期
onMounted(() => {
  // 延迟初始化滚动动画，确保DOM完全渲染
  setTimeout(() => {
    initScrollAnimations()
  }, 100)
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
/* 全局样式 */
.home-container {
    min-height: 100vh;
    overflow-x: hidden;
}

/* Hero Section */
.hero-section {
    position: relative;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #52c41a 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* 动态背景粒子 */
.particles-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.particle {
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    animation: float infinite linear;
}

@keyframes float {
    0% {
        transform: translateY(100vh) rotate(0deg);
        opacity: 0;
    }
    10% {
        opacity: 1;
    }
    90% {
        opacity: 1;
    }
    100% {
        transform: translateY(-100px) rotate(360deg);
        opacity: 0;
    }
}

/* 浮动元素 */
.floating-elements {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.floating-icon {
    position: absolute;
    font-size: 2rem;
    animation: floatIcon 6s ease-in-out infinite;
}

.health-icon { top: 20%; left: 10%; animation-delay: 0s; }
.heart-icon { top: 30%; right: 15%; animation-delay: 1s; }
.brain-icon { top: 60%; left: 20%; animation-delay: 2s; }
.fitness-icon { top: 70%; right: 25%; animation-delay: 3s; }
.meditation-icon { top: 40%; left: 80%; animation-delay: 4s; }

@keyframes floatIcon {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(5deg); }
}

/* Hero内容 */
.hero-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px;
    text-align: center;
    z-index: 2;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 50px;
    padding: 8px 20px;
    margin-bottom: 2rem;
    font-size: 0.9rem;
    animation-delay: 0.2s;
}

.badge-text {
    background: linear-gradient(45deg, #fff, #f0f0f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-title {
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 1.5rem;
    line-height: 1.1;
    animation-delay: 0.4s;
}

.title-gradient {
    background: linear-gradient(45deg, #fff, #f0f0f0, #fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 200%;
    animation: gradientShift 3s ease-in-out infinite;
}

.title-subtitle {
    font-size: 2rem;
    font-weight: 300;
    opacity: 0.9;
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.hero-subtitle {
    font-size: 1.3rem;
    margin-bottom: 3rem;
    opacity: 0.9;
    line-height: 1.6;
    animation-delay: 0.6s;
}

/* 按钮样式 */
.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 4rem;
    animation-delay: 0.8s;
}

.cta-button {
    position: relative;
    padding: 16px 32px;
    border: none;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.cta-button.primary {
    background: linear-gradient(45deg, #52c41a, #389e0d);
    color: white;
    box-shadow: 0 8px 25px rgba(82, 196, 26, 0.3);
}

.cta-button.secondary {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.cta-button.large {
    padding: 20px 40px;
    font-size: 1.2rem;
}

.cta-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(82, 196, 26, 0.4);
}

.button-content {
    display: flex;
    align-items: center;
    gap: 8px;
    position: relative;
    z-index: 2;
}

.button-ripple {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
    transform: scale(0);
    transition: transform 0.6s ease;
}

.cta-button:active .button-ripple {
    transform: scale(1);
}

/* 滚动指示器 */
.scroll-indicator {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    opacity: 0.7;
    animation-delay: 1s;
}

.scroll-arrow {
    font-size: 1.5rem;
    margin-bottom: 8px;
}

.scroll-text {
    font-size: 0.9rem;
    opacity: 0.8;
}

/* Features Section */
.features-section {
    padding: 120px 20px;
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    position: relative;
}

.section-header {
    text-align: center;
    margin-bottom: 4rem;
}

.section-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #1a202c;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.title-icon {
    font-size: 3rem;
}

.section-subtitle {
    font-size: 1.2rem;
    color: #64748b;
    max-width: 600px;
    margin: 0 auto;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.4s ease;
    cursor: pointer;
    position: relative;
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.feature-card-inner {
    padding: 2rem;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.feature-icon-container {
    position: relative;
    margin-bottom: 1.5rem;
    align-self: flex-start;
}

.feature-icon {
    font-size: 3rem;
    display: block;
    position: relative;
    z-index: 2;
}

.icon-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: linear-gradient(45deg, #52c41a, #389e0d);
    border-radius: 50%;
    opacity: 0.1;
    transition: all 0.3s ease;
}

.feature-card:hover .icon-glow {
    opacity: 0.2;
    transform: translate(-50%, -50%) scale(1.2);
}

.feature-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.feature-content h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1a202c;
}

.feature-content p {
    color: #64748b;
    line-height: 1.6;
    flex: 1;
    margin-bottom: 1rem;
}

.feature-arrow {
    font-size: 1.2rem;
    color: #52c41a;
    font-weight: bold;
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.3s ease;
    align-self: flex-start;
}

.feature-card:hover .feature-arrow {
    opacity: 1;
    transform: translateX(0);
}

/* Stats Section */
.stats-section {
    position: relative;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 100px 20px;
    overflow: hidden;
}

.stats-bg-pattern {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.1) 1px, transparent 1px),
        radial-gradient(circle at 80% 80%, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: patternMove 20s linear infinite;
}

@keyframes patternMove {
    0% { transform: translate(0, 0); }
    100% { transform: translate(50px, 50px); }
}

.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    max-width: 1000px;
    margin: 0 auto;
    position: relative;
    z-index: 2;
}

.stat-item {
    text-align: center;
    padding: 2rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}

.stat-item:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.15);
}

.stat-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}

.stat-number {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    background: linear-gradient(45deg, #fff, #f0f0f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.stat-progress {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #52c41a, #389e0d);
    border-radius: 2px;
    transition: width 2s ease;
    width: 0%;
}

/* CTA Section */
.cta-section {
    padding: 120px 20px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    position: relative;
}

.cta-container {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.cta-content {
    text-align: left;
}

.cta-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a202c;
    line-height: 1.2;
}

.cta-subtitle {
    font-size: 1.2rem;
    color: #64748b;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.cta-buttons {
    display: flex;
    gap: 1rem;
}

.cta-visual {
    position: relative;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.floating-health-icons {
    position: relative;
    width: 300px;
    height: 300px;
}

.health-icon-float {
    position: absolute;
    font-size: 3rem;
    background: white;
    border-radius: 50%;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    animation: floatHealthIcon 4s ease-in-out infinite;
}

.health-icon-float:nth-child(1) {
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    animation-delay: 0s;
}

.health-icon-float:nth-child(2) {
    top: 20%;
    right: 0;
    animation-delay: 0.8s;
}

.health-icon-float:nth-child(3) {
    bottom: 20%;
    right: 0;
    animation-delay: 1.6s;
}

.health-icon-float:nth-child(4) {
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    animation-delay: 2.4s;
}

.health-icon-float:nth-child(5) {
    top: 20%;
    left: 0;
    animation-delay: 3.2s;
}

@keyframes floatHealthIcon {
    0%, 100% {
        transform: translateY(0px) scale(1);
    }
    50% {
        transform: translateY(-15px) scale(1.05);
    }
}

/* 动画类 */
.animate-fade-in-up {
    opacity: 0;
    transform: translateY(30px);
    animation: fadeInUp 1s ease forwards;
}

.animate-bounce {
    animation: bounce 2s infinite;
}

.animate-on-scroll {
    opacity: 0;
    transform: translateY(50px);
    transition: all 0.8s ease;
}

.animate-on-scroll.animate-in {
    opacity: 1;
    transform: translateY(0);
}

@keyframes fadeInUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
        transform: translateY(0);
    }
    40% {
        transform: translateY(-10px);
    }
    60% {
        transform: translateY(-5px);
    }
}

/* 响应式设计 */
@media (max-width: 1024px) {
    .cta-container {
        grid-template-columns: 1fr;
        text-align: center;
    }

    .cta-content {
        text-align: center;
    }
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }

    .title-subtitle {
        font-size: 1.5rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
    }

    .section-title {
        font-size: 2rem;
    }

    .title-icon {
        font-size: 2rem;
    }

    .stat-number {
        font-size: 2rem;
    }

    .cta-title {
        font-size: 2rem;
    }

    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }

    .cta-button {
        width: 100%;
        max-width: 300px;
    }

    .features-grid {
        grid-template-columns: 1fr;
    }

    .stats-container {
        grid-template-columns: repeat(2, 1fr);
    }

    .floating-elements {
        display: none;
    }
}

@media (max-width: 480px) {
    .hero-title {
        font-size: 2rem;
    }

    .title-subtitle {
        font-size: 1.2rem;
    }

    .hero-subtitle {
        font-size: 1rem;
    }

    .section-title {
        font-size: 1.5rem;
    }

    .cta-title {
        font-size: 1.5rem;
    }

    .stats-container {
        grid-template-columns: 1fr;
    }

    .stat-number {
        font-size: 1.8rem;
    }
}

/* 性能优化 */
.feature-card,
.stat-item,
.cta-button {
    will-change: transform;
}

/* 滚动条样式 */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #52c41a, #389e0d);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, #389e0d, #237804);
}
</style>