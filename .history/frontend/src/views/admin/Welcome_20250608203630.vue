<template>
    <div class="welcome-container">
        <div class="welcome-header">
            <h1 class="text-2xl font-bold mb-4">欢迎使用 AuraWell 管理系统</h1>
            <p class="text-gray-600">今天是 {{ currentDate }}</p>
        </div>
        
        <div class="stats-grid mt-8">
            <a-card class="stat-card">
                <template #title>
                    <div class="flex items-center">
                        <UserOutlined class="mr-2 text-blue-500" />
                        用户总数
                    </div>
                </template>
                <div class="text-3xl font-bold text-blue-500">1,234</div>
            </a-card>
            
            <a-card class="stat-card">
                <template #title>
                    <div class="flex items-center">
                        <MessageOutlined class="mr-2 text-green-500" />
                        今日对话
                    </div>
                </template>
                <div class="text-3xl font-bold text-green-500">256</div>
            </a-card>
            
            <a-card class="stat-card">
                <template #title>
                    <div class="flex items-center">
                        <ClockCircleOutlined class="mr-2 text-purple-500" />
                        平均响应时间
                    </div>
                </template>
                <div class="text-3xl font-bold text-purple-500">0.8s</div>
            </a-card>
            
            <a-card class="stat-card">
                <template #title>
                    <div class="flex items-center">
                        <SmileOutlined class="mr-2 text-orange-500" />
                        满意度
                    </div>
                </template>
                <div class="text-3xl font-bold text-orange-500">98%</div>
            </a-card>
        </div>

        <div class="quick-actions mt-8">
            <h2 class="text-xl font-bold mb-4">快捷操作</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <a-card hoverable @click="navigateTo('/admin/users')">
                    <template #cover>
                        <div class="p-4 text-center">
                            <UserOutlined class="text-4xl text-blue-500" />
                        </div>
                    </template>
                    <a-card-meta title="用户管理" description="管理系统用户" />
                </a-card>
                
                <a-card hoverable @click="navigateTo('/admin/settings')">
                    <template #cover>
                        <div class="p-4 text-center">
                            <SettingOutlined class="text-4xl text-green-500" />
                        </div>
                    </template>
                    <a-card-meta title="系统设置" description="配置系统参数" />
                </a-card>
                
                <a-card hoverable @click="navigateTo('/admin/dashboard')">
                    <template #cover>
                        <div class="p-4 text-center">
                            <DashboardOutlined class="text-4xl text-purple-500" />
                        </div>
                    </template>
                    <a-card-meta title="数据统计" description="查看系统数据" />
                </a-card>
                
                <a-card hoverable @click="navigateTo('/admin/logs')">
                    <template #cover>
                        <div class="p-4 text-center">
                            <FileTextOutlined class="text-4xl text-orange-500" />
                        </div>
                    </template>
                    <a-card-meta title="系统日志" description="查看操作记录" />
                </a-card>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import {
    UserOutlined,
    MessageOutlined,
    ClockCircleOutlined,
    SmileOutlined,
    SettingOutlined,
    DashboardOutlined,
    FileTextOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const currentDate = ref(new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
}));

const navigateTo = (path) => {
    router.push(path);
};
</script>

<style scoped>
.welcome-container {
    padding: 24px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
}

.stat-card {
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-actions .ant-card {
    cursor: pointer;
    transition: all 0.3s ease;
}

.quick-actions .ant-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style> 