import request from '@/utils/request'

/**
 * 获取badcase统计数据
 * @param {string} timeRange - 时间范围 ('today', 'week', 'month', 'year', 'all')
 * @returns {Promise}
 */
export function getBadcaseStatistics(timeRange = 'week') {
  return request({
    url: '/api/badcase/statistics',
    method: 'get',
    params: {
      time_range: timeRange
    }
  })
}

/**
 * 获取badcase列表
 * @param {Object} params - 查询参数
 * @param {string} params.time_range - 时间范围
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页大小
 * @param {string} params.status - 状态筛选
 * @returns {Promise}
 */
export function getBadcaseList(params) {
  return request({
    url: '/api/badcase/list',
    method: 'get',
    params
  })
}

/**
 * 获取badcase详情
 * @param {number} id - 问题ID
 * @returns {Promise}
 */
export function getBadcaseDetail(id) {
  return request({
    url: `/api/badcase/detail/${id}`,
    method: 'get'
  })
}

/**
 * 更新复核状态
 * @param {number} id - 问题ID
 * @param {Object} data - 更新数据
 * @param {string} data.status - 复核状态 ('reviewed', 'optimized')
 * @param {Object} data.scores - 新的评分数据（可选）
 * @returns {Promise}
 */
export function updateReviewStatus(id, data) {
  return request({
    url: `/api/badcase/review/${id}`,
    method: 'put',
    data
  })
}

/**
 * 手动触发badcase检测
 * @param {Object} data - 检测参数
 * @param {Array} data.question_business_ids - 问题业务ID列表（可选）
 * @returns {Promise}
 */
export function manualDetectBadcase(data = {}) {
  return request({
    url: '/api/badcase/detect',
    method: 'post',
    data
  })
}

/**
 * 获取当前badcase阈值
 * @returns {Promise}
 */
export function getBadcaseThreshold() {
  return request({
    url: '/api/badcase/threshold',
    method: 'get'
  })
}

/**
 * 获取系统配置
 * @param {string} prefix - 配置前缀（可选）
 * @returns {Promise}
 */
export function getSystemConfigs(prefix = '') {
  return request({
    url: '/api/config',
    method: 'get',
    params: prefix ? { prefix } : {}
  })
}

/**
 * 获取单个配置
 * @param {string} key - 配置键名
 * @returns {Promise}
 */
export function getSystemConfig(key) {
  return request({
    url: `/api/config/${key}`,
    method: 'get'
  })
}

/**
 * 更新配置
 * @param {string} key - 配置键名
 * @param {Object} data - 配置数据
 * @param {any} data.value - 配置值
 * @param {string} data.config_type - 配置类型（可选）
 * @param {string} data.description - 配置描述（可选）
 * @returns {Promise}
 */
export function updateSystemConfig(key, data) {
  return request({
    url: `/api/config/${key}`,
    method: 'put',
    data
  })
}

/**
 * 获取监控相关配置
 * @returns {Promise}
 */
export function getMonitorConfigs() {
  return request({
    url: '/api/config/monitor',
    method: 'get'
  })
}

/**
 * 更新监控配置
 * @param {string} key - 配置键名
 * @param {Object} data - 配置数据
 * @param {any} data.value - 配置值
 * @returns {Promise}
 */
export function updateMonitorConfig(key, data) {
  return request({
    url: `/api/config/monitor/${key}`,
    method: 'put',
    data
  })
}

/**
 * 重置配置为默认值
 * @param {string} key - 配置键名
 * @returns {Promise}
 */
export function resetConfig(key) {
  return request({
    url: `/api/config/reset/${key}`,
    method: 'post'
  })
}

/**
 * 批量更新配置
 * @param {Object} configs - 配置键值对
 * @returns {Promise}
 */
export function batchUpdateConfigs(configs) {
  return request({
    url: '/api/config/batch',
    method: 'put',
    data: configs
  })
}
