import request from './index'

// 获取问题列表
export function getQuestions(params) {
  return request({
    url: '/questions',
    method: 'get',
    params
  })
}

// 获取问题详情
export function getQuestionDetail(id) {
  return request({
    url: `/questions/${id}`,
    method: 'get'
  })
}

// 更新问题信息
export function updateQuestion(id, data) {
  return request({
    url: `/questions/${id}`,
    method: 'put',
    data
  })
}

// 批量操作问题
export function batchUpdateQuestions(data) {
  return request({
    url: '/questions/batch',
    method: 'post',
    data
  })
}

// 导出问题数据
export function exportQuestions(params) {
  return request({
    url: '/questions/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

// 获取问题分类列表
export function getQuestionCategories() {
  return request({
    url: '/questions/categories',
    method: 'get'
  })
}

// 重新分类问题
export function reclassifyQuestion(id) {
  return request({
    url: `/questions/${id}/reclassify`,
    method: 'post'
  })
} 