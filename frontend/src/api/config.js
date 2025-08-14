/**
 * 系统配置API服务
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

/**
 * 获取工作流配置
 */
export function getWorkflowConfig() {
  return request({
    url: '/config/workflow',
    method: 'get'
  })
}

/**
 * 更新工作流配置
 */
export function updateWorkflowConfig(data) {
  return request({
    url: '/config/workflow',
    method: 'put',
    data
  })
}

/**
 * 获取待导出问题数量
 */
export function getExportQuestionsCount() {
  return request({
    url: '/answer-generation/export/questions-count',
    method: 'get'
  })
}

/**
 * 导出问题Excel
 */
export function exportQuestionsForAnswerGeneration(data = {}) {
  return request({
    url: '/answer-generation/export/questions-for-answer-generation',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * 验证导入文件
 */
export function validateImportFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/answer-generation/import/validate-file',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导入生成的答案
 */
export function importGeneratedAnswers(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/answer-generation/import/generated-answers',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取导入历史记录
 */
export function getImportHistory(params = {}) {
  return request({
    url: '/answer-generation/import/history',
    method: 'get',
    params
  })
}
