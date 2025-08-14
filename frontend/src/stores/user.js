/**
 * 用户状态管理
 */
import { ref, computed } from 'vue'
import { getCurrentUser } from '@/utils/auth'

// 响应式用户信息
export const userInfo = ref(getCurrentUser())

// 计算属性：是否为管理员
export const isAdmin = computed(() => {
  if (!userInfo.value) {
    return false
  }
  return userInfo.value.role === 'admin' || userInfo.value.isAdmin === true
})

/**
 * 更新用户信息
 * @param {object} user 用户信息
 */
export function updateUserInfo(user) {
  userInfo.value = user
  if (user) {
    localStorage.setItem('current_user', JSON.stringify(user))
  }
}

/**
 * 清除用户信息
 */
export function clearUserInfo() {
  userInfo.value = null
  localStorage.removeItem('current_user')
}

/**
 * 检查用户是否有特定权限
 * @param {string} permission 权限名称
 * @returns {boolean} 是否有权限
 */
export function hasPermission(permission) {
  if (!userInfo.value) {
    return false
  }

  // 管理员拥有所有权限
  if (isAdmin.value) {
    return true
  }

  // 检查用户权限列表
  const permissions = userInfo.value.permissions || []
  return permissions.includes(permission)
}

/**
 * 获取用户角色
 * @returns {string} 用户角色
 */
export function getUserRole() {
  return userInfo.value?.role || 'guest'
}

/**
 * 检查用户是否可以访问指定路由
 * @param {string} routeName 路由名称
 * @returns {boolean} 是否可以访问
 */
export function canAccessRoute(routeName) {
  if (!userInfo.value) {
    return false
  }

  // 管理员可以访问所有路由
  if (isAdmin.value) {
    return true
  }

  // 根据路由名称检查权限
  const routePermissions = {
    'Dashboard': ['view_dashboard'],
    'Questions': ['view_questions'],
    'Answers': ['view_answers'],
    'Scores': ['view_scores'],
    'Settings': ['admin'],
    'Monitor': ['view_monitor']
  }

  const requiredPermissions = routePermissions[routeName] || []
  return requiredPermissions.some(permission => hasPermission(permission))
}
