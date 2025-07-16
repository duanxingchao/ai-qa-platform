import request from './index'

// 获取统计数据
export function getStats() {
  return request({
    url: '/sync/statistics',
    method: 'get'
  })
}

// 获取系统健康状态
export function getSystemHealth() {
  return request({
    url: '/sync/health',
    method: 'get'
  })
}

// 获取同步状态
export function getSyncStatus() {
  return request({
    url: '/sync/status',
    method: 'get'
  })
}

// 获取趋势数据
export function getTrends(params) {
  return request({
    url: '/dashboard/trends',
    method: 'get',
    params
  })
}

// 获取模型性能对比数据
export function getModelComparison() {
  return request({
    url: '/dashboard/model-comparison',
    method: 'get'
  })
} 