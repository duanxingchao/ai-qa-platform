/**
 * 访问统计API接口
 */
import request from '@/utils/request'

/**
 * 获取访问统计数据
 */
export function getAccessStats() {
  return request({
    url: '/stats/access',
    method: 'get'
  })
}

/**
 * 获取访问日志
 * @param {Object} params - 查询参数
 */
export function getAccessLogs(params = {}) {
  return request({
    url: '/stats/access-logs',
    method: 'get',
    params
  })
}
