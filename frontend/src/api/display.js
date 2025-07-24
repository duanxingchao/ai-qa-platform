/**
 * 大屏展示页面API服务
 */
import request from './index'

/**
 * 获取大屏仪表板数据
 */
export function getDisplayDashboard() {
  return request({
    url: '/display/dashboard',
    method: 'get'
  })
}

/**
 * 获取实时更新数据
 */
export function getRealtimeUpdate() {
  return request({
    url: '/display/realtime',
    method: 'get'
  })
} 