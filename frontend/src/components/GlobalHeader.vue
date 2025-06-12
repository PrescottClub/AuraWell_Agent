<template>
    <div id="globalHeader">
        <a-row :wrap="false">
            <a-col felx="100px">
                <div class="title-bar">
                <img src="../../public/vite.svg" class="logo">
                <div class="title">Auraweell Agent</div>
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
            <a-col felx="100px">
                <div class="user-login-status">
                <a-button type="primary" href="/login">LoginIn</a-button>
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
  SettingOutlined,
  DashboardOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const route = useRoute();
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
        key: 'dashboard',
        icon: () => h(DashboardOutlined),
        label: '健康数据',
        title: '健康数据',
    },
    {
        key: 'settings',
        icon: () => h(SettingOutlined),
        label: '设置',
        title: '设置',
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
    case 'dashboard':
      router.push('/admin/dashboard');
      break;
    case 'settings':
      router.push('/admin/settings');
      break;
  }
};

// 根据当前路由设置选中状态
const updateCurrentMenu = () => {
  const path = route.path;
  if (path === '/') {
    current.value = ['home'];
  } else if (path.includes('health-chat')) {
    current.value = ['health-chat'];
  } else if (path.includes('dashboard')) {
    current.value = ['dashboard'];
  } else if (path.includes('settings')) {
    current.value = ['settings'];
  }
};

// 监听路由变化
router.afterEach(() => {
  updateCurrentMenu();
});

// 初始化
updateCurrentMenu();
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



</style>