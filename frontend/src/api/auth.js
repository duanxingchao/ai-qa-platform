/**
 * 认证相关API接口
 */
import request from '@/utils/request'

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 */
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

/**
 * 验证token有效性
 */
export function verifyToken() {
  return request({
    url: '/auth/verify',
    method: 'get'
  })
}

/**
 * 用户注册申请
 * @param {Object} data - 注册数据
 * @param {string} data.username - 登录账号（员工号码）
 * @param {string} data.display_name - 用户显示名称
 * @param {string} data.password - 密码
 * @param {string} data.apply_role - 申请角色 (admin/user)
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 */
export function getUserProfile() {
  return request({
    url: '/auth/profile',
    method: 'get'
  })
}

/**
 * 检查用户名是否可用
 * @param {string} username - 用户名
 */
export function checkUsername(username) {
  return request({
    url: '/auth/check-username',
    method: 'post',
    data: { username }
  })
}
