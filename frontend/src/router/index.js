import { createRouter, createWebHistory } from 'vue-router';

import BasicLayout from '../layout/BasicLayout.vue';
import UserLogin from '../views/UserLogin.vue';

const routes = [
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/user/UserHome.vue'),
      },
      {
        path: 'health-chat',
        name: 'HealthChat',
        component: () => import('../views/user/HealthChat.vue'),
      },
      /*
      {
        path: 'health-chat-demo',
        name: 'HealthChatDemo',
        component: () => import('../views/user/HealthChatDemo.vue')
      },
      {
        path: 'simple-demo',
        name: 'SimpleChatDemo',
        component: () => import('../views/user/SimpleChatDemo.vue')
      },

      {
        path: 'gemini-components-test',
        name: 'GeminiComponentsTest',
        component: () => import('../views/test/GeminiComponentsTest.vue'),
        meta: { title: 'Gemini 组件测试' }
      },
      */

      /*
      {
        path: 'mcp-test',
        name: 'MCPTest',
        component: () => import('../views/test/MCPTestPage.vue'),
        meta: { title: 'MCP功能测试' }
      },
      */
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/user/UserProfile.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'health-plan',
        name: 'HealthPlan',
        component: () => import('../views/user/HealthPlan.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'health-report',
        name: 'HealthReport',
        component: () => import('../views/user/HealthReport.vue'),
        meta: { requiresAuth: true },
      },
      // 家庭管理路由
      {
        path: 'family',
        name: 'FamilyDashboard',
        component: () => import('../views/user/FamilyDashboard.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'family/members',
        name: 'FamilyMembers',
        component: () => import('../views/user/FamilyMembers.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'family/member/:memberId/health',
        name: 'MemberHealth',
        component: () => import('../views/user/MemberHealth.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'family/challenges',
        name: 'FamilyChallenges',
        component: () => import('../views/user/FamilyChallenges.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'family/alerts',
        name: 'FamilyAlerts',
        component: () => import('../views/user/FamilyAlerts.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'family/settings',
        name: 'FamilySettings',
        component: () => import('../views/user/FamilySettings.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  {
    path: '/login',
    name: 'Login',
    component: UserLogin,
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/UserRegister.vue'),
  },
  {
    path: '/admin',
    component: () => import('../layout/AdminLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminDashboard.vue'),
        meta: { requiresAuth: true, isAdmin: true },
      },
      {
        path: 'prompt-playground',
        name: 'PromptPlayground',
        component: () => import('../views/admin/PromptPlayground.vue'),
        meta: { requiresAuth: true, isAdmin: true },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/AdminUsers.vue'),
        meta: { requiresAuth: true, isAdmin: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

import { useAuthStore } from '../stores/auth';

// 🔧 统一路由守卫 - 使用认证状态管理
router.beforeEach(async (to, _from, next) => {
  // 使用认证状态管理
  const authStore = useAuthStore();

  // 如果路由需要认证
  if (to.meta.requiresAuth) {
    try {
      // 使用统一的认证检查方法
      const isAuthenticated = await authStore.ensureAuthenticated();

      if (isAuthenticated) {
        console.log('✅ 路由守卫：用户已认证，允许访问');
        next();
      } else {
        console.log('🔐 路由守卫：用户未认证，重定向到登录页');
        next({
          path: '/login',
          query: { redirect: to.fullPath },
        });
      }
    } catch (error) {
      console.error('❌ 路由守卫：认证检查失败', error);
      next({
        path: '/login',
        query: { redirect: to.fullPath },
      });
    }
  } else {
    // 不需要认证的路由直接通过
    next();
  }
});

export default router;
