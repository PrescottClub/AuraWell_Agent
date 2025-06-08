<template>
    <div class="welcome-container">
        <a-card class="welcome-card" :loading="loading">
            <template #title>
                <div class="welcome-title">
                    <UserOutlined />
                    <span>欢迎回来，{{ userInfo.display_name }}</span>
                </div>
            </template>
            <a-descriptions bordered>
                <a-descriptions-item label="用户ID" :span="3">
                    {{ userInfo.user_id }}
                </a-descriptions-item>
                <a-descriptions-item label="邮箱" :span="3">
                    {{ userInfo.email }}
                </a-descriptions-item>
                <a-descriptions-item label="年龄">
                    {{ userInfo.age }} 岁
                </a-descriptions-item>
                <a-descriptions-item label="性别">
                    {{ userInfo.gender }}
                </a-descriptions-item>
                <a-descriptions-item label="身高">
                    {{ userInfo.height_cm }} cm
                </a-descriptions-item>
                <a-descriptions-item label="体重">
                    {{ userInfo.weight_kg }} kg
                </a-descriptions-item>
                <a-descriptions-item label="活动水平">
                    {{ userInfo.activity_level }}
                </a-descriptions-item>
                <a-descriptions-item label="创建时间" :span="3">
                    {{ formatDate(userInfo.created_at) }}
                </a-descriptions-item>
                <a-descriptions-item label="更新时间" :span="3">
                    {{ formatDate(userInfo.updated_at) }}
                </a-descriptions-item>
            </a-descriptions>
        </a-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { UserOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import request from '../../utils/request';

const loading = ref(true);
const userInfo = ref({
    user_id: '',
    display_name: '',
    email: '',
    age: 0,
    gender: '',
    height_cm: 0,
    weight_kg: 0,
    activity_level: '',
    created_at: '',
    updated_at: ''
});

const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

const fetchUserProfile = async () => {
    try {
        loading.value = true;
        const response = await request.get('/user/profile');
        if (response.status === 'success') {
            userInfo.value = response;
        } else {
            message.error(response.message || '获取用户信息失败');
        }
    } catch (error) {
        console.error('获取用户信息失败：', error);
        message.error('获取用户信息失败');
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchUserProfile();
});
</script>

<style scoped>
.welcome-container {
    padding: 24px;
}

.welcome-card {
    max-width: 800px;
    margin: 0 auto;
}

.welcome-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
}

:deep(.ant-descriptions-item-label) {
    width: 120px;
    font-weight: bold;
}
</style> 