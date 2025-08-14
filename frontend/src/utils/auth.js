/**
 * 认证相关工具函数
 */

/**
 * 检查用户是否已登录
 * @returns {boolean} 是否已登录
 */
export function isLoggedIn() {
  // 简单的登录状态检查，可以根据实际需求修改
  const token = localStorage.getItem('auth_token')
  return !!token
}

/**
 * 获取当前用户信息
 * @returns {object|null} 用户信息
 */
export function getCurrentUser() {
  const userStr = localStorage.getItem('current_user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch (e) {
      console.error('解析用户信息失败:', e)
      return null
    }
  }
  return null
}

/**
 * 设置用户登录状态
 * @param {string} token 认证令牌
 * @param {object} user 用户信息
 */
export function setLoginStatus(token, user) {
  localStorage.setItem('auth_token', token)
  localStorage.setItem('current_user', JSON.stringify(user))
}

/**
 * 清除登录状态
 */
export function clearLoginStatus() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('current_user')
}

/**
 * 获取认证令牌
 * @returns {string|null} 认证令牌
 */
export function getAuthToken() {
  return localStorage.getItem('auth_token')
}

/**
 * 清除认证信息（别名函数）
 */
export function clearAuth() {
  clearLoginStatus()
}

/**
 * 设置认证令牌（别名函数）
 * @param {string} token 认证令牌
 * @param {object} user 用户信息
 */
export function setToken(token, user) {
  setLoginStatus(token, user)
}
