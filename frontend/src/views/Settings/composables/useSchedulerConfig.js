/**
 * 调度器配置管理逻辑
 */
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getSchedulerStatus,
  getWorkflowStatus,
  getScheduledJobs,
  getSchedulerConfig,
  updateSchedulerConfig,
  executeWorkflowPhase,
  pauseJob,
  resumeJob,
  triggerJob
} from '@/api/scheduler'

export function useSchedulerConfig() {
  // 响应式数据
  const loading = ref(false)
  const schedulerStatus = ref({
    running: false,
    lastExecution: null,
    currentTime: null
  })

  const basicConfig = reactive({
    schedulerEnabled: false,
    autoProcessOnStartup: false,
    autoSuspendWhenNoData: true,
    dataCheckEnabled: true,
    workflowIntervalMinutes: 3,
    batchSize: 100,
    minBatchSize: 1
  })

  const workflowPhases = ref([
    {
      key: 'data_sync',
      name: '数据同步',
      description: '从table1同步最新数据到questions和answers表',
      enabled: true,
      status: 'pending'
    },
    {
      key: 'classification',
      name: '问题分类',
      description: '调用分类API对新问题进行分类',
      enabled: true,
      status: 'pending'
    },
    {
      key: 'answer_generation',
      name: '答案生成',
      description: '调用AI API生成问题答案',
      enabled: true,
      status: 'pending'
    },
    {
      key: 'scoring',
      name: '评分处理',
      description: '对生成的答案进行质量评分',
      enabled: true,
      status: 'pending'
    }
  ])

  const scheduledTasks = ref([])

  // 自动刷新定时器
  let refreshTimer = null

  // 获取调度器状态
  const fetchSchedulerStatus = async () => {
    try {
      const response = await getSchedulerStatus()
      if (response.success) {
        schedulerStatus.value = {
          running: response.data.scheduler_running || false,
          lastExecution: response.data.workflow?.execution_history?.[0]?.timestamp || null,
          currentTime: response.data.current_time
        }
      }
    } catch (error) {
      console.error('获取调度器状态失败:', error)
    }
  }

  // 获取工作流状态
  const fetchWorkflowStatus = async () => {
    try {
      const response = await getWorkflowStatus()
      if (response.success && response.data.phases) {
        // 更新工作流阶段状态
        workflowPhases.value.forEach(phase => {
          const serverPhase = response.data.phases[phase.key]
          if (serverPhase) {
            phase.status = serverPhase.status
            phase.enabled = serverPhase.status !== 'disabled'
          }
        })
      }
    } catch (error) {
      console.error('获取工作流状态失败:', error)
    }
  }

  // 获取定时任务
  const fetchScheduledJobs = async () => {
    try {
      const response = await getScheduledJobs()
      if (response.success) {
        scheduledTasks.value = response.data.jobs || []
      }
    } catch (error) {
      console.error('获取定时任务失败:', error)
    }
  }

  // 获取配置信息
  const fetchConfig = async () => {
    try {
      const response = await getSchedulerConfig()
      if (response.success) {
        const config = response.data
        Object.assign(basicConfig, {
          schedulerEnabled: config.scheduler_enabled || false,
          autoProcessOnStartup: config.auto_process_on_startup || false,
          autoSuspendWhenNoData: config.auto_suspend_when_no_data !== false,
          dataCheckEnabled: config.data_check_enabled !== false,
          workflowIntervalMinutes: config.workflow_interval_minutes || 3,
          batchSize: config.batch_size || 100,
          minBatchSize: config.min_batch_size || 1
        })
      }
    } catch (error) {
      console.error('获取配置失败:', error)
    }
  }

  // 保存配置
  const saveConfig = async () => {
    loading.value = true
    try {
      const configData = {
        scheduler_enabled: basicConfig.schedulerEnabled,
        auto_process_on_startup: basicConfig.autoProcessOnStartup,
        auto_suspend_when_no_data: basicConfig.autoSuspendWhenNoData,
        data_check_enabled: basicConfig.dataCheckEnabled,
        workflow_interval_minutes: basicConfig.workflowIntervalMinutes,
        batch_size: basicConfig.batchSize,
        min_batch_size: basicConfig.minBatchSize
      }

      const response = await updateSchedulerConfig(configData)
      if (response.success) {
        ElMessage.success('配置保存成功')
        // 重新获取状态
        await fetchSchedulerStatus()
      } else {
        throw new Error(response.message || '保存失败')
      }
    } catch (error) {
      ElMessage.error(error.message || '配置保存失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 手动执行工作流阶段
  const executePhase = async (phase) => {
    try {
      const response = await executeWorkflowPhase(phase.key)
      if (response.success) {
        ElMessage.success(`${phase.name}执行成功`)
        await fetchWorkflowStatus()
      } else {
        throw new Error(response.message || '执行失败')
      }
    } catch (error) {
      ElMessage.error(`${phase.name}执行失败: ${error.message}`)
    }
  }

  // 任务操作
  const handleTaskAction = async (action, task) => {
    try {
      let response
      switch (action) {
        case 'pause':
          response = await pauseJob(task.id)
          break
        case 'resume':
          response = await resumeJob(task.id)
          break
        case 'trigger':
          response = await triggerJob(task.id)
          break
        default:
          throw new Error('未知操作')
      }

      if (response.success) {
        ElMessage.success('操作成功')
        await fetchScheduledJobs()
      } else {
        throw new Error(response.message || '操作失败')
      }
    } catch (error) {
      ElMessage.error(`操作失败: ${error.message}`)
    }
  }

  // 初始化数据
  const initData = async () => {
    loading.value = true
    try {
      await Promise.all([
        fetchSchedulerStatus(),
        fetchWorkflowStatus(),
        fetchScheduledJobs(),
        fetchConfig()
      ])
    } catch (error) {
      console.error('初始化数据失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 开始自动刷新
  const startAutoRefresh = () => {
    refreshTimer = setInterval(async () => {
      await fetchSchedulerStatus()
      await fetchWorkflowStatus()
    }, 30000) // 30秒刷新一次
  }

  // 停止自动刷新
  const stopAutoRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  // 组件挂载时初始化
  onMounted(() => {
    initData()
    startAutoRefresh()
  })

  // 组件卸载时清理
  onUnmounted(() => {
    stopAutoRefresh()
  })

  return {
    loading,
    schedulerStatus,
    basicConfig,
    workflowPhases,
    scheduledTasks,
    saveConfig,
    executePhase,
    handleTaskAction,
    refreshData: initData
  }
}
