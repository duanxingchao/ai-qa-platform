/**
 * 热词分析API服务
 */
import request from './index'

/**
 * 获取词云数据
 * @param {Object} params - 查询参数
 * @param {string} params.time_range - 时间范围 ('week', 'month', 'all')
 * @param {number} params.limit - 返回热词数量限制
 */
export function getWordCloudData(params = {}) {
  return request({
    url: '/analysis/word-cloud',
    method: 'get',
    params: {
      time_range: params.time_range || 'week',
      limit: params.limit || 20
    }
  })
}

/**
 * 获取热词列表（简化版本）
 * @param {Object} params - 查询参数
 * @param {string} params.time_range - 时间范围
 * @param {number} params.limit - 返回热词数量限制
 */
export function getHotWords(params = {}) {
  return request({
    url: '/analysis/hot-words',
    method: 'get',
    params: {
      time_range: params.time_range || 'week',
      limit: params.limit || 20
    }
  })
}
