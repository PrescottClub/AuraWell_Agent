<template>
    <a-layout class="min-h-screen">
        <a-layout-sider v-model:collapsed="collapsed" collapsible>
            <div class="logo p-4 text-white text-center text-lg font-bold">
                AuraWell
            </div>
            <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
                <a-menu-item key="dashboard" @click="() => router.push('/admin/dashboard')">
                    <template #icon>
                        <DashboardOutlined />
                    </template>
                    <span>仪表盘</span>
                </a-menu-item>
                <a-menu-item key="users" @click="() => router.push('/admin/users')">
                    <template #icon>
                        <UserOutlined />
                    </template>
                    <span>用户管理</span>
                </a-menu-item>
                <a-menu-item key="settings" @click="() => router.push('/admin/settings')">
                    <template #icon>
                        <SettingOutlined />
                    </template>
                    <span>系统设置</span>
                </a-menu-item>
            </a-menu>
        </a-layout-sider>
        <a-layout>
            <a-layout-header class="bg-white px-4 flex items-center justify-between">
                <div class="flex-1"></div>
                <div class="flex items-center">
                    <a-dropdown>
                        <a class="ant-dropdown-link" @click.prevent>
                            <template>
                                <a-avatar :size="{ xs: 24, sm: 32, md: 40, lg: 64, xl: 80, xxl: 100 }">
                                    1
                                </a-avatar>
                            </template>
                            管理员
                            <DownOutlined />
                        </a>
                        <template #overlay>
                            <a-menu>
                                <a-menu-item key="profile">
                                    个人信息
                                </a-menu-item>
                                <a-menu-item key="logout" @click="handleLogout">
                                    退出登录
                                </a-menu-item>
                            </a-menu>
                        </template>
                    </a-dropdown>
                </div>
            </a-layout-header>
            <a-layout-content class="content-container">
                <div class="content-wrapper">
                    <router-view></router-view>
                </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
                Ant Design ©2018 Created by Ant UED
            </a-layout-footer>
        </a-layout>
    </a-layout>
</template>
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    DashboardOutlined,
    UserOutlined,
    SettingOutlined,
    DownOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const collapsed = ref(false);
const selectedKeys = ref(['dashboard']);

const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    router.push('/login');
};
</script>
<style scoped>
.trigger {
    cursor: pointer;
    transition: color 0.3s;
}

.trigger:hover {
    color: #1890ff;
}

.logo {
    height: 32px;
    margin: 16px;
    background: rgba(255, 255, 255, 0.3);
}

.content-container {
    height: calc(100vh - 64px);
    overflow: auto;
    background: #f0f2f5;
}

.content-wrapper {
    padding: 24px;
    min-height: 100%;
    background: #fff;
    margin: 0;
    height: 100%;
}
</style>