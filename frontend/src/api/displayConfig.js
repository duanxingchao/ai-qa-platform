/**
 * 大屏展示配置API服务
 */
import request from './index'

/**
 * 获取大屏展示配置
 */
export function getDisplayConfigs() {
  return request({
    url: '/config/display',
    method: 'get'
  })
}

/**
 * 更新大屏展示配置
 */
export function updateDisplayConfigs(data) {
  return request({
    url: '/config/display',
    method: 'put',
    data
  })
}
