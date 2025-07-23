import request from './index'

// 获取评分数据列表
export function getScores(params) {
  return request({
    url: '/scores',
    method: 'get',
    params
  })
}

// 获取评分统计数据
export function getScoreStatistics() {
  return request({
    url: '/scores/statistics',
    method: 'get'
  })
}

// 获取模型对比数据
export function getModelComparison(params) {
  return request({
    url: '/scores/model-comparison',
    method: 'get',
    params
  })
} 