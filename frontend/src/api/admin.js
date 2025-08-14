/**
 * 管理员功能API接口
 */
import request from '@/utils/request'

/**
 * 获取用户申请列表
 * @param {Object} params - 查询参数
 */
export function getApplications(params = {}) {
  return request({
    url: '/admin/applications',
    method: 'get',
    params
  })
}

/**
 * 批准用户申请
 * @param {number} id - 申请ID
 */
export function approveApplication(id) {
  return request({
    url: `/admin/applications/${id}/approve`,
    method: 'post'
  })
}

/**
 * 拒绝用户申请
 * @param {number} id - 申请ID
 */
export function rejectApplication(id) {
  return request({
    url: `/admin/applications/${id}/reject`,
    method: 'post'
  })
}

/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 */
export function getUsers(params = {}) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 修改用户状态
 * @param {number} id - 用户ID
 * @param {string} status - 新状态 (active/inactive)
 */
export function updateUserStatus(id, status) {
  return request({
    url: `/admin/users/${id}`,
    method: 'put',
    data: { status }
  })
}

/**
 * 删除用户
 * @param {number} id - 用户ID
 */
export function deleteUser(id) {
  return request({
    url: `/admin/users/${id}`,
    method: 'delete'
  })
}
