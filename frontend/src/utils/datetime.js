/**
 * 时间处理工具函数
 */

/**
 * 格式化显示时间（后端已返回北京时间）
 * @param {string} timeString - 时间字符串（已经是北京时间）
 * @param {string} format - 格式化选项 'datetime' | 'date' | 'time'
 * @returns {string} 格式化后的时间字符串
 */
export function formatDateTime(timeString, format = 'datetime') {
  if (!timeString) return '-'

  try {
    // 后端已经返回北京时间字符串，直接使用
    if (format === 'datetime') {
      return timeString
    }

    // 如果需要其他格式，解析后重新格式化
    const date = new Date(timeString)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    switch (format) {
      case 'date':
        return `${year}-${month}-${day}`
      case 'time':
        return `${hours}:${minutes}:${seconds}`
      case 'datetime':
      default:
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  } catch (error) {
    console.error('时间格式化错误:', error)
    return timeString
  }
}

/**
 * 获取当前北京时间
 * @param {string} format - 格式化选项
 * @returns {string} 格式化后的当前北京时间
 */
export function getCurrentBeijingTime(format = 'datetime') {
  const now = new Date()
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000)
  const beijingTime = new Date(utcTime + (8 * 3600000))
  
  const year = beijingTime.getFullYear()
  const month = String(beijingTime.getMonth() + 1).padStart(2, '0')
  const day = String(beijingTime.getDate()).padStart(2, '0')
  const hours = String(beijingTime.getHours()).padStart(2, '0')
  const minutes = String(beijingTime.getMinutes()).padStart(2, '0')
  const seconds = String(beijingTime.getSeconds()).padStart(2, '0')
  
  switch (format) {
    case 'date':
      return `${year}-${month}-${day}`
    case 'time':
      return `${hours}:${minutes}:${seconds}`
    case 'datetime':
    default:
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }
}

/**
 * 计算时间差（相对时间）
 * @param {string} utcTimeString - UTC时间字符串
 * @returns {string} 相对时间描述
 */
export function getRelativeTime(utcTimeString) {
  if (!utcTimeString) return '-'
  
  try {
    const utcDate = new Date(utcTimeString + (utcTimeString.includes('Z') ? '' : 'Z'))
    const now = new Date()
    const diffMs = now.getTime() - utcDate.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffMinutes < 1) {
      return '刚刚'
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`
    } else if (diffHours < 24) {
      return `${diffHours}小时前`
    } else if (diffDays < 30) {
      return `${diffDays}天前`
    } else {
      return formatDateTime(utcTimeString, 'date')
    }
  } catch (error) {
    console.error('相对时间计算错误:', error)
    return utcTimeString
  }
}
