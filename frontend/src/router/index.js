import { createRouter, createWebHistory } from 'vue-router';

import BasicLayout from '../layout/BasicLayout.vue';
import Login from '../views/Login.vue';

const routes = [
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/user/Home.vue')
      },
      {
        path: 'health-chat',
        name: 'HealthChat',
        component: () => import('../views/user/HealthChat.vue')
      },
      {
        path: 'health-chat-demo',
        name: 'HealthChatDemo',
        component: () => import('../views/user/HealthChatDemo.vue')
      },
      {
        path: 'test',
        name: 'TestPage',
        component: () => import('../views/user/TestPage.vue')
      },
      {
        path: 'simple-demo',
        name: 'SimpleChatDemo',
        component: () => import('../views/user/SimpleChatDemo.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/user/Profile.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'health-plan',
        name: 'HealthPlan',
        component: () => import('../views/user/HealthPlan.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'health-report',
        name: 'HealthReport',
        component: () => import('../views/user/HealthReport.vue'),
        meta: { requiresAuth: true }
      },
      // 家庭管理路由
      {
        path: 'family',
        name: 'FamilyDashboard',
        component: () => import('../views/user/FamilyDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'family/members',
        name: 'FamilyMembers',
        component: () => import('../views/user/FamilyMembers.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'family/member/:memberId/health',
        name: 'MemberHealth',
        component: () => import('../views/user/MemberHealth.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'family/challenges',
        name: 'FamilyChallenges',
        component: () => import('../views/user/FamilyChallenges.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'family/alerts',
        name: 'FamilyAlerts',
        component: () => import('../views/user/FamilyAlerts.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'family/settings',
        name: 'FamilySettings',
        component: () => import('../views/user/FamilySettings.vue'),
        meta: { requiresAuth: true }
      }

    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 🔧 统一路由守卫 - 使用认证状态管理
router.beforeEach(async (to, _from, next) => {
  // 导入认证状态管理
  const { useAuthStore } = await import('../stores/auth');
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
          query: { redirect: to.fullPath }
        });
      }
    } catch (error) {
      console.error('❌ 路由守卫：认证检查失败', error);
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    }
  } else {
    // 不需要认证的路由直接通过
    next();
  }
});

export default router; 