import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard/index.vue'),
    meta: {
      title: '数据概览'
    }
  },
  {
    path: '/questions',
    name: 'Questions',
    component: () => import('@/views/Questions/index.vue'),
    meta: {
      title: '问题管理'
    }
  },
  {
    path: '/answers',
    name: 'Answers',
    component: () => import('@/views/Answers/index.vue'),
    meta: {
      title: '答案对比'
    }
  },
  {
    path: '/scores',
    name: 'Scores',
    component: () => import('@/views/Scores/index.vue'),
    meta: {
      title: '评分分析'
    }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/Monitor/index.vue'),
    meta: {
      title: '系统监控'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings/index.vue'),
    meta: {
      title: '系统配置'
    }
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
  next()
})

export default router 