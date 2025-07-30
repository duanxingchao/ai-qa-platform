/**
 * 调度器相关API服务
 */
import request from './index'

/**
 * 获取调度器状态
 */
export function getSchedulerStatus() {
  return request({
    url: '/scheduler/status',
    method: 'get'
  })
}

/**
 * 启用调度器
 */
export function enableScheduler() {
  return request({
    url: '/scheduler/enable',
    method: 'post'
  })
}

/**
 * 禁用调度器
 */
export function disableScheduler() {
  return request({
    url: '/scheduler/disable',
    method: 'post'
  })
}

/**
 * 获取工作流状态
 */
export function getWorkflowStatus() {
  return request({
    url: '/scheduler/workflow/status',
    method: 'get'
  })
}

/**
 * 手动执行工作流阶段
 */
export function executeWorkflowPhase(phase) {
  return request({
    url: `/scheduler/workflow/phases/${phase}/execute`,
    method: 'post'
  })
}

/**
 * 获取定时任务列表
 */
export function getScheduledJobs() {
  return request({
    url: '/scheduler/jobs',
    method: 'get'
  })
}

/**
 * 暂停任务
 */
export function pauseJob(jobId) {
  return request({
    url: `/scheduler/jobs/${jobId}/pause`,
    method: 'post'
  })
}

/**
 * 恢复任务
 */
export function resumeJob(jobId) {
  return request({
    url: `/scheduler/jobs/${jobId}/resume`,
    method: 'post'
  })
}

/**
 * 立即执行任务
 */
export function triggerJob(jobId) {
  return request({
    url: `/scheduler/jobs/${jobId}/trigger`,
    method: 'post'
  })
}

/**
 * 获取调度器配置
 */
export function getSchedulerConfig() {
  return request({
    url: '/scheduler/config',
    method: 'get'
  })
}

/**
 * 更新调度器配置
 */
export function updateSchedulerConfig(config) {
  return request({
    url: '/scheduler/config',
    method: 'put',
    data: config
  })
}
