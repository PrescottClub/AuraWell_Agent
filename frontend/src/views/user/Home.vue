<template>
    <div class="home-container">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">智能对话，改变未来</h1>
                <p class="hero-subtitle">基于先进AI技术的智能对话系统，为企业提供全方位的智能服务解决方案</p>
                <div class="hero-buttons">
                    <a-button type="primary" size="large" class="mr-4">立即体验</a-button>
                    <a-button size="large">了解更多</a-button>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features-section">
            <h2 class="section-title">核心优势</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <RobotOutlined />
                    </div>
                    <h3>智能对话</h3>
                    <p>基于先进AI技术，提供自然流畅的对话体验</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <SafetyCertificateOutlined />
                    </div>
                    <h3>安全可靠</h3>
                    <p>多重安全机制，保障数据安全与隐私</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <RocketOutlined />
                    </div>
                    <h3>快速部署</h3>
                    <p>简单配置，快速上线，即刻享受智能服务</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <LineChartOutlined />
                    </div>
                    <h3>数据分析</h3>
                    <p>深度分析对话数据，助力业务决策</p>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="stats-section">
            <div class="stats-container">
                <div class="stat-item">
                    <h3>1000+</h3>
                    <p>企业客户</p>
                </div>
                <div class="stat-item">
                    <h3>99.9%</h3>
                    <p>服务可用性</p>
                </div>
                <div class="stat-item">
                    <h3>50万+</h3>
                    <p>日均对话量</p>
                </div>
                <div class="stat-item">
                    <h3>24/7</h3>
                    <p>全天候服务</p>
                </div>
            </div>
        </section>

        <!-- Testimonials Section -->
        <section class="testimonials-section">
            <h2 class="section-title">客户评价</h2>
            <div class="testimonials-grid">
                <a-card class="testimonial-card">
                    <template #cover>
                        <img alt="客户头像" src="https://via.placeholder.com/150" />
                    </template>
                    <a-card-meta title="张先生">
                        <template #description>
                            "AuraWell的智能对话系统帮助我们提升了50%的客户服务效率，非常满意！"
                        </template>
                    </a-card-meta>
                </a-card>
                <a-card class="testimonial-card">
                    <template #cover>
                        <img alt="客户头像" src="https://via.placeholder.com/150" />
                    </template>
                    <a-card-meta title="李女士">
                        <template #description>
                            "系统响应速度快，对话自然流畅，大大提升了我们的服务质量。"
                        </template>
                    </a-card-meta>
                </a-card>
                <a-card class="testimonial-card">
                    <template #cover>
                        <img alt="客户头像" src="https://via.placeholder.com/150" />
                    </template>
                    <a-card-meta title="王总">
                        <template #description>
                            "部署简单，维护方便，是提升企业效率的得力助手。"
                        </template>
                    </a-card-meta>
                </a-card>
            </div>
        </section>

        <!-- Contact Section -->
        <section class="contact-section">
            <h2 class="section-title">联系我们</h2>
            <div class="contact-container">
                <div class="contact-info">
                    <h3>立即开始您的智能对话之旅</h3>
                    <p>我们的团队随时为您提供专业支持</p>
                    <div class="contact-details">
                        <p><PhoneOutlined /> 400-123-4567</p>
                        <p><MailOutlined /> contact@aurawell.com</p>
                        <p><EnvironmentOutlined /> 北京市朝阳区科技园区88号</p>
                    </div>
                </div>
                <div class="contact-form">
                    <a-form layout="vertical">
                        <a-form-item label="姓名">
                            <a-input placeholder="请输入您的姓名" />
                        </a-form-item>
                        <a-form-item label="邮箱">
                            <a-input placeholder="请输入您的邮箱" />
                        </a-form-item>
                        <a-form-item label="留言">
                            <a-textarea rows="4" placeholder="请输入您的留言" />
                        </a-form-item>
                        <a-form-item>
                            <a-button type="primary" block>提交</a-button>
                        </a-form-item>
                    </a-form>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import {
    RobotOutlined,
    SafetyCertificateOutlined,
    RocketOutlined,
    LineChartOutlined,
    PhoneOutlined,
    MailOutlined,
    EnvironmentOutlined
} from '@ant-design/icons-vue';
</script>

<style scoped>
.home-container {
    min-height: 100vh;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
    color: white;
    padding: 100px 0;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
}

.hero-title {
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 1.5rem;
}

.hero-subtitle {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

/* Features Section */
.features-section {
    padding: 80px 20px;
    background: #f5f5f5;
}

.section-title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 3rem;
    color: #333;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: white;
    padding: 30px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 2.5rem;
    color: #1890ff;
    margin-bottom: 1rem;
}

/* Stats Section */
.stats-section {
    background: #1890ff;
    color: white;
    padding: 60px 20px;
}

.stats-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
    text-align: center;
}

.stat-item h3 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

/* Testimonials Section */
.testimonials-section {
    padding: 80px 20px;
    background: white;
}

.testimonials-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

.testimonial-card {
    text-align: center;
}

.testimonial-card img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    margin: 20px auto;
}

/* Contact Section */
.contact-section {
    padding: 80px 20px;
    background: #f5f5f5;
}

.contact-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 50px;
    max-width: 1200px;
    margin: 0 auto;
}

.contact-info {
    padding: 20px;
}

.contact-info h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

.contact-details {
    margin-top: 2rem;
}

.contact-details p {
    margin: 1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.contact-form {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2rem;
    }

    .hero-subtitle {
        font-size: 1rem;
    }

    .section-title {
        font-size: 1.5rem;
    }

    .stat-item h3 {
        font-size: 2rem;
    }
}
</style>