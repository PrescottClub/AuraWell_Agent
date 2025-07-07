<template>
  <div class="min-h-screen bg-background flex">
    <!-- 侧边栏 -->
    <aside class="w-64 bg-background-alt border-r border-border flex flex-col">
      <!-- Logo 区域 -->
      <div class="p-4 border-b border-border">
        <div class="flex items-center space-x-3">
          <img src="/vite.svg" class="w-8 h-8">
          <h1 class="text-xl font-bold text-text-primary">AuraWell</h1>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 p-2 space-y-1">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <a @click="navigate" :class="[
            'flex items-center w-full text-left p-3 rounded-lg transition-colors duration-200 cursor-pointer',
            isActive
              ? 'bg-secondary text-primary font-semibold'
              : 'text-text-secondary hover:bg-secondary/60'
          ]">
            <component :is="item.icon" class="w-5 h-5 mr-3" />
            <span>{{ item.name }}</span>
          </a>
        </router-link>
      </nav>

      <!-- 用户信息区域 -->
      <div class="p-4 border-t border-border">
        <div v-if="!authStore.token" class="space-y-2">
          <button
            @click="router.push('/login')"
            class="w-full text-primary bg-white border border-border hover:bg-secondary/60 font-semibold rounded-lg text-sm px-5 py-2.5 text-center transition-colors duration-200"
          >
            登录
          </button>
          <button
            @click="router.push('/register')"
            class="w-full text-white bg-primary hover:bg-primary-hover font-semibold rounded-lg text-sm px-5 py-2.5 text-center transition-colors duration-200"
          >
            注册
          </button>
        </div>

        <div v-else class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
            <UserOutlined class="w-5 h-5 text-primary" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-semibold text-text-primary">
              {{ userStore.userProfile.username || '用户' }}
            </p>
            <button
              @click="handleLogout"
              class="text-xs text-text-secondary hover:underline"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区域 -->
    <div class="flex-1 flex flex-col">
      <!-- 顶部栏 -->
      <header class="bg-white border-b border-border px-6 py-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-text-primary">
            {{ currentPageTitle }}
          </h2>
          <!-- 可以添加搜索框、通知等 -->
        </div>
      </header>

      <!-- 主内容 -->
      <main class="flex-1 p-4 sm:p-6 md:p-8 bg-background overflow-y-auto">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <TheToaster />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  HomeOutlined,
  MessageOutlined,
  UserOutlined,
  FileTextOutlined,
  TeamOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';
import { message } from 'ant-design-vue';
import TheToaster from '../components/ui/TheToaster.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const userStore = useUserStore();

// 菜单项数据
const menuItems = ref([
  {
    path: '/',
    name: '首页',
    icon: HomeOutlined,
  },
  {
    path: '/health-chat',
    name: '健康咨询',
    icon: MessageOutlined,
  },
  {
    path: '/health-plan',
    name: '健康计划',
    icon: FileTextOutlined,
  },
  {
    path: '/health-report',
    name: '健康报告',
    icon: BarChartOutlined,
  },
  {
    path: '/family',
    name: '家庭管理',
    icon: TeamOutlined,
  },
  {
    path: '/profile',
    name: '个人档案',
    icon: UserOutlined,
  },
]);

// 当前页面标题
const currentPageTitle = computed(() => {
  const currentItem = menuItems.value.find(item => item.path === route.path);
  return currentItem?.name || '页面';
});

// 处理退出登录
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

// 初始化认证状态
const initializeAuth = async () => {
  try {
    const isAuthenticated = await authStore.ensureAuthenticated();
    if (isAuthenticated && !userStore.userProfile.username) {
      await userStore.fetchUserProfile();
    }
  } catch (error) {
    console.warn('⚠️ 认证初始化失败:', error);
  }
};

// 页面加载时初始化
initializeAuth();
</script>

<style scoped>
/* 页面转场动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* 额外的样式优化 */
.router-link-active {
  /* Vue Router 会自动添加这个类 */
}

/* 滚动条美化 */
main::-webkit-scrollbar {
  width: 6px;
}

main::-webkit-scrollbar-track {
  @apply bg-background-alt;
}

main::-webkit-scrollbar-thumb {
  @apply bg-border rounded-full;
}

main::-webkit-scrollbar-thumb:hover {
  @apply bg-text-disabled;
}
</style>