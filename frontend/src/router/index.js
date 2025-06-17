import { createRouter, createWebHistory } from 'vue-router';

import App from '../App.vue';
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

    ]
  },
  // 家庭管理路由
  {
    path: '/family',
    component: () => import('../layout/BasicLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'FamilyDashboard',
        component: () => import('../views/user/FamilyDashboard.vue'),
        meta: { requiresAuth: true }
      }
      // 其他家庭管理页面暂时注释，等待后续实现
      // {
      //   path: 'members',
      //   name: 'FamilyMembers',
      //   component: () => import('../views/user/FamilyMembers.vue'),
      //   meta: { requiresAuth: true }
      // },
      // {
      //   path: 'member/:memberId/health',
      //   name: 'MemberHealth',
      //   component: () => import('../views/user/MemberHealth.vue'),
      //   meta: { requiresAuth: true }
      // },
      // {
      //   path: 'challenges',
      //   name: 'FamilyChallenges',
      //   component: () => import('../views/user/FamilyChallenges.vue'),
      //   meta: { requiresAuth: true }
      // },
      // {
      //   path: 'alerts',
      //   name: 'FamilyAlerts',
      //   component: () => import('../views/user/FamilyAlerts.vue'),
      //   meta: { requiresAuth: true }
      // },
      // {
      //   path: 'settings',
      //   name: 'FamilySettings',
      //   component: () => import('../views/user/FamilySettings.vue'),
      //   meta: { requiresAuth: true }
      // }
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

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token');
  const isLoggedIn = !!token;

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    });
  } else {
    next();
  }
});

export default router; 