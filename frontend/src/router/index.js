import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '@/utils/auth'
import { isAdmin } from '@/stores/user'

const routes = [
  {
    path: '/',
    redirect: '/questions'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '用户登录',
      hideLayout: true,
      requiresAuth: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: {
      title: '用户注册',
      hideLayout: true,
      requiresAuth: false
    }
  },
  {
    path: '/questions',
    name: 'Questions',
    component: () => import('@/views/Questions/index.vue'),
    meta: {
      title: '问题管理',
      requiresAuth: true
    }
  },
  {
    path: '/badcase',
    name: 'BadcaseAnalysis',
    component: () => import('@/views/BadcaseAnalysis/index.vue'),
    meta: {
      title: 'badcase分析',
      requiresAuth: true
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: {
      title: '系统配置',
      requiresAuth: true
    }
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: () => import('@/views/UserManagement.vue'),
    meta: {
      title: '用户管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/application-management',
    name: 'ApplicationManagement',
    component: () => import('@/views/ApplicationManagement.vue'),
    meta: {
      title: '申请审核',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/access-stats',
    name: 'AccessStats',
    component: () => import('@/views/AccessStats.vue'),
    meta: {
      title: '访问统计',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/display',
    name: 'Display',
    component: () => import('@/views/Display/index.vue'),
    meta: {
      title: '大屏展示',
      hideLayout: true  // 隐藏默认布局
    }
  },
  {
    path: '/bigscreen',
    name: 'BigScreen',
    component: () => import('@/views/BigScreen.vue'),
    meta: {
      title: 'AI实验室数据大屏',
      hideLayout: true  // 隐藏默认布局
    }
  },
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('@/views/Debug.vue'),
    meta: { title: 'API调试', requiresAuth: false }
  },
  {
    path: '/responsive-test',
    name: 'ResponsiveTest',
    component: () => import('@/views/ResponsiveTest.vue'),
    meta: { title: '响应式测试', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI问答平台管理后台`
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth !== false) {
    if (!isLoggedIn()) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }

    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !isAdmin.value) {
      // 没有管理员权限，跳转到首页
      next('/')
      return
    }
  }

  // 如果已登录用户访问登录页，跳转到首页
  if ((to.path === '/login' || to.path === '/register') && isLoggedIn()) {
    next('/')
    return
  }

  next()
})

export default router 