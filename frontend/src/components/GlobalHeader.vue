<template>
    <div id="globalHeader">
        <a-row :wrap="false">
            <a-col felx="100px">
                <div class="title-bar">
                <img src="/vite.svg" class="logo">
                <div class="title">AuraWell Agent</div>
            </div>
            </a-col>
            <a-col flex="auto">
                <a-menu
                  v-model:selectedKeys="current"
                  mode="horizontal"
                  :items="items"
                  @click="handleMenuClick"
                />
            </a-col>
            <a-col flex="200px">
                <div class="user-actions">
                    <!-- 未登录状态 -->
                    <div v-if="!authStore.token" class="auth-buttons">
                        <a-button @click="router.push('/login')">登录</a-button>
                        <a-button type="primary" @click="router.push('/register')">注册</a-button>
                    </div>

                    <!-- 已登录状态 -->
                    <div v-else class="user-menu">
                        <a-dropdown>
                            <a-button type="text" class="user-info-btn">
                                <UserOutlined />
                                <span class="username">{{ userStore.userProfile.username || '用户' }}</span>
                                <DownOutlined />
                            </a-button>
                            <template #overlay>
                                <a-menu>
                                    <a-menu-item @click="router.push('/profile')">
                                        <UserOutlined />
                                        个人档案
                                    </a-menu-item>
                                    <a-menu-item @click="router.push('/health-plan')">
                                        <FileTextOutlined />
                                        我的计划
                                    </a-menu-item>
                                    <a-menu-divider />
                                    <a-menu-item @click="handleLogout" class="logout-item">
                                        <LogoutOutlined />
                                        退出登录
                                    </a-menu-item>
                                </a-menu>
                            </template>
                        </a-dropdown>
                    </div>
                </div>
            </a-col>
        </a-row>
    </div>
</template>
<script setup>
import { h, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  HomeOutlined,
  MessageOutlined,
  UserOutlined,
  FileTextOutlined,
  DownOutlined,
  LogoutOutlined,
  TeamOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';
import { message } from 'ant-design-vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const userStore = useUserStore();
const current = ref(['home']);

const items = ref([
    {
        key: 'home',
        icon: () => h(HomeOutlined),
        label: '首页',
        title: '首页',
    },
    {
        key: 'health-chat',
        icon: () => h(MessageOutlined),
        label: '健康咨询',
        title: '健康咨询',
    },
    {
        key: 'health-plan',
        icon: () => h(FileTextOutlined),
        label: '健康计划',
        title: '健康计划',
    },
    {
        key: 'health-report',
        icon: () => h(BarChartOutlined),
        label: '健康报告',
        title: '健康报告',
    },
    {
        key: 'family',
        icon: () => h(TeamOutlined),
        label: '家庭管理',
        title: '家庭管理',
    },
    {
        key: 'profile',
        icon: () => h(UserOutlined),
        label: '个人档案',
        title: '个人档案',
    }
]);

// 处理菜单点击
const handleMenuClick = ({ key }) => {
  current.value = [key];

  switch (key) {
    case 'home':
      router.push('/');
      break;
    case 'health-chat':
      router.push('/health-chat');
      break;
    case 'health-plan':
      router.push('/health-plan');
      break;
    case 'health-report':
      router.push('/health-report');
      break;
    case 'family':
      router.push('/family');
      break;
    case 'profile':
      router.push('/profile');
      break;
  }
};

// 处理用户退出登录
const handleLogout = async () => {
  try {
    authStore.clearToken();
    userStore.clearUserData();
    message.success('退出登录成功');
    router.push('/');
  } catch (error) {
    message.error('退出登录失败');
  }
};

// 根据当前路由设置选中状态
const updateCurrentMenu = () => {
  const path = route.path;
  if (path === '/') {
    current.value = ['home'];
  } else if (path.includes('health-chat')) {
    current.value = ['health-chat'];
  } else if (path.includes('health-plan')) {
    current.value = ['health-plan'];
  } else if (path.includes('health-report')) {
    current.value = ['health-report'];
  } else if (path.includes('family')) {
    current.value = ['family'];
  } else if (path.includes('profile')) {
    current.value = ['profile'];
  } else {
    current.value = [];
  }
};

// 监听路由变化
router.afterEach(() => {
  updateCurrentMenu();
});

// 初始化
updateCurrentMenu();

// 🔧 开发环境自动认证和获取用户信息
const initializeAuth = async () => {
  try {
    // 确保认证状态
    const isAuthenticated = await authStore.ensureAuthenticated();

    if (isAuthenticated && !userStore.userProfile.username) {
      // 获取用户信息
      await userStore.fetchUserProfile();
      console.log('✅ 用户信息获取成功');
    }
  } catch (error) {
    console.warn('⚠️ 认证初始化失败:', error);
  }
};

// 初始化认证
initializeAuth();
</script>

<style scoped>
#globalHeader {
    padding: 0 50px;
    background-color: #fff;
    box-shadow: 0 2px rgba(0, 0, 0, 0.15);
}

.title-bar {
    display: flex;
    align-items: center;
}

.title {
    color: black;
    font-size: 18px;
    margin-left: 16px;
}

.logo {
    height: 18px;
}

.user-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
}

.auth-buttons {
    display: flex;
    gap: 12px;
    align-items: center;
}

.user-menu {
    display: flex;
    align-items: center;
}

.user-info-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
}

.user-info-btn:hover {
    background-color: #f5f5f5;
}

.username {
    font-weight: 500;
    color: #1f2937;
}

.logout-item {
    color: #ef4444 !important;
}

.logout-item:hover {
    background-color: #fef2f2 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .auth-buttons {
        gap: 8px;
    }

    .auth-buttons .ant-btn {
        padding: 4px 8px;
        font-size: 12px;
    }

    .username {
        display: none;
    }
}



</style>