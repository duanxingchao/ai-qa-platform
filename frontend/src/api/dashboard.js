import request from './index'

// 获取仪表板汇总数据
export function getStats(params) {
  return request({
    url: '/dashboard',
    method: 'get',
    params
  })
}

// 获取系统健康状态
export function getSystemHealth() {
  return request({
    url: '/scheduler/status',
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

// 获取问题统计数据
export function getTrends(params) {
  return request({
    url: '/questions/statistics',
    method: 'get',
    params
  })
}

// 获取处理统计数据
export function getModelComparison() {
  return request({
    url: '/process/statistics',
    method: 'get'
  })
} 