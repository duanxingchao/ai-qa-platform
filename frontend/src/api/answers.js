import request from './index'

// 获取答案列表
export function getAnswers(params) {
  return request({
    url: '/answers',
    method: 'get',
    params
  })
}

// 获取答案详情（包含评分信息）
export function getAnswerDetail(answerId) {
  return request({
    url: `/answers/${answerId}`,
    method: 'get'
  })
}

// 获取问题的所有答案对比
export function getAnswerComparison(questionId) {
  return request({
    url: '/answers/comparison',
    method: 'get',
    params: { question_id: questionId }
  })
}

// 批量评分
export function batchScore(data) {
  return request({
    url: '/answers/batch-score',
    method: 'post',
    data
  })
}

// 导出答案数据
export function exportAnswers(params) {
  return request({
    url: '/answers/export',
    method: 'post',
    data: params,
    responseType: 'blob'
  })
}

// 获取答案统计数据
export function getAnswerStatistics(params) {
  return request({
    url: '/answers/statistics',
    method: 'get',
    params
  })
}

// 更新答案状态
export function updateAnswerStatus(answerId, data) {
  return request({
    url: `/answers/${answerId}/status`,
    method: 'put',
    data
  })
} 