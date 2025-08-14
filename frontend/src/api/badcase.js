import request from './index'

// 获取badcase统计数据
export function getBadcaseStatistics(params) {
  return request({
    url: '/badcase/statistics',
    method: 'get',
    params
  })
}

// 获取badcase列表
export function getBadcaseList(params) {
  return request({
    url: '/badcase/list',
    method: 'get',
    params
  })
}

// 获取badcase详情
export function getBadcaseDetail(id) {
  return request({
    url: `/badcase/detail/${id}`,
    method: 'get'
  })
}

// 提交badcase复核
export function submitBadcaseReview(id, data) {
  return request({
    url: `/badcase/review/${id}`,
    method: 'put',
    data
  })
}

// 获取分类列表
export function getBadcaseCategories() {
  return request({
    url: '/questions/categories',
    method: 'get'
  })
}

// 获取badcase分类分布
export function getBadcaseCategoryDistribution(params) {
  return request({
    url: '/badcase/category-distribution',
    method: 'get',
    params
  })
}

// 获取badcase趋势数据
export function getBadcaseTrend(params) {
  return request({
    url: '/badcase/trend',
    method: 'get',
    params
  })
}

// 获取AI模型badcase对比数据
export function getBadcaseModelComparison(params) {
  return request({
    url: '/badcase/model-comparison',
    method: 'get',
    params
  })
}

// 标记badcase为已处理
export function markBadcaseResolved(id, data) {
  return request({
    url: `/badcase/${id}/resolve`,
    method: 'post',
    data
  })
}

// 优化badcase
export function optimizeBadcase(id, data) {
  return request({
    url: `/badcase/${id}/optimize`,
    method: 'post',
    data
  })
}

// 批量处理badcase
export function batchProcessBadcase(data) {
  return request({
    url: '/badcase/batch-process',
    method: 'post',
    data
  })
}

// 导出badcase报告
export function exportBadcaseReport(params) {
  return request({
    url: '/badcase/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 获取badcase优化建议
export function getBadcaseOptimizationSuggestions(id) {
  return request({
    url: `/badcase/${id}/suggestions`,
    method: 'get'
  })
}

// 提交badcase反馈
export function submitBadcaseFeedback(id, data) {
  return request({
    url: `/badcase/${id}/feedback`,
    method: 'post',
    data
  })
}

// 获取维度分析数据
export function getDimensionAnalysis(params) {
  return request({
    url: '/badcase/dimension-analysis',
    method: 'get',
    params
  })
}

// 获取Top3分类分析数据（大屏专用）
export function getTopCategoriesAnalysis(params) {
  return request({
    url: '/badcase/top-categories-analysis',
    method: 'get',
    params
  })
}
